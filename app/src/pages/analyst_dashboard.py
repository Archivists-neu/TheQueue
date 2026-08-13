import logging
import os
from datetime import date

import pandas as pd
import requests
import streamlit as st

from modules.nav import SideBarLinks


logger = logging.getLogger(__name__)


# ------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------

st.set_page_config(
    page_title="Performance Dashboard",
    page_icon="📈",
    layout="wide"
)

SideBarLinks()


# ------------------------------------------------------
# API CONFIGURATION
# ------------------------------------------------------

API_URL = os.getenv("API_URL", "http://api:4000")


def get_api_data(endpoint):
    """
    Send a GET request to the Flask API.
    Returns an empty list if the request fails.
    """
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        logger.error(
            f"API request failed for {endpoint}: {e}"
        )

        return []


# ------------------------------------------------------
# LOAD API DATA
# ------------------------------------------------------

users = get_api_data("/user")
media = get_api_data("/media")
reviews = get_api_data("/review/reviews")
friendships = get_api_data("/friendship/friendships")


users_df = pd.DataFrame(users)
media_df = pd.DataFrame(media)
reviews_df = pd.DataFrame(reviews)
friendships_df = pd.DataFrame(friendships)


# ------------------------------------------------------
# CLEAN DATES
# ------------------------------------------------------

if (
    not reviews_df.empty
    and "review_date" in reviews_df.columns
):
    reviews_df["review_date"] = pd.to_datetime(
        reviews_df["review_date"],
        errors="coerce"
    )


if (
    not users_df.empty
    and "date_account_creation" in users_df.columns
):
    users_df["date_account_creation"] = pd.to_datetime(
        users_df["date_account_creation"],
        errors="coerce"
    )


# ------------------------------------------------------
# MEDIA TYPE LABELS
# ------------------------------------------------------

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


# ------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------

st.title("📈 Performance Dashboard")

st.caption(
    "Evaluate engagement and interaction performance across The Queue."
)

st.divider()


# ------------------------------------------------------
# DATE RANGE
# ------------------------------------------------------

if (
    not reviews_df.empty
    and "review_date" in reviews_df.columns
    and reviews_df["review_date"].notna().any()
):

    min_date = reviews_df["review_date"].min().date()
    max_date = reviews_df["review_date"].max().date()

else:

    min_date = date(2026, 1, 1)
    max_date = date.today()


# ------------------------------------------------------
# FILTERS
# ------------------------------------------------------

filter_col1, filter_col2, filter_col3 = st.columns(
    [1, 1, 1.4],
    gap="large"
)


with filter_col1:

    start_date = st.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )


with filter_col2:

    end_date = st.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )


with filter_col3:

    selected_categories = st.multiselect(
        "Media Category",
        options=[
            "Books",
            "TV Shows",
            "Movies",
            "Games"
        ],
        default=[
            "Books",
            "TV Shows",
            "Movies",
            "Games"
        ]
    )


# ------------------------------------------------------
# CONNECT REVIEWS TO MEDIA
# ------------------------------------------------------

if (
    not reviews_df.empty
    and not media_df.empty
    and "media_id" in reviews_df.columns
    and "media_id" in media_df.columns
):

    review_media_df = reviews_df.merge(
        media_df[
            [
                "media_id",
                "media_type"
            ]
        ],
        on="media_id",
        how="left"
    )

else:

    review_media_df = pd.DataFrame()


# ------------------------------------------------------
# APPLY DATE + MEDIA FILTERS
# ------------------------------------------------------

filtered_reviews_df = review_media_df.copy()

selected_media_types = [
    LABEL_TO_MEDIA_TYPE[category]
    for category in selected_categories
]


if not filtered_reviews_df.empty:

    filtered_reviews_df = filtered_reviews_df[
        (
            filtered_reviews_df["review_date"].dt.date
            >= start_date
        )
        &
        (
            filtered_reviews_df["review_date"].dt.date
            <= end_date
        )
    ]

    filtered_reviews_df = filtered_reviews_df[
        filtered_reviews_df["media_type"].isin(
            selected_media_types
        )
    ]


# ------------------------------------------------------
# PERFORMANCE METRICS
# ------------------------------------------------------

review_count = len(filtered_reviews_df)


if (
    not filtered_reviews_df.empty
    and "user_id" in filtered_reviews_df.columns
):

    unique_reviewers = (
        filtered_reviews_df["user_id"].nunique()
    )

else:

    unique_reviewers = 0


# Reviews per active reviewer
if unique_reviewers > 0:

    reviews_per_reviewer = (
        review_count / unique_reviewers
    )

else:

    reviews_per_reviewer = 0


# Average likes per review
if (
    review_count > 0
    and "likes" in filtered_reviews_df.columns
):

    avg_likes_per_review = (
        filtered_reviews_df["likes"]
        .fillna(0)
        .mean()
    )

else:

    avg_likes_per_review = 0


# ------------------------------------------------------
# FRIENDSHIP ACCEPTANCE RATE
# ------------------------------------------------------

if (
    not friendships_df.empty
    and "status" in friendships_df.columns
):

    total_friendships = len(friendships_df)

    accepted_friendships = len(
        friendships_df[
            friendships_df["status"] == "accepted"
        ]
    )

    if total_friendships > 0:

        friendship_acceptance_rate = (
            accepted_friendships
            / total_friendships
            * 100
        )

    else:

        friendship_acceptance_rate = 0

else:

    total_friendships = 0
    accepted_friendships = 0
    friendship_acceptance_rate = 0


# ------------------------------------------------------
# % OF USERS WHO REVIEWED
# ------------------------------------------------------

total_users = len(users_df)


if total_users > 0:

    reviewer_percentage = (
        unique_reviewers
        / total_users
        * 100
    )

else:

    reviewer_percentage = 0


# ------------------------------------------------------
# TOP PERFORMANCE CARDS
# ------------------------------------------------------

st.divider()

st.subheader("User Engagement")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(
    4,
    gap="large"
)


with metric_col1:

    st.metric(
        label="Reviews per Reviewer",
        value=f"{reviews_per_reviewer:.2f}"
    )


with metric_col2:

    st.metric(
        label="Avg Likes per Review",
        value=f"{avg_likes_per_review:.2f}"
    )


with metric_col3:

    st.metric(
        label="Friendship Acceptance Rate",
        value=f"{friendship_acceptance_rate:.1f}%"
    )

with metric_col4:

    st.metric(
        label="% of Users Who Reviewed",
        value=f"{reviewer_percentage:.1f}%"
    )


# ------------------------------------------------------
# TABLE SECTION
# ------------------------------------------------------

st.divider()

media_col, engagement_col = st.columns(
    [1.4, 1],
    gap="large"
)

# ======================================================
# MEDIA TYPE PERFORMANCE
# ======================================================

with media_col:

    st.subheader("Media Type Performance")

    media_performance_rows = []

    for category in [
        "Books",
        "TV Shows",
        "Movies",
        "Games"
    ]:

        media_type = LABEL_TO_MEDIA_TYPE[category]

        category_reviews = filtered_reviews_df[
            filtered_reviews_df["media_type"]
            == media_type
        ]

        category_review_count = len(
            category_reviews
        )


        if (
            not category_reviews.empty
            and "user_id" in category_reviews.columns
        ):

            category_reviewers = (
                category_reviews["user_id"].nunique()
            )

        else:

            category_reviewers = 0


        if category_reviewers > 0:

            category_reviews_per_reviewer = (
                category_review_count
                / category_reviewers
            )

        else:

            category_reviews_per_reviewer = 0


        if (
            category_review_count > 0
            and "likes" in category_reviews.columns
        ):

            category_avg_likes = (
                category_reviews["likes"]
                .fillna(0)
                .mean()
            )

        else:

            category_avg_likes = 0


        media_performance_rows.append(
            {
                "Media Type": category,
                "Reviews / Reviewer":
                    round(
                        category_reviews_per_reviewer,
                        2
                    ),
                "Avg Likes / Review":
                    round(
                        category_avg_likes,
                        2
                    )
            }
        )


    media_performance_df = pd.DataFrame(
        media_performance_rows
    )

    

    # Only show categories currently selected
    media_performance_df = (
        media_performance_df[
            media_performance_df[
                "Media Type"
            ].isin(
                selected_categories
            )
        ]
    )


    st.dataframe(
    media_performance_df,
    hide_index=True
    )


# ------------------------------------------------------
# SUPPORTING COUNTS
# ------------------------------------------------------

st.divider()

st.subheader("Supporting Activity")

support_col1, support_col2, support_col3 = st.columns(3)


with support_col1:

    st.metric(
        "Reviews in Period",
        review_count
    )


with support_col2:

    st.metric(
        "Unique Reviewers",
        unique_reviewers
    )


with support_col3:

    st.metric(
        "Accepted Friendships",
        accepted_friendships
    )
