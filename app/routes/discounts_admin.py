from flask import Blueprint, request, jsonify, render_template
import app.database
from app.database import create_item, init_db, update_item
from app.records.users import User, UserType
from flask_login import current_user, login_required, login_user
from bson import ObjectId

discounts_bp = Blueprint("discounts", __name__, url_prefix="/admin/discounts")

@discounts_bp.before_app_request
def ensure_db():
    init_db()

@discounts_bp.route("/add", methods=["POST"])
@login_required
def add_discount():
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    # check admin
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    payload = request.get_json() or {}
    try:
        code = payload["code"]
        discount_percent = float(payload["discount_percent"])
        if not (0 < discount_percent < 100):
            return jsonify({"error": "Discount percent must be between 0 and 100."}), 400
        success = app.database.db["discounts"].insert_one({
            "code": code,
            "discount_percent": discount_percent
        })
        return jsonify({"success": True, "inserted_id": str(success.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@discounts_bp.route("/", methods=["GET"])
@login_required
def admin_discounts_page():
    # ensure DB is ready (optional)
    if not app.database.init_db():
        return "Internal error", 500
    # check admin
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return "Access denied", 403
    return render_template("admin/discounts.html", title="Admin — Discounts")


# admin only list of discounts
@discounts_bp.route("/list", methods=["GET"])
@login_required
def list_discounts():
    """Fetch all discounts as JSON for admin UI"""
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    discounts_cursor = app.database.db["discounts"].find({})
    discounts = []
    for discount in discounts_cursor:
        discounts.append({
            "id": str(discount.get("_id")),
            "code": discount.get("code", ""),
            "discount_percent": discount.get("discount_percent", 0)
        })
    return jsonify({"discounts": discounts}), 200


# edit discounts from a list
@discounts_bp.route("/edit", methods=["POST"])
@login_required
def edit_discount():
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    payload = request.get_json() or {}
    try:
        discount_id = payload["discount_id"]
        update_fields = payload.get("update_fields", {})
        result = app.database.db["discounts"].update_one(
            {"_id": ObjectId(discount_id)},
            {"$set": update_fields}
        )
        if result.modified_count > 0:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "No changes made."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# delete discount by id route
@discounts_bp.route("/delete", methods=["POST"])
@login_required
def delete_discount():
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    
    if not (isinstance(current_user, User) and current_user.get_permissions() == UserType.ADMIN):
        return jsonify({"message": "Access denied"}), 403
    
    payload = request.get_json() or {}
    try:
        discount_id = payload["discount_id"]
        result = app.database.db["discounts"].delete_one(
            {"_id": ObjectId(discount_id)}
        )
        if result.deleted_count > 0:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Discount not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400