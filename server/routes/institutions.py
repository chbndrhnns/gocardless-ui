from flask import Blueprint, jsonify, request

from ..services.institutions import get_institutions

institutions_bp = Blueprint("institutions", __name__)


@institutions_bp.route("/", methods=["GET"])
async def list_institutions():
    try:
        country = request.args.get("country")
        institutions = await get_institutions(country)
        return jsonify(institutions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
