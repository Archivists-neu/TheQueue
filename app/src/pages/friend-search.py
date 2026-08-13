import logging
logger = logging.getLogger(__name__)

import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# Friends")

# Columns where a plain title-case of the snake_case name reads badly.
headerNames = {
    "user_id": "User ID",
    "dob": "Date of Birth",
    "location_id": "Location ID",
}


def PrettyColumns(records):
    """API records -> DataFrame with human-readable column names."""
    df = pd.DataFrame(records)
    df.columns = [headerNames.get(c, c.replace("_", " ").title()) for c in df.columns]
    return df

# --- Search form ---
with st.form("user_search_form"):
    col1, col2= st.columns(2)
    with col1:
        name = st.text_input("Name")
    with col2:
        email = st.text_input("Email")

    submitted = st.form_submit_button("Search")

if submitted:
    params = {}
    if name:
        params["name"] = name
    if email:
        params["email"] = email

    try:
        response = requests.get(GetUsersApi(), params=params)
        search_results = response.json()
        
        st.write("### Search Results")
        if search_results:
            st.dataframe(PrettyColumns(search_results), hide_index=True)

        else:
            st.write("No users found matching your search.")
    except requests.exceptions.RequestException as e:
        st.write("**Important**: Could not connect to sample API, so no search results to show.")
        logger.error(f"Error searching users: {e}")

st.divider()



data = {}
try:
    data = requests.get(GetUsersApi()).json()
    st.write("### Users")
except requests.exceptions.RequestException as e:
    st.write("**Important**: Could not connect to sample API, so using dummy data.")
    data = {}

st.dataframe(PrettyColumns(data), hide_index=True)

if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
    
