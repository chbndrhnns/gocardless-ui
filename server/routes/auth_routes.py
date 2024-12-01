from flask import Blueprint, jsonify

from ..services.auth import get_access_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/token", methods=["POST"])
async def token():
    try:
        token = get_access_token()
        return jsonify(token)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
