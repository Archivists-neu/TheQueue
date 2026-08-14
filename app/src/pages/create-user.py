import datetime
import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi
from shared.social import FindUserByEmail, SignInUser

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Create Your User")


# ------------------------------------------------------
# SIGN BACK IN
# ------------------------------------------------------

# Logging in as an account that already exists keeps the friendships,
# reviews and recommendations built up in earlier sessions.

with st.expander("Already a user? Log in with your email"):

    login_email = st.text_input(
        "Email",
        key="login_email",
        placeholder="maya.lopez@gmail.com",
    )

    if st.button("Log In", key="login_button", use_container_width=True):

        existing_user = FindUserByEmail(login_email)

        if existing_user is None:
            st.error(
                f"No account found for '{login_email.strip()}'."
            )

        else:
            SignInUser(existing_user)
            st.switch_page("pages/book-lovers.py")

if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "success_user_name" not in st.session_state:
    st.session_state.success_user_name = ""
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

@st.dialog("Success")
def show_success_dialog(user_name):
    st.markdown(f"### {user_name} has been successfully added to the system!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.success_ngo_name = ""
            st.switch_page("pages/book-lovers.py")
    
    with col2:
        if st.button("Add Another User", use_container_width=True):
            st.session_state.show_success_modal = False
            st.session_state.success_user_name= ""
            st.session_state.reset_form = True
            st.rerun()

if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

API_URL = GetUsersApi()

with st.form(f"add_ngo_form_{st.session_state.form_key_counter}"):
    st.subheader("User Information")

    first_name = st.text_input("First Name *")
    last_name = st.text_input("LastName *")
    email = st.text_input("Email *")
    current_year = datetime.date.today().year
    location_id = st.number_input(
        "location_id*", value=0
    )

    # Form submission button
    submitted = st.form_submit_button("Create")

    if submitted:
        # Validate required fields
        if not all([first_name, last_name, email, location_id]):
            st.error("Please fill in all required fields marked with *")
        else:
            # Prepare the data for API
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "date_account_creation": datetime.datetime.now().strftime("%Y-%m-%d"),
                "location_id": location_id,
            }

            try:
                response = requests.post(API_URL, json=user_data)

                if response.status_code == 201:
                    st.session_state.show_success_modal = True
                    st.session_state.success_user_name = f"{first_name} {last_name}"

                    # The API returns the new user_id. Every "my reviews" /
                    # "my recommendations" page keys off this.
                    SignInUser(
                        {
                            "user_id": response.json()["user_id"],
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                        }
                    )
                    st.rerun()
                else:
                    st.error(
                        f"Failed to add User: {response.json().get('error', 'Unknown error')}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {str(e)}")
                st.info("Please ensure the API server is running")


st.session_state['name'] = st.session_state.success_user_name

# Show success modal if NGO was added successfully
if st.session_state.show_success_modal:
    show_success_dialog(st.session_state.success_user_name)

if st.button("← Home"):
    st.switch_page("pages/book-lovers.py")
    
