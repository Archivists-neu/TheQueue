import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Add New Media")

st.write("### Add Media")
st.write(
    "Add new books, movies, TV shows, or games for users to interact with."
)

if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")