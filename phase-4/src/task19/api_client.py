
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://employee-ml-project-ea41.onrender.com",
).rstrip("/")

TIMEOUT = 30


class APIError(Exception):
    """Raised when the CortexHR API returns an error."""


def api_request(method, endpoint, user_id=None, **kwargs):
    """Send a request to the existing CortexHR FastAPI service."""

    headers = kwargs.pop("headers", {})

    if user_id:
        headers["X-Demo-User"] = user_id

    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            headers=headers,
            timeout=TIMEOUT,
            **kwargs,
        )

        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", "Request failed.")
            except ValueError:
                detail = "The server returned an unexpected response."

            raise APIError(f"{detail} (HTTP {response.status_code})")

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("The server returned an invalid response.") from exc

    except requests.exceptions.Timeout as exc:
        raise APIError(
            "The server took too long to respond. Please try again."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise APIError(
            "Unable to connect to CortexHR. Please check the API connection."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise APIError(
            "A network error occurred. Please try again."
        ) from exc


def show_api_error(error):
    """Display a friendly error message in Streamlit."""
    st.error(f"Unable to complete the request: {error}")
