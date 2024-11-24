import os
from datetime import datetime

import httpx

from .storage import write_links, read_links

LUNCHMONEY_API_URL = "https://dev.lunchmoney.app/v1"


def get_lunchmoney_headers():
    return {
        "Authorization": f"Bearer {os.getenv('LUNCHMONEY_ACCESS_TOKEN')}",
        "Content-Type": "application/json",
    }


async def get_assets():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LUNCHMONEY_API_URL}/assets", headers=get_lunchmoney_headers()
            )
            response.raise_for_status()
            data = response.json()

            # Get linked accounts to add linking information
            links_data = read_links()

            # Add linked status to each asset
            assets_with_links = [
                {
                    **asset,
                    "linked_account": next(
                        (
                            link["gocardlessId"]
                            for link in links_data["links"]
                            if link["lunchmoneyId"] == asset["id"]
                        ),
                        None,
                    ),
                }
                for asset in data["assets"]
            ]

            return assets_with_links
    except Exception as e:
        raise Exception(f"Error fetching Lunchmoney assets: {str(e)}")


def link_accounts(lunchmoney_id: int, gocardless_id: str):
    try:
        data = read_links()

        # Remove any existing links for either account
        data["links"] = [
            link
            for link in data["links"]
            if link["lunchmoneyId"] != lunchmoney_id
            and link["gocardlessId"] != gocardless_id
        ]

        # Add new link
        data["links"].append(
            {
                "lunchmoneyId": lunchmoney_id,
                "gocardlessId": gocardless_id,
                "createdAt": datetime.now().isoformat(),
            }
        )

        write_links(data)
        return True
    except Exception as e:
        raise Exception(f"Error linking accounts: {str(e)}")


def unlink_accounts(lunchmoney_id: int):
    try:
        data = read_links()
        data["links"] = [
            link for link in data["links"] if link["lunchmoneyId"] != lunchmoney_id
        ]
        write_links(data)
        return True
    except Exception as e:
        raise Exception(f"Error unlinking accounts: {str(e)}")
