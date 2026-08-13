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
    page_title="User Insights",
    page_icon="👥",
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
reviews = get_api_data("/review/reviews")
media = get_api_data("/media")


users_df = pd.DataFrame(users)
reviews_df = pd.DataFrame(reviews)
media_df = pd.DataFrame(media)


# ------------------------------------------------------
# CLEAN DATES
# ------------------------------------------------------

if (
    not users_df.empty
    and "dob" in users_df.columns
):
    users_df["dob"] = pd.to_datetime(
        users_df["dob"],
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


if (
    not reviews_df.empty
    and "review_date" in reviews_df.columns
):
    reviews_df["review_date"] = pd.to_datetime(
        reviews_df["review_date"],
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
# CALCULATE USER AGE
# ------------------------------------------------------

today = pd.Timestamp.today()


if (
    not users_df.empty
    and "dob" in users_df.columns
):

    users_df["age"] = (
        today.year
        - users_df["dob"].dt.year
        - (
            (
                today.month < users_df["dob"].dt.month
            )
            |
            (
                (
                    today.month == users_df["dob"].dt.month
                )
                &
                (
                    today.day < users_df["dob"].dt.day
                )
            )
        ).astype(int)
    )


# ------------------------------------------------------
# CREATE AGE GROUPS
# ------------------------------------------------------

if (
    not users_df.empty
    and "age" in users_df.columns
):

    users_df["age_group"] = pd.cut(
        users_df["age"],
        bins=[
            0,
            17,
            24,
            34,
            44,
            54,
            64,
            200
        ],
        labels=[
            "Under 18",
            "18–24",
            "25–34",
            "35–44",
            "45–54",
            "55–64",
            "65+"
        ]
    )


# ------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------

st.title("👥 User Insights")

st.caption(
    "Explore user demographics and engagement patterns across The Queue."
)

st.divider()


# ------------------------------------------------------
# DETERMINE REVIEW DATE RANGE
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

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(
    [1, 1, 1.3, 1.3],
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
        "Media Type",
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


with filter_col4:

    gender_options = []

    if (
        not users_df.empty
        and "gender" in users_df.columns
    ):
        gender_options = sorted(
            users_df["gender"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    selected_genders = st.multiselect(
        "Gender",
        options=gender_options,
        default=gender_options
    )


# ------------------------------------------------------
# AGE GROUP FILTER
# ------------------------------------------------------

age_group_options = [
    "Under 18",
    "18–24",
    "25–34",
    "35–44",
    "45–54",
    "55–64",
    "65+"
]

selected_age_groups = st.multiselect(
    "Age Group",
    options=age_group_options,
    default=age_group_options
)


# ------------------------------------------------------
# FILTER USERS
# ------------------------------------------------------

filtered_users_df = users_df.copy()


if (
    not filtered_users_df.empty
    and "gender" in filtered_users_df.columns
    and selected_genders
):

    filtered_users_df = filtered_users_df[
        filtered_users_df["gender"].isin(
            selected_genders
        )
    ]


if (
    not filtered_users_df.empty
    and "age_group" in filtered_users_df.columns
    and selected_age_groups
):

    filtered_users_df = filtered_users_df[
        filtered_users_df["age_group"]
        .astype(str)
        .isin(selected_age_groups)
    ]


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
# CONNECT REVIEW ACTIVITY TO USERS
# ------------------------------------------------------

if (
    not review_media_df.empty
    and not filtered_users_df.empty
    and "user_id" in review_media_df.columns
    and "user_id" in filtered_users_df.columns
):

    user_review_df = review_media_df.merge(
        filtered_users_df[
            [
                "user_id",
                "gender",
                "age",
                "age_group"
            ]
        ],
        on="user_id",
        how="inner"
    )

else:

    user_review_df = pd.DataFrame()


# ------------------------------------------------------
# APPLY REVIEW FILTERS
# ------------------------------------------------------

selected_media_types = [
    LABEL_TO_MEDIA_TYPE[category]
    for category in selected_categories
]


if not user_review_df.empty:

    user_review_df = user_review_df[
        (
            user_review_df["review_date"].dt.date
            >= start_date
        )
        &
        (
            user_review_df["review_date"].dt.date
            <= end_date
        )
    ]

    user_review_df = user_review_df[
        user_review_df["media_type"].isin(
            selected_media_types
        )
    ]


# ------------------------------------------------------
# TOP METRICS
# ------------------------------------------------------

st.divider()

st.subheader("User Summary")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(
    4,
    gap="large"
)


filtered_user_count = len(filtered_users_df)


if (
    not user_review_df.empty
    and "user_id" in user_review_df.columns
):

    active_reviewers = (
        user_review_df["user_id"].nunique()
    )

else:

    active_reviewers = 0


review_count = len(user_review_df)


if (
    review_count > 0
    and "likes" in user_review_df.columns
):

    avg_likes = (
        user_review_df["likes"]
        .fillna(0)
        .mean()
    )

else:

    avg_likes = 0


with metric_col1:

    st.metric(
        "Users in Segment",
        filtered_user_count
    )


with metric_col2:

    st.metric(
        "Active Reviewers",
        active_reviewers
    )


with metric_col3:

    st.metric(
        "Reviews",
        review_count
    )


with metric_col4:

    st.metric(
        "Avg Likes per Review",
        f"{avg_likes:.2f}"
    )


# ------------------------------------------------------
# DEMOGRAPHIC DISTRIBUTION
# ------------------------------------------------------

st.divider()

gender_col, age_col = st.columns(
    2,
    gap="large"
)


# ======================================================
# GENDER DISTRIBUTION
# ======================================================

with gender_col:

    st.subheader("Users by Gender")

    if (
        filtered_users_df.empty
        or "gender" not in filtered_users_df.columns
    ):

        st.info("No gender data available.")

    else:

        gender_counts = (
            filtered_users_df["gender"]
            .fillna("Not specified")
            .value_counts()
            .rename_axis("Gender")
            .reset_index(name="Users")
        )

        st.bar_chart(
            gender_counts,
            x="Gender",
            y="Users"
        )


# ======================================================
# AGE DISTRIBUTION
# ======================================================

with age_col:

    st.subheader("Users by Age Group")

    if (
        filtered_users_df.empty
        or "age_group" not in filtered_users_df.columns
    ):

        st.info("No age data available.")

    else:

        age_counts = (
            filtered_users_df["age_group"]
            .astype(str)
            .value_counts()
            .reindex(
                age_group_options,
                fill_value=0
            )
            .rename_axis("Age Group")
            .reset_index(name="Users")
        )

        st.bar_chart(
            age_counts,
            x="Age Group",
            y="Users"
        )


# ------------------------------------------------------
# ENGAGEMENT BY DEMOGRAPHIC
# ------------------------------------------------------

st.divider()

st.subheader("Engagement by Demographic")


demographic_view = st.selectbox(
    "Group By",
    options=[
        "Age Group",
        "Gender"
    ]
)


# ------------------------------------------------------
# BUILD DEMOGRAPHIC ENGAGEMENT TABLE
# ------------------------------------------------------

if user_review_df.empty:

    st.info(
        "No engagement data is available for the selected filters."
    )

else:

    if demographic_view == "Age Group":

        group_column = "age_group"
        display_column = "Age Group"

    else:

        group_column = "gender"
        display_column = "Gender"


    demographic_engagement = (
        user_review_df
        .groupby(
            group_column,
            observed=False
        )
        .agg(
            Users=("user_id", "nunique"),
            Reviews=("user_id", "size"),
            Avg_Likes=("likes", "mean")
        )
        .reset_index()
    )


    demographic_engagement = (
        demographic_engagement.rename(
            columns={
                group_column: display_column,
                "Avg_Likes": "Avg Likes / Review"
            }
        )
    )


    demographic_engagement[
        "Avg Likes / Review"
    ] = (
        demographic_engagement[
            "Avg Likes / Review"
        ]
        .fillna(0)
        .round(2)
    )


    st.dataframe(
        demographic_engagement,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------
# MEDIA PREFERENCES BY DEMOGRAPHIC
# ------------------------------------------------------

st.divider()

st.subheader("Media Engagement by Demographic")


if user_review_df.empty:

    st.info(
        "No media engagement data is available for the selected filters."
    )

else:

    media_demographic_df = user_review_df.copy()

    media_demographic_df["Media Type"] = (
        media_demographic_df["media_type"]
        .map(MEDIA_LABELS)
    )


    if demographic_view == "Age Group":

        group_column = "age_group"
        display_column = "Age Group"

    else:

        group_column = "gender"
        display_column = "Gender"


    media_summary = (
        media_demographic_df
        .groupby(
            [
                group_column,
                "Media Type"
            ],
            observed=False
        )
        .size()
        .reset_index(name="Reviews")
    )


    media_summary = media_summary.rename(
        columns={
            group_column: display_column
        }
    )


    media_pivot = (
        media_summary
        .pivot(
            index=display_column,
            columns="Media Type",
            values="Reviews"
        )
        .fillna(0)
        .reset_index()
    )


    st.dataframe(
        media_pivot,
        use_container_width=True,
        hide_index=True
    )
