import logging
import re
logger = logging.getLogger(__name__)

import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks
from shared.apifuncs import GetMediaSearchApi
from shared.social import (
    DescribeGenre,
    LoadFriendRecommendations,
    LoadFriends,
    LoadReviewsForUsers,
    RequireUserId,
)


st.set_page_config(layout='wide')

SideBarLinks()
st.header('Media Search')
st.write(f"### Hi, {st.session_state.get('first_name', 'there')}.")

user_id = RequireUserId()

if "media_search_query" not in st.session_state:
    st.session_state.media_search_query = None



friend_recs_df = LoadFriendRecommendations(user_id)

if friend_recs_df.empty:
    recommendations_label = "Recommendation From Your Friends"
else:
    recommendations_label = (
        f"Recommendation From Your Friends "
        f"({len(friend_recs_df)} from "
        f"{friend_recs_df['From'].nunique()} friend(s))"
    )

with st.expander(recommendations_label, expanded=False):

    if friend_recs_df.empty:
        st.info("No friends have recommended anything yet.")

    else:
        st.caption("Pick one to see the full details.")

        for _, recommendation in friend_recs_df.iterrows():

            label = (
                f"{recommendation['title']}  ·  "
                f"{DescribeGenre(recommendation)}  ·  "
                f"from {recommendation['From']}"
            )

            if st.button(
                label,
                key=f"friend_rec_{recommendation['recommendation_id']}",
                use_container_width=True,
            ):
                st.session_state["selected_media_id"] = int(
                    recommendation["media_id"]
                )
                st.switch_page("pages/media-detail.py")



with st.form("media_search_form"):
    st.subheader("Media Information")

    title = st.text_input("Media Title *")
    media_type = st.selectbox(
        "Media Type", ["any", "book", "tvshow", "game", "movie"]
    )

    submitted = st.form_submit_button("Search")

    if submitted:
        if not title.strip():
            st.error("Please fill in all required fields marked with *")
        else:
            st.session_state.media_search_query = {
                "title": title.strip(),
                "media_type": media_type,
            }

query = st.session_state.media_search_query

if query:
    criteria = {"title": query["title"]}
    if query["media_type"] != "any":
        criteria["media_type"] = query["media_type"]

    try:
        response = requests.get(
            GetMediaSearchApi(**criteria), params=criteria, timeout=5
        )

        if response.status_code == 200:
            results = response.json()
            results_df = pd.DataFrame(results)
            query['title'] = re.sub(r'[^a-zA-Z0-9]', '', query['title'])


            if not results:
                st.warning(f"No media found matching '{query['title']}'.")
            else:
                st.success(f"Found {len(results)} result(s).")

                st.caption("Click a row to open it.")

                # results_df keeps every column -- the row click below needs
                # media_id. Only the copy on screen gets trimmed and tidied.
                display_df = results_df.drop(
                    columns=["media_id", "release_date"],
                    errors="ignore",
                )

                display_df = display_df[
                    ["title"]
                    + [c for c in display_df.columns if c != "title"]
                ]

                display_df.columns = [
                    column.replace("_", " ").title()
                    for column in display_df.columns
                ]

                results_selection = st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="media_results_table",
                )

                if results_selection.selection.rows:
                    picked_row = results_selection.selection.rows[0]
                    st.session_state["selected_media_id"] = int(
                        results_df.iloc[picked_row]["media_id"]
                    )
                    st.switch_page("pages/media-detail.py")

                # What Sam's circle thought of whatever just came back.
                st.subheader("What Your Friends Said")

                friends_df = LoadFriends(user_id)

                if friends_df.empty:
                    st.info("No confirmed friends yet.")

                else:
                    friend_reviews_df = LoadReviewsForUsers(
                        friends_df["friend_id"].tolist()
                    )

                    if (
                        not friend_reviews_df.empty
                        and "media_id" in results_df.columns
                    ):
                        friend_reviews_df = friend_reviews_df[
                            friend_reviews_df["media_id"].isin(
                                results_df["media_id"]
                            )
                        ]

                    if friend_reviews_df.empty:
                        st.info(
                            "None of your friends have reviewed these yet."
                        )

                    else:
                        friend_reviews_df = friend_reviews_df.rename(
                            columns={
                                "display_name": "Friend",
                                "title": "Title",
                                "review_comment": "Review",
                                "likes": "Likes",
                            }
                        )

                        friend_reviews_df["Reviewed"] = (
                            friend_reviews_df["review_date"]
                            .dt.strftime("%b %d, %Y")
                        )

                        st.dataframe(
                            friend_reviews_df[
                                ["Friend", "Title", "Review", "Likes", "Reviewed"]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )
        elif response.status_code == 404:
            st.error(f"No media found matching '{query['title']}'.")
        else:
            st.error(f"Search failed ({response.status_code}): {response.text}")

    except requests.exceptions.RequestException as e:
        logger.warning("media search request failed: %s", e)
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running")

# add recommendations view


if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
