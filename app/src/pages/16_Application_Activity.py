import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetMediaApi, GetRecommendationApi, GetReviewsApi


st.set_page_config(layout="wide")


SideBarLinks(show_home=True)


st.title("Application Activity")


st.write("### Monitor Application Activity")
st.write(
    "Monitor application activity and changes in user activity."
)


# API locations
REVIEWS_URL = GetReviewsApi()
RECOMMENDATIONS_URL = GetRecommendationApi()
MEDIA_URL = GetMediaApi()


# GET APPLICATION DATA
try:
    reviews_response = requests.get(REVIEWS_URL)
    recommendations_response = requests.get(RECOMMENDATIONS_URL)
    media_response = requests.get(MEDIA_URL)

    reviews = []
    recommendations = []
    media = []

    if reviews_response.status_code == 200:
        reviews = reviews_response.json()

    if recommendations_response.status_code == 200:
        recommendations = recommendations_response.json()

    if media_response.status_code == 200:
        media = media_response.json()


    # APPLICATION SUMMARY
    st.write("### Application Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Reviews",
            len(reviews)
        )

    with col2:
        st.metric(
            "Total Recommendations",
            len(recommendations)
        )

    with col3:
        st.metric(
            "Total Media",
            len(media)
        )


    # RECENT USER ACTIVITY
    st.write("### Recent User Activity")

    if reviews:

        # Sort reviews by review ID so newest entries appear first
        recent_reviews = sorted(
            reviews,
            key=lambda review: review.get("review_id", 0),
            reverse=True
        )

        st.dataframe(
            recent_reviews,
            use_container_width=True
        )

    else:
        st.info("No recent user activity is currently available.")


except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the application API: {e}"
    )


# BACK BUTTON
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")