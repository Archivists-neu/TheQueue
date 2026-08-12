import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetMediaApi

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# Add New Media")

st.write("""
Use the form below to add a new piece of media to the database.
""")

with st.form("add_media_form"):
    col1, col2 = st.columns(2)
    with col1:
        media_type = st.selectbox("Category", ["Book", "TV Show", "Movie", "Game"])
        title = st.text_input("Title")
        author = st.text_input("Author")
    with col2:
        media_id = st.text_input("Media ID")
        genre = st.text_input("Genre")
        summary = st.text_area("Summary")

    submitted = st.form_submit_button("Add Media")

if submitted:
    if not title or not author:
        st.error("Title and Author are required fields.")
    else:
        new_media = {
            "title": title,
            "author": author,
            "media_type": media_type,
            "genre": genre,
            "summary": summary,
        }
        if media_id:
            new_media["media_id"] = media_id

    try:
        response = requests.post(GetMediaApi(), json=new_media)

        if response.status_code == 201:
            st.success(f"Successfully added '{title}' to the database!")
            st.json(response.json())
        else:
            st.error(f"Failed to add media: {response.json().get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        st.error("Could not connect to the API to add media.")
        logger.error(f"Error adding media: {e}")

st.divider()

st.write("### All Media")

data = {}
try:
    data = requests.get(GetMediaApi()).json()
except requests.exceptions.RequestException as e:
    st.write("**Important**: Could not connect to sample API, so using dummy data.")
    data = {}

st.dataframe(data)

if st.button("← Home"):
    st.switch_page("pages/system-admin.py")