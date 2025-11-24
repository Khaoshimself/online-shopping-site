from flask import Blueprint, request, jsonify, render_template
import app.database
from app.database import create_item, init_db, update_item
from app.records.usermodel import ItemCategory
from app.records.users import User, UserType
from flask_login import current_user, login_required, login_user
from bson import ObjectId

items_bp = Blueprint("items", __name__, url_prefix="/admin/items")

@items_bp.before_app_request
def ensure_db():
    init_db()

@items_bp.route("/add", methods=["POST"])
@login_required
def add_item():
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
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
        return jsonify({"success": True, "inserted_id": str(success)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@items_bp.route("/", methods=["GET"])
@login_required
def admin_items_page():
    # ensure DB is ready (optional)
    if not app.database.init_db():
        return "Internal error", 500
    # check admin
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return "Access denied", 403
    return render_template("admin/items.html", title="Admin — Items")

# admin only list of items
@items_bp.route("/list", methods=["GET"])
@login_required
def list_items():
    """Fetch all items as JSON for admin UI"""
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    try:
        items_col = app.database.db["items"]
        items = []
        for it in items_col.find().sort("name", 1):
            it["_id"] = str(it["_id"])
            items.append(it)
        return jsonify({"items": items}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# edit items from a list
@items_bp.route("/edit", methods=["POST"])
@login_required
def edit_item():
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    payload = request.get_json() or {}
    try:
        item_id = payload["item_id"]
        update_fields = payload.get("update_fields", {})
        success = app.database.update_item(item_id, update_fields)
        if success:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Item not found or no changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# delete item by id route
@items_bp.route("/delete/<item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    """Delete an item by ID"""
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    try:
        obj_id = ObjectId(item_id)
        result = app.database.db["items"].delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400