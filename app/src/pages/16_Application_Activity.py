import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Application Activity")

st.write("### Monitor Application Activity")
st.write(
    "Monitor application activity and changes in user activity."
)

if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")