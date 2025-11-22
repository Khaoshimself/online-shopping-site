from dotenv import load_dotenv
import os

load_dotenv()

from pymongo import MongoClient

user = os.getenv("MONGO_ROOT_USER")
password = os.getenv("MONGO_ROOT_PASSWORD")

client = MongoClient(f"mongodb://{user}:{password}@localhost:27017/?authSource=admin")
db = client["shop"]

products_col = db["products"]
discounts_col = db["discount_codes"]

PRODUCTS = [
    {
        "_id": "prod_101",
        "name": "Organic Honey",
        "description": "Pure, locally sourced honey.",
        "price": 9.99,
        "quantity": 25,
        "image_path": "images/sample1.jpg",
        "is_sale_item": False,
    },
    {
        "_id": "prod_102",
        "name": "Artisan Bread",
        "description": "Freshly baked sourdough loaf.",
        "price": 4.49,
        "quantity": 40,
        "image_path": "images/sample2.jpg",
        "is_sale_item": False,
    },
    {
        "_id": "prod_103",
        "name": "Texas Olive Oil",
        "description": "Cold-pressed and rich in flavor.",
        "price": 14.99,
        "quantity": 15,
        "image_path": "images/sample3.jpg",
        "is_sale_item": True,
    },
    {
        "_id": "prod_104",
        "name": "HEB Ground Coffee",
        "description": "Medium roast, 12oz bag.",
        "price": 7.49,
        "quantity": 50,
        "image_path": "images/sample4.jpg",
        "is_sale_item": False,
    },
]

DISCOUNT_CODES = [
    {
        "code": "WELCOME10",
        "percent_off": 10,
        "is_active": True,
        "description": "10% off your first order.",
    },
    {
        "code": "HEB5",
        "percent_off": 5,
        "is_active": True,
        "description": "5% off any purchase.",
    },
    {
        "code": "COFFEE20",
        "percent_off": 20,
        "is_active": True,
        "description": "20% off all coffee items.",
    },
]


def seed_products():
    print("Clearing existing products...")
    products_col.delete_many({})

    print(f"Inserting {len(PRODUCTS)} products...")
    products_col.insert_many(PRODUCTS)
    print("Products seeded.")


def seed_discounts():
    print("Clearing existing discount codes...")
    discounts_col.delete_many({})

    print(f"Inserting {len(DISCOUNT_CODES)} discount codes...")
    discounts_col.insert_many(DISCOUNT_CODES)
    print("Discount codes seeded.")


if __name__ == "__main__":
    seed_products()
    seed_discounts()
    print("✅ Seeding complete.")
