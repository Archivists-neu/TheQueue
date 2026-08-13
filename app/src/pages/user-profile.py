import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Profile')

data = {
    "first_name": st.session_state['first_name'],
    "last_name": st.session_state['last_name'],
    "status": st.session_state['status'],
    "email": st.session_state['email']
}

st.divider()

first_name = st.text_input('First name', data['first_name'])
last_name = st.text_input('Last name', data['last_name'])
status = st.selectbox('Status', ['online', 'busy', 'offline'])
email = st.text_input('Email', data['email'])

radio = st.radio(
    "Status",
    key="visibility",
    options=["offline", "online", "busy", "custom"],
    horizontal=True,
)
# if it's custom, then we want to enable the input field, else we want to disable it
if radio == "custom":
    custom_status_message = st.text_input('Custom status message', max_chars=150)
else:
    custom_status_message = None


st.divider()

if st.button("Update Profile"):
    st.switch_page("pages/book-lovers.py")


if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")

