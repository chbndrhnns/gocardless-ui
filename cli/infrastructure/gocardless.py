from datetime import datetime
import httpx
from dotenv import load_dotenv
import os

from ..domain.models import Account, Requisition
from ..domain.ports import RequisitionPort, AccountPort


class GoCardlessClient:
    """GoCardless API client."""

    def __init__(self):
        load_dotenv()

        self.base_url = "https://bankaccountdata.gocardless.com/api/v2"
        self.client_id = os.getenv("GOCARDLESS_SECRET_ID")
        self.client_secret = os.getenv("GOCARDLESS_SECRET_KEY")
        self.access_token = None

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Please set GOCARDLESS_SECRET_ID and GOCARDLESS_SECRET_KEY in .env file"
            )

        self._authenticate()

    def _authenticate(self):
        """Authenticate with the API and get an access token."""
        auth_url = f"{self.base_url}/token/new/"
        payload = {
            "secret_id": self.client_id,
            "secret_key": self.client_secret,
        }

        response = httpx.post(auth_url, json=payload)
        response.raise_for_status()
        self.access_token = response.json()["access"]

    def get_headers(self):
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }


class GoCardlessAdapter(RequisitionPort, AccountPort):
    """Adapter for GoCardless API implementing both ports."""

    def __init__(self):
        self.client = GoCardlessClient()

    async def get_requisitions(self) -> list[Requisition]:
        """Get all requisitions."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.base_url}/requisitions/",
                headers=self.client.get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            requisitions = []
            for item in data["results"]:
                if item["status"] == "LN":  # Only include active requisitions
                    requisitions.append(
                        Requisition(
                            id=item["id"],
                            institution_id=item["institution_id"],
                            status=item["status"],
                            created=datetime.fromisoformat(item["created"]),
                            accounts=[],  # Will be populated in get_requisition_details
                        )
                    )
            return requisitions

    async def get_requisition_details(self, requisition_id: str) -> Requisition:
        """Get details for a specific requisition."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.base_url}/requisitions/{requisition_id}/",
                headers=self.client.get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            # Get account details
            accounts = []
            for account_id in data["accounts"]:
                account = await self.get_account_details(account_id)
                accounts.append(account)

            return Requisition(
                id=data["id"],
                institution_id=data["institution_id"],
                status=data["status"],
                created=datetime.fromisoformat(data["created"]),
                accounts=accounts,
            )

    async def delete_requisition(self, requisition_id: str) -> None:
        """Delete a requisition."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.client.base_url}/requisitions/{requisition_id}/",
                headers=self.client.get_headers(),
            )
            response.raise_for_status()

    async def get_account_details(self, account_id: str) -> Account:
        """Get details for a specific account."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.client.base_url}/accounts/{account_id}/",
                headers=self.client.get_headers(),
            )
            response.raise_for_status()
            data = response.json()

            return Account(
                id=data["id"],
                iban=data.get("iban"),
                currency=data.get("currency"),
                status=data["status"],
            )
