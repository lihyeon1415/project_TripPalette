import unittest
from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import (
    Accommodation,
    Destination,
    GoodsOrder,
    GoodsOrderItem,
    Payment,
    Product,
    ProductImage,
    Reservation,
    User,
)


class TestConfig:
    TESTING = True
    SECRET_KEY = "goods-model-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class GoodsModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            email="goods@example.com",
            password_hash=generate_password_hash("password123"),
            name="굿즈 테스트",
            phone="010-1234-5678",
            payment_customer_key="test_customer-key",
        )
        self.product = Product(
            sku="PALLY-TEST-001",
            name="팰리 테스트 굿즈",
            price=12000,
            stock_quantity=10,
        )
        db.session.add_all((self.user, self.product))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def make_goods_order(self):
        order = GoodsOrder(
            order_number="GOODS-TEST-0001",
            user_id=self.user.id,
            recipient_name="수령인",
            recipient_phone="010-1111-2222",
            postal_code="12345",
            address="서울특별시 테스트로 1",
            items_amount=24000,
            shipping_fee=3000,
            total_amount=27000,
            expires_at=datetime.now() + timedelta(minutes=10),
        )
        order.items.append(
            GoodsOrderItem(
                product_id=self.product.id,
                product_name=self.product.name,
                sku=self.product.sku,
                unit_price=self.product.price,
                quantity=2,
                subtotal=24000,
            )
        )
        return order

    def test_goods_order_keeps_product_and_shipping_snapshots(self):
        self.product.images.extend(
            (
                ProductImage(image_url="img/goods/main.png", sort_order=0),
                ProductImage(image_url="img/goods/detail.png", sort_order=1),
            )
        )
        order = self.make_goods_order()
        payment = Payment(
            goods_order=order,
            merchant_order_id="GOODS-PAYMENT-0001",
            amount=27000,
        )
        db.session.add_all((order, payment))
        db.session.commit()

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.items[0].product_name, "팰리 테스트 굿즈")
        self.assertEqual(order.items[0].subtotal, 24000)
        self.assertEqual(order.address, "서울특별시 테스트로 1")
        self.assertEqual(payment.goods_order, order)
        self.assertIsNone(payment.reservation_id)
        self.assertEqual(payment.provider, "TOSS")
        self.assertEqual(payment.payment_status, "READY")
        self.assertEqual(
            [image.sort_order for image in self.product.images],
            [0, 1],
        )

    def test_payment_requires_exactly_one_reservation_or_goods_order(self):
        invalid_payment = Payment(
            merchant_order_id="INVALID-PAYMENT-0001",
            amount=1000,
        )
        db.session.add(invalid_payment)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_payment_rejects_two_targets(self):
        destination = Destination(name="결제 테스트 여행지", region="테스트")
        db.session.add(destination)
        db.session.flush()
        accommodation = Accommodation(
            destination_id=destination.id,
            name="결제 테스트 숙소",
            address="테스트 주소",
            price_per_night=100000,
            capacity=2,
        )
        db.session.add(accommodation)
        db.session.flush()
        reservation = Reservation(
            user_id=self.user.id,
            accommodation_id=accommodation.id,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=2),
            people_count=2,
            total_price=100000,
        )
        order = self.make_goods_order()
        db.session.add_all((reservation, order))
        db.session.flush()
        payment = Payment(
            reservation_id=reservation.id,
            goods_order_id=order.id,
            merchant_order_id="INVALID-PAYMENT-0002",
            amount=100000,
        )
        db.session.add(payment)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_negative_product_price_is_rejected(self):
        db.session.add(
            Product(
                sku="PALLY-INVALID-001",
                name="잘못된 상품",
                price=-1,
                stock_quantity=1,
            )
        )

        with self.assertRaises(IntegrityError):
            db.session.commit()


if __name__ == "__main__":
    unittest.main()
