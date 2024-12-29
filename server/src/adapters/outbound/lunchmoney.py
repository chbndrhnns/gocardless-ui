"""Lunch Money API adapter implementation."""

import os
from typing import Any, Dict, List

import httpx

from server.src.core.domain.models import Transaction
from server.src.core.ports.services import LunchMoneyService

LUNCHMONEY_API_URL = "https://dev.lunchmoney.app/v1"


class LunchMoneyApiAdapter(LunchMoneyService):
    def __init__(self):
        self.api_key = os.getenv("LUNCHMONEY_ACCESS_TOKEN")
        if not self.api_key:
            raise ValueError("LUNCHMONEY_ACCESS_TOKEN is not set")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_assets(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{LUNCHMONEY_API_URL}/assets/",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()["assets"]
        except Exception as e:
            raise Exception(f"Error fetching Lunchmoney assets: {str(e)}")

    async def get_transactions(
        self, asset_id: int, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{LUNCHMONEY_API_URL}/transactions",
                    headers=self._get_headers(),
                    params={
                        "asset_id": asset_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                response.raise_for_status()
                return response.json().get("transactions", [])
        except Exception as e:
            raise Exception(f"Error fetching transactions: {str(e)}")

    async def create_transactions(
        self, transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        if not transactions:
            return []

        try:
            all_responses = []
            for batch in self._batch_transactions(transactions):
                data = {
                    "transactions": [self._transform_transaction(tx) for tx in batch],
                    "check_for_recurring": True,
                    "debit_as_negative": True,
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{LUNCHMONEY_API_URL}/transactions/",
                        headers=self._get_headers(),
                        json=data,
                    )
                    response.raise_for_status()
                    all_responses.append(response.json())

            return all_responses
        except Exception as e:
            raise Exception(f"Error creating transactions: {str(e)}")

    def _batch_transactions(
        self, transactions: List[Transaction], batch_size: int = 500
    ):
        """Split transactions into batches."""
        for i in range(0, len(transactions), batch_size):
            yield transactions[i : i + batch_size]

    def _transform_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Transform a Transaction model to Lunch Money API format."""
        return {
            "date": transaction.date,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "payee": transaction.payee,
            "notes": transaction.notes,
            "asset_id": transaction.asset_id,
            "external_id": transaction.external_id,
            "status": transaction.status,
        }
