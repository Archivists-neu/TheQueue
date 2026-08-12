import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Recommendation Data")

st.write("### Review Recommendation Data")
st.write(
    "View recommendation data to test functionality and verify correct results."
)

if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")