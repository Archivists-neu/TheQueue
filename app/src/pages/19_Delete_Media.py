import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(layout="wide")
SideBarLinks(show_home=True)

st.title("Delete Media")

st.write("### Manage Media")
st.write(
    "Review media and remove duplicate or irrelevant items from the platform."
)


# Media API
MEDIA_URL = "http://api:4000/media"


# Get existing media
media_items = []

try:
    response = requests.get(MEDIA_URL)

    if response.status_code == 200:
        media_items = response.json()

    else:
        st.error(f"Could not load media: {response.text}")

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to API: {e}")


# Display existing media
st.write("### Existing Media")

if media_items:

    st.dataframe(
        media_items,
        use_container_width=True,
        hide_index=True
    )

    st.write("### Delete Media")

    # Show the title and type instead of only an ID
    media_options = {
        f"{item['title']} ({item['media_type']})":
        item["media_id"]
        for item in media_items
    }

    selected_media = st.selectbox(
        "Select Media",
        list(media_options.keys())
    )

    selected_media_id = media_options[selected_media]

    st.warning(
        "Deleting media is permanent. Related reviews, recommendations, "
        "common interests, and genre links may also need to be removed "
        "to keep the database consistent."
    )

    if st.button(
        "Delete Media",
        type="primary",
        use_container_width=True
    ):

        try:
            delete_response = requests.delete(
                f"{MEDIA_URL}/{selected_media_id}"
            )

            if delete_response.status_code == 200:
                st.success("Media deleted successfully!")
                st.rerun()

            else:
                st.error(
                    f"Could not delete media: {delete_response.text}"
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to API: {e}")

else:
    st.info("No media is currently available.")


# Back button
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")