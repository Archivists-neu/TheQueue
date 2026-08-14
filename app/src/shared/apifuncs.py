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


def GetApiData(endpoint, params=None):
    url = endpoint if endpoint.startswith("http") else GetApiRoute(endpoint)

    try:
        response = requests.get(
            url,
            params=params,
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


def PostApiData(endpoint, payload):
    """
    POST JSON to the API.

    Returns (ok, body). On a non-2xx or a connection failure, ok is False
    and body carries whatever the caller should show the user.
    """
    url = endpoint if endpoint.startswith("http") else GetApiRoute(endpoint)

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        if response.status_code in (200, 201):
            return True, response.json()

        try:
            error = response.json().get("error", response.text)
        except ValueError:
            error = response.text

        logger.error(f"POST {url} failed ({response.status_code}): {error}")

        return False, error

    except requests.RequestException as e:
        logger.error(f"POST {url} failed: {e}")

        return False, f"Could not reach the API at {url}."


def PutApiData(endpoint, payload):
    """PUT JSON to the API. Same (ok, body) contract as PostApiData."""
    url = endpoint if endpoint.startswith("http") else GetApiRoute(endpoint)

    try:
        response = requests.put(
            url,
            json=payload,
            timeout=10
        )

        if response.status_code in (200, 201):
            return True, response.json()

        try:
            error = response.json().get("error", response.text)
        except ValueError:
            error = response.text

        logger.error(f"PUT {url} failed ({response.status_code}): {error}")

        return False, error

    except requests.RequestException as e:
        logger.error(f"PUT {url} failed: {e}")

        return False, f"Could not reach the API at {url}."


def fetchUserApiData():
    return GetApiData("user")


def GetUsersApi(user_id=None) -> str:
    """
    Base user URL, or the URL of one user.

    The API exposes list/create on /user and update/delete on /user/<id>.
    """
    if user_id is None:
        return GetApiRoute("user")

    return GetApiRoute(f"user/{user_id}")


def GetLocationsApi() -> str:
    """Base location URL. The API exposes list/create on /location."""
    return GetApiRoute("location")


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


def GetFriendshipsApi(friendship_id=None) -> str:
    """
    Base friendships URL, or the URL of one friendship.

    The API exposes list/create on /friendship/friendships and update on
    /friendship/friendships/<friendship_id>.
    """
    if friendship_id is None:
        return GetApiRoute("friendship/friendships")

    return GetApiRoute(f"friendship/friendships/{friendship_id}")


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
