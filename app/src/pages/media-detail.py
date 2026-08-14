"""
Detail view for a single piece of media.

Reached by clicking a row in one of the tables on media-search.py, never
from the sidebar -- the caller puts a media_id in session state and
switches here. One file serves every title; only the id changes.
"""

import logging

import streamlit as st

from modules.nav import SideBarLinks
from shared.apifuncs import GetReviewsApi, PostApiData
from shared.social import (
    LoadAllReviews,
    LoadFriendRecommendations,
    LoadFriends,
    LoadMediaById,
    LoadReviewsForMedia,
    RequireUserId,
)
from shared.review import ReviewDialog

logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Media Detail",
    page_icon="📖",
    layout="wide"
)

SideBarLinks()

user_id = RequireUserId()


# ------------------------------------------------------
# WHICH TITLE ARE WE LOOKING AT
# ------------------------------------------------------

media_id = st.session_state.get("selected_media_id")

if media_id is None:
    st.title("📖 Media Detail")
    st.info("Pick a title from Media Search to see its details.")

    if st.button("← Media Search"):
        st.switch_page("pages/media-search.py")

    st.stop()


media = LoadMediaById(media_id)

if media is None:
    st.title("📖 Media Detail")
    st.error(f"Could not load media #{media_id}.")

    if st.button("← Media Search"):
        st.switch_page("pages/media-search.py")

    st.stop()


# ------------------------------------------------------
# HEADER
# ------------------------------------------------------


title_col, mid_col, action_col = st.columns(
    [4, 1, 1],
    gap="small",
    vertical_alignment="bottom",
)

with title_col:
    st.title(f"📖 {media['title']}")
    st.caption(media.get("category") or "Unknown type")

with mid_col:
    if st.button("← Back", type="secondary", use_container_width=True):
        st.switch_page("pages/media-search.py")


with action_col:
    if st.button(
        "✎ Write Review",
        type="primary",
        use_container_width=True,
    ):
        ReviewDialog(user_id, media_id, media["title"])


if st.session_state.get("review_created"):
    st.success(st.session_state.pop("review_created"))

st.divider()


info_col, summary_col = st.columns([1, 2], gap="large")


with info_col:

    st.metric("Media Type", media.get("category") or "—")

    release_date = media.get("release_date")

    st.metric(
        "Released",
        release_date if release_date else "—"
    )


with summary_col:

    st.subheader("Summary")
    st.write(media.get("summary") or "No summary available.")


# ------------------------------------------------------
# DID A FRIEND RECOMMEND THIS
# ------------------------------------------------------

st.divider()

st.subheader("Recommended To You")

recs_df = LoadFriendRecommendations(user_id)


if recs_df.empty or "media_id" not in recs_df.columns:

    st.info("No friend has recommended this to you.")

else:

    media_recs_df = recs_df[recs_df["media_id"] == media_id]

    if media_recs_df.empty:

        st.info("No friend has recommended this to you.")

    else:

        for _, recommendation in media_recs_df.iterrows():

            sent = recommendation["recommendation_date"]

            sent_label = (
                sent.strftime("%b %d, %Y")
                if sent is not None and not str(sent) == "NaT"
                else "—"
            )

            st.markdown(
                f"**{recommendation['From']}** · {sent_label}"
            )

            if recommendation["attached_message"]:
                st.markdown(f"> {recommendation['attached_message']}")


# ------------------------------------------------------
# REVIEWS
# ------------------------------------------------------

st.divider()

st.subheader("Reviews")

reviews_df = LoadReviewsForMedia(media_id)


if reviews_df.empty:

    st.info("Nobody has reviewed this yet.")

else:

    friends_df = LoadFriends(user_id)

    if not friends_df.empty:
        friend_ids = set(friends_df["friend_id"].tolist())
    else:
        friend_ids = set()

    # Split so Sam sees her own circle's take before the general crowd.
    friend_reviews_df = reviews_df[reviews_df["user_id"].isin(friend_ids)]

    other_reviews_df = reviews_df[
        ~reviews_df["user_id"].isin(friend_ids | {user_id})
    ]

    my_reviews_df = reviews_df[reviews_df["user_id"] == user_id]

    metric_col1, metric_col2, metric_col3 = st.columns(3, gap="large")

    with metric_col1:
        st.metric("Reviews", len(reviews_df))

    with metric_col2:
        st.metric("From Friends", len(friend_reviews_df))

    with metric_col3:
        st.metric(
            "Total Likes",
            int(reviews_df["likes"].fillna(0).sum())
        )

    def RenderReviews(frame, empty_message):
        if frame.empty:
            st.caption(empty_message)
            return

        for _, review in frame.iterrows():
            reviewer = review.get("display_name") or "Unknown user"
            written = review["review_date"]

            written_label = (
                written.strftime("%b %d, %Y")
                if written is not None and not str(written) == "NaT"
                else "—"
            )

            with st.container(border=True):
                st.markdown(
                    f"**{reviewer}** · {written_label} · "
                    f"👍 {int(review['likes'] or 0)}"
                )
                st.write(review["review_comment"] or "No comment.")

    if not my_reviews_df.empty:
        st.markdown("##### Your Review")
        RenderReviews(my_reviews_df, "")

    st.markdown("##### From Your Friends")
    RenderReviews(
        friend_reviews_df,
        "None of your friends have reviewed this."
    )

    st.markdown("##### Everyone Else")
    RenderReviews(
        other_reviews_df,
        "No other reviews yet."
    )


# ------------------------------------------------------
# NAVIGATION
# ------------------------------------------------------

st.divider()

back_col1, back_col2 = st.columns(2)

with back_col1:
    if st.button("← Media Search", use_container_width=True):
        st.switch_page("pages/media-search.py")

with back_col2:
    if st.button("← Home", use_container_width=True):
        st.switch_page("pages/book-lovers.py")
