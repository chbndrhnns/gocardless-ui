from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from server.services.sync_service import (
    get_token_storage,
    get_gocardless_account_name,
    get_lunchmoney_account_name,
    load_account_links,
    sync_transactions,
    get_gocardless_token,
    get_account_status,
    fetch_all_lunchmoney_accounts,
    TokenStorage,
    reset_sync_status,
)

router = APIRouter()


class SyncRequest(BaseModel):
    accountId: Optional[str] = None


@router.get("/status")
async def get_sync_status():
    await reset_sync_status()

    token_storage = get_token_storage()
    accounts = await load_account_links()
    access_token = await get_gocardless_token(token_storage)
    lunchmoney_accounts = await fetch_all_lunchmoney_accounts()

    status_list = []
    for account in accounts:
        status = await get_account_status(account["gocardlessId"])
        status_list.append(
            {
                "gocardlessId": account["gocardlessId"],
                "gocardlessName": await get_gocardless_account_name(
                    account["gocardlessId"], access_token
                ),
                "lunchmoneyName": await get_lunchmoney_account_name(
                    account["lunchmoneyId"], lunchmoney_accounts
                ),
                **status,
            }
        )

    return {"accounts": status_list}


@router.post("")
async def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks):
    token_storage = get_token_storage()
    background_tasks.add_task(sync_transactions, token_storage, request.accountId)
    return {"status": "success"}


async def schedule_sync(token_storage: TokenStorage):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(
        sync_transactions,
        args=(token_storage,),
        id="startup_sync_job",
        replace_existing=True,
    )
