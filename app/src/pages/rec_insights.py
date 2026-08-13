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
    page_title="Recommendation Insights",
    page_icon="🎯",
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

recommendations = get_api_data(
    "/recommendation/recommendations"
)

media = get_api_data("/media")


recommendations_df = pd.DataFrame(
    recommendations
)

media_df = pd.DataFrame(
    media
)


# ------------------------------------------------------
# CLEAN DATES
# ------------------------------------------------------

if (
    not recommendations_df.empty
    and "recommendation_date"
    in recommendations_df.columns
):
    recommendations_df[
        "recommendation_date"
    ] = pd.to_datetime(
        recommendations_df[
            "recommendation_date"
        ],
        errors="coerce"
    )


# ------------------------------------------------------
# MEDIA LABELS
# ------------------------------------------------------

MEDIA_LABELS = {
    "book": "Books",
    "tvshow": "TV Shows",
    "movie": "Movies",
    "game": "Games"
}

LABEL_TO_MEDIA_TYPE = {
    label: media_type
    for media_type, label
    in MEDIA_LABELS.items()
}


# ------------------------------------------------------
# CONNECT RECOMMENDATIONS TO MEDIA
# ------------------------------------------------------

if (
    not recommendations_df.empty
    and not media_df.empty
    and "media_id"
    in recommendations_df.columns
    and "media_id"
    in media_df.columns
):

    recommendation_media_df = (
        recommendations_df.merge(
            media_df[
                [
                    "media_id",
                    "title",
                    "media_type"
                ]
            ],
            on="media_id",
            how="left"
        )
    )

else:

    recommendation_media_df = (
        pd.DataFrame()
    )


# ------------------------------------------------------
# ADD READABLE MEDIA TYPE
# ------------------------------------------------------

if (
    not recommendation_media_df.empty
    and "media_type"
    in recommendation_media_df.columns
):

    recommendation_media_df[
        "category"
    ] = (
        recommendation_media_df[
            "media_type"
        ].map(
            MEDIA_LABELS
        )
    )


# ------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------

st.title(
    "🎯 Recommendation Insights"
)

st.caption(
    "Analyze recommendation activity, media trends, "
    "and the most frequently recommended content across The Queue."
)

st.divider()


# ------------------------------------------------------
# DETERMINE DATE RANGE
# ------------------------------------------------------

if (
    not recommendation_media_df.empty
    and "recommendation_date"
    in recommendation_media_df.columns
    and recommendation_media_df[
        "recommendation_date"
    ].notna().any()
):

    min_date = (
        recommendation_media_df[
            "recommendation_date"
        ]
        .min()
        .date()
    )

    max_date = (
        recommendation_media_df[
            "recommendation_date"
        ]
        .max()
        .date()
    )

else:

    min_date = date(
        2026,
        1,
        1
    )

    max_date = date.today()


# ------------------------------------------------------
# FILTERS
# ------------------------------------------------------

filter_col1, filter_col2, filter_col3, filter_col4 = (
    st.columns(
        [
            1,
            1,
            1.4,
            1
        ],
        gap="large"
    )
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

    selected_categories = (
        st.multiselect(
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
    )


with filter_col4:

    granularity = st.selectbox(
        "Granularity",
        options=[
            "Day",
            "Week",
            "Month"
        ],
        index=2
    )


# ------------------------------------------------------
# APPLY FILTERS
# ------------------------------------------------------

filtered_recommendations_df = (
    recommendation_media_df.copy()
)


selected_media_types = [
    LABEL_TO_MEDIA_TYPE[
        category
    ]
    for category
    in selected_categories
]


if not filtered_recommendations_df.empty:

    filtered_recommendations_df = (
        filtered_recommendations_df[
            (
                filtered_recommendations_df[
                    "recommendation_date"
                ].dt.date
                >= start_date
            )
            &
            (
                filtered_recommendations_df[
                    "recommendation_date"
                ].dt.date
                <= end_date
            )
        ]
    )

    filtered_recommendations_df = (
        filtered_recommendations_df[
            filtered_recommendations_df[
                "media_type"
            ].isin(
                selected_media_types
            )
        ]
    )


# ------------------------------------------------------
# SUMMARY METRICS
# ------------------------------------------------------

total_recommendations = len(
    filtered_recommendations_df
)


if (
    not filtered_recommendations_df.empty
    and "media_id"
    in filtered_recommendations_df.columns
):

    unique_media_recommended = (
        filtered_recommendations_df[
            "media_id"
        ].nunique()
    )

else:

    unique_media_recommended = 0


if unique_media_recommended > 0:

    recommendations_per_media = (
        total_recommendations
        / unique_media_recommended
    )

else:

    recommendations_per_media = 0


# Most recommended media type
if (
    not filtered_recommendations_df.empty
    and "category"
    in filtered_recommendations_df.columns
):

    category_counts = (
        filtered_recommendations_df[
            "category"
        ]
        .value_counts()
    )

    if not category_counts.empty:

        top_media_type = (
            category_counts.index[0]
        )

    else:

        top_media_type = "—"

else:

    top_media_type = "—"


# ------------------------------------------------------
# KPI CARDS
# ------------------------------------------------------

st.divider()

st.subheader(
    "Recommendation Summary"
)

metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(
        4,
        gap="large"
    )
)


with metric_col1:

    st.metric(
        "Total Recommendations",
        total_recommendations
    )


with metric_col2:

    st.metric(
        "Unique Media Recommended",
        unique_media_recommended
    )


with metric_col3:

    st.metric(
        "Recommendations / Media",
        f"{recommendations_per_media:.2f}"
    )


with metric_col4:

    st.metric(
        "Top Media Type",
        top_media_type
    )


# ------------------------------------------------------
# RECOMMENDATIONS OVER TIME
# ------------------------------------------------------

st.divider()

st.subheader(
    "Recommendations Over Time"
)


if filtered_recommendations_df.empty:

    st.info(
        "No recommendation activity is available "
        "for the selected filters."
    )

else:

    trend_df = (
        filtered_recommendations_df.copy()
    )


    # --------------------------------------------------
    # GRANULARITY
    # --------------------------------------------------

    if granularity == "Day":

        trend_df["period"] = (
            trend_df[
                "recommendation_date"
            ]
            .dt.floor("D")
        )


    elif granularity == "Week":

        trend_df["period"] = (
            trend_df[
                "recommendation_date"
            ]
            .dt.to_period(
                "W-SUN"
            )
            .dt.start_time
        )


    else:

        trend_df["period"] = (
            trend_df[
                "recommendation_date"
            ]
            .dt.to_period("M")
            .dt.to_timestamp()
        )


    # --------------------------------------------------
    # COUNT RECOMMENDATIONS
    # --------------------------------------------------

    trend_summary = (
        trend_df
        .groupby(
            "period"
        )
        .size()
        .reset_index(
            name="Recommendations"
        )
    )


    # --------------------------------------------------
    # ADD ZERO-ACTIVITY PERIODS
    # --------------------------------------------------

    if granularity == "Day":

        full_range = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )


    elif granularity == "Week":

        full_range = pd.date_range(
            start=(
                pd.Timestamp(
                    start_date
                )
                .to_period(
                    "W-SUN"
                )
                .start_time
            ),
            end=end_date,
            freq="W-MON"
        )


    else:

        full_range = pd.date_range(
            start=(
                pd.Timestamp(
                    start_date
                )
                .to_period("M")
                .start_time
            ),
            end=(
                pd.Timestamp(
                    end_date
                )
                .to_period("M")
                .start_time
            ),
            freq="MS"
        )


    full_range_df = pd.DataFrame(
        {
            "period": full_range
        }
    )


    trend_summary = (
        full_range_df.merge(
            trend_summary,
            on="period",
            how="left"
        )
        .fillna(
            {
                "Recommendations": 0
            }
        )
    )


    # --------------------------------------------------
    # DISPLAY LABEL
    # --------------------------------------------------

    if granularity == "Day":

        trend_summary[
            "Period"
        ] = (
            trend_summary[
                "period"
            ]
            .dt.strftime(
                "%b %d"
            )
        )


    elif granularity == "Week":

        trend_summary[
            "Period"
        ] = (
            trend_summary[
                "period"
            ]
            .dt.strftime(
                "%b %d"
            )
        )


    else:

        trend_summary[
            "Period"
        ] = (
            trend_summary[
                "period"
            ]
            .dt.strftime(
                "%b %Y"
            )
        )


    st.line_chart(
        trend_summary,
        x="Period",
        y="Recommendations"
    )


# ------------------------------------------------------
# LOWER SECTION
# ------------------------------------------------------

st.divider()

media_type_col, ranking_col = (
    st.columns(
        [
            1,
            1.5
        ],
        gap="large"
    )
)


# ======================================================
# RECOMMENDATIONS BY MEDIA TYPE
# ======================================================

with media_type_col:

    st.subheader(
        "Recommendations by Media Type"
    )


    if filtered_recommendations_df.empty:

        st.info(
            "No recommendation data available."
        )

    else:

        type_summary = (
            filtered_recommendations_df[
                "category"
            ]
            .value_counts()
            .reindex(
                [
                    "Books",
                    "TV Shows",
                    "Movies",
                    "Games"
                ],
                fill_value=0
            )
            .rename_axis(
                "Media Type"
            )
            .reset_index(
                name="Recommendations"
            )
        )


        # Only show selected categories
        type_summary = (
            type_summary[
                type_summary[
                    "Media Type"
                ].isin(
                    selected_categories
                )
            ]
        )


        st.bar_chart(
            type_summary,
            x="Media Type",
            y="Recommendations"
        )


# ======================================================
# MOST RECOMMENDED MEDIA
# ======================================================

with ranking_col:

    st.subheader(
        "Most Recommended Media"
    )


    if filtered_recommendations_df.empty:

        st.info(
            "No recommendation data available."
        )

    else:

        top_media_df = (
            filtered_recommendations_df
            .groupby(
                [
                    "media_id",
                    "title",
                    "category"
                ],
                dropna=False
            )
            .size()
            .reset_index(
                name="Recommendations"
            )
        )


        top_media_df = (
            top_media_df
            .sort_values(
                "Recommendations",
                ascending=False
            )
            .head(10)
            .reset_index(
                drop=True
            )
        )


        top_media_df.insert(
            0,
            "Rank",
            range(
                1,
                len(top_media_df) + 1
            )
        )


        top_media_df = (
            top_media_df.rename(
                columns={
                    "title": "Title",
                    "category": "Media Type"
                }
            )
        )


        top_media_df = (
            top_media_df[
                [
                    "Rank",
                    "Title",
                    "Media Type",
                    "Recommendations"
                ]
            ]
        )


        st.dataframe(
            top_media_df,
            use_container_width=True,
            hide_index=True
        )


# ------------------------------------------------------
# MOST RECOMMENDED TITLE
# ------------------------------------------------------

st.divider()

st.subheader(
    "Recommendation Highlights"
)


if filtered_recommendations_df.empty:

    st.info(
        "No recommendation highlights are available."
    )

else:

    title_counts = (
        filtered_recommendations_df
        .groupby(
            [
                "title",
                "category"
            ],
            dropna=False
        )
        .size()
        .reset_index(
            name="Recommendations"
        )
        .sort_values(
            "Recommendations",
            ascending=False
        )
    )


    if not title_counts.empty:

        most_recommended = (
            title_counts.iloc[0]
        )


        highlight_col1, highlight_col2, highlight_col3 = (
            st.columns(3)
        )


        with highlight_col1:

            st.metric(
                "Most Recommended Title",
                most_recommended[
                    "title"
                ]
            )


        with highlight_col2:

            st.metric(
                "Media Type",
                most_recommended[
                    "category"
                ]
            )


        with highlight_col3:

            st.metric(
                "Recommendations",
                int(
                    most_recommended[
                        "Recommendations"
                    ]
                )
            )
