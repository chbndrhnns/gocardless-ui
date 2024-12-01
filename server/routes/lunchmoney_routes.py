from flask import Blueprint, jsonify, request

from ..services.lunchmoney import link_accounts, unlink_accounts, get_assets

lunchmoney_bp = Blueprint("lunchmoney", __name__)


@lunchmoney_bp.route("/assets", methods=["GET"])
async def list_assets():
    try:
        assets = await get_assets()
        return jsonify({"assets": assets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lunchmoney_bp.route("/link", methods=["POST"])
async def link():
    try:
        data = request.json
        link_accounts(data["lunchmoneyId"], data["gocardlessId"])
        return jsonify({"message": "Accounts linked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lunchmoney_bp.route("/unlink", methods=["POST"])
async def unlink():
    try:
        data = request.json
        unlink_accounts(data["lunchmoneyId"])
        return jsonify({"message": "Account unlinked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
