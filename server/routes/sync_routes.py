from flask import Blueprint, jsonify, request

from ..services.sync_service import (
    get_token_storage,
    get_gocardless_account_name,
    get_lunchmoney_account_name,
    load_account_links,
    sync_transactions,
    get_gocardless_token,
    get_account_status,
    is_manual_sync_running,
    sync_lock,
    fetch_all_lunchmoney_accounts,
)

sync_bp = Blueprint("sync", __name__)


@sync_bp.route("/status")
def get_sync_status():
    token_storage = get_token_storage()
    accounts = load_account_links()
    access_token = get_gocardless_token(token_storage)
    lunchmoney_accounts = fetch_all_lunchmoney_accounts()

    status_list = []
    for account in accounts:
        status = get_account_status(account["gocardlessId"], access_token)
        status_list.append(
            {
                "gocardlessId": account["gocardlessId"],
                "gocardlessName": get_gocardless_account_name(
                    account["gocardlessId"], access_token
                ),
                "lunchmoneyName": get_lunchmoney_account_name(
                    account["lunchmoneyId"], lunchmoney_accounts
                ),
                **status,
            }
        )

    return jsonify({"accounts": status_list})


@sync_bp.route("", methods=["POST"])
def trigger_sync():
    token_storage = get_token_storage()
    data = request.get_json()

    if "accountId" not in data:
        return jsonify({"status": "error", "message": "accountId not provided"}), 400

    is_manual_sync_running.set()

    with sync_lock:
        try:
            sync_transactions(token_storage, data["accountId"])
        finally:
            is_manual_sync_running.clear()

    return jsonify({"status": "success"})
