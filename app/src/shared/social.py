"""
Shared data loading for the book-lover persona.

Several of Sam's pages need the same three joins:

    friendship -> who is my friend
    recommendation -> friendship -> media
    review -> user + media

The REST API returns each table on its own, so those joins happen here in
one place instead of being copy-pasted across every page.
"""

import logging
import random

import pandas as pd
import streamlit as st

from shared.apifuncs import (
    GetApiData,
    GetFriendshipsApi,
    GetLocationsApi,
    GetMediaSearchApi,
    GetReviewsApi,
    GetUserRecommendationsApi,
    GetUsersApi,
    PostApiData,
    PutApiData,
)


logger = logging.getLogger(__name__)


MEDIA_LABELS = {
    "book": "Books",
    "tvshow": "TV Shows",
    "movie": "Movies",
    "game": "Games"
}

LABEL_TO_MEDIA_TYPE = {
    label: media_type
    for media_type, label in MEDIA_LABELS.items()
}

MEDIA_CATEGORIES = list(MEDIA_LABELS.values())

MEDIA_JOIN_COLUMNS = [
    "media_id",
    "title",
    "media_type",
    "summary",
    "category",
    "genres",
]


# ------------------------------------------------------
# RAW TABLE LOADERS
# ------------------------------------------------------

# Streamlit reruns the whole script on every widget change, so without a
# cache each filter click refetches every table. 60s keeps the demo live.

@st.cache_data(ttl=60)
def LoadMedia():
    """media_id, title, media_type, summary + readable category."""
    media_df = pd.DataFrame(GetApiData("media"))

    if media_df.empty or "media_type" not in media_df.columns:
        return media_df

    media_df["category"] = media_df["media_type"].map(MEDIA_LABELS)

    if "genres" not in media_df.columns:
        media_df["genres"] = None

    return media_df


@st.cache_data(ttl=60)
def LoadUsers():
    """user_id + a single display name column."""
    users_df = pd.DataFrame(GetApiData("user"))

    if users_df.empty or "first_name" not in users_df.columns:
        return users_df

    users_df["display_name"] = (
        users_df["first_name"].fillna("")
        + " "
        + users_df["last_name"].fillna("")
    ).str.strip()

    return users_df


def FormatLocation(record):
    """
    "City, State" the way someone would say it out loud.

    Country is only tacked on when it is not the default, so the demo
    data does not read as "Boston, Massachusetts, United States".
    """
    parts = [record.get("city"), record.get("state")]

    if (record.get("country") or "United States") != "United States":
        parts.append(record.get("country"))

    return ", ".join(part for part in parts if part)


@st.cache_data(ttl=60)
def LoadLocations():
    """location_id + a single display_location column."""
    locations_df = pd.DataFrame(GetApiData(GetLocationsApi()))

    if locations_df.empty or "city" not in locations_df.columns:
        return locations_df

    locations_df["display_location"] = [
        FormatLocation(record)
        for record in locations_df.to_dict("records")
    ]

    return locations_df.sort_values("display_location").reset_index(drop=True)


def LoadLocationOptions():
    locations_df = LoadLocations()

    if locations_df.empty:
        return {}

    return {
        record["display_location"]: int(record["location_id"])
        for record in locations_df.to_dict("records")
    }


@st.cache_data(ttl=60)
def LoadAllReviews():
    """Every review, with review_date parsed."""
    reviews_df = pd.DataFrame(GetApiData(GetReviewsApi()))

    if reviews_df.empty or "review_date" not in reviews_df.columns:
        return reviews_df

    reviews_df["review_date"] = pd.to_datetime(
        reviews_df["review_date"],
        errors="coerce"
    )

    return reviews_df


@st.cache_data(ttl=60)
def LoadFriendships(user_id):
    """
    Friendships this user is part of, flattened so the other person is
    always in friend_id / friend_name regardless of who sent the request.
    """
    friendships_df = pd.DataFrame(GetApiData(GetFriendshipsApi()))

    if friendships_df.empty or "friendship_id" not in friendships_df.columns:
        return pd.DataFrame()

    rows = []

    for _, friendship in friendships_df.iterrows():

        if friendship["requester_id"] == user_id:
            friend_id = friendship["addressee_id"]
            friend_name = friendship["addressee_name"]

        elif friendship["addressee_id"] == user_id:
            friend_id = friendship["requester_id"]
            friend_name = friendship["requester_name"]

        else:
            # Someone else's friendship.
            continue

        rows.append({
                "friendship_id": friendship["friendship_id"],
                "friend_id": friend_id,
                "friend_name": friend_name,
                "status": friendship["status"],
                "date_requested": friendship["date_requested"],
                "date_accepted": friendship["date_accepted"]
            }
        )

    return pd.DataFrame(rows)


# ------------------------------------------------------
# JOINED VIEWS
# ------------------------------------------------------

def LoadFriends(user_id, status="accepted"):
    """Confirmed friends only, unless a different status is asked for."""
    friendships_df = LoadFriendships(user_id)

    if friendships_df.empty or status is None:
        return friendships_df

    return friendships_df[
        friendships_df["status"] == status
    ].reset_index(drop=True)


def LoadFriendRecommendations(user_id):
    """
    Media recommended to this user by their friends.

    A recommendation points at a friendship rather than a person, so the
    sender comes from whichever side of that friendship is not this user.
    """
    recommendations = GetApiData(GetUserRecommendationsApi(user_id))
    recs_df = pd.DataFrame(recommendations)

    if recs_df.empty or "media_id" not in recs_df.columns:
        return pd.DataFrame()

    recs_df["recommendation_date"] = pd.to_datetime(
        recs_df["recommendation_date"],
        errors="coerce"
    )

    media_df = LoadMedia()

    if media_df.empty or "media_id" not in media_df.columns:
        return pd.DataFrame()

    recs_df = recs_df.merge(
        media_df[MEDIA_JOIN_COLUMNS],
        on="media_id",
        how="left"
    )

    friendships_df = LoadFriendships(user_id)

    if not friendships_df.empty:
        recs_df = recs_df.merge(
            friendships_df[["friendship_id", "friend_name"]],
            on="friendship_id",
            how="left"
        )
        recs_df = recs_df.rename(columns={"friend_name": "From"})

    else:
        recs_df["From"] = "Unknown"

    recs_df["From"] = recs_df["From"].fillna("Unknown")

    return recs_df.sort_values(
        "recommendation_date",
        ascending=False
    ).reset_index(drop=True)


def LoadReviewsForUsers(user_ids):
    """
    Reviews written by the given users, joined to media and reviewer name.

    Used for both "my reviews" and "my friends' reviews" -- the only
    difference is which ids get passed in.
    """
    reviews_df = LoadAllReviews()

    if reviews_df.empty or "user_id" not in reviews_df.columns:
        return pd.DataFrame()

    reviews_df = reviews_df[reviews_df["user_id"].isin(list(user_ids))]

    if reviews_df.empty:
        return pd.DataFrame()

    media_df = LoadMedia()

    if not media_df.empty and "media_id" in media_df.columns:
        reviews_df = reviews_df.merge(
            media_df[MEDIA_JOIN_COLUMNS],
            on="media_id",
            how="left"
        )

    users_df = LoadUsers()

    if not users_df.empty and "display_name" in users_df.columns:
        reviews_df = reviews_df.merge(
            users_df[["user_id", "display_name"]],
            on="user_id",
            how="left"
        )

    return reviews_df.sort_values(
        "review_date",
        ascending=False
    ).reset_index(drop=True)


def LoadMediaById(media_id):
    """
    One piece of media, or None if the id does not exist.

    /media/<id> returns a single object rather than a list.
    """
    record = GetApiData(GetMediaSearchApi(media_id=media_id))

    if not record or not isinstance(record, dict):
        return None

    media_type = record.get("media_type") or ""
    record["category"] = MEDIA_LABELS.get(media_type, media_type)

    return record


def LoadReviewsForMedia(media_id):
    """Every review of one piece of media, with the reviewer's name."""
    reviews_df = LoadAllReviews()

    if reviews_df.empty or "media_id" not in reviews_df.columns:
        return pd.DataFrame()

    reviews_df = reviews_df[reviews_df["media_id"] == media_id]

    if reviews_df.empty:
        return pd.DataFrame()

    users_df = LoadUsers()

    if not users_df.empty and "display_name" in users_df.columns:
        reviews_df = reviews_df.merge(
            users_df[["user_id", "display_name"]],
            on="user_id",
            how="left"
        )

    return reviews_df.sort_values(
        "likes",
        ascending=False
    ).reset_index(drop=True)


def DescribeGenre(row):
    """
    Genre label for a list item, falling back to the media type when a
    title has not been linked to any genre yet.
    """
    genres = row.get("genres")

    if genres and str(genres).lower() != "nan":
        return str(genres)

    return row.get("category") or "Unknown"


# ------------------------------------------------------
# FRIEND REQUESTS
# ------------------------------------------------------

# This is mock data, so a request resolves itself instead of waiting on a
# real person. Most are accepted; the rest are declined so the UI has to
# handle both outcomes.
DECLINE_CHANCE = 0.10


def SendFriendRequest(requester_id, addressee_id):
    """Create a pending friendship. Returns (ok, body)."""
    ok, body = PostApiData(
        GetFriendshipsApi(),
        {
            "requester_id": int(requester_id),
            "addressee_id": int(addressee_id),
            "status": "pending",
        },
    )

    LoadFriendships.clear()

    return ok, body


def ResolveFriendRequest(friendship_id):
    """
    Settle a pending request the way a real person eventually would.

    Returns (ok, status, body) where status is "accepted" or "declined".
    """
    status = "declined" if random.random() < DECLINE_CHANCE else "accepted"

    ok, body = PutApiData(
        GetFriendshipsApi(friendship_id),
        {"status": status},
    )

    LoadFriendships.clear()

    return ok, status, body


# ------------------------------------------------------
# SIGNING IN
# ------------------------------------------------------

def FindUserByEmail(email):
    """
    One account by email, or None.

    The /user email filter is a LIKE match, so the exact address is picked
    out here rather than trusting the first row back.
    """
    email = (email or "").strip()

    if not email:
        return None

    records = GetApiData(GetUsersApi(), params={"email": email})

    if not records:
        return None

    for record in records:
        if (record.get("email") or "").lower() == email.lower():
            return record

    return None


def FindUserById(user_id):
    """One account by id, or None. /user has no by-id GET route."""
    records = GetApiData(GetUsersApi())

    for record in records or []:
        if record.get("user_id") == user_id:
            return record

    return None


def SignInUser(record):
    """
    Populate the session for the book-lover persona straight from a
    database row, so the profile shows the account the data belongs to.
    """
    st.session_state["authenticated"] = True
    st.session_state["role"] = "book_lover"
    st.session_state["user_id"] = int(record["user_id"])
    st.session_state["first_name"] = record.get("first_name") or ""
    st.session_state["last_name"] = record.get("last_name") or ""
    st.session_state["email"] = record.get("email") or ""
    st.session_state["status"] = record.get("account_status") or "offline"

    # Friendships are cached per user, so drop them when the account changes.
    LoadFriendships.clear()


def RequireUserId():
    """
    Read the logged-in user's id, or stop the page with a clear message.

    Home.py seeds this and create-user.py overwrites it once the API hands
    back a real id.
    """
    user_id = st.session_state.get("user_id")

    if user_id is None:
        st.warning(
            "No account is loaded. Head back to the home page and log in."
        )
        st.stop()

    return user_id
