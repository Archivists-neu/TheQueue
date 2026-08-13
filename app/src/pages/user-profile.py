import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi, PutApiData
from shared.social import (
    LABEL_TO_MEDIA_TYPE,
    MEDIA_CATEGORIES,
    FindUserById,
    LoadUsers,
    LoadReviewsForUsers,
    RequireUserId,
    SignInUser,
)
from shared.review import ReviewDialog

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Profile')
lHeader, rHeader = st.columns([4, 1])
with lHeader:
    st.caption(f"Hello, {st.session_state['first_name']}")

with rHeader:
    if st.button("← Home", type="primary", use_container_width=True):
        st.switch_page("pages/book-lovers.py")

user_id = RequireUserId()




if st.session_state.pop("profile_updated", False):
    st.success("Profile updated.")

account = FindUserById(user_id)

if account is None:
    st.error(f"Could not load account #{user_id}. Is the API running?")
    st.stop()

STATUS_OPTIONS = ["online", "busy", "offline", "custom"]
current_status = account.get("account_status") or "offline"

if current_status not in STATUS_OPTIONS:
    current_status = "offline"

st.divider()
first_name = st.text_input('First name', account.get("first_name") or "")
last_name = st.text_input('Last name', account.get("last_name") or "")
email = st.text_input('Email', account.get("email") or "")

status = st.radio("Status", options=STATUS_OPTIONS, index=STATUS_OPTIONS.index(current_status), horizontal=True)

if status == "custom":
    custom_status_message = st.text_input('Custom status message', value=account.get("custom_status_message") or "", max_chars=150)
else:
    custom_status_message = None


st.divider()

if st.button("Update Profile", type="primary"):

    if not first_name.strip() or not last_name.strip() or not email.strip():
        st.error("First name, last name and email cannot be empty.")

    elif status == "custom" and not (custom_status_message or "").strip():
        st.error("Add a custom status message, or pick another status.")

    else:
        payload = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "account_status": status,
            # Clear the message when leaving custom, so a stale one cannot
            # linger behind an unrelated status.
            "custom_status_message": (
                custom_status_message.strip()
                if status == "custom" and custom_status_message
                else None
            ),
        }

        ok, body = PutApiData(GetUsersApi(user_id), payload)

        if not ok:
            st.error(f"Could not update your profile: {body}")

        else:
            LoadUsers.clear()

            refreshed = FindUserById(user_id)

            if refreshed is not None:
                SignInUser(refreshed)

            # Survives the rerun that repaints the form with saved values.
            st.session_state["profile_updated"] = True
            st.rerun()

l_col, r_col = st.columns([4, 1])

st.divider()

with l_col:
    st.subheader("My Reviews")
    st.caption("Everything you have reviewed, newest first.")

with r_col:
    if st.button(
            "✎ Write Review",
            type="primary",
            use_container_width=True,
        ):
            ReviewDialog(user_id)

if st.session_state.get("review_created"):
    st.success(st.session_state.pop("review_created"))





my_reviews_df = LoadReviewsForUsers([user_id])


if my_reviews_df.empty:

    st.info("You have not reviewed anything yet.")

else:

    selected_categories = st.multiselect("Media Type", options=MEDIA_CATEGORIES, default=MEDIA_CATEGORIES)

    selected_media_types = [
        LABEL_TO_MEDIA_TYPE[category]
        for category in selected_categories
    ]

    filtered_reviews_df = my_reviews_df.copy()

    if "media_type" in filtered_reviews_df.columns:
        filtered_reviews_df = filtered_reviews_df[
            filtered_reviews_df["media_type"].isin(selected_media_types)
        ]

    metric_col1, metric_col2, metric_col3 = st.columns(3, gap="large")

    with metric_col1:
        st.metric("Reviews Written", len(filtered_reviews_df))

    with metric_col2:
        if filtered_reviews_df.empty:
            st.metric("Likes Received", 0)
        else:
            st.metric(
                "Likes Received",
                int(filtered_reviews_df["likes"].fillna(0).sum()),
            )

    with metric_col3:
        if filtered_reviews_df.empty:
            st.metric("Favourite Type", "—")
        else:
            category_counts = filtered_reviews_df["category"].value_counts()

            if category_counts.empty:
                st.metric("Favourite Type", "—")
            else:
                st.metric("Favourite Type", category_counts.index[0])

    if filtered_reviews_df.empty:

        st.info("No reviews match the selected filters.")

    else:

        display_df = filtered_reviews_df.copy()

        display_df["Reviewed"] = (
            display_df["review_date"].dt.strftime("%b %d, %Y")
        )

        display_df = display_df.rename(
            columns={
                "title": "Title",
                "category": "Media Type",
                "review_comment": "Review",
                "likes": "Likes",
            }
        )

        st.dataframe(
            display_df[
                ["Title", "Media Type", "Review", "Likes", "Reviewed"]
            ],
            use_container_width=True,
            hide_index=True,
        )

