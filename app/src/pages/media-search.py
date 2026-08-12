import logging
logger = logging.getLogger(__name__)

import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

API_URL = "http://web-api:4000/media/search"


st.set_page_config(layout='wide')

SideBarLinks()
st.header('Media Search')
st.write(f"### Hi, {st.session_state.get('first_name', 'there')}.")

if "media_search_query" not in st.session_state:
    st.session_state.media_search_query = None

with st.form("media_search_form"):
    st.subheader("Media Information")

    title = st.text_input("Media Title *")
    media_type = st.selectbox(
        "Media Type", ["any", "book", "tvshow", "game", "movie"]
    )

    submitted = st.form_submit_button("Search")

    if submitted:
        if not title.strip():
            st.error("Please fill in all required fields marked with *")
        else:
            st.session_state.media_search_query = {
                "title": title.strip(),
                "media_type": media_type,
            }

query = st.session_state.media_search_query

if query:
    params = {"title": query["title"]}
    if query["media_type"] != "any":
        params["media_type"] = query["media_type"]

    try:
        response = requests.get(API_URL, params=params, timeout=5)

        if response.status_code == 200:
            results = response.json()

            if not results:
                st.warning(f"No media found matching '{query['title']}'.")
            else:
                st.success(f"Found {len(results)} result(s).")
                st.dataframe(
                    pd.DataFrame(results),
                    use_container_width=True,
                    hide_index=True,
                )
        elif response.status_code == 404:
            st.error("Search failed (404): the /media/search endpoint does not exist yet.")
        else:
            st.error(f"Search failed ({response.status_code}): {response.text}")

    except requests.exceptions.RequestException as e:
        logger.warning("media search request failed: %s", e)
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running")

if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
