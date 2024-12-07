from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Blueprint, jsonify, request

from ..services.sync_service import (
    get_token_storage,
    get_gocardless_account_name,
    get_lunchmoney_account_name,
    load_account_links,
    sync_transactions,
    get_gocardless_token,
    get_account_status,
    fetch_all_lunchmoney_accounts,
    TokenStorage,
)

sync_bp = Blueprint("sync", __name__)


@sync_bp.route("/status")
async def get_sync_status():
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

    return jsonify({"accounts": status_list})


@sync_bp.route("", methods=["POST"])
async def trigger_sync():
    token_storage = get_token_storage()
    data = request.get_json()

    await sync_transactions(token_storage, data["accountId"])

    return jsonify({"status": "success"})


async def periodic_sync(token_storage):
    await sync_transactions(token_storage)


def schedule_sync(token_storage: TokenStorage):
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(
        periodic_sync,
        args=(token_storage,),
        id="startup_sync_job",
        replace_existing=True,
    )

    # from apscheduler.triggers.cron import CronTrigger
    # scheduler.add_job(
    #     lambda: periodic_sync(token_storage),
    #     trigger=CronTrigger(hour="*/3"),
    #     id="sync_job",
    #     replace_existing=True,
    # )
