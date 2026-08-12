import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome Booker Lover, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

with st.container(key="home_container_div"):
    if st.button('View Media Search',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/media-search.py')
    if st.button('View Friend Search',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/friend-search.py')



    if st.button('View World Map Demo',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/02_Map_Demo.py')

