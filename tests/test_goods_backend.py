import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import GoodsOrder, Payment, Product, ProductCategory, ProductImage, User
from app.services.goods_order_service import expire_pending_goods_orders


class TestConfig:
    TESTING = True
    SECRET_KEY = "goods-backend-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class GoodsBackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.user = User(
            email="buyer@example.com",
            password_hash=generate_password_hash("password123"),
            name="구매자",
            phone="010-1234-5678",
        )
        self.other_user = User(
            email="other-buyer@example.com",
            password_hash=generate_password_hash("password123"),
            name="다른 구매자",
            phone="010-9999-9999",
        )
        self.product = Product(
            sku="PALLY-BUY-001",
            name="구매 테스트 상품",
            description="테스트 설명",
            price=8000,
            stock_quantity=1000,
            thumbnail_url="img/goods/test.png",
        )
        self.product.categories.extend(
            (ProductCategory(category="daily"), ProductCategory(category="stationery"))
        )
        self.product.images.append(ProductImage(image_url="img/goods/test.png", sort_order=0))
        self.inactive = Product(
            sku="PALLY-HIDDEN-001",
            name="숨김 상품",
            price=1000,
            stock_quantity=1,
            is_active=False,
        )
        db.session.add_all((self.user, self.other_user, self.product, self.inactive))
        db.session.commit()
        self.user_id = self.user.id
        self.other_user_id = self.other_user.id
        self.product_id = self.product.id
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login_as(self, user_id=None):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id or self.user_id

    def valid_order_data(self, **overrides):
        data = {
            "quantity": "2",
            "recipient_name": "팰리",
            "recipient_phone": "010-1234-5678",
            "postal_code": "12345",
            "address": "서울특별시 테스트로 1",
            "address_detail": "101호",
            "delivery_request": "문 앞에 놓아주세요",
            "price": "1",
        }
        data.update(overrides)
        return data

    def test_list_filters_by_category_and_hides_inactive_products(self):
        response = self.client.get("/goods?category=stationery")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("구매 테스트 상품", page)
        self.assertNotIn("숨김 상품", page)
        self.assertEqual(self.client.get("/goods?category=unknown").status_code, 404)

    def test_checkout_requires_login(self):
        response = self.client.get(f"/goods/{self.product_id}/checkout")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)

    def test_detail_opens_purchase_as_modal_instead_of_separate_page(self):
        response = self.client.get(f"/goods/{self.product_id}")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data-buy-modal", page)
        self.assertIn("data-buy-modal-open", page)
        self.assertIn("로그인 후 구매할 수 있어요", page)

        self.login_as()
        response = self.client.get(f"/goods/{self.product_id}/checkout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            f"/goods/{self.product_id}?buy=1",
        )
        modal_page = self.client.get(response.location).get_data(as_text=True)
        self.assertIn('data-auto-open="true"', modal_page)
        self.assertIn("배송 정보 확인하고 결제하기", modal_page)

    def test_create_order_uses_server_price_and_temporarily_decrements_stock(self):
        self.login_as()
        response = self.client.post(
            f"/goods/{self.product_id}/orders",
            data=self.valid_order_data(),
        )
        order = db.session.scalar(db.select(GoodsOrder))
        payment = db.session.scalar(db.select(Payment))
        db.session.refresh(self.product)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f"/payments/{payment.id}")
        self.assertEqual(order.items_amount, 16000)
        self.assertEqual(order.total_amount, 19000)
        self.assertEqual(order.items[0].unit_price, 8000)
        self.assertEqual(self.product.stock_quantity, 998)
        self.assertEqual(payment.goods_order_id, order.id)
        self.assertEqual(payment.amount, 19000)

    def test_invalid_address_or_quantity_does_not_create_order(self):
        self.login_as()
        response = self.client.post(
            f"/goods/{self.product_id}/orders",
            data=self.valid_order_data(quantity="11", postal_code="abc"),
        )
        db.session.refresh(self.product)
        self.assertEqual(response.status_code, 400)
        self.assertIn('data-auto-open="true"', response.get_data(as_text=True))
        self.assertIsNone(db.session.scalar(db.select(GoodsOrder)))
        self.assertEqual(self.product.stock_quantity, 1000)

    def test_cancellation_restores_stock_only_once(self):
        self.login_as()
        self.client.post(f"/goods/{self.product_id}/orders", data=self.valid_order_data())
        order = db.session.scalar(db.select(GoodsOrder))

        first = self.client.post(f"/orders/{order.id}/cancel")
        second = self.client.post(f"/orders/{order.id}/cancel")
        db.session.refresh(self.product)
        db.session.refresh(order)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(order.status, "CANCELLED")
        self.assertEqual(self.product.stock_quantity, 1000)

    def test_expired_order_restores_stock(self):
        self.login_as()
        self.client.post(f"/goods/{self.product_id}/orders", data=self.valid_order_data())
        order = db.session.scalar(db.select(GoodsOrder))
        order.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
        db.session.commit()

        self.assertEqual(expire_pending_goods_orders(), 1)
        db.session.refresh(self.product)
        db.session.refresh(order)
        self.assertEqual(order.status, "EXPIRED")
        self.assertEqual(self.product.stock_quantity, 1000)

    def test_another_user_cannot_view_order(self):
        self.login_as()
        self.client.post(f"/goods/{self.product_id}/orders", data=self.valid_order_data())
        order = db.session.scalar(db.select(GoodsOrder))
        self.login_as(self.other_user_id)
        self.assertEqual(self.client.get(f"/orders/{order.id}").status_code, 404)

    def test_goods_payment_success_and_toss_cancel_restore_stock(self):
        self.login_as()
        self.client.post(f"/goods/{self.product_id}/orders", data=self.valid_order_data())
        order = db.session.scalar(db.select(GoodsOrder))
        payment = order.payment
        approved = {
            "paymentKey": "goods-payment-key",
            "orderId": payment.merchant_order_id,
            "totalAmount": payment.amount,
            "status": "DONE",
            "method": "카드",
        }
        with patch(
            "app.services.payment_service.toss_client.confirm_payment",
            return_value=approved,
        ):
            response = self.client.get(
                f"/payments/{payment.id}/success?paymentKey=goods-payment-key"
                f"&orderId={payment.merchant_order_id}&amount={payment.amount}"
            )
        db.session.refresh(order)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.status, "PAID")

        with patch(
            "app.services.payment_service.toss_client.cancel_payment",
            return_value={"status": "CANCELED"},
        ):
            self.client.post(f"/orders/{order.id}/cancel")
        db.session.refresh(order)
        db.session.refresh(self.product)
        self.assertEqual(order.status, "CANCELLED")
        self.assertEqual(self.product.stock_quantity, 1000)

    def test_mypage_separates_goods_orders_from_stay_reservations(self):
        self.login_as()
        self.client.post(f"/goods/{self.product_id}/orders", data=self.valid_order_data())
        order = db.session.scalar(db.select(GoodsOrder))

        orders_page = self.client.get("/mypage/orders").get_data(as_text=True)
        reservations_page = self.client.get("/mypage/reservations").get_data(as_text=True)
        self.assertIn("구매 테스트 상품", orders_page)
        self.assertIn("굿즈 주문", orders_page)
        self.assertIn("숙소 예약", orders_page)
        self.assertNotIn("구매 테스트 상품", reservations_page)
        self.assertEqual(
            self.client.get(f"/mypage/orders/{order.id}").status_code,
            302,
        )


if __name__ == "__main__":
    unittest.main()
