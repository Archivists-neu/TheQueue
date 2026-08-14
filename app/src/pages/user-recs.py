import logging

import streamlit as st

from modules.nav import SideBarLinks
from shared.apifuncs import GetRecommendationApi, PostApiData
from shared.social import (
    LABEL_TO_MEDIA_TYPE,
    MEDIA_CATEGORIES,
    DescribeGenre,
    LoadFriendRecommendations,
    LoadFriends,
    LoadMedia,
    RequireUserId,
)


logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="My Recommendations",
    page_icon="💌",
    layout="wide"
)

SideBarLinks()
user_id = RequireUserId()

@st.dialog("Recommend Media")
def RecommendDialog(sender_id):
    """
    A recommendation hangs off a friendship, so the friend picker supplies
    the friendship_id the API needs.
    """
    friends_df = LoadFriends(sender_id)

    if friends_df.empty:
        st.info(
            "You need a confirmed friend before you can recommend anything."
        )
        return

    media_df = LoadMedia()

    if media_df.empty:
        st.error("Could not load the media catalog.")
        return

    friend_row = st.selectbox(
        "Send to",
        options=list(range(len(friends_df))),
        format_func=lambda i: friends_df.iloc[i]["friend_name"],
    )

    media_row = st.selectbox(
        "Media",
        options=list(range(len(media_df))),
        format_func=lambda i: (
            f"{media_df.iloc[i]['title']} "
            f"({media_df.iloc[i]['category']})"
        ),
    )

    message = st.text_area(
        "Message",
        placeholder="Why should they check this out?",
    )

    if st.button(
        "Send Recommendation",
        type="primary",
        use_container_width=True,
    ):
        ok, body = PostApiData(
            GetRecommendationApi(),
            {
                "friendship_id": int(
                    friends_df.iloc[friend_row]["friendship_id"]
                ),
                "media_id": int(media_df.iloc[media_row]["media_id"]),
                "attached_message": message.strip() or None,
            },
        )

        if ok:
            st.session_state["rec_created"] = (
                f"Recommended {media_df.iloc[media_row]['title']} "
                f"to {friends_df.iloc[friend_row]['friend_name']}."
            )
            st.rerun()

        else:
            st.error(f"Could not send the recommendation: {body}")


title_col, action_col, ret = st.columns(
    [4, 1, 1],
    gap="small",
    vertical_alignment="bottom",
)

with title_col:
    st.title("💌 My Recommendations")

    st.caption(
        "Media your friends have sent your way."
    )

with action_col:
    if st.button(
        "＋ Create",
        type="primary",
        use_container_width=True,
    ):
        RecommendDialog(user_id)
with ret:
    if st.button("← Home", use_container_width=True):
        st.switch_page("pages/book-lovers.py")


# Surface the result once the dialog has closed.
if st.session_state.get("rec_created"):
    st.success(st.session_state.pop("rec_created"))


# ------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------

recs_df = LoadFriendRecommendations(user_id)


# ------------------------------------------------------
# FILTERS
# ------------------------------------------------------

st.divider()

filter_col1, filter_col2 = st.columns(
    [1.4, 1],
    gap="large"
)


with filter_col1:

    selected_categories = st.multiselect(
        "Media Type",
        options=MEDIA_CATEGORIES,
        default=MEDIA_CATEGORIES
    )


with filter_col2:

    if not recs_df.empty and "From" in recs_df.columns:
        friend_options = sorted(recs_df["From"].dropna().unique().tolist())
    else:
        friend_options = []

    selected_friends = st.multiselect(
        "From",
        options=friend_options,
        default=friend_options
    )


selected_media_types = [
    LABEL_TO_MEDIA_TYPE[category]
    for category in selected_categories
]


filtered_recs_df = recs_df.copy()

if not filtered_recs_df.empty:

    filtered_recs_df = filtered_recs_df[
        filtered_recs_df["media_type"].isin(selected_media_types)
    ]

    if selected_friends:
        filtered_recs_df = filtered_recs_df[
            filtered_recs_df["From"].isin(selected_friends)
        ]


# ------------------------------------------------------
# SUMMARY METRICS
# ------------------------------------------------------

st.divider()

metric_col1, metric_col2, metric_col3 = st.columns(
    3,
    gap="large"
)


total_recs = len(filtered_recs_df)


if not filtered_recs_df.empty and "From" in filtered_recs_df.columns:
    friends_recommending = filtered_recs_df["From"].nunique()
else:
    friends_recommending = 0


if not filtered_recs_df.empty and "category" in filtered_recs_df.columns:

    category_counts = filtered_recs_df["category"].value_counts()

    if not category_counts.empty:
        top_category = category_counts.index[0]
    else:
        top_category = "—"

else:
    top_category = "—"


with metric_col1:
    st.metric("Recommendations", total_recs)

with metric_col2:
    st.metric("Friends Recommending", friends_recommending)

with metric_col3:
    st.metric("Most Recommended Type", top_category)


# ------------------------------------------------------
# RECOMMENDATION LIST
# ------------------------------------------------------

st.divider()

st.subheader("Your Queue")


if filtered_recs_df.empty:

    st.info(
        "No recommendations match the selected filters."
    )

else:

    st.caption("Pick one to see the full details.")

    for _, recommendation in filtered_recs_df.iterrows():

        label = (
            f"{recommendation['title']}  ·  "
            f"{DescribeGenre(recommendation)}  ·  "
            f"from {recommendation['From']}"
        )

        if st.button(
            label,
            key=f"queue_rec_{recommendation['recommendation_id']}",
            use_container_width=True,
        ):
            st.session_state["selected_media_id"] = int(
                recommendation["media_id"]
            )
            st.switch_page("pages/media-detail.py")


st.divider()

lfoot, rfoot = st.columns([1, 4])
with lfoot:
    if st.button("← Home", type="primary", use_container_width=True):
        st.switch_page("pages/book-lovers.py")
