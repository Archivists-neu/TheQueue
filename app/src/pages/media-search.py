import logging
logger = logging.getLogger(__name__)

import pandas as pd
import requests
import streamlit as st
from modules.nav import SideBarLinks

# Endpoint your partner is building. Expected response: JSON list of media rows.
API_URL = "http://web-api:4000/media/search"


def style_return_button():
    st.markdown("""
    <style>
    [data-testid="stButton"] button {
        background-color: transparent;
        color: #000;
        border-radius: 10px;
        border: 1px solid #000;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        justify-content: start;

    }
    </style>
    """, unsafe_allow_html=True)


st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

style_return_button()

# set the header of the page
st.header('Media Search')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state.get('first_name', 'there')}.")

# Remembers the last search across reruns so the results stay on screen
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

# Results are rendered outside the form so they survive the rerun
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

if st.button("Return Home"):
    st.switch_page("pages/book-lovers.py")
