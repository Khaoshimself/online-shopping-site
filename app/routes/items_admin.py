from flask import Blueprint, request, jsonify
from app.database import create_item, init_db
from app.records.usermodel import ItemCategory

items_bp = Blueprint("items", __name__, url_prefix="/admin/items")

@items_bp.before_app_request
def ensure_db():
    init_db()

@items_bp.route("/", methods=["POST"])
def add_item():
    payload = request.get_json() or {}
    try:
        category = ItemCategory(payload.get("category"))
        success = create_item(
            name = payload["name"],
            description = payload.get("description",""),
            price_cents = int(payload["price_cents"]),
            category = category,
            stock = int(payload.get("stock", 0)),
            image_urls = payload.get("image_urls", []),
            tags = payload.get("tags", [])
        )
        return jsonify({"success": success}), (201 if success else 400)
    except Exception as e:
        return jsonify({"error": str(e)}), 400