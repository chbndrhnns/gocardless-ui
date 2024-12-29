"""Sync API routes."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from server.src.core.services.sync_service import SyncService
from server.src.core.ports.services import (
    GoCardlessService,
    LunchMoneyService,
    TokenService,
)
from server.src.adapters.inbound.web.dependencies import (
    get_gocardless_service,
    get_lunchmoney_service,
    get_sync_service,
    get_token_service,
)

router = APIRouter()


class SyncRequest(BaseModel):
    accountId: Optional[str] = None


async def get_next_sync_time() -> str:
    now = datetime.now()
    next_sync = now.replace(
        hour=((now.hour // 3) * 3 + 3) % 24, minute=0, second=0, microsecond=0
    )
    if next_sync <= now:
        next_sync += timedelta(hours=3)
    return next_sync.isoformat()


@router.get("/status")
async def get_sync_status(
    sync_service: SyncService = Depends(get_sync_service),
    token_service: TokenService = Depends(get_token_service),
    gocardless_service: GoCardlessService = Depends(get_gocardless_service),
    lunchmoney_service: LunchMoneyService = Depends(get_lunchmoney_service),
):
    # Reset any stale sync statuses
    await sync_service.sync_status_repository.reset_sync_status()

    # Get necessary data
    account_links = await sync_service.account_link_repository.load_links()
    access_token = token_service.get_token()
    lunchmoney_accounts = await lunchmoney_service.get_assets()
    lunchmoney_accounts_dict = {acc["id"]: acc["name"] for acc in lunchmoney_accounts}

    # Build status response
    status_list = []
    for link in account_links:
        account_details, _ = await gocardless_service.get_account_details(
            link.gocardless_id, access_token
        )
        status = await sync_service.sync_status_repository.get_status(
            link.gocardless_id
        )

        status_list.append(
            {
                "gocardlessId": link.gocardless_id,
                "gocardlessName": account_details.get("iban", "Unknown Account"),
                "lunchmoneyName": lunchmoney_accounts_dict.get(
                    link.lunchmoney_id, "Unknown Account"
                ),
                "lastSync": status.last_sync,
                "lastSyncStatus": status.last_sync_status,
                "lastS yncTransactions": status.last_sync_transactions,
                "isSyncing": status.is_syncing,
                "rateLimit": {
                    "limit": status.rate_limit.limit if status.rate_limit else -1,
                    "remaining": status.rate_limit.remaining
                    if status.rate_limit
                    else -1,
                    "reset": status.rate_limit.reset if status.rate_limit else None,
                },
                "nextSync": await get_next_sync_time(),
            }
        )

    return {"accounts": status_list}


@router.post("")
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    sync_service: SyncService = Depends(get_sync_service),
):
    background_tasks.add_task(sync_service.sync_transactions, request.accountId)
    return {"status": "success"}
