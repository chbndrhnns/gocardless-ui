"""File-based storage adapter implementations."""

import json
from pathlib import Path
from typing import List, Optional

from server.src.core.domain import AccountLink, AccountStatus, RateLimit
from server.src.core.ports.repositories import (
    AccountLinkRepository,
    SyncStatusRepository,
)

project_dir = Path(__file__).parents[3]
LINKS_FILE = Path(project_dir / "data" / "account-links.json")
SYNC_STATUS_FILE = Path(project_dir / "data" / "sync-status.json")


class FileAccountLinkRepository(AccountLinkRepository):
    def __init__(self, file_path: Path = LINKS_FILE):
        self.file_path = file_path

    async def load_links(self, account_id: Optional[str] = None) -> List[AccountLink]:
        try:
            if not self.file_path.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_links({"links": []})
                return []

            with open(self.file_path, "r") as f:
                data = json.load(f)
                links = [
                    AccountLink(
                        lunchmoney_id=link["lunchmoneyId"],
                        gocardless_id=link["gocardlessId"],
                        created_at=link["createdAt"],
                    )
                    for link in data["links"]
                ]

                if account_id:
                    links = [link for link in links if link.gocardless_id == account_id]

                return links
        except Exception as e:
            raise Exception(f"Error reading links: {str(e)}")

    def save_link(self, link: AccountLink) -> None:
        try:
            data = self._read_links()

            # Remove any existing links for either account
            data["links"] = [
                l
                for l in data["links"]
                if not (
                    l["lunchmoneyId"] == link.lunchmoney_id
                    or l["gocardlessId"] == link.gocardless_id
                )
            ]

            # Add new link
            data["links"].append(
                {
                    "lunchmoneyId": link.lunchmoney_id,
                    "gocardlessId": link.gocardless_id,
                    "createdAt": link.created_at,
                }
            )

            self._write_links(data)
        except Exception as e:
            raise Exception(f"Error saving link: {str(e)}")

    def remove_link(self, lunchmoney_id: int, gocardless_id: str) -> None:
        try:
            data = self._read_links()
            data["links"] = [
                link
                for link in data["links"]
                if not (
                    link["lunchmoneyId"] == lunchmoney_id
                    and link["gocardlessId"] == gocardless_id
                )
            ]
            self._write_links(data)
        except Exception as e:
            raise Exception(f"Error removing link: {str(e)}")

    def _read_links(self) -> dict:
        if not self.file_path.exists():
            return {"links": []}
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _write_links(self, data: dict) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)


class FileSyncStatusRepository(SyncStatusRepository):
    def __init__(self, file_path: Path = SYNC_STATUS_FILE):
        self.file_path = file_path

    async def get_status(self, account_id: str) -> AccountStatus:
        status_data = await self._load_status()
        account_status = status_data.get(account_id, {})

        if not account_status:
            return AccountStatus(
                last_sync=None,
                last_sync_status=None,
                last_sync_transactions=0,
                is_syncing=False,
                rate_limit=RateLimit(limit=-1, remaining=-1, reset=None),
            )

        return AccountStatus(
            last_sync=account_status.get("lastSync"),
            last_sync_status=account_status.get("lastSyncStatus"),
            last_sync_transactions=account_status.get("lastSyncTransactions", 0),
            is_syncing=account_status.get("isSyncing", False),
            rate_limit=RateLimit(
                limit=account_status.get("rateLimit", {}).get("limit", -1),
                remaining=account_status.get("rateLimit", {}).get("remaining", -1),
                reset=account_status.get("rateLimit", {}).get("reset"),
            )
            if account_status.get("rateLimit")
            else RateLimit(limit=-1, remaining=-1, reset=None),
        )

    async def save_status(self, account_id: str, status: AccountStatus) -> None:
        status_data = await self._load_status()

        status_data[account_id] = {
            "lastSync": status.last_sync,
            "lastSyncStatus": status.last_sync_status,
            "lastSyncTransactions": status.last_sync_transactions,
            "isSyncing": status.is_syncing,
            "rateLimit": {
                "limit": status.rate_limit.limit if status.rate_limit else -1,
                "remaining": status.rate_limit.remaining if status.rate_limit else -1,
                "reset": status.rate_limit.reset if status.rate_limit else None,
            }
            if status.rate_limit
            else None,
        }

        await self._save_status(status_data)

    async def reset_sync_status(self) -> None:
        status_data = await self._load_status()

        for account_id in status_data:
            if status_data[account_id].get("isSyncing"):
                status_data[account_id]["isSyncing"] = False
            if status_data[account_id].get("lastSyncStatus") == "pending":
                status_data[account_id]["lastSyncStatus"] = "error"

        await self._save_status(status_data)

    async def _load_status(self) -> dict:
        if not self.file_path.exists():
            return {}
        with open(self.file_path) as f:
            return json.load(f)

    async def _save_status(self, status: dict) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(status, f, indent=2)
