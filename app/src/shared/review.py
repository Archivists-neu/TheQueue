import streamlit as st

from shared.apifuncs import GetReviewsApi, PostApiData
from shared.social import LoadAllReviews, LoadMedia


@st.dialog("Write a Review")
def ReviewDialog(reviewer_id, reviewed_media_id=None, media_title=None):
    """
    Post a review.

    Called two ways. media-detail.py already knows the title, so it passes
    the id and name and the dialog just shows them. user-profile.py has no
    media in scope, so it passes neither and the dialog asks which title
    the review is for.
    """
    if reviewed_media_id is None:
        media_df = LoadMedia()

        if media_df.empty or "media_id" not in media_df.columns:
            st.error("Could not load the media list. Try again in a moment.")
            return

        titles = dict(zip(media_df["media_id"], media_df["title"]))

        reviewed_media_id = st.selectbox(
            "Which title?",
            options=list(titles),
            format_func=lambda media_id: titles[media_id],
            index=None,
            placeholder="Pick a title",
        )

    else:
        st.markdown(f"**{media_title}**")

    comment = st.text_area(
        "Your review",
        placeholder="What did you think?",
    )

    if st.button(
        "Post Review",
        type="primary",
        use_container_width=True,
    ):
        if reviewed_media_id is None:
            st.error("Pick a title before posting.")
            return

        if not comment.strip():
            st.error("Write something before posting.")
            return

        ok, body = PostApiData(
            GetReviewsApi(),
            {
                "review_comment": comment.strip(),
                "user_id": reviewer_id,
                "media_id": reviewed_media_id,
            },
        )

        if ok:
            # The review list is cached, so drop it or the new review will
            # not show up for up to a minute.
            LoadAllReviews.clear()
            st.session_state["review_created"] = "Your review was posted."
            st.rerun()

        else:
            st.error(f"Could not post the review: {body}")
