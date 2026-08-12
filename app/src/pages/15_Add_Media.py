import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Add New Media")

st.write("### Add Media")
st.write("Add a new piece of media to The Queue.")

# These values match the existing media table
media_type = st.selectbox(
    "Media Type",
    ["book", "tvshow", "game", "movie"]
)

title = st.text_input("Title")

summary = st.text_area("Summary")

release_date = st.date_input("Release Date")


if st.button("Add Media", type="primary", use_container_width=True):

    # Build data using the EXISTING media schema
    media_data = {
        "media_type": media_type,
        "title": title,
        "summary": summary,
        "release_date": release_date.isoformat()
    }

    try:
        response = requests.post(
            "http://api:4000/media/media",
            json=media_data
        )

        if response.status_code == 201:
            st.success("Media added successfully!")
            st.json(response.json())
        else:
            st.error(
                f"Could not add media: {response.text}"
            )

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to API: {e}")


if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")