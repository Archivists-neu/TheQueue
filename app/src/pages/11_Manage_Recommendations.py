import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")

SideBarLinks(show_home=True)

st.title("Manage Recommendations")

st.write("### Recommendation Algorithm")
st.write(
    "Review recommendation information and update recommendation functionality."
)

if st.button("Back to Developer Dashboard"):
    st.switch_page("pages/10_Software_Developer_Home.py")