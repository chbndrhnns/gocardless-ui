from flask import Blueprint, jsonify

from ..services.accounts import get_account_details

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/<id>", methods=["GET"])
async def get_account(id):
    try:
        account = await get_account_details(id)
        return jsonify(account)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
