"""
app/routes/cart_api.py

This is a NEW backend file that provides all the API endpoints
your cart.js needs to function.

IT IS A TEMPORARY, PHASE 2 IMPLEMENTATION.
It uses a MOCK DICTIONARY for products and the FLASK SESSION for cart storage.
When Phase 3 starts, the backend team will replace this file's logic
with real MongoDB calls, and your JS will keep working.
"""

from flask import Blueprint, jsonify, request, session
import time
from app.records.usermodel import ItemModel, CartItem, CartItemFull
from app.records.users import User
import app.database
from flask_login import current_user, login_required, login_user
from bson import ObjectId
from math import ceil
from typing import List, Dict

cart_api_bp = Blueprint("cart_api", __name__, url_prefix="/api/cart")


def _get_cart_data(user):
    """Internal helper function to calculate cart totals."""
    # Get the cart from the session, default to an empty dict
    if not isinstance(user, User) or not app.database.init_db():
        return {
            "items": [],
            "item_count": 0,
            "subtotal_cents": 0,
            "tax_cents": 0,
            "total_cents": 0,
        }
    cart: List[CartItem] = user.get_cart()

    items = app.database.db["items"]
    cart_ids: List[ObjectId] = [cart_item["item_id"] for cart_item in cart]
    cart_items_raw: List[ItemModel] = items.find({"_id": {"$in": cart_ids}})
    item_lookup: Dict[ObjectId, ItemModel] = {items["_id"]: item for item in cart_items_raw}
    cart_items: List[CartItemFull] = [
        {
            'item_id': cart_item['item_id'],
            'quantity': cart_item['quantity'],
            'item': item_lookup[cart_item['item_id']]
        }
        for cart_item in cart
    ]
    # cart_items = session.get("cart", {})

    line_items = []
    subtotal_cents = 0
    item_count = 0

    for cart_item in cart_items:
        total_price = cart_item['item']['price_cents'] * cart_item['quantity']
        subtotal_cents += total_price
        item_count += cart_item['quantity']
        line_items.append(
            {
                "product_id": cart_item['item_id'],
                "name": cart_item['item']["name"],
                "price_cents": cart_item['item']["price_cents"],
                "image_url": cart_item['item']["image_urls"],
                "quantity": cart_item['quantity'],
                "total_price_cents": total_price,
            }
        )

    # Calculate tax (e.g., 8.25%)
    # tax should be ceil
    tax_cents = ceil(subtotal_cents * 0.0825)
    total_cents = subtotal_cents + tax_cents

    return {
        "items": line_items,
        "item_count": item_count,
        "subtotal_cents": subtotal_cents,
        "tax_cents": tax_cents,
        "total_cents": total_cents,
    }


@cart_api_bp.route("", methods=["GET"])
@login_required
def get_cart():
    """
    Get the current user's cart from the session.
    This is called by cart.js when you load the cart page.
    """
    return jsonify(_get_cart_data(current_user))


@cart_api_bp.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    """
    Add an item to the cart in the session.
    This is called by cart.js when you click "Add to Cart".
    """
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    items = app.database.db["items"]
    product = items.find_one({'_id': product_id})
    if not product_id or not product:
        return jsonify({"message": "Invalid product."}), 400

    # Get cart from session, modify it, and save it back
    cart = current_user.get_cart()
    for cart_item in cart:
        if cart_item["product_id"] == product_id:
            cart_item["quantity"] += quantity
            break
    else:
        cart.append({"product_id": product_id, "quantity": quantity})

    current_user.update_cart(cart)


    cart_data = _get_cart_data(current_user)
    return (
        jsonify(
            {
                "message": f"Added {product['name']} to cart!",
                "cart_item_count": cart_data["item_count"],
            }
        ),
        200,
    )


@cart_api_bp.route("/update", methods=["POST"])
def update_cart_item():
    """Update an item's quantity in the session cart."""
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    items = app.database.db["items"]
    product = items.find_one({'_id': product_id})
    if not product_id or product:
        return jsonify({"message": "Invalid product."}), 400

    cart = current_user.get_cart()
    if quantity > 1:
        for cart_item in cart:
            if cart_item["product_id"] == product_id:
                cart_item["quantity"] = quantity
                break
        else:
            cart.append({"product_id": product_id, "quantity": quantity})
    else:
        cart = list( filter(lambda item: item["product_id"] != product_id, cart) )
    current_user.update_cart(cart)

    return jsonify(_get_cart_data(current_user)), 200


@cart_api_bp.route("/remove", methods=["POST"])
def remove_cart_item():
    """Remove an item from the session cart."""
    if not app.database.init_db():
        return jsonify({"message": "Internal error"}), 500
    data = request.get_json()
    product_id = data.get("product_id")

    cart = current_user.get_cart()

    cart = list( filter(lambda item: item["product_id"] != product_id, cart) )

    current_user.update_cart(cart)

    return jsonify(_get_cart_data(current_user)), 200
