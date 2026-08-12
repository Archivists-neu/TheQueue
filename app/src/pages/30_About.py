import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About The Queue")

st.markdown(
    """
    *CS 3200 · Summer B 2026 · Database Design Project*

    ---

    ### All Stories. One Place.

    The Queue brings movies, TV shows, books, and games together in one social platform where users can rate, review, discover, and organize the stories they love.

    Rather than relying on engagement-driven recommendations, The Queue puts users in control by providing personalized suggestions based on their interests and the people they trust.

    By connecting different forms of media, the platform makes it easy to discover new favorites, build personalized queues and rankings, share opinions, and connect with others who have similar interests.

    ---

    ### About This Demo

    This demo showcases the technology stack behind The Queue and highlights features of the various platforms used to build it.

    **Stay tuned for more features to come!**
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
