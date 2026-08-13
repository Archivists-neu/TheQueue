# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


def load_nav_css():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #171922;
            border-right: 1px solid #2d3040;
        }
        [data-testid="stVerticalBlock"] {
            display: flex;
            align-items: center;
        }

        [data-testid="stSidebarContent"] {
            padding: 1.25rem 0.75rem;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            margin-bottom: 0.35rem;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            padding: 0.7rem 0.85rem;
            border-radius: 10px;
            color: #d9dbe7;
            text-decoration: none;
            transition:
                background-color 150ms ease,
                color 150ms ease,
                transform 150ms ease;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background-color: #282c3d;
            color: #ffffff;
            transform: translateX(3px);
        }

        [data-testid="stSidebar"]
        [data-testid="stPageLink"] a[aria-current="page"] {
            background-color: #6c63ff;
            color: #ffffff;
            font-weight: 600;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] button {
            width: 100%;
            margin-top: 1rem;
            border: 1px solid #6c63ff;
            border-radius: 10px;
            background-color: transparent;
            color: #ffffff;
            transition: background-color 150ms ease;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] img {
            width: 100%;
            margin-top: 1rem;
            border: 1px solid #6c63ff;
            border-radius: 10px;
            background-color: transparent;
            color: #ffffff;
            transition: background-color 150ms ease;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background-color: #6c63ff;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,)

    # ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


    # --- switched to book lovers----
# ---- Role: pol_strat_advisor ------------------------------------------------

def book_lover_home_nav():
    st.sidebar.page_link("pages/book-lovers.py", label="Home", icon="📚")


def media_search_nav():
    st.sidebar.page_link("pages/media-search.py", label="Media Search", icon="🔎")

def friend_search_nav():
    st.sidebar.page_link("pages/friend-search.py", label="Friend Search", icon="🫂")

def profile_view_nav():
    st.sidebar.page_link("pages/user-profile.py", label="Profile", icon="👤")

def map_demo_nav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demonstration", icon="🗺️")


# ---- Role: data analyst -----------------------------------------------------

def analyst_overview_nav():
    st.sidebar.page_link(
        "pages/analyst.py", label="Analyst Overview", icon="📊"
    )


def performance_nav():
    st.sidebar.page_link("pages/analyst_dashboard.py", label="Performance Dashboard", icon="📈")


    # --- Kept as System Admin ------
# ---- Role: administrator ----------------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/system-admin.py", label="System Admin", icon="🖥️")


def user_search_nav():
    st.sidebar.page_link(
        "pages/user-search.py", label="User Search", icon="🔎"
    )

def add_new_media_nav():
    st.sidebar.page_link(
        "pages/add-media.py", label="Add New Media", icon="📖"
    )

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    load_nav_css()
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/the-queue-logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "book_lover":
            book_lover_home_nav()
            media_search_nav()
            friend_search_nav()
            profile_view_nav()
            map_demo_nav()

        if st.session_state["role"] == "analyst":
            analyst_overview_nav()
            performance_nav()

        if st.session_state["role"] == "administrator":
            admin_home_nav()
            user_search_nav()
            add_new_media_nav()

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
