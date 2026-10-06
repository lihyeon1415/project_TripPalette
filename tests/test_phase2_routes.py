import unittest
from contextlib import contextmanager

from flask import template_rendered

from app import create_app, db
from app.models import Accommodation, Destination


class TestConfig:
    TESTING = True
    SECRET_KEY = "phase2-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class Phase2RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.jeju = Destination(
            name="제주",
            region="제주특별자치도",
            description="바다와 오름을 함께 즐기는 여행지",
            season="봄",
            purpose="자연",
            atmosphere="낭만적인",
            budget_level="보통",
            recommended_days=3,
        )
        self.gangneung = Destination(
            name="강릉",
            region="강원특별자치도",
            description="겨울 바다와 커피를 즐기는 여행지",
            season="겨울",
            purpose="휴양",
            atmosphere="조용한",
            budget_level="보통",
            recommended_days=2,
        )
        db.session.add_all((self.jeju, self.gangneung))
        db.session.flush()

        self.jeju_hotel = Accommodation(
            destination_id=self.jeju.id,
            name="제주 테스트 호텔",
            address="제주특별자치도 제주시",
            description="제주 테스트 숙소",
            price_per_night=100000,
            capacity=2,
            rating=4.5,
            image_url="https://external.example/legacy-photo.jpg",
        )
        self.gangneung_hotel = Accommodation(
            destination_id=self.gangneung.id,
            name="강릉 테스트 호텔",
            address="강원특별자치도 강릉시",
            description="강릉 테스트 숙소",
            price_per_night=90000,
            capacity=3,
            rating=4.2,
        )
        db.session.add_all((self.jeju_hotel, self.gangneung_hotel))
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_context(self, path):
        with captured_templates(self.app) as templates:
            response = self.client.get(path)
        self.assertTrue(templates, f"Template이 렌더링되지 않았습니다: {path}")
        return response, templates[-1][0].name, templates[-1][1]

    def test_main_page_uses_database_destinations(self):
        response, template, context = self.get_context("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "main/index.html")
        self.assertEqual(len(context["hero_slides"]), 4)
        self.assertEqual(
            context["hero_slides"][0]["filename"],
            "img/main/hero-jeju-sunset.png",
        )
        self.assertEqual(context["hero_slides"][0]["caption"], "바다와 섬이 빚어낸 쉼")
        self.assertEqual(context["hero_slides"][0]["destination"].name, "제주")
        self.assertEqual(
            [item.name for item in context["popular_destinations"]],
            ["제주"],
        )
        page = response.get_data(as_text=True)
        self.assertEqual(page.count('class="hero__slide"'), 4)
        self.assertIn("data-hero-current", page)
        self.assertIn("data-hero-prev", page)
        self.assertIn("data-hero-next", page)
        self.assertIn("data-hero-autoplay", page)
        self.assertIn('action="/destinations"', page)
        self.assertIn('name="keyword"', page)
        self.assertIn("여행지 찾기", page)
        self.assertIn("img/main/pally-popular-title-v1.png", page)
        self.assertIn("data-region-map", page)
        self.assertEqual(page.count('data-map-image="'), 6)
        self.assertIn("regional-map-gangwon.png", page)
        self.assertIn("지역 여행지 더보기", page)
        self.assertIn("data-pally-goods-ad", page)
        self.assertIn("pally-goods-ad-v1.png", page)
        self.assertIn('<a class="pally-goods-ad__button" href="/goods"', page)
        self.assertIn("바다와 섬이 빚어낸 쉼", page)
        self.assertIn(
            "img/destination/generated/jeju-dol-hareubang-v1.png",
            page,
        )
        self.assertEqual(
            [group["headline"] for group in context["companion_groups"]],
            [
                "나를 위한 특별한 시간",
                "둘만의 특별한 추억",
                "함께여서 더 행복한 여행",
                "언제나 즐거운 우리",
            ],
        )

    def test_shared_footer_contains_full_width_goods_cta(self):
        for path in ("/", "/destinations", "/auth/login", "/goods"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                page = response.get_data(as_text=True)
                self.assertIn('class="site-footer-goods"', page)
                self.assertIn('class="site-footer-goods__button" href="/goods"', page)
                self.assertIn("여행의 기분을,", page)

    def test_destination_list(self):
        response, template, context = self.get_context("/destinations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "destination/list.html")
        self.assertEqual(len(context["destinations"]), 2)
        self.assertEqual(context["keyword"], "")
        self.assertIn(
            "jeju-dol-hareubang-v1.png",
            response.get_data(as_text=True),
        )
        page = response.get_data(as_text=True)
        self.assertNotIn("TRIP SEARCH", page)
        self.assertNotIn("DESTINATIONS", page)
        self.assertNotIn("TRIPPALETTE EXPLORE", page)
        self.assertIn('type="radio" name="season"', page)
        self.assertIn("조건에 맞는 여행지", page)

    def test_removed_external_photo_endpoint_returns_not_found(self):
        response = self.client.get("/destinations/api/photo?name=제주")
        self.assertEqual(response.status_code, 404)

    def test_destination_keyword_search(self):
        response, _, context = self.get_context(
            "/destinations?keyword=%EB%B0%94%EB%8B%A4"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.name for item in context["destinations"]],
            ["제주", "강릉"],
        )

    def test_destination_filters_individually(self):
        cases = {
            "region=%EC%A0%9C%EC%A3%BC%ED%8A%B9%EB%B3%84%EC%9E%90%EC%B9%98%EB%8F%84": "제주",
            "season=%EA%B2%A8%EC%9A%B8": "강릉",
            "purpose=%EC%9E%90%EC%97%B0": "제주",
            "atmosphere=%EC%A1%B0%EC%9A%A9%ED%95%9C": "강릉",
        }
        for query, expected_name in cases.items():
            with self.subTest(query=query):
                response, _, context = self.get_context(
                    f"/destinations?{query}"
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item.name for item in context["destinations"]],
                    [expected_name],
                )

    def test_destination_filters_are_combined_with_and(self):
        response, _, context = self.get_context(
            "/destinations?season=%EB%B4%84&purpose=%EC%9E%90%EC%97%B0"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.name for item in context["destinations"]],
            ["제주"],
        )

    def test_invalid_filter_returns_empty_result(self):
        response, _, context = self.get_context(
            "/destinations?season=NOT-A-SEASON"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["destinations"], [])

    def test_destination_detail_and_missing_destination(self):
        response, template, context = self.get_context(
            f"/destinations/{self.jeju.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "destination/detail.html")
        self.assertEqual(context["destination"].name, "제주")
        self.assertEqual(context["reviews"], [])
        page = response.get_data(as_text=True)
        self.assertIn("destination-detail-gallery", page)
        self.assertIn("jeju-sea-v1.png", page)
        self.assertIn("jeju-dol-hareubang-v1.png", page)
        self.assertIn("jeju-night-v1.png", page)
        self.assertEqual(
            [item.name for item in context["accommodations"]],
            ["제주 테스트 호텔"],
        )
        self.assertEqual(self.client.get("/destinations/9999").status_code, 404)

    def test_nearby_accommodations_redirect_to_filtered_list(self):
        response = self.client.get(
            f"/destinations/{self.jeju.id}/accommodations"
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                f"/accommodations?destination_id={self.jeju.id}"
            )
        )

        response, template, context = self.get_context(
            f"/accommodations?destination_id={self.jeju.id}"
        )
        self.assertEqual(template, "accommodation/list.html")
        self.assertEqual(context["destination"].name, "제주")
        self.assertEqual(
            [item.name for item in context["accommodations"]],
            ["제주 테스트 호텔"],
        )
        page = response.get_data(as_text=True)
        self.assertIn("제주 주변 숙소", page)
        self.assertIn("제주 테스트 호텔", page)
        self.assertNotIn("강릉 테스트 호텔", page)
        self.assertIn("100,000원", page)
        self.assertIn("숙소 이미지 준비 중", page)

    def test_destination_detail_shows_more_button_for_three_or_more_stays(self):
        for index in range(2, 4):
            db.session.add(
                Accommodation(
                    destination_id=self.jeju.id,
                    name=f"제주 테스트 숙소 {index}",
                    address="제주특별자치도 제주시",
                    description="제주 추가 테스트 숙소",
                    price_per_night=80000 + index,
                    capacity=2,
                    rating=4.0,
                )
            )
        db.session.commit()

        response, template, context = self.get_context(
            f"/destinations/{self.jeju.id}"
        )
        self.assertEqual(template, "destination/detail.html")
        self.assertEqual(len(context["accommodations"]), 3)
        self.assertEqual(context["accommodation_count"], 3)
        page = response.get_data(as_text=True)
        self.assertIn("숙소 더보기", page)
        self.assertIn(
            f"/accommodations?destination_id={self.jeju.id}",
            page,
        )

        response = self.client.get(f"/destinations/{self.gangneung.id}")
        self.assertNotIn("숙소 더보기", response.get_data(as_text=True))

    def test_accommodation_list_and_detail(self):
        response, template, context = self.get_context("/accommodations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "accommodation/list.html")
        self.assertIsNone(context["destination"])
        self.assertEqual(len(context["accommodations"]), 2)
        list_page = response.get_data(as_text=True)
        self.assertIn("전체 숙소", list_page)
        self.assertIn("제주 테스트 호텔", list_page)
        self.assertIn("강릉 테스트 호텔", list_page)
        self.assertIn("최대 2명", list_page)
        self.assertNotIn("external.example", list_page)

        response, template, context = self.get_context(
            f"/accommodations/{self.jeju_hotel.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "accommodation/detail.html")
        self.assertEqual(context["accommodation"].name, "제주 테스트 호텔")
        self.assertEqual(context["accommodation"].destination.name, "제주")
        self.assertEqual(
            context["booking_facts"],
            {
                "wifi_available": True,
                "parking_available": True,
                "check_in_time": "15:00",
                "check_out_time": "11:00",
            },
        )
        detail_page = response.get_data(as_text=True)
        self.assertIn("제주 테스트 숙소", detail_page)
        self.assertIn("여행지 상세 보기", detail_page)
        self.assertIn("예약하기", detail_page)
        self.assertIn("와이파이", detail_page)
        self.assertIn("주차 가능", detail_page)
        self.assertIn("입실 시간", detail_page)
        self.assertIn("퇴실 시간", detail_page)
        self.assertIn(f'/reservations/new/{self.jeju_hotel.id}', detail_page)
        self.assertNotIn("external.example", detail_page)
        self.assertEqual(self.client.get("/accommodations/9999").status_code, 404)


class EmptyDatabaseRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_empty_database_pages_do_not_fail(self):
        for path in ("/", "/destinations", "/accommodations"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

        accommodation_page = self.client.get("/accommodations").get_data(
            as_text=True
        )
        self.assertIn("표시할 숙소가 없습니다.", accommodation_page)


if __name__ == "__main__":
    unittest.main()
