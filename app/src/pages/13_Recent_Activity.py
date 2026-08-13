import streamlit as st
import requests
from datetime import datetime
from modules.nav import SideBarLinks


st.set_page_config(layout="wide")


SideBarLinks(show_home=True)


st.title("Recent User Activity")


st.write("### Recent Activity")
st.write(
    "Review recent user activity to identify possible issues with the application."
)


# API location
API_URL = "http://api:4000/review/reviews"


# GET RECENT USER ACTIVITY
try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        reviews = response.json()

        if reviews:

            # Sort reviews by date from newest to oldest
            if "review_date" in reviews[0]:
                reviews = sorted(
                    reviews,
                    key=lambda review: datetime.strptime(
                        review["review_date"],
                        "%a, %d %b %Y %H:%M:%S GMT"
                    ),
                    reverse=True
                )

            st.write("### Recent Reviews")

            st.dataframe(
                reviews,
                use_container_width=True
            )

            st.write(
                f"Total Recent Reviews: {len(reviews)}"
            )

        else:
            st.info("No recent user activity is currently available.")

    else:
        st.error(
            f"Could not load recent user activity: {response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the review API: {e}"
    )


# BACK BUTTON
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")