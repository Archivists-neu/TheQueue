import logging
import os
from urllib.parse import quote

import requests
import streamlit as st

# author: TuringProblem @1300 20260813

logger = logging.getLogger(__name__)

MEDIA_COLLECTION = "media"

# Hostname of the Flask API container (see docker-compose.yaml).
API_URL = os.getenv("API_URL", "http://web-api:4000")


def GetApiRoute(routLink: str) -> str:
    """
    Builds a full API URL. Accepts endpoints with or without a
    leading slash so both "user" and "/user" work.
    """
    return f"{API_URL}/{routLink.lstrip('/')}"


def GetApiData(endpoint):
    url = endpoint if endpoint.startswith("http") else GetApiRoute(endpoint)

    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        logger.error(f"API request failed for {url}: {e}")

        st.error(
            f"Unable to load data from {url}."
        )

        return []


def fetchUserApiData():
    return GetApiData("user")


def GetUsersApi() -> str:
    return GetApiRoute("user")


def GetMediaApi() -> str:
    return GetApiRoute(MEDIA_COLLECTION)


def GetRecommendationApi(recommendation_id=None) -> str:
    """
    Base recommendation URL, or the URL of one recommendation.

    The API exposes list/create on /recommendation and
    get/update/delete on /recommendation/<recommendation_id>.
    """
    if recommendation_id is None:
        return GetApiRoute("recommendation")

    return GetApiRoute(f"recommendation/{recommendation_id}")


def GetUserRecommendationsApi(user_id) -> str:
    return GetApiRoute(f"recommendation/users/{user_id}/recommendations")


def GetFriendshipsApi() -> str:
    return GetApiRoute("friendship/friendships")


def GetReviewsApi() -> str:
    return GetApiRoute("review/reviews")


def GetMediaSearchApi(**criteria: str) -> str:
    match criteria:
        case {"media_id": media_id, **rest} if not rest:
            return GetApiRoute(f"{MEDIA_COLLECTION}/{media_id}")
        case {"title": title, **rest} if not rest:
            return GetApiRoute(f"{MEDIA_COLLECTION}/title/{quote(title)}")
        case {"media_type": media_type, **rest} if not rest:
            return GetApiRoute(f"{MEDIA_COLLECTION}/type/{quote(media_type)}")
        case _:
            return GetApiRoute(MEDIA_COLLECTION)
