import httpx

from .auth import API_CONFIG, get_access_token


async def get_account_details(account_id: str):
    token = get_access_token()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_CONFIG['base_url']}/accounts/{account_id}/",
            headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
