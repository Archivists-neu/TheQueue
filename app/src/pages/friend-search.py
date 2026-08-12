import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# Friends")

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
            st.dataframe(search_results)
        else:
            st.write("No users found matching your search.")
    except requests.exceptions.RequestException as e:
        st.write("**Important**: Could not connect to sample API, so no search results to show.")
        logger.error(f"Error searching users: {e}")

st.divider()



data = {}
try:
    data = requests.get(GetUsersApi()).json()
except requests.exceptions.RequestException as e:
    st.write("**Important**: Could not connect to sample API, so using dummy data.")
    data = {}

st.dataframe(data)

if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
    
