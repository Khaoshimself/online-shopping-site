from flask import Blueprint, jsonify, request, session, url_for
from flask_login import login_required, current_user
from datetime import datetime
import time
import app.database
from bson import ObjectId

cart_api_bp = Blueprint("cart_api", __name__, url_prefix="/api/cart")


def _get_cart_data():
    # internal helper function to calculate cart totals

    cart_items = session.get("cart", {})

    line_items = []
    subtotal_cents = 0
    item_count = 0

    if not cart_items:
        # Return empty cart structure
        return {
            "items": [],
            "item_count": 0,
            "subtotal_cents": 0,
            "tax_cents": 0,
            "total_cents": 0,
        }

    product_ids = list(cart_items.keys())

    # Convert string product_ids to ObjectId for lookup
    object_ids = []
    for pid in product_ids:
        try:
            object_ids.append(ObjectId(pid))
        except:
            pass  # Skip invalid IDs

    if not object_ids:
        return {
            "items": [],
            "item_count": 0,
            "subtotal_cents": 0,
            "tax_cents": 0,
            "total_cents": 0,
        }

    # Fetch items from Mongo by their _id
    products = list(app.database.db["items"].find({"_id": {"$in": object_ids}}))

    # Map by id for quick lookup
    product_map = {str(p["_id"]): p for p in products}

    for product_id, quantity in cart_items.items():
        product = product_map.get(product_id)
        if not product:
            # Product was deleted or missing then skip it
            continue

        # price_cents is already stored in cents in ItemModel
        price_cents = product.get("price_cents", 0)

        # image_urls is a list of image URLs from ItemModel
        image_urls = product.get("image_urls", [])
        # fallback placeholder for the love of the game
        image_url = (
            image_urls[0]
            if image_urls
            else "https://placehold.co/60x60/EFEFEF/333333?text=Item"
        )

        line_total_cents = price_cents * quantity
        subtotal_cents += line_total_cents
        item_count += quantity

        line_items.append(
            {
                "product_id": product_id,
                "name": product.get("name", ""),
                "price_cents": price_cents,
                "image_url": image_url,
                "quantity": quantity,
                "total_price_cents": line_total_cents,
            }
        )

        # --- Discount handling --- # FIXXXXX
        applied_code = session.get("discount_code")
        discount_percent = float(session.get("discount_percent", 0))

        discount_cents = 0
        if discount_percent > 0 and subtotal_cents > 0:
            discount_cents = round(subtotal_cents * (discount_percent / 100.0))

        # Subtotal after discount
        subtotal_after_discount = subtotal_cents - discount_cents

        # Tax (8.25%) applied after discount
        tax_cents = round(subtotal_after_discount * 0.0825)
        total_cents = subtotal_after_discount + tax_cents

        return {
            "items": line_items,
            "item_count": item_count,
            "subtotal_cents": subtotal_cents,
            "discount_cents": discount_cents,
            "tax_cents": tax_cents,
            "total_cents": total_cents,
            "discount_code": applied_code,
            "discount_percent": discount_percent,
        }


@cart_api_bp.route("", methods=["GET"])
@login_required
def get_cart():
    # Get the current user's cart from the session.
    return jsonify(_get_cart_data())


@cart_api_bp.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id:
        return jsonify({"message": "Missing product_id."}), 400

    # Verify the product exists in Mongo
    # Convert product_id string to ObjectId for lookup
    try:
        obj_id = ObjectId(product_id)
    except:
        return jsonify({"message": "Invalid product_id."}), 400

    product = app.database.db["items"].find_one({"_id": obj_id})
    if not product:
        return jsonify({"message": "Invalid product."}), 400

    # Thought this would be cool
    time.sleep(0.3)

    # get cart from session, modify it, and save back
    cart = session.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session["cart"] = cart

    cart_data = _get_cart_data()
    return (
        jsonify(
            {
                "message": f"Added {product.get('name', 'item')} to cart!",
                "cart_item_count": cart_data["item_count"],
            }
        ),
        200,
    )


@cart_api_bp.route("/update", methods=["POST"])
def update_cart_item():
    # Update an item's quantity in the session cart
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id:
        return jsonify({"message": "Missing product_id."}), 400

    # Verify product still exists
    try:
        obj_id = ObjectId(product_id)
    except:
        return jsonify({"message": "Invalid product_id."}), 400

    product = app.database.db["items"].find_one({"_id": obj_id})
    if not product:
        return jsonify({"message": "Invalid product."}), 400

    cart = session.get("cart", {})
    if quantity > 0:
        cart[product_id] = quantity
    else:
        cart.pop(product_id, None)

    session["cart"] = cart

    return jsonify(_get_cart_data()), 200


@cart_api_bp.route("/remove", methods=["POST"])
def remove_cart_item():
    data = request.get_json() or {}
    product_id = data.get("product_id")

    cart = session.get("cart", {})
    cart.pop(product_id, None)
    session["cart"] = cart

    return jsonify(_get_cart_data()), 200


@cart_api_bp.route("/apply-discount", methods=["POST"])  # FIXXXXXX
def apply_discount():
    """
    Apply a discount code to the current cart.
    Body: {"code": "WELCOME10"}
    Looks up code in Mongo `discount_codes`, stores in session,
    and returns updated cart totals.
    """
    data = request.get_json() or {}
    code = (data.get("code") or "").strip().upper()

    if not code:
        return jsonify({"ok": False, "message": "Please enter a code."}), 400

    # Make sure there is something in the cart
    cart = session.get("cart", {})
    if not cart:
        session.pop("discount_code", None)
        session.pop("discount_percent", None)
        return jsonify({"ok": False, "message": "Your cart is empty."}), 400

    discount_doc = app.database.db["discount_codes"].find_one(
        {"code": code, "is_active": True}
    )
    if not discount_doc:
        # Clear any previous discount if they type a bad one
        session.pop("discount_code", None)
        session.pop("discount_percent", None)
        return jsonify({"ok": False, "message": "Invalid or expired code."}), 404

    percent_off = float(discount_doc.get("percent_off", 0))

    # Save discount in session
    session["discount_code"] = code
    session["discount_percent"] = percent_off

    cart_data = _get_cart_data()

    return (
        jsonify(
            {
                "ok": True,
                "message": f"Code {code} applied: {percent_off:.0f}% off.",
                "cart": cart_data,
            }
        ),
        200,
    )


@cart_api_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    """
    Convert the current cart into an order in MongoDB.

    - Requires there to be items in the cart.
    - Uses _get_cart_data() so discounts/tax/total are consistent.
    - Clears the cart + discount from the session after placing the order.
    """
    cart = session.get("cart", {})
    if not cart:
        return jsonify({"ok": False, "message": "Your cart is empty."}), 400

    cart_data = _get_cart_data()
    if cart_data is None or cart_data["item_count"] == 0:
        return jsonify({"ok": False, "message": "Your cart is empty."}), 400

    # Build the order document
    order_doc = {
        "owner": current_user.get_id(),
        "items": cart_data[
            "items"
        ],  # list of {product_id, name, price_cents, quantity, total_price_cents, image_url}
        "item_count": cart_data["item_count"],
        "subtotal_cents": cart_data["subtotal_cents"],
        "discount_cents": cart_data.get("discount_cents", 0),
        "tax_cents": cart_data["tax_cents"],
        "total_cents": cart_data["total_cents"],
        "discount_code": cart_data.get("discount_code"),
        "discount_percent": cart_data.get("discount_percent", 0),
        "created_at": datetime.utcnow(),
        "status": "pending",  # could be 'pending', 'paid', etc later
    }

    result = app.database.db["orders"].insert_one(order_doc)
    order_id = str(result.inserted_id)

    # Clear cart + discounts from session
    session.pop("cart", None)
    session.pop("discount_code", None)
    session.pop("discount_percent", None)

    return (
        jsonify(
            {
                "ok": True,
                "message": "Order placed successfully!",
                "order_id": order_id,
            }
        ),
        200,
    )
