import httpx

from .auth import get_access_token, API_CONFIG


async def get_institutions(country: str):
    token = get_access_token()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_CONFIG['base_url']}/institutions/?country={country}",
            headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
