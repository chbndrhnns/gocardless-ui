import os
import httpx
from datetime import datetime, timedelta

API_CONFIG = {
    "base_url": "https://bankaccountdata.gocardless.com/api/v2",
    "headers": {"Accept": "application/json", "Content-Type": "application/json"},
}

access_token = None
refresh_token = None
access_expires = None
refresh_expires = None


def get_access_token():
    global access_token, refresh_token, access_expires, refresh_expires

    if access_token and access_expires and datetime.now() < access_expires:
        return access_token

    if refresh_token and refresh_expires and datetime.now() < refresh_expires:
        return refresh_access_token()

    return create_new_token()


def create_new_token():
    global access_token, refresh_token, access_expires, refresh_expires

    try:
        with httpx.Client() as client:
            response = client.post(
                f"{API_CONFIG['base_url']}/token/new/",
                headers=API_CONFIG["headers"],
                json={
                    "secret_id": os.getenv("GOCARDLESS_SECRET_ID"),
                    "secret_key": os.getenv("GOCARDLESS_SECRET_KEY"),
                },
            )
            response.raise_for_status()
            data = response.json()

            update_tokens(data)
            return data["access"]
    except Exception as e:
        raise Exception(f"Error creating token: {str(e)}")


def refresh_access_token():
    global access_token, refresh_token, access_expires, refresh_expires

    if not refresh_token:
        return create_new_token()

    try:
        with httpx.Client() as client:
            response = client.post(
                f"{API_CONFIG['base_url']}/token/refresh/",
                headers=API_CONFIG["headers"],
                json={"refresh": refresh_token},
            )

            if not response.is_success:
                return create_new_token()

            data = response.json()
            update_tokens(data)
            return data["access"]

    except Exception:
        return create_new_token()


def update_tokens(data):
    global access_token, refresh_token, access_expires, refresh_expires

    access_token = data["access"]
    refresh_token = data["refresh"]
    access_expires = datetime.now() + timedelta(seconds=data["access_expires"])
    refresh_expires = datetime.now() + timedelta(seconds=data["refresh_expires"])
