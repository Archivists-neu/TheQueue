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


# Genre API
API_URL = "http://api:4000/genre/"


# Get existing genres
genres = []

try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        genres = response.json()

    else:
        st.error(f"Could not load genres: {response.text}")

except requests.exceptions.RequestException as e:
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

    # Show the genre name instead of making
    # the developer choose only by ID
    genre_options = {
        f"{genre['name']} - "
        f"{genre.get('description') or 'No description'}":
        genre["genre_id"]
        for genre in genres
    }

    selected_genre = st.selectbox(
        "Select Genre",
        list(genre_options.keys())
    )

    selected_genre_id = genre_options[selected_genre]

    # Explain what happens to media when a genre is deleted
    st.warning(
        "Deleting a genre removes the genre and its media links. "
        "Books, movies, games, and TV shows themselves will NOT be deleted. "
        "If a media item only had this genre, it will simply have no genre "
        "association afterward."
    )

    if st.button(
        "Delete Genre",
        type="primary",
        use_container_width=True
    ):

        try:
            delete_response = requests.delete(
                API_URL,
                json={
                    "genre_id": selected_genre_id
                }
            )

            if delete_response.status_code == 200:
                st.success("Genre deleted successfully!")
                st.rerun()

            else:
                st.error(
                    f"Could not delete genre: {delete_response.text}"
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to API: {e}")

else:
    st.info("No genres are currently available.")


# Back button
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")