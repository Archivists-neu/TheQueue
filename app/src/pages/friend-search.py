import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# Accessing a REST API from Within Streamlit")

st.write("""
Simply retrieving data from a REST API running in a separate Docker container.

If the container isn't running, this page will fall back to dummy data.
""")

data = {}
try:
    data = requests.get(GetUsersApi()).json()
except requests.exceptions.RequestException as e:
    st.write("**Important**: Could not connect to sample API, so using dummy data.")
    data = {}

st.dataframe(data)

if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
    
