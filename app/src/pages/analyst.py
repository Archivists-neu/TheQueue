import logging
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from modules.nav import SideBarLinks
from shared.apifuncs import GetApiData


logger = logging.getLogger(__name__)


# ------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------

st.set_page_config(
    page_title="Analyst Overview",
    page_icon="📊",
    layout="wide"
)

SideBarLinks()


# ------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------

users = GetApiData("/user")
media = GetApiData("/media")
reviews = GetApiData("/review/reviews")
friendships = GetApiData("/friendship/friendships")


# ------------------------------------------------------
# CONVERT API RESULTS TO DATAFRAMES
# ------------------------------------------------------

users_df = pd.DataFrame(users)
media_df = pd.DataFrame(media)
reviews_df = pd.DataFrame(reviews)
friendships_df = pd.DataFrame(friendships)


# ------------------------------------------------------
# CLEAN / PREPARE DATA
# ------------------------------------------------------

# Convert review dates to pandas datetime values.
if not reviews_df.empty and "review_date" in reviews_df.columns:
    reviews_df["review_date"] = pd.to_datetime(
        reviews_df["review_date"],
        errors="coerce"
    )

# Convert user creation dates.
if not users_df.empty and "date_account_creation" in users_df.columns:
    users_df["date_account_creation"] = pd.to_datetime(
        users_df["date_account_creation"],
        errors="coerce"
    )


# ------------------------------------------------------
# MEDIA TYPE LABELS
# ------------------------------------------------------

# Database value -> user-friendly dashboard label
MEDIA_LABELS = {
    "book": "Books",
    "tvshow": "TV Shows",
    "movie": "Movies",
    "game": "Games"
}

# Reverse dictionary:
# "Books" -> "book"
LABEL_TO_MEDIA_TYPE = {
    value: key
    for key, value in MEDIA_LABELS.items()
}


# Add readable media type names.
if not media_df.empty and "media_type" in media_df.columns:
    media_df["category"] = media_df["media_type"].map(
        MEDIA_LABELS
    )


# ------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------

st.title("📊 Analyst Overview")

if "first_name" in st.session_state:
    st.markdown(
        f"Welcome, **{st.session_state['first_name']}**."
    )
else:
    st.markdown(
        "Explore high-level activity and engagement across **The Queue**."
    )

st.divider()


# ------------------------------------------------------
# FILTER + CHART LAYOUT
# ------------------------------------------------------

filter_col, chart_col = st.columns(
    [1, 2.4],
    gap="large"
)


# ======================================================
# FILTERS
# ======================================================

with filter_col:

    st.subheader("Filters")

    # ------------------------------------------
    # Determine available review date range
    # ------------------------------------------

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

    start_date = st.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

    end_date = st.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

    st.markdown("##### Media Category")

    selected_categories = st.multiselect(
        "Select Categories",
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
        ],
        label_visibility="collapsed"
    )

    # ------------------------------------------
    # Metric
    # ------------------------------------------

    st.markdown("##### Metric")

    selected_metric = st.selectbox(
        "Metric",
        options=[
            "Reviews",
            "Review Likes",
            "Unique Reviewers"
        ],
        label_visibility="collapsed"
    )

    # ------------------------------------------
    # Granularity
    # ------------------------------------------

    st.markdown("##### Granularity")

    granularity = st.selectbox(
        "Granularity",
        options=[
            "Day",
            "Week",
            "Month"
        ],
        index=2,
        label_visibility="collapsed"
    )

# ------------------------------------------------------
# FILTER MEDIA
# ------------------------------------------------------

selected_media_types = [
    LABEL_TO_MEDIA_TYPE[category]
    for category in selected_categories
]

if not media_df.empty:

    filtered_media_df = media_df[
        media_df["media_type"].isin(selected_media_types)
    ].copy()

else:

    filtered_media_df = media_df.copy()


# ------------------------------------------------------
# CONNECT REVIEWS TO MEDIA
# ------------------------------------------------------

# The review table contains media_id.
# Joining it to the media data lets us determine whether
# each review belongs to a book, movie, TV show, or game.

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
                "media_type",
                "category"
            ]
        ],
        on="media_id",
        how="left"
    )

else:

    review_media_df = pd.DataFrame()


# ------------------------------------------------------
# APPLY FILTERS
# ------------------------------------------------------

if not review_media_df.empty:

    filtered_reviews_df = review_media_df.copy()

    # Date filter
    if "review_date" in filtered_reviews_df.columns:

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

    # Media category filter
    filtered_reviews_df = filtered_reviews_df[
        filtered_reviews_df["media_type"].isin(
            selected_media_types
        )
    ]

else:

    filtered_reviews_df = pd.DataFrame()


# ======================================================
# ACTIVITY CHART
# ======================================================

with chart_col:

    st.subheader(f"{selected_metric} Over Time")

    if filtered_reviews_df.empty:

        st.info(
            "No review activity is available for the selected filters."
        )

    else:

        chart_df = filtered_reviews_df.copy()

        # --------------------------------------
        # CREATE TIME PERIOD BASED ON GRANULARITY
        # --------------------------------------

        if granularity == "Day":

            chart_df["period"] = (
                chart_df["review_date"]
                .dt.floor("D")
            )

        elif granularity == "Week":

            # Weeks begin on Monday
            chart_df["period"] = (
                chart_df["review_date"]
                .dt.to_period("W-SUN")
                .dt.start_time
            )

        else:  # Month

            chart_df["period"] = (
                chart_df["review_date"]
                .dt.to_period("M")
                .dt.to_timestamp()
            )

        # --------------------------------------
        # CALCULATE SELECTED METRIC
        # --------------------------------------

        if selected_metric == "Reviews":

            period_data = (
                chart_df
                .groupby("period")
                .size()
                .reset_index(name="value")
            )

        elif selected_metric == "Review Likes":

            period_data = (
                chart_df
                .groupby("period")["likes"]
                .sum()
                .reset_index(name="value")
            )

        else:  # Unique Reviewers

            period_data = (
                chart_df
                .groupby("period")["user_id"]
                .nunique()
                .reset_index(name="value")
            )

        # --------------------------------------
        # INCLUDE PERIODS WITH ZERO ACTIVITY
        # --------------------------------------

        if granularity == "Day":

            full_range = pd.date_range(
                start=start_date,
                end=end_date,
                freq="D"
            )

        elif granularity == "Week":

            full_range = pd.date_range(
                start=pd.Timestamp(start_date).to_period("W-SUN").start_time,
                end=end_date,
                freq="W-MON"
            )

        else:

            full_range = pd.date_range(
                start=pd.Timestamp(start_date).to_period("M").start_time,
                end=pd.Timestamp(end_date).to_period("M").start_time,
                freq="MS"
            )

        full_range_df = pd.DataFrame({
            "period": full_range
        })

        period_data = (
            full_range_df
            .merge(
                period_data,
                on="period",
                how="left"
            )
            .fillna({"value": 0})
        )

        # --------------------------------------
        # FORMAT X-AXIS LABELS
        # --------------------------------------

        if granularity == "Day":

            period_data["label"] = (
                period_data["period"]
                .dt.strftime("%b %d")
            )

        elif granularity == "Week":

            period_data["label"] = (
                period_data["period"]
                .dt.strftime("%b %d")
            )

        else:

            period_data["label"] = (
                period_data["period"]
                .dt.strftime("%b %Y")
            )

        # --------------------------------------
        # CREATE CHART
        # --------------------------------------

        fig, ax = plt.subplots(
            figsize=(10, 4.5)
        )

        ax.plot(
            period_data["label"],
            period_data["value"],
            marker="o",
            linewidth=2
        )

        ax.set_xlabel(granularity)
        ax.set_ylabel(selected_metric)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.grid(
            axis="y",
            alpha=0.15
        )

        # Rotate labels when there are many data points.
        if len(period_data) > 12:
            plt.xticks(
                rotation=45,
                ha="right"
            )

        # Prevent an extremely crowded x-axis when viewing daily data.
        if len(period_data) > 20:

            step = max(
                1,
                len(period_data) // 10
            )

            for index, label in enumerate(
                ax.get_xticklabels()
            ):
                label.set_visible(
                    index % step == 0
                )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

# ------------------------------------------------------
# QUICK PLATFORM STATS
# ------------------------------------------------------

st.divider()

st.subheader("Platform Overview")

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:

    st.metric(
        "Total Users",
        len(users_df)
    )

with metric2:

    st.metric(
        "Media Catalog",
        len(media_df)
    )

with metric3:

    st.metric(
        "Total Reviews",
        len(reviews_df)
    )

with metric4:

    if (
        not friendships_df.empty
        and "status" in friendships_df.columns
    ):

        accepted_friendships = len(
            friendships_df[
                friendships_df["status"] == "accepted"
            ]
        )

    else:

        accepted_friendships = 0

    st.metric(
        "Friendships",
        accepted_friendships
    )


# ======================================================
# MEDIA SUMMARY TABLE
# ======================================================

st.divider()

st.subheader("Media Summary")

categories = [
    "Books",
    "TV Shows",
    "Movies",
    "Games"
]

summary = {
    "Metric": [
        "Reviews",
        "Catalog",
        "Review Likes",
        "Users Reviewed"
    ]
}


# ------------------------------------------------------
# CALCULATE EACH MEDIA CATEGORY
# ------------------------------------------------------

for category in categories:

    media_type = LABEL_TO_MEDIA_TYPE[category]

    # ------------------------------------------
    # Catalog count
    # ------------------------------------------

    if not media_df.empty:

        catalog_count = len(
            media_df[
                media_df["media_type"] == media_type
            ]
        )

    else:

        catalog_count = 0

    # ------------------------------------------
    # Review statistics
    # ------------------------------------------

    if not filtered_reviews_df.empty:

        category_reviews = filtered_reviews_df[
            filtered_reviews_df["media_type"]
            == media_type
        ]

        review_count = len(category_reviews)

        if "likes" in category_reviews.columns:
            review_likes = category_reviews[
                "likes"
            ].fillna(0).sum()
        else:
            review_likes = 0

        if "user_id" in category_reviews.columns:
            users_reviewed = category_reviews[
                "user_id"
            ].nunique()
        else:
            users_reviewed = 0

    else:

        review_count = 0
        review_likes = 0
        users_reviewed = 0

    summary[category] = [
        review_count,
        catalog_count,
        int(review_likes),
        users_reviewed
    ]


summary_df = pd.DataFrame(summary)


# ------------------------------------------------------
# ONLY DISPLAY SELECTED MEDIA TYPES
# ------------------------------------------------------

visible_columns = [
    "Metric"
] + selected_categories

if len(selected_categories) == 0:

    st.info(
        "Select at least one media category to view the summary."
    )

else:

    st.dataframe(
        summary_df[visible_columns],
        use_container_width=True,
        hide_index=True
    )
