from flask import Blueprint, jsonify, request

from ..services.sync_service import (
    get_token_storage,
    get_gocardless_account_name,
    get_lunchmoney_account_name,
    load_account_links,
    sync_transactions,
    get_last_sync,
    get_gocardless_token,
)

# Blueprint Setup
sync_bp = Blueprint(
    "sync", __name__, template_folder="templates", static_folder="static"
)


@sync_bp.route("/status")
def get_accounts():
    token_storage = get_token_storage()
    accounts = load_account_links()
    last_sync = get_last_sync()
    access_token = get_gocardless_token(token_storage)

    for account in accounts:
        account["gocardlessName"] = get_gocardless_account_name(
            account["gocardlessId"], access_token
        )
        account["lunchmoneyName"] = get_lunchmoney_account_name(account["lunchmoneyId"])

    return jsonify({"accounts": accounts, "lastSync": last_sync})


@sync_bp.route("", methods=["POST"])
def trigger_sync():
    token_storage = get_token_storage()
    data = request.get_json()
    if "accountId" in data:
        sync_transactions(token_storage, data["accountId"])
        return jsonify({"status": "success"})
    return jsonify({"status": "failure", "reason": "accountId not provided"}), 400
