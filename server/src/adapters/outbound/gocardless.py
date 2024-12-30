"""GoCardless API adapter implementation."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx

from server.src.core.domain import TokenInfo, Institution, Requisition
from server.src.core.ports import (
    GoCardlessService,
    TokenService,
    InstitutionService,
    RequisitionService,
)

API_CONFIG = {
    "base_url": "https://bankaccountdata.gocardless.com/api/v2",
    "headers": {"Accept": "application/json", "Content-Type": "application/json"},
}

logger = logging.getLogger(__name__)


class GoCardlessTokenAdapter(TokenService):
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.access_expires = None
        self.refresh_expires = None

    def get_token(self) -> str:
        if (
            self.access_token
            and self.access_expires
            and datetime.now() < self.access_expires
        ):
            return self.access_token

        if (
            self.refresh_token
            and self.refresh_expires
            and datetime.now() < self.refresh_expires
        ):
            return self.refresh_token()

        token_info = self.create_token()
        return token_info.access_token

    def refresh_token(self) -> str:
        if not self.refresh_token:
            token_info = self.create_token()
            return token_info.access_token

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{API_CONFIG['base_url']}/token/refresh/",
                    headers=API_CONFIG["headers"],
                    json={"refresh": self.refresh_token},
                )

                if not response.is_success:
                    token_info = self.create_token()
                    return token_info.access_token

                data = response.json()
                token_info = self._update_tokens(data)
                return token_info.access_token

        except Exception:
            token_info = self.create_token()
            return token_info.access_token

    def create_token(self) -> TokenInfo:
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

                return self._update_tokens(data)
        except Exception as e:
            raise Exception(f"Error creating token: {str(e)}")

    def _update_tokens(self, data: Dict[str, Any]) -> TokenInfo:
        self.access_token = data["access"]
        self.refresh_token = data["refresh"]
        self.access_expires = datetime.now() + timedelta(seconds=data["access_expires"])
        self.refresh_expires = datetime.now() + timedelta(
            seconds=data["refresh_expires"]
        )

        return TokenInfo(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            access_expires=self.access_expires,
            refresh_expires=self.refresh_expires,
        )


class GoCardlessApiAdapter(GoCardlessService):
    async def get_account_details(
        self, account_id: str, access_token: str
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_CONFIG['base_url']}/accounts/{account_id}/",
                headers={
                    **API_CONFIG["headers"],
                    "Authorization": f"Bearer {access_token}",
                },
            )
            response.raise_for_status()
            rate_limits = await self._extract_rate_limits(response.headers)
            account_details = response.json()

            balance_response = await client.get(
                f"{API_CONFIG['base_url']}/accounts/{account_id}/balances/",
                headers={
                    **API_CONFIG["headers"],
                    "Authorization": f"Bearer {access_token}",
                },
            )

            if balance_response.status_code == 429:
                # Return dummy values for balance if rate limited
                account_details["balance"] = "0.00"
                account_details["currency"] = "EUR"
            else:
                balance_response.raise_for_status()
                balance_data = balance_response.json()
                if balance_data.get("balances"):
                    latest_balance = balance_data["balances"][0]
                    account_details["balance"] = latest_balance.get(
                        "balanceAmount", {}
                    ).get("amount")
                    account_details["currency"] = latest_balance.get(
                        "balanceAmount", {}
                    ).get("currency")

            return account_details, rate_limits

    async def get_transactions(
        self,
        account_id: str,
        access_token: str,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        url = f"{API_CONFIG['base_url']}/accounts/{account_id}/transactions/"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"date_from": from_date} | ({"date_to": to_date} if to_date else {})

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, headers=headers, params=params, follow_redirects=True
            )
            rate_limits = await self._extract_rate_limits(response.headers)

            if response.status_code == 429:  # Too Many Requests
                return {}, rate_limits

            response.raise_for_status()
            return response.json()["transactions"], rate_limits

    # noinspection PyMethodMayBeStatic
    async def _extract_rate_limits(self, headers: httpx.Headers) -> Dict[str, Any]:
        seconds_until_reset = int(
            headers.get("HTTP_X_RATELIMIT_ACCOUNT_SUCCESS_RESET", 0)
        )
        delta = (
            timedelta(seconds=seconds_until_reset)
            if seconds_until_reset
            else timedelta(hours=24)
        )
        reset_timestamp = (datetime.now() + delta).isoformat()

        return {
            "limit": int(headers.get("HTTP_X_RATELIMIT_ACCOUNT_SUCCESS_LIMIT", 0)),
            "remaining": int(
                headers.get("HTTP_X_RATELIMIT_ACCOUNT_SUCCESS_REMAINING", 0)
            ),
            "reset": reset_timestamp,
        }


class GoCardlessInstitutionAdapter(InstitutionService):
    async def get_institutions(self, country: str) -> list[Institution]:
        token_adapter = GoCardlessTokenAdapter()
        token = token_adapter.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_CONFIG['base_url']}/institutions/?country={country}",
                headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

            return [
                Institution(
                    id=inst["id"],
                    name=inst["name"],
                    bic=inst["bic"],
                    transaction_total_days=inst["transaction_total_days"],
                    countries=inst["countries"],
                    logo=inst["logo"],
                )
                for inst in data
            ]


class GoCardlessRequisitionAdapter(RequisitionService):
    def __init__(self):
        self.token_adapter = GoCardlessTokenAdapter()

    async def get_requisitions(self) -> list[Requisition]:
        token = self.token_adapter.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_CONFIG['base_url']}/requisitions/",
                headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            data = response.json()

            # Filter and sort requisitions
            requisitions = [
                Requisition(**req) for req in data["results"] if req["status"] == "LN"
            ]
            requisitions.sort(key=lambda x: datetime.fromisoformat(x.created))
            return requisitions

    async def get_requisition_details(self, requisition_id: str) -> Dict[str, Any]:
        async def extract_account_details(account_id, token):
            details, _ = await gocardless_api.get_account_details(account_id, token)
            return details

        token = self.token_adapter.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_CONFIG['base_url']}/requisitions/{requisition_id}/",
                headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            requisition = response.json()

            # Get details for each account
            gocardless_api = GoCardlessApiAdapter()
            account_details = await asyncio.gather(
                *[
                    extract_account_details(account_id, token)
                    for account_id in requisition["accounts"]
                ]
            )

            requisition["accounts"] = account_details
            return requisition

    async def create_requisition(self, params: Dict[str, Any]) -> Requisition:
        token = self.token_adapter.get_token()

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
            return Requisition(**response.json())

    async def delete_requisition(self, requisition_id: str) -> None:
        token = self.token_adapter.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_CONFIG['base_url']}/requisitions/{requisition_id}/",
                headers={**API_CONFIG["headers"], "Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
