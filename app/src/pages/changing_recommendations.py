import streamlit as st
import requests
from modules.nav import SideBarLinks
from shared.apifuncs import GetFriendshipsApi, GetRecommendationApi


st.set_page_config(layout="wide")
SideBarLinks(show_home=True)

st.title("Recommendation Data")

st.write("### Review Recommendation Data")
st.write(
    "Reviewing recommendations."
)


RECOMMENDATION_URL = GetRecommendationApi()

FRIENDSHIP_URL = GetFriendshipsApi()


# Get friendships so we can display people's names
friendships = []
friendship_lookup = {}

try:
    friendship_response = requests.get(FRIENDSHIP_URL)

    if friendship_response.status_code == 200:

        friendships = friendship_response.json()

        friendship_lookup = {
            friendship["friendship_id"]: (
                f"{friendship['requester_name']} ↔ "
                f"{friendship['addressee_name']}"
            )
            for friendship in friendships
        }

    else:
        st.error(
            f"Could not load friendships: "
            f"{friendship_response.text}"
        )

except requests.exceptions.RequestException as e:
    st.error(
        f"Could not connect to the friendship API: {e}"
    )


# --- Search bar at the top: keyword or poster name ---
st.write("### Search Recommendations")

col1, col2 = st.columns(2)
with col1:
    keyword_search = st.text_input(
        "Search by Keyword",
        placeholder="Search within attached messages..."
    )
with col2:
    user_search = st.text_input(
        "Search by User",
        placeholder="Search by requester or addressee name..."
    )



# Build query parameters
params = {}


# Get recommendation data
recommendations = []

try:

    response = requests.get(
        RECOMMENDATION_URL,
        params=params
    )

    if response.status_code == 200:

        recommendations = response.json()

        # --- Client-side keyword / user search on top of the API filters ---
        if keyword_search:
            keyword_lower = keyword_search.lower()
            recommendations = [
                r for r in recommendations
                if keyword_lower in str(r.get("attached_message", "")).lower()
            ]

        if user_search:
            user_lower = user_search.lower()

            def matches_user(r):
                names = friendship_lookup.get(r.get("friendship_id"), "")
                return user_lower in names.lower()

            recommendations = [r for r in recommendations if matches_user(r)]

        st.write("### Recommendation Results")

        if recommendations:

            display_recommendations = []

            for recommendation in recommendations:

                display_row = recommendation.copy()

                # Remove the confusing friendship ID
                friendship_id = display_row.pop(
                    "friendship_id",
                    None
                )

                # Replace it with the names of the people
                display_row["friendship"] = (
                    friendship_lookup.get(
                        friendship_id,
                        f"Friendship {friendship_id}"
                    )
                )

                display_recommendations.append(
                    display_row
                )

            st.dataframe(
                display_recommendations,
                use_container_width=True,
                hide_index=True
            )

            st.write(
                f"Total Recommendations: "
                f"{len(recommendations)}"
            )

        else:
            st.info(
                "No recommendations match the selected filters."
            )

    else:
        st.error(
            f"Could not load recommendation data: "
            f"{response.text}"
        )

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not connect to the recommendation API: {e}"
    )


# --- Edit the attached message on a recommendation ---
st.divider()
st.write("### Edit a Recommendation's Message")

if recommendations:
    edit_options = {}
    for r in recommendations:
        friendship_label = friendship_lookup.get(
            r.get("friendship_id"), f"Friendship {r.get('friendship_id')}"
        )
        label = f"Rec {r['recommendation_id']} — {friendship_label}"
        edit_options[label] = r

    selected_edit_label = st.selectbox(
        "Select a recommendation to edit",
        list(edit_options.keys()),
        key="edit_select"
    )

    selected_recommendation = edit_options[selected_edit_label]

    new_message = st.text_area(
        "Attached Message",
        value=selected_recommendation.get("attached_message") or "",
        key="edit_message_text"
    )

    if st.button("Save Message Changes"):
        try:
            edit_url = GetRecommendationApi(
                selected_recommendation["recommendation_id"]
            )
            edit_response = requests.put(
                edit_url,
                json={"attached_message": new_message}
            )

            if edit_response.status_code == 200:
                st.success("Recommendation updated successfully. Refresh to see the change.")
            else:
                st.error(
                    f"Failed to update recommendation: "
                    f"{edit_response.json().get('error', 'Unknown error')}"
                )
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the recommendation API: {e}")
else:
    st.info("No recommendations available to edit.")


# --- Delete a recommendation ---
st.divider()
st.write("### Delete a Recommendation")

if recommendations:
    delete_options = {}
    for r in recommendations:
        friendship_label = friendship_lookup.get(
            r.get("friendship_id"), f"Friendship {r.get('friendship_id')}"
        )
        label = f"Rec {r['recommendation_id']} — {friendship_label}"
        delete_options[label] = r["recommendation_id"]

    selected_delete_labels = st.multiselect(
        "Select recommendation(s) to delete",
        list(delete_options.keys())
    )

    if selected_delete_labels:
        st.warning(
            f"You are about to delete {len(selected_delete_labels)} "
            f"recommendation(s). This cannot be undone."
        )
        if st.button("Confirm Delete", type="primary"):
            deleted = 0
            errors = []
            for label in selected_delete_labels:
                recommendation_id = delete_options[label]
                try:
                    delete_url = GetRecommendationApi(recommendation_id)
                    resp = requests.delete(delete_url)
                    if resp.status_code == 200:
                        deleted += 1
                    else:
                        errors.append(
                            f"{label}: {resp.json().get('error', 'Unknown error')}"
                        )
                except requests.exceptions.RequestException as e:
                    errors.append(f"{label}: could not connect to API")

            if deleted:
                st.success(f"Deleted {deleted} recommendation(s). Refresh the page to update the table.")
            for err in errors:
                st.error(err)
else:
    st.info("No recommendations available to delete.")


# Back button
if st.button("Back to Home"):
    st.switch_page(
        "pages/system-admin.py"
    )