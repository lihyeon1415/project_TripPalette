import unittest

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Accommodation, AccommodationReview, Destination, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "accommodation-review-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AccommodationReviewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        destination = Destination(name="제주", region="제주특별자치도")
        user = User(
            email="reviewer@example.com",
            password_hash=generate_password_hash("password123"),
            name="리뷰어",
            phone="010-1111-2222",
        )
        other_user = User(
            email="other-reviewer@example.com",
            password_hash=generate_password_hash("password123"),
            name="다른 여행자",
            phone="010-3333-4444",
        )
        db.session.add_all((destination, user, other_user))
        db.session.flush()
        accommodation = Accommodation(
            destination_id=destination.id,
            name="제주 바다 숙소",
            address="제주특별자치도 제주시",
            description="바다 가까이에서 쉬어가는 숙소",
            price_per_night=150000,
            capacity=4,
            rating=4.0,
        )
        db.session.add(accommodation)
        db.session.commit()

        self.user_id = user.id
        self.other_user_id = other_user.id
        self.accommodation_id = accommodation.id
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as(self, user_id=None):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id or self.user_id

    def test_review_form_is_visible_and_anonymous_post_requires_login(self):
        page = self.client.get(
            f"/accommodations/{self.accommodation_id}"
        ).get_data(as_text=True)
        self.assertIn("로그인", page)
        self.assertIn("숙소 후기를 남겨보세요", page)

        response = self.client.post(
            f"/accommodations/{self.accommodation_id}/reviews",
            data={"rating": "5", "content": "좋았어요"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith("/auth/login"))

    def test_review_validation_creation_and_duplicate_prevention(self):
        self.login_as()
        review_url = f"/accommodations/{self.accommodation_id}/reviews"

        for data in (
            {"rating": "0", "content": "평점 오류"},
            {"rating": "6", "content": "평점 오류"},
            {"rating": "not-number", "content": "평점 오류"},
            {"rating": "5", "content": "   "},
        ):
            response = self.client.post(review_url, data=data)
            self.assertEqual(response.status_code, 302)

        self.assertEqual(
            db.session.scalar(db.select(db.func.count(AccommodationReview.id))),
            0,
        )

        response = self.client.post(
            review_url,
            data={"rating": "5", "content": " 창밖 풍경이 정말 좋았어요. "},
            follow_redirects=False,
        )
        review = db.session.scalar(db.select(AccommodationReview))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("#stay-reviews"))
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "창밖 풍경이 정말 좋았어요.")

        self.client.post(
            review_url,
            data={"rating": "4", "content": "두 번째 후기"},
        )
        self.assertEqual(
            db.session.scalar(db.select(db.func.count(AccommodationReview.id))),
            1,
        )

    def test_real_reviews_drive_average_and_rendered_list(self):
        db.session.add_all(
            (
                AccommodationReview(
                    user_id=self.user_id,
                    accommodation_id=self.accommodation_id,
                    rating=5,
                    content="바다가 잘 보여요.",
                ),
                AccommodationReview(
                    user_id=self.other_user_id,
                    accommodation_id=self.accommodation_id,
                    rating=3,
                    content="조용하게 쉬기 좋았어요.",
                ),
            )
        )
        db.session.commit()

        page = self.client.get(
            f"/accommodations/{self.accommodation_id}"
        ).get_data(as_text=True)
        self.assertIn("4.0", page)
        self.assertIn("후기 2개 기준", page)
        self.assertIn("바다가 잘 보여요.", page)
        self.assertIn("조용하게 쉬기 좋았어요.", page)

    def test_own_accommodation_review_appears_in_mypage(self):
        db.session.add_all(
            (
                AccommodationReview(
                    user_id=self.user_id,
                    accommodation_id=self.accommodation_id,
                    rating=5,
                    content="내가 작성한 숙소 후기",
                ),
                AccommodationReview(
                    user_id=self.other_user_id,
                    accommodation_id=self.accommodation_id,
                    rating=3,
                    content="다른 회원의 숙소 후기",
                ),
            )
        )
        db.session.commit()
        self.login_as()

        page = self.client.get("/mypage/reviews").get_data(as_text=True)

        self.assertIn("제주 바다 숙소", page)
        self.assertIn("내가 작성한 숙소 후기", page)
        self.assertNotIn("다른 회원의 숙소 후기", page)
        self.assertIn("숙소 1", page)

    def test_user_can_delete_only_own_accommodation_review(self):
        own_review = AccommodationReview(
            user_id=self.user_id,
            accommodation_id=self.accommodation_id,
            rating=5,
            content="삭제할 숙소 후기",
        )
        other_review = AccommodationReview(
            user_id=self.other_user_id,
            accommodation_id=self.accommodation_id,
            rating=3,
            content="남겨둘 숙소 후기",
        )
        db.session.add_all((own_review, other_review))
        db.session.commit()
        own_review_id = own_review.id
        other_review_id = other_review.id
        self.login_as()

        self.assertEqual(
            self.client.post(
                f"/mypage/reviews/accommodation/{other_review_id}/delete"
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                f"/mypage/reviews/accommodation/{own_review_id}/delete"
            ).status_code,
            405,
        )
        response = self.client.post(
            f"/mypage/reviews/accommodation/{own_review_id}/delete",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/mypage/reviews")
        self.assertIsNone(db.session.get(AccommodationReview, own_review_id))
        self.assertIsNotNone(db.session.get(AccommodationReview, other_review_id))


if __name__ == "__main__":
    unittest.main()
