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


RECOMMENDATION_URL = (
    "http://api:4000/recommendation/recommendations"
)

FRIENDSHIP_URL = (
    "http://api:4000/friendship/friendships"
)


# Get friendships so we can display people's names
friendships = []
friendship_lookup = {}

try:
    friendship_response = requests.get(FRIENDSHIP_URL)

    if friendship_response.status_code == 200:

        friendships = friendship_response.json()

        friendship_lookup = {
            friendship["friendship_id"]: (
                f"{friendship['requester_name']} ↔ "
                f"{friendship['addressee_name']}"
            )
            for friendship in friendships
        }

    else:
        st.error(
            f"Could not load friendships: "
            f"{friendship_response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the friendship API: {e}"
    )


# Recommendation filters
st.write("### Filter Recommendations")


# Friendship dropdown
friendship_options = {
    "All Friendships": None
}

for friendship in friendships:

    label = (
        f"{friendship['requester_name']} ↔ "
        f"{friendship['addressee_name']}"
    )

    friendship_options[label] = friendship["friendship_id"]


selected_friendship = st.selectbox(
    "Friendship",
    list(friendship_options.keys())
)

selected_friendship_id = friendship_options[
    selected_friendship
]


# Media filter
media_id = st.number_input(
    "Media ID",
    min_value=0,
    step=1,
    value=0
)


# Date filter
recommendation_date = st.text_input(
    "Recommendation Date",
    placeholder="YYYY-MM-DD"
)


# Build query parameters
params = {}

if selected_friendship_id is not None:
    params["friendship_id"] = selected_friendship_id

if media_id > 0:
    params["media_id"] = media_id

if recommendation_date:
    params["recommendation_date"] = recommendation_date


# Get recommendation data
try:

    response = requests.get(
        RECOMMENDATION_URL,
        params=params
    )

    if response.status_code == 200:

        recommendations = response.json()

        st.write("### Recommendation Results")

        if recommendations:

            display_recommendations = []

            for recommendation in recommendations:

                display_row = recommendation.copy()

                # Remove the confusing friendship ID
                friendship_id = display_row.pop(
                    "friendship_id",
                    None
                )

                # Replace it with the names of the people
                display_row["friendship"] = (
                    friendship_lookup.get(
                        friendship_id,
                        f"Friendship {friendship_id}"
                    )
                )

                display_recommendations.append(
                    display_row
                )

            st.dataframe(
                display_recommendations,
                use_container_width=True,
                hide_index=True
            )

            st.write(
                f"Total Recommendations: "
                f"{len(recommendations)}"
            )

        else:
            st.info(
                "No recommendations match the selected filters."
            )

    else:
        st.error(
            f"Could not load recommendation data: "
            f"{response.text}"
        )

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not connect to the recommendation API: {e}"
    )


# Back button
if st.button("Back to Developer Dashboard"):
    st.switch_page(
        "pages/10_Software_Developer_Home.py"
    )