import unittest

from app import create_app, db
from app.models import Product, ProductCategory, ProductImage
from seed import PRODUCTS_PATH, load_json, upsert_products, validate_products


class TestConfig:
    TESTING = True
    SECRET_KEY = "product-seed-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductSeedTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_product_seed_is_repeatable_and_syncs_catalog(self):
        items = load_json(PRODUCTS_PATH)
        validate_products(items)

        self.assertEqual(upsert_products(items), (15, 0))
        db.session.commit()
        self.assertEqual(upsert_products(items), (0, 15))
        db.session.commit()

        self.assertEqual(db.session.scalar(db.select(db.func.count(Product.id))), 15)
        self.assertEqual(db.session.scalar(db.select(db.func.count(ProductImage.id))), 15)
        self.assertEqual(db.session.scalar(db.select(db.func.count(ProductCategory.id))), 16)

        masking_tape = db.session.scalar(
            db.select(Product).where(Product.sku == "PALLY-MASKING-TAPE-001")
        )
        self.assertEqual(masking_tape.price, 8000)
        self.assertEqual(masking_tape.stock_quantity, 1000)
        self.assertEqual(
            {category.category for category in masking_tape.categories},
            {"daily", "stationery"},
        )


if __name__ == "__main__":
    unittest.main()
