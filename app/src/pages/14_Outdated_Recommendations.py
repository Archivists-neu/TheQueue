import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Outdated Recommendations")

st.write("### Manage Outdated Recommendations")
st.write(
    "Review and remove outdated recommendations from the platform."
)

if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")