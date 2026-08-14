import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

def styleHomeContainer():
    st.markdown(
        """
        <style>
        div.st-key-home_container_div {
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,.12);
            border: 1px solid #ffffff;
            padding: 1rem;
            transition: box-shadow .2s ease-in-out;
        }
        div.st-key-home_container_div:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,.16);
        }

        div.st-key-btn_media_search button {
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: black;
        }
        div.st-key-btn_recommendations button {
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: black;
        }
        div.st-key-btn_friend_search button {
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: black;
        }
        div.st-key-btn_profile button {
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: black;
        }
        div.st-key-btn_media_search button:hover {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_recommendations button:hover {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_friend_search button:hover {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_profile button:hover {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_media_search button:focus-visible {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_recommendations button:focus-visible {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_friend_search button:focus-visible {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        div.st-key-btn_profile button:focus-visible {
            background-color: rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(0, 0, 0, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True)

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome Booker Lover, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

st.divider()


styleHomeContainer()
with st.container(key="home_container_div", border=True):
    st.write('#### Media')
    l_media, r_media = st.columns(2)
    with l_media:
        if st.button('Media Search', key='btn_media_search',
                     type='primary',
                     use_container_width=True):
            st.switch_page('pages/media-search.py')
    with r_media:
        if st.button('Recommendations', key='btn_recommendations',
                     type='primary',
                     use_container_width=True):
            st.switch_page('pages/user-recs.py')


    st.write('#### Friends')
    if st.button('Friend Search', key='btn_friend_search',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/friend-search.py')

    st.write('#### Profile Information')
    if st.button('Profile', key='btn_profile',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/user-profile.py')


if st.button("← Logout"):
    st.session_state['authenticated'] = False
    del st.session_state['role']
    st.switch_page("Home.py")
