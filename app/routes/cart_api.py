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

# A mock database of products for our cart to use
# This mimics what will be in MongoDB
MOCK_PRODUCTS = {
    # We will add these IDs to your index.html buttons
    "prod_101": {"name": "Organic Honey", "price_cents": 999, "image_url": "https://placehold.co/60x60/EFEFEF/333333?text=Honey"},
    "prod_102": {"name": "Artisan Bread", "price_cents": 449, "image_url": "https://placehold.co/60x60/EFEFEF/333333?text=Bread"},
    "prod_103": {"name": "Texas Olive Oil", "price_cents": 1499, "image_url": "https://placehold.co/60x60/EFEFEF/333333?text=Oil"},
    "prod_104": {"name": "HEB Ground Coffee", "price_cents": 749, "image_url": "https://placehold.co/60x60/EFEFEF/333333?text=Coffee"},
}

cart_api_bp = Blueprint("cart_api", __name__, url_prefix="/api/cart")

def _get_cart_data():
    """Internal helper function to calculate cart totals."""
    # Get the cart from the session, default to an empty dict
    cart_items = session.get("cart", {})  
    
    line_items = []
    subtotal_cents = 0
    item_count = 0
    
    for product_id, quantity in cart_items.items():
        product_info = MOCK_PRODUCTS.get(product_id)
        if product_info:
            total_price = product_info["price_cents"] * quantity
            subtotal_cents += total_price
            item_count += quantity
            line_items.append({
                "product_id": product_id,
                "name": product_info["name"],
                "price_cents": product_info["price_cents"],
                "image_url": product_info["image_url"],
                "quantity": quantity,
                "total_price_cents": total_price
            })
            
    # Calculate tax (e.g., 8.25%)
    tax_cents = round(subtotal_cents * 0.0825)
    total_cents = subtotal_cents + tax_cents
    
    return {
        "items": line_items,
        "item_count": item_count,
        "subtotal_cents": subtotal_cents,
        "tax_cents": tax_cents,
        "total_cents": total_cents
    }


@cart_api_bp.route("", methods=["GET"])
def get_cart():
    """
    Get the current user's cart from the session.
    This is called by cart.js when you load the cart page.
    """
    return jsonify(_get_cart_data())


@cart_api_bp.route("/add", methods=["POST"])
def add_to_cart():
    """
    Add an item to the cart in the session.
    This is called by cart.js when you click "Add to Cart".
    """
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or product_id not in MOCK_PRODUCTS:
        return jsonify({"message": "Invalid product."}), 400

    # Simulate network delay so the loading spinner is visible
    time.sleep(0.3)

    # Get cart from session, modify it, and save it back
    cart = session.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session["cart"] = cart # This saves it to the user's cookie
    
    cart_data = _get_cart_data()
    return jsonify({
        "message": f"Added {MOCK_PRODUCTS[product_id]['name']} to cart!",
        "cart_item_count": cart_data["item_count"]
    }), 200

@cart_api_bp.route("/update", methods=["POST"])
def update_cart_item():
    """Update an item's quantity in the session cart."""
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or product_id not in MOCK_PRODUCTS:
        return jsonify({"message": "Invalid product."}), 400

    cart = session.get("cart", {})
    if quantity > 0:
        cart[product_id] = quantity
    else:
        # Remove if quantity is 0 or less
        cart.pop(product_id, None) 
    
    session["cart"] = cart
    
    return jsonify(_get_cart_data()), 200


@cart_api_bp.route("/remove", methods=["POST"])
def remove_cart_item():
    """Remove an item from the session cart."""
    data = request.get_json()
    product_id = data.get("product_id")

    cart = session.get("cart", {})
    cart.pop(product_id, None) # Safely remove the item
    session["cart"] = cart
    
    return jsonify(_get_cart_data()), 200