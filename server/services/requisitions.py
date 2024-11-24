import asyncio

import httpx
from datetime import datetime

from .accounts import get_account_details
from .auth import get_access_token, API_CONFIG


async def get_requisitions():
    token = get_access_token()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_CONFIG['base_url']}/requisitions/",
            headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        data = response.json()

        # Sort results by creation date
        data["results"].sort(key=lambda x: datetime.fromisoformat(x["created"]))
        return data


async def get_requisition_details(requisition_id: str):
    token = get_access_token()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_CONFIG['base_url']}/requisitions/{requisition_id}/",
            headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        requisition = response.json()

        # Get details for each account
        account_details = await asyncio.gather(
            *[get_account_details(account_id) for account_id in requisition["accounts"]]
        )

        requisition["accounts"] = account_details
        return requisition


async def create_new_requisition(params: dict):
    token = get_access_token()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_CONFIG['base_url']}/requisitions/",
            headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
            json={
                "institution_id": params["institution_id"],
                "redirect": params["redirect"],
                "reference": params["reference"],
                "user_language": params["user_language"],
            },
        )
        response.raise_for_status()
        return response.json()


async def remove_requisition(requisition_id: str):
    token = get_access_token()

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_CONFIG['base_url']}/requisitions/{requisition_id}/",
            headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
