import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(layout="wide")

SideBarLinks(show_home=True)


st.title("Delete Genre")


st.write("### Manage Genres")
st.write(
    "Review existing genres and remove a genre from the platform."
)


# API location
API_URL = "http://api:4000/genre/"


# Get all existing genres
try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        genres = response.json()
    else:
        genres = []
        st.error(f"Could not load genres: {response.text}")

except requests.exceptions.RequestException as e:
    genres = []
    st.error(f"Could not connect to API: {e}")


# Display existing genres
st.write("### Existing Genres")

if genres:
    st.dataframe(
        genres,
        use_container_width=True,
        hide_index=True
    )

    st.write("### Delete a Genre")

    # Create dropdown using the existing genre IDs
    genre_options = {
        f"{genre['genre_id']} - {genre['name']}": genre["genre_id"]
        for genre in genres
    }

    selected_genre = st.selectbox(
        "Select Genre",
        list(genre_options.keys())
    )

    selected_genre_id = genre_options[selected_genre]

    st.warning(
        "Deleting a genre will permanently remove it and its media links."
    )

    if st.button(
        "Delete Genre",
        type="primary",
        use_container_width=True
    ):
        try:
            response = requests.delete(
                API_URL,
                json={
                    "genre_id": selected_genre_id
                }
            )

            if response.status_code == 200:
                st.success("Genre deleted successfully!")
                st.rerun()

            else:
                st.error(
                    f"Could not delete genre: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to API: {e}")

else:
    st.info("No genres are currently available.")


if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")