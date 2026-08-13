import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(layout="wide")


SideBarLinks(show_home=True)


st.title("Outdated Recommendations")


st.write("### Manage Outdated Recommendations")
st.write(
    "Review and remove outdated recommendations from the platform."
)


# API location
API_URL = "http://api:4000/recommendation/recommendations"

# GET EXISTING RECOMMENDATIONS
try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        recommendations = response.json()

        if recommendations:
            st.write("### Existing Recommendations")

            # Display recommendations in a table
            st.dataframe(recommendations, use_container_width=True)

            st.write("### Delete a Recommendation")

            # Get the recommendation IDs for the dropdown
            recommendation_ids = [
                recommendation["recommendation_id"]
                for recommendation in recommendations
            ]

            selected_id = st.selectbox(
                "Select Recommendation ID",
                recommendation_ids
            )

            st.warning(
                "Deleting a recommendation will permanently remove it."
            )

            # DELETE RECOMMENDATION
            if st.button("Delete Recommendation"):

                delete_response = requests.delete(
                    f"{API_URL}/{selected_id}"
                )

                if delete_response.status_code == 200:
                    st.success("Recommendation deleted successfully!")

                    # Refresh the page so the deleted recommendation
                    # disappears from the table
                    st.rerun()

                else:
                    st.error(
                        f"Could not delete recommendation: "
                        f"{delete_response.text}"
                    )

        else:
            st.info("No recommendations found.")

    else:
        st.error(
            f"Could not load recommendations: {response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the recommendation API: {e}")

# BACK BUTTON
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")