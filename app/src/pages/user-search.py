import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
from shared.apifuncs import GetUsersApi

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# User Search")

st.write("""
Search for users by name, email, or account status. All users in the database
are listed in the table below the search results.
""")

# --- Search form ---
with st.form("user_search_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name")
    with col2:
        email = st.text_input("Email")
    with col3:
        # Mirrors the account_status ENUM in ddl.sql; "" means no filter.
        status = st.selectbox("Status", ["", "online", "busy", "offline", "custom"])

    submitted = st.form_submit_button("Search")

if submitted:
    params = {}
    if name:
        params["name"] = name
    if email:
        params["email"] = email
    if status:
        params["account_status"] = status

    try:
        response = requests.get(GetUsersApi(), params=params)
        search_results = response.json()

        st.write("### Search Results")
        if search_results:
            st.dataframe(search_results)
        else:
            st.write("No users found matching your search.")
    except requests.exceptions.RequestException as e:
        st.write("**Important**: Could not connect to sample API, so no search results to show.")
        logger.error(f"Error searching users: {e}")

st.divider()

# --- Full table of all users ---

st.write("### All Users")

data = {}
try:
    data = requests.get(GetUsersApi()).json()
except requests.exceptions.RequestException as e:
    st.write("**Important**: Could not connect to sample API, so using dummy data.")
    data = {}

if data:
    df = pd.DataFrame(data)

    column_labels = {
        "user_id": "User ID",
        "first_name": "First Name",
        "last_name": "Last Name",
        "email": "Email",
        "phone": "Phone",
        "dob": "Date of Birth",
        "gender": "Gender",
        "account_status": "Status",
        "custom_status_message": "Status Message",
        "date_account_creation": "Member Since",
        "location_id": "Location",
    }

    df = df.rename(columns=column_labels)
    st.dataframe(df, hide_index=True)
else:
    st.dataframe(data)

# --- Delete a user ---
st.divider()
st.write("### Delete a User")

if data:
    user_options = {
        f"{row['first_name']} {row['last_name']} (ID {row['user_id']})": row['user_id']
        for row in data
    }

    selected_labels = st.multiselect("Select user(s) to delete", list(user_options.keys()))

    if selected_labels:
        st.warning(f"You are about to delete {len(selected_labels)} user(s). This cannot be undone.")
        if st.button("Confirm Delete", type="primary"):
            deleted = 0
            errors = []
            for label in selected_labels:
                user_id = user_options[label]
                try:
                    resp = requests.delete(f"{GetUsersApi()}/{user_id}")
                    if resp.status_code == 200:
                        deleted += 1
                    else:
                        errors.append(f"{label}: {resp.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    errors.append(f"{label}: could not connect to API")
                    logger.error(f"Error deleting user {user_id}: {e}")

            if deleted:
                st.success(f"Deleted {deleted} user(s). Refresh the page to update the table.")
            for err in errors:
                st.error(err)

if st.button("← Home"):
    st.switch_page("pages/system-admin.py")