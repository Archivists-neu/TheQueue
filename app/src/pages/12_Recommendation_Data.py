import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(layout="wide")


SideBarLinks(show_home=True)


st.title("Recommendation Data")


st.write("### Review Recommendation Data")
st.write(
    "View recommendation data to test functionality and verify correct results."
)


# API location
API_URL = "http://api:4000/recommendation/recommendations"


# FILTER RECOMMENDATION DATA
st.write("### Filter Recommendations")

friendship_id = st.number_input(
    "Friendship ID",
    min_value=0,
    step=1,
    value=0
)

media_id = st.number_input(
    "Media ID",
    min_value=0,
    step=1,
    value=0
)

recommendation_date = st.text_input(
    "Recommendation Date",
    placeholder="YYYY-MM-DD"
)


# Build filters to send to the API
params = {}

if friendship_id > 0:
    params["friendship_id"] = friendship_id

if media_id > 0:
    params["media_id"] = media_id

if recommendation_date:
    params["recommendation_date"] = recommendation_date


# GET RECOMMENDATION DATA
try:
    response = requests.get(
        API_URL,
        params=params
    )

    if response.status_code == 200:

        recommendations = response.json()

        st.write("### Recommendation Results")

        if recommendations:

            st.dataframe(
                recommendations,
                use_container_width=True
            )

            st.write(
                f"Total Recommendations: {len(recommendations)}"
            )

        else:
            st.info(
                "No recommendations match the selected filters."
            )

    else:
        st.error(
            f"Could not load recommendation data: {response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the recommendation API: {e}"
    )


# BACK BUTTON
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")