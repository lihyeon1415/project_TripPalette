import unittest
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Accommodation, Destination, Payment, Reservation, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "reservation-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ReservationFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        destination = Destination(name="제주", region="제주특별자치도")
        user = User(
            email="traveler@example.com",
            password_hash=generate_password_hash("password123"),
            name="여행자",
            phone="010-1234-5678",
        )
        other_user = User(
            email="other@example.com",
            password_hash=generate_password_hash("password123"),
            name="다른 회원",
            phone="010-9999-9999",
        )
        db.session.add_all((destination, user, other_user))
        db.session.flush()

        accommodation = Accommodation(
            destination_id=destination.id,
            name="제주 테스트 숙소",
            address="제주특별자치도 제주시",
            description="예약 기능 테스트 숙소",
            price_per_night=120000,
            capacity=3,
            rating=4.7,
        )
        db.session.add(accommodation)
        db.session.commit()

        self.user_id = user.id
        self.other_user_id = other_user.id
        self.accommodation_id = accommodation.id
        self.client = self.app.test_client()
        self.check_in = date.today() + timedelta(days=7)
        self.check_out = self.check_in + timedelta(days=2)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as(self, user_id=None):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id or self.user_id

    def reservation_data(self, **overrides):
        data = {
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "people_count": "2",
        }
        data.update(overrides)
        return data

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(
            f"/reservations/new/{self.accommodation_id}",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login?next=/reservations/new/", response.location)

    def test_reservation_form_renders_accommodation_summary(self):
        self.login_as()
        response = self.client.get(f"/reservations/new/{self.accommodation_id}")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("제주 테스트 숙소", page)
        self.assertIn("120,000", page)
        self.assertIn("예약 후 결제하기", page)

    def test_logged_in_header_links_to_reservation_history(self):
        self.login_as()
        page = self.client.get("/").get_data(as_text=True)

        self.assertIn('href="/mypage/reservations"', page)
        self.assertIn("예약·주문 내역", page)

        reservation_page = self.client.get("/mypage/reservations").get_data(
            as_text=True
        )
        self.assertIn('href="#icon-mypage-calendar"', reservation_page)
        self.assertIn("mypage-nav-link--active", reservation_page)
        self.assertIn('aria-current="page"', reservation_page)

    def test_valid_reservation_is_saved_with_server_calculated_total(self):
        self.login_as()
        response = self.client.post(
            f"/reservations/new/{self.accommodation_id}",
            data=self.reservation_data(),
            follow_redirects=False,
        )

        reservation = db.session.scalar(db.select(Reservation))
        self.assertEqual(response.status_code, 302)
        payment = db.session.scalar(db.select(Payment))
        self.assertEqual(response.location, f"/payments/{payment.id}")
        self.assertEqual(reservation.user_id, self.user_id)
        self.assertEqual(reservation.people_count, 2)
        self.assertEqual(reservation.total_price, 240000)
        self.assertEqual(reservation.status, "PAYMENT_PENDING")
        self.assertEqual(payment.amount, 240000)
        self.assertEqual(payment.reservation_id, reservation.id)
        self.assertIsNotNone(reservation.expires_at)

    def test_invalid_dates_and_capacity_do_not_create_reservation(self):
        self.login_as()
        invalid_payloads = (
            self.reservation_data(check_out=self.check_in.isoformat()),
            self.reservation_data(
                check_in=(date.today() - timedelta(days=1)).isoformat()
            ),
            self.reservation_data(people_count="4"),
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    f"/reservations/new/{self.accommodation_id}",
                    data=payload,
                )
                self.assertEqual(response.status_code, 200)

        self.assertEqual(
            db.session.scalar(db.select(db.func.count(Reservation.id))),
            0,
        )

    def test_overlapping_active_reservation_is_rejected(self):
        existing = Reservation(
            user_id=self.other_user_id,
            accommodation_id=self.accommodation_id,
            check_in=self.check_in,
            check_out=self.check_out,
            people_count=1,
            total_price=240000,
            status="PENDING",
        )
        db.session.add(existing)
        db.session.commit()
        self.login_as()

        response = self.client.post(
            f"/reservations/new/{self.accommodation_id}",
            data=self.reservation_data(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "선택한 날짜에는 이미 예약이 있습니다.",
            response.get_data(as_text=True),
        )
        self.assertEqual(
            db.session.scalar(db.select(db.func.count(Reservation.id))),
            1,
        )

    def test_completion_and_history_are_limited_to_owner(self):
        reservation = Reservation(
            user_id=self.user_id,
            accommodation_id=self.accommodation_id,
            check_in=self.check_in,
            check_out=self.check_out,
            people_count=2,
            total_price=240000,
            status="PENDING",
        )
        db.session.add(reservation)
        db.session.commit()

        self.login_as(self.other_user_id)
        self.assertEqual(
            self.client.get(f"/reservations/{reservation.id}/complete").status_code,
            404,
        )
        self.assertNotIn(
            "제주 테스트 숙소",
            self.client.get("/mypage/reservations").get_data(as_text=True),
        )

        self.login_as(self.user_id)
        self.assertIn(
            "제주 테스트 숙소",
            self.client.get("/mypage/reservations").get_data(as_text=True),
        )

    def test_owner_can_cancel_and_cancelled_dates_become_available(self):
        reservation = Reservation(
            user_id=self.user_id,
            accommodation_id=self.accommodation_id,
            check_in=self.check_in,
            check_out=self.check_out,
            people_count=2,
            total_price=240000,
            status="PENDING",
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id
        self.login_as()

        response = self.client.post(
            f"/reservations/{reservation_id}/cancel",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, f"/reservations/{reservation_id}/complete")
        db.session.refresh(reservation)
        self.assertEqual(reservation.status, "CANCELLED")
        history_page = self.client.get("/mypage/reservations").get_data(
            as_text=True
        )
        self.assertNotIn("제주 테스트 숙소", history_page)
        self.assertIn("현재 예약된 숙소가 없습니다.", history_page)

        response = self.client.post(
            f"/reservations/new/{self.accommodation_id}",
            data=self.reservation_data(),
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            db.session.scalar(db.select(db.func.count(Reservation.id))),
            2,
        )

    def test_non_owner_cannot_cancel_reservation(self):
        reservation = Reservation(
            user_id=self.user_id,
            accommodation_id=self.accommodation_id,
            check_in=self.check_in,
            check_out=self.check_out,
            people_count=2,
            total_price=240000,
            status="PENDING",
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id

        self.login_as(self.other_user_id)
        self.assertEqual(
            self.client.post(f"/reservations/{reservation_id}/cancel").status_code,
            404,
        )
        self.assertEqual(
            self.client.get(f"/reservations/{reservation_id}/cancel").status_code,
            405,
        )
        db.session.refresh(reservation)
        self.assertEqual(reservation.status, "PENDING")


if __name__ == "__main__":
    unittest.main()
