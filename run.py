from app import app
from app.database import init_db, create_item
from app.records.usermodel import ItemCategory

if __name__ == "__main__":
    if init_db():
        # example seed item
        create_item(
            name="Test item",
            description="A test worthy item.",
            price_cents=65535,
            category=ItemCategory.OTHER,
            stock=99,
            image_urls=[],
            tags=["test", "other"]
        )
    app.run(debug=True)
