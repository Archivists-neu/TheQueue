import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome Booker Lover, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

st.divider()

with st.container(key="home_container_div"):
    col1, col2 = st.columns(2)
    with col1:
        st.write('### Entertainment')
        if st.button('Media Search',
                     type='primary',
                     use_container_width=True):
            st.switch_page('pages/media-search.py')
        if st.button('Friend Search',
                     type='primary',
                     use_container_width=True):
            st.switch_page('pages/friend-search.py')
        if st.button('Recommendations',
                     type='primary',
                     use_container_width=True):
            st.switch_page('pages/02_Map_Demo.py')

    with col2:
        st.write('### Account')
        if st.button('Profile', type='primary', use_container_width=True):
            st.switch_page('pages/user-profile.py')


if st.button("← Logout"):
    st.session_state['authenticated'] = False
    st.switch_page("pages/home.py")
