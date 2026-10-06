import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import CartItem, GoodsOrder, Payment, Product, ProductCategory, ProductImage, User
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

    def create_cart_order(self, **overrides):
        data = self.valid_order_data(**overrides)
        quantity = data.pop("quantity", "2")
        self.client.post(
            f"/cart/items/{self.product_id}",
            data={"quantity": quantity},
        )
        return self.client.post("/cart/checkout", data=data)

    def test_list_filters_by_category_and_hides_inactive_products(self):
        response = self.client.get("/goods?category=stationery")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("구매 테스트 상품", page)
        self.assertNotIn("숨김 상품", page)
        self.assertEqual(self.client.get("/goods?category=unknown").status_code, 404)

    def test_checkout_requires_login(self):
        response = self.client.get("/cart")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)

        response = self.client.get(f"/goods/{self.product_id}/checkout")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)

    def test_detail_adds_selected_quantity_to_cart(self):
        response = self.client.get(f"/goods/{self.product_id}")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'action="/cart/items/{self.product_id}"', page)
        self.assertIn("장바구니 담기", page)

        self.login_as()
        response = self.client.post(
            f"/cart/items/{self.product_id}", data={"quantity": "3"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/cart")
        item = db.session.scalar(db.select(CartItem))
        self.assertEqual(item.quantity, 3)

    def test_direct_buy_opens_modal_and_creates_single_product_order(self):
        self.login_as()
        response = self.client.get(f"/goods/{self.product_id}/checkout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f"/goods/{self.product_id}?buy=1")

        modal_page = self.client.get(response.location).get_data(as_text=True)
        self.assertIn('data-auto-open="true"', modal_page)
        self.assertIn(f'action="/goods/{self.product_id}/orders"', modal_page)
        self.assertIn('id="goods-shipping-dialog"', modal_page)
        self.assertIn('class="shipping-dialog"', modal_page)

        response = self.client.post(
            f"/goods/{self.product_id}/orders", data=self.valid_order_data()
        )
        order = db.session.scalar(db.select(GoodsOrder))
        db.session.refresh(self.product)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f"/payments/{order.payment.id}")
        self.assertEqual(self.client.get(response.location).status_code, 200)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(order.total_amount, 19000)
        self.assertEqual(self.product.stock_quantity, 998)

    def test_create_order_uses_server_price_and_temporarily_decrements_stock(self):
        self.login_as()
        response = self.create_cart_order()
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

    def test_cart_checkout_combines_products_and_charges_shipping_once(self):
        second_product = Product(
            sku="PALLY-BUY-002",
            name="두 번째 테스트 상품",
            price=5000,
            stock_quantity=1000,
            thumbnail_url="img/goods/test-2.png",
        )
        db.session.add(second_product)
        db.session.commit()
        self.login_as()
        self.client.post(
            f"/cart/items/{self.product_id}", data={"quantity": "2"}
        )
        self.client.post(
            f"/cart/items/{second_product.id}", data={"quantity": "3"}
        )

        response = self.client.post("/cart/checkout", data=self.valid_order_data())
        order = db.session.scalar(db.select(GoodsOrder))
        db.session.refresh(second_product)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.items_amount, 31000)
        self.assertEqual(order.shipping_fee, 3000)
        self.assertEqual(order.total_amount, 34000)
        self.assertEqual(self.product.stock_quantity, 998)
        self.assertEqual(second_product.stock_quantity, 997)
        self.assertEqual(db.session.scalar(db.select(db.func.count(CartItem.id))), 0)
        payment_page = self.client.get(response.location).get_data(as_text=True)
        self.assertIn(self.product.name, payment_page)
        self.assertIn(second_product.name, payment_page)
        self.assertIn("배송지", payment_page)
        self.assertIn("총 결제 금액", payment_page)

    def test_direct_buy_and_cart_use_the_same_shipping_dialog_component(self):
        self.login_as()
        self.client.post(f"/cart/items/{self.product_id}", data={"quantity": "1"})

        detail_page = self.client.get(f"/goods/{self.product_id}").get_data(as_text=True)
        cart_page = self.client.get("/cart").get_data(as_text=True)

        for page in (detail_page, cart_page):
            self.assertIn('class="shipping-dialog"', page)
            self.assertIn("DELIVERY INFORMATION", page)
            self.assertIn("배송지 확인하고 결제하기", page)
            self.assertIn("js/shipping/shipping-dialog.js", page)

    def test_cart_checkout_orders_only_selected_items(self):
        second_product = Product(
            sku="PALLY-BUY-SELECT-002",
            name="장바구니에 남을 상품",
            price=5000,
            stock_quantity=1000,
            thumbnail_url="img/goods/test-2.png",
        )
        db.session.add(second_product)
        db.session.commit()
        self.login_as()
        self.client.post(f"/cart/items/{self.product_id}", data={"quantity": "2"})
        self.client.post(f"/cart/items/{second_product.id}", data={"quantity": "1"})
        selected_item = db.session.scalar(
            db.select(CartItem).where(CartItem.product_id == self.product_id)
        )

        response = self.client.post(
            "/cart/checkout",
            data={
                **self.valid_order_data(),
                "selection_present": "1",
                "cart_item_ids": str(selected_item.id),
            },
        )
        order = db.session.scalar(db.select(GoodsOrder))
        remaining_item = db.session.scalar(
            db.select(CartItem).where(CartItem.product_id == second_product.id)
        )
        db.session.refresh(second_product)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].product_id, self.product_id)
        self.assertIsNotNone(remaining_item)
        self.assertEqual(second_product.stock_quantity, 1000)

    def test_invalid_address_or_quantity_does_not_create_order(self):
        self.login_as()
        self.client.post(f"/cart/items/{self.product_id}", data={"quantity": "2"})
        response = self.client.post(
            "/cart/checkout",
            data=self.valid_order_data(postal_code="abc"),
        )
        db.session.refresh(self.product)
        self.assertEqual(response.status_code, 400)
        self.assertIn("장바구니", response.get_data(as_text=True))
        self.assertIsNone(db.session.scalar(db.select(GoodsOrder)))
        self.assertEqual(self.product.stock_quantity, 1000)

    def test_cancellation_restores_stock_only_once(self):
        self.login_as()
        self.create_cart_order()
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
        self.create_cart_order()
        order = db.session.scalar(db.select(GoodsOrder))
        order.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
        db.session.commit()

        self.assertEqual(expire_pending_goods_orders(), 1)
        db.session.refresh(self.product)
        db.session.refresh(order)
        self.assertEqual(order.status, "EXPIRED")
        self.assertEqual(self.product.stock_quantity, 1000)

    def test_only_expired_or_cancelled_order_can_be_removed_from_order_history(self):
        self.login_as()
        self.create_cart_order()
        order = db.session.scalar(db.select(GoodsOrder))

        self.assertEqual(self.client.post(f"/orders/{order.id}/hide").status_code, 409)
        db.session.refresh(order)
        self.assertIsNone(order.hidden_at)

        order.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
        db.session.commit()
        self.assertEqual(expire_pending_goods_orders(), 1)

        page_before = self.client.get("/mypage/orders").get_data(as_text=True)
        self.assertIn(order.order_number, page_before)
        self.assertIn("목록에서 삭제", page_before)

        response = self.client.post(f"/orders/{order.id}/hide")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/mypage/orders")
        db.session.refresh(order)
        self.assertIsNotNone(order.hidden_at)
        self.assertNotIn(
            order.order_number,
            self.client.get("/mypage/orders").get_data(as_text=True),
        )

        self.create_cart_order()
        cancelled_order = db.session.scalar(
            db.select(GoodsOrder).where(GoodsOrder.hidden_at.is_(None))
        )
        self.client.post(f"/orders/{cancelled_order.id}/cancel")
        db.session.refresh(cancelled_order)
        self.assertEqual(cancelled_order.status, "CANCELLED")

        cancelled_page = self.client.get("/mypage/orders").get_data(as_text=True)
        self.assertIn(cancelled_order.order_number, cancelled_page)
        self.assertIn("목록에서 삭제", cancelled_page)

        response = self.client.post(f"/orders/{cancelled_order.id}/hide")
        self.assertEqual(response.status_code, 302)
        db.session.refresh(cancelled_order)
        self.assertIsNotNone(cancelled_order.hidden_at)

    def test_another_user_cannot_view_order(self):
        self.login_as()
        self.create_cart_order()
        order = db.session.scalar(db.select(GoodsOrder))
        self.login_as(self.other_user_id)
        self.assertEqual(self.client.get(f"/orders/{order.id}").status_code, 404)

    def test_order_detail_renders_structured_order_information(self):
        self.login_as()
        self.create_cart_order()
        order = db.session.scalar(db.select(GoodsOrder))

        response = self.client.get(f"/orders/{order.id}")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("css/order-detail.css", page)
        self.assertIn("주문 상세", page)
        self.assertIn("주문 상품", page)
        self.assertIn("배송지 정보", page)
        self.assertIn("결제 정보", page)
        self.assertIn("주문 상태", page)
        self.assertIn("결제 대기", page)
        self.assertIn(order.order_number, page)
        self.assertIn(self.product.thumbnail_url, page)

    def test_goods_payment_success_and_toss_cancel_restore_stock(self):
        self.login_as()
        self.create_cart_order()
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
        self.create_cart_order()
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
