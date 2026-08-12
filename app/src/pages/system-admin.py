import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Welcome System Admin Morgan')
st.write('### What would you like to do today?')

if st.button('Search Users',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/user-search.py')
