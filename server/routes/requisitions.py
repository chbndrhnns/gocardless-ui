from flask import Blueprint, jsonify, request

from ..services.requisitions import (
    get_requisition_details,
    create_new_requisition,
    remove_requisition,
    get_requisitions,
)

requisitions_bp = Blueprint("requisitions", __name__)


@requisitions_bp.route("", methods=["GET"])
async def list_requisitions():
    try:
        requisitions = await get_requisitions()
        return jsonify(requisitions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@requisitions_bp.route("/<id>", methods=["GET"])
async def get_details(id):
    try:
        details = await get_requisition_details(id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@requisitions_bp.route("", methods=["POST"])
async def create():
    try:
        requisition = await create_new_requisition(request.json)
        return jsonify(requisition)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@requisitions_bp.route("/<id>", methods=["DELETE"])
async def delete(id):
    try:
        await remove_requisition(id)
        return "", 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
