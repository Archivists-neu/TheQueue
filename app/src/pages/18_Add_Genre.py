import streamlit as st
import requests
from modules.nav import SideBarLinks


st.set_page_config(layout="wide")
SideBarLinks(show_home=True)

st.title("Add Genre")

st.write("### Add a New Genre")
st.write("Create a new genre that can be linked to media in The Queue.")


# Genre API
API_URL = "http://api:4000/genre/"


# Genre information
name = st.text_input("Genre Name")

description = st.text_area("Description")


# Add Genre button
if st.button(
    "Add Genre",
    type="primary",
    use_container_width=True
):

    # Make sure a name was entered
    if not name.strip():
        st.error("Genre name is required.")

    else:
        genre_data = {
            "name": name.strip(),
            "description": description.strip() or None
        }

        try:
            response = requests.post(
                API_URL,
                json=genre_data
            )

            if response.status_code == 201:
                st.success("Genre added successfully!")
                st.json(response.json())

            else:
                st.error(
                    f"Could not add genre: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to API: {e}")


# Back button
if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")