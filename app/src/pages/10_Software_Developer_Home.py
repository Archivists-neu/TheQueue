# Taylor - Software Developer Home Page

import logging
import streamlit as st
from modules.nav import SideBarLinks


# Set up logging
logger = logging.getLogger(__name__)


# Configure the Streamlit page
st.set_page_config(layout="wide")


# Display sidebar navigation
SideBarLinks(show_home=True)


# Page title
st.title("Software Developer Dashboard")


# Welcome Taylor
st.write("### Welcome, Taylor!")
st.write("Manage and monitor The Queue's application features.")

logger.info("Loading Taylor's Software Developer Home Page")


# SOFTWARE DEVELOPER FEATURES

st.write("## Developer Tools")


# Feature 1 - Recommendation Algorithm

st.write("### Recommendation Algorithm")
st.write("Update and review recommendation functionality.")

if st.button("Manage Recommendations", use_container_width=True):
    st.switch_page("pages/11_Manage_Recommendations.py")


# Feature 2 - Recommendation Data

st.write("### Recommendation Data")
st.write("Review recommendation data to test application functionality.")

if st.button("Review Recommendation Data", use_container_width=True):
    st.switch_page("pages/12_Recommendation_Data.py")


# Feature 3 - Recent User Activity

st.write("### Recent User Activity")
st.write("Review recent user activity to identify application issues.")

if st.button("View Recent Activity", use_container_width=True):
    st.switch_page("pages/13_Recent_Activity.py")


# Feature 4 - Outdated Recommendations

st.write("### Outdated Recommendations")
st.write("Remove outdated recommendations from the platform.")

if st.button(
    "Manage Outdated Recommendations",
    use_container_width=True
):
    st.switch_page("pages/14_Outdated_Recommendations.py")


# Feature 5 - Media

st.write("### Media")
st.write("Add new media for users to interact with.")

if st.button("Add New Media", use_container_width=True):
    st.switch_page("pages/15_Add_Media.py")


# Feature 6 - Application Activity

st.write("### Application Activity")
st.write("Monitor application activity and changes in user activity.")

if st.button(
    "Monitor Application Activity",
    use_container_width=True
):
    st.switch_page("pages/16_Application_Activity.py")


# Feature 7 - Genre Management

st.write("### Genre Management")
st.write("Review and remove genres from the platform.")

if st.button("Manage Genres", use_container_width=True):
    st.switch_page("pages/17_Delete_Genre.py")