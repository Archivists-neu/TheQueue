import logging
logger = logging.getLogger(__name__)

import time

import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi
from shared.social import (
    LABEL_TO_MEDIA_TYPE,
    MEDIA_CATEGORIES,
    LoadFriends,
    LoadFriendships,
    LoadReviewsForUsers,
    RequireUserId,
    ResolveFriendRequest,
    SendFriendRequest,
)

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# Friends")

user_id = RequireUserId()

# Columns where a plain title-case of the snake_case name reads badly.
headerNames = {
    "user_id": "User ID",
    "dob": "Date of Birth",
    "location_id": "Location ID",
}

# Internal keys that mean nothing to someone browsing for friends.
hiddenColumns = {
    "user_uuid",
    "location_id",
    "date_account_deletion",
}


def PrettyColumns(records):
    """API records -> DataFrame with human-readable column names."""
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df = df[[c for c in df.columns if c not in hiddenColumns]]
    df.columns = [headerNames.get(c, c.replace("_", " ").title()) for c in df.columns]
    return df


def RenderPeople(records, viewer_id):
    """
    One row per person, with an Add Friend button when there is no
    existing friendship between them and the viewer.
    """
    existing_df = LoadFriendships(viewer_id)

    if existing_df.empty:
        existing_status = {}
    else:
        existing_status = dict(
            zip(existing_df["friend_id"], existing_df["status"])
        )

    for person in records:

        person_id = person["user_id"]

        display_name = (
            f"{person.get('first_name', '')} "
            f"{person.get('last_name', '')}"
        ).strip()

        name_col, action_col = st.columns([3, 1], vertical_alignment="center")

        with name_col:
            st.markdown(f"**{display_name}**")
            st.caption(person.get("email") or "No email on file")

        with action_col:

            if person_id == viewer_id:
                st.caption("This is you")

            elif person_id in existing_status:
                st.caption(existing_status[person_id].title())

            elif st.button(
                "Add Friend",
                key=f"add_friend_{person_id}",
                use_container_width=True,
            ):
                ok, body = SendFriendRequest(viewer_id, person_id)

                if not ok:
                    st.error(f"Could not send the request: {body}")

                else:
                    # Mock data, so nobody is on the other end to answer.
                    # Hold on pending for a beat, then settle it.
                    with st.spinner(f"Request sent to {display_name} — pending…"):
                        time.sleep(3)

                        resolved_ok, resolved_status, resolved_body = (
                            ResolveFriendRequest(body["friendship_id"])
                        )

                    if not resolved_ok:
                        st.session_state["friend_request_result"] = (
                            "error",
                            f"Request sent, but it could not be settled: "
                            f"{resolved_body}",
                        )

                    elif resolved_status == "accepted":
                        st.session_state["friend_request_result"] = (
                            "success",
                            f"{display_name} accepted your friend request.",
                        )

                    else:
                        st.session_state["friend_request_result"] = (
                            "warning",
                            f"{display_name} declined your friend request.",
                        )

                    st.rerun()


# Outcome of the last friend request. Sits above the accordions so it is
# visible no matter which one is open.
if st.session_state.get("friend_request_result"):
    kind, message = st.session_state.pop("friend_request_result")

    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.error(message)


friends_df = LoadFriends(user_id)


# ======================================================
# MY FRIENDS
# ======================================================

if friends_df.empty:
    friends_label = "My Friends"
else:
    friends_label = f"My Friends ({len(friends_df)})"


with st.expander(friends_label, expanded=False):

    if friends_df.empty:
        st.info("You have no confirmed friends yet.")

    else:
        friends_display_df = friends_df.rename(
            columns={
                "friend_name": "Friend",
                "status": "Status",
                "date_accepted": "Friends Since",
            }
        )

        st.dataframe(
            friends_display_df[["Friend", "Status", "Friends Since"]],
            use_container_width=True,
            hide_index=True,
        )


# ======================================================
# WHAT MY FRIENDS ARE REVIEWING
# ======================================================

if friends_df.empty:
    friend_reviews_df = pd.DataFrame()
else:
    friend_reviews_df = LoadReviewsForUsers(friends_df["friend_id"].tolist())


if friend_reviews_df.empty:
    reviews_label = "What My Friends Are Saying"
else:
    reviews_label = (
        f"What My Friends Are Saying ({len(friend_reviews_df)})"
    )


with st.expander(reviews_label, expanded=False):

    st.caption(
        "Reviews written by your confirmed friends. "
        "Sort by likes to see what landed best."
    )

    if friends_df.empty:
        st.info("Add some friends to see what they are reviewing.")

    elif friend_reviews_df.empty:
        st.info("None of your friends have written a review yet.")

    else:

        # ------------------------------------------
        # FILTERS
        # ------------------------------------------

        filter_col1, filter_col2 = st.columns([1, 1.4], gap="large")

        with filter_col1:
            friend_options = sorted(
                friend_reviews_df["display_name"].dropna().unique().tolist()
            )

            selected_friends = st.multiselect(
                "Friend",
                options=friend_options,
                default=friend_options,
            )

        with filter_col2:
            selected_categories = st.multiselect(
                "Media Type",
                options=MEDIA_CATEGORIES,
                default=MEDIA_CATEGORIES,
            )

        selected_media_types = [
            LABEL_TO_MEDIA_TYPE[category]
            for category in selected_categories
        ]

        filtered_reviews_df = friend_reviews_df.copy()

        if selected_friends:
            filtered_reviews_df = filtered_reviews_df[
                filtered_reviews_df["display_name"].isin(selected_friends)
            ]

        if "media_type" in filtered_reviews_df.columns:
            filtered_reviews_df = filtered_reviews_df[
                filtered_reviews_df["media_type"].isin(selected_media_types)
            ]

        # ------------------------------------------
        # SUMMARY
        # ------------------------------------------

        metric_col1, metric_col2, metric_col3 = st.columns(3, gap="large")

        with metric_col1:
            st.metric("Reviews", len(filtered_reviews_df))

        with metric_col2:
            if filtered_reviews_df.empty:
                st.metric("Friends Reviewing", 0)
            else:
                st.metric(
                    "Friends Reviewing",
                    filtered_reviews_df["display_name"].nunique(),
                )

        with metric_col3:
            if filtered_reviews_df.empty:
                st.metric("Top Pick", "—")
            else:
                top_row = filtered_reviews_df.sort_values(
                    "likes", ascending=False
                ).iloc[0]
                st.metric("Top Pick", top_row["title"])

        # ------------------------------------------
        # REVIEW TABLE
        # ------------------------------------------

        if filtered_reviews_df.empty:
            st.info("No reviews match the selected filters.")

        else:
            display_df = filtered_reviews_df.copy()

            display_df["Reviewed"] = (
                display_df["review_date"].dt.strftime("%b %d, %Y")
            )

            display_df = display_df.rename(
                columns={
                    "display_name": "Friend",
                    "title": "Title",
                    "category": "Media Type",
                    "review_comment": "Review",
                    "likes": "Likes",
                }
            )

            display_df = display_df.sort_values("Likes", ascending=False)

            st.dataframe(
                display_df[
                    ["Friend", "Title", "Media Type", "Review", "Likes", "Reviewed"]
                ],
                use_container_width=True,
                hide_index=True,
            )


# ======================================================
# FIND PEOPLE
# ======================================================

with st.expander("Find People", expanded=True):

    with st.form("user_search_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
        with col2:
            email = st.text_input("Email")

        submitted = st.form_submit_button("Search")

    # Keep the query in session state so results survive the rerun that a
    # friend request triggers.
    if submitted:
        st.session_state["people_search"] = {"name": name, "email": email}

    people_search = st.session_state.get("people_search")

    if people_search:
        params = {
            key: value
            for key, value in people_search.items()
            if value
        }

        try:
            response = requests.get(GetUsersApi(), params=params, timeout=10)
            search_results = response.json()

            st.write("### Search Results")
            if search_results:
                RenderPeople(search_results, user_id)

            else:
                st.write("No users found matching your search.")
        except requests.exceptions.RequestException as e:
            st.write("**Important**: Could not connect to sample API, so no search results to show.")
            logger.error(f"Error searching users: {e}")


# ======================================================
# EVERYONE ON THE PLATFORM
# ======================================================

with st.expander("All Users", expanded=False):

    data = {}

    try:
        data = requests.get(GetUsersApi(), timeout=10).json()
    except requests.exceptions.RequestException as e:
        st.write("**Important**: Could not connect to sample API, so using dummy data.")
        logger.error(f"Error loading users: {e}")
        data = {}

    st.dataframe(PrettyColumns(data), hide_index=True)


st.divider()

if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
