import streamlit as st
import requests

from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Manage Recommendations")

st.write("### Recommendation Algorithm")
st.write(
    "Review existing recommendations and update recommendation functionality."
)

# Flask API locations
API_URL = "http://api:4000/recommendation/recommendations"
FRIENDSHIP_URL = "http://api:4000/friendship/friendships"


# GET FRIENDSHIPS
# Get friendship information so friendship IDs can be
# displayed as the names of the two people instead.

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
            f"Unable to retrieve friendships: "
            f"{friendship_response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the friendship API: {e}"
    )

# GET EXISTING RECOMMENDATIONS
st.write("### Existing Recommendations")

try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        recommendations = response.json()

        if recommendations:

            # Create a separate version for display.
            # Keep the original recommendations unchanged
            # because the IDs may still be needed internally.
            display_recommendations = []

            for recommendation in recommendations:

                display_row = recommendation.copy()

                # Remove friendship_id from what the user sees.
                friendship_id = display_row.pop(
                    "friendship_id",
                    None
                )

                # Replace it with the people's names.
                display_row["friendship"] = (
                    friendship_lookup.get(
                        friendship_id,
                        "Unknown Friendship"
                    )
                )

                display_recommendations.append(display_row)

            # Display names instead of friendship IDs.
            st.dataframe(
                display_recommendations,
                use_container_width=True,
                hide_index=True
            )

            # Create a list of recommendation IDs
            # for the update dropdown.
            recommendation_ids = [
                recommendation["recommendation_id"]
                for recommendation in recommendations
            ]

            st.write("### Update a Recommendation")

            selected_id = st.selectbox(
                "Select Recommendation ID",
                recommendation_ids
            )

            new_message = st.text_input(
                "New Attached Message"
            )

            new_media_id = st.number_input(
                "New Media ID",
                min_value=1,
                step=1
            )


            # -------------------------------------------------
            # UPDATE RECOMMENDATION
            # -------------------------------------------------

            if st.button("Update Recommendation"):

                update_data = {
                    "attached_message": new_message,
                    "media_id": int(new_media_id)
                }

                try:
                    update_response = requests.put(
                        f"{API_URL}/{selected_id}",
                        json=update_data
                    )

                    if update_response.status_code == 200:
                        st.success(
                            "Recommendation updated successfully!"
                        )
                        st.rerun()

                    else:
                        st.error(
                            f"Unable to update recommendation: "
                            f"{update_response.text}"
                        )

                except requests.exceptions.RequestException as e:
                    st.error(
                        f"Could not connect to the "
                        f"recommendation API: {e}"
                    )

        else:
            st.info(
                "No recommendations are currently available."
            )

    else:
        st.error(
            f"Unable to retrieve recommendations: "
            f"{response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the recommendation API: {e}"
    )


# NAVIGATION
if st.button("Back to Developer Dashboard"):
    st.switch_page(
        "pages/10_Software_Developer_Home.py"
    )