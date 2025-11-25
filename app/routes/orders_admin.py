from bson import ObjectId
from flask import Blueprint, redirect, request, jsonify, render_template, url_for
import app.database
from flask_login import current_user, login_required

from app.records.users import User, UserType, get_users

from typing import Optional
import pymongo

order_bp = Blueprint("orders", __name__, url_prefix="/admin/orders")


@order_bp.route("/", methods=["GET"])
@login_required
def admin_orders_page():
    # ensure DB is ready (optional)
    if not app.database.init_db():
        return "Internal error", 500
    # check admin
    if not (
        isinstance(current_user, User)
        and current_user.get_permissions() == UserType.ADMIN
    ):
        return "Access denied", 403

    page = request.args.get("page", 0, type=int)
    sort = request.args.get("sort", "date")
    status = request.args.get("status", "any")
    sort_direction = request.args.get("sort_direction", 0, type=int)

    orders = app.database.db["orders"]
    orders.create_indexes(
        [
            pymongo.IndexModel([("created_at", pymongo.ASCENDING)]),
            pymongo.IndexModel([("owner", pymongo.ASCENDING)]),
            pymongo.IndexModel([("total_cents", pymongo.ASCENDING)]),
        ]
    )
    if status == "any":
        total_orders = orders.count_documents({})
    else:
        total_orders = orders.count_documents({"status": status})
    match sort:
        case "date":
            sort_by = "created_at"
        case "owner":
            sort_by = "owner"
        case "value":
            sort_by = "total_cents"
        case _:
            sort_by = "created_at"
    on_page = orders.aggregate(
        [
            {
                "$sort": {
                    sort_by: (
                        pymongo.DESCENDING if sort_direction == 0 else pymongo.ASCENDING
                    )
                }
            },
            {"$skip": page * 25},
            {"$limit": 25},
        ]
    )
    total_pages = (total_orders + 24) // 25

    return render_template(
        "admin/orders.html",
        title="Admin — Orders",
        orders=on_page,
        sort=sort,
        sort_direction=sort_direction,
        status=status,
        page=page,
        total_pages=total_pages,
    )
