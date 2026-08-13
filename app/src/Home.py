##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks
from shared.social import FindUserById, SignInUser

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")
st.title('The Queue')
st.write('#### Hi! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button("Act as persona Sam, The Book lover", type='primary', use_container_width=True):
    seeded_user = FindUserById(1)

    if seeded_user is not None:
        SignInUser(seeded_user)

    else:
        # API unreachable -- fall back so the demo still opens.
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'book_lover'
        st.session_state['first_name'] = 'Sam'
        st.session_state['last_name'] = 'W'
        st.session_state['status'] = 'busy'
        st.session_state['email'] = 'sam@gmail.com'
        st.session_state['user_id'] = 1
    logger.info("Logging in as Book Lover Persona")
    # make it so when the user clicks the button - we send through Create workflow -> create user -> send to book-lovers.py from create
    # st.switch_page('pages/book-lovers.py')
    st.switch_page('pages/create-user.py')

if st.button('Act as Andy, Data Analyst',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'analyst'
    st.session_state['first_name'] = 'Andy'
    st.switch_page('pages/analyst.py')
    
if st.button('Act as Taylor, the Software Developer',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'software_developer'
    st.session_state['first_name'] = 'Taylor'
    st.switch_page('pages/10_Software_Developer_Home.py')

if st.button('Act as Morgan, System Administrator',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'administrator'
    st.session_state['first_name'] = 'SysAdmin'

    st.switch_page('pages/system-admin.py')



