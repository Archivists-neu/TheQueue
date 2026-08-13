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

# The Flask API is running in the api Docker container.
API_URL = "http://api:4000/recommendation/recommendations"


# GET EXISTING RECOMMENDATIONS

st.write("### Existing Recommendations")

try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        recommendations = response.json()

        if recommendations:
            st.dataframe(recommendations, use_container_width=True)

            # Create a list of recommendation IDs for the dropdown.
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
          
            # UPDATE RECOMMENDATION
        

            if st.button("Update Recommendation"):

                update_data = {
                    "attached_message": new_message,
                    "media_id": int(new_media_id)
                }

                update_response = requests.put(
                    f"{API_URL}/{selected_id}",
                    json=update_data
                )

                if update_response.status_code == 200:
                    st.success("Recommendation updated successfully!")
                else:
                    st.error(
                        f"Unable to update recommendation: "
                        f"{update_response.text}"
                    )

        else:
            st.info("No recommendations are currently available.")

    else:
        st.error(
            f"Unable to retrieve recommendations: {response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the recommendation API: {e}")


# NAVIGATION
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")