from flask import Blueprint, render_template

from app import db
from app.models import Destination


main_bp = Blueprint("main", __name__)

POPULAR_DESTINATION_NAMES = ("제주", "창원 진해", "삼척", "여수")
FALL_DESTINATION_NAME = "정읍"

HERO_SLIDES = (
    {
        "filename": "img/main/hero-jeju-sunset.png",
        "destination_name": "제주",
        "caption": "바다와 섬이 빚어낸 쉼",
        "alt": "제주 바다와 야자수가 어우러진 저녁 풍경",
    },
    {
        "filename": "img/main/hero-busan-gwangalli-hd.png",
        "destination_name": "부산",
        "caption": "도시와 바다가 만나는 밤",
        "alt": "부산 광안리 바다를 가로지르는 대교와 해안 야경",
    },
    {
        "filename": "img/main/hero-pohang-sunset-hd.png",
        "destination_name": "포항",
        "caption": "해가 가장 먼저 머무는 곳",
        "alt": "붉은 저녁 아래 포항 해변과 야생화",
    },
    {
        "filename": "img/destination/generated/yeosu-harbor-night-v1.png",
        "destination_name": "여수",
        "caption": "빛으로 물드는 낭만적인 밤바다",
        "alt": "불빛이 바다에 비치는 여수 항구의 야경",
    },
)

REGION_GROUP_RULES = (
    ("서울·경기", ("서울", "경기", "인천")),
    ("강원", ("강원",)),
    ("충청", ("충청",)),
    ("전라", ("전라", "전북")),
    ("경상", ("경상", "부산", "대구", "울산")),
    ("제주", ("제주",)),
)

COMPANION_DESTINATION_GROUPS = (
    {
        "label": "혼자",
        "icon": "solo",
        "headline": "나를 위한 특별한 시간",
        "recommendation_title": "혼자 떠나기 좋은 여행지",
        "names": ("제주", "강릉", "구례", "안동"),
    },
    {
        "label": "연인",
        "icon": "couple",
        "headline": "둘만의 특별한 추억",
        "recommendation_title": "연인과 떠나기 좋은 여행지",
        "names": ("남해", "여수", "경주", "제주"),
    },
    {
        "label": "가족",
        "icon": "family",
        "headline": "함께여서 더 행복한 여행",
        "recommendation_title": "가족과 떠나기 좋은 여행지",
        "names": ("제주", "평창", "안동", "경주"),
    },
    {
        "label": "친구와",
        "icon": "friends",
        "headline": "언제나 즐거운 우리",
        "recommendation_title": "친구와 떠나기 좋은 여행지",
        "names": ("창원 진해", "삼척", "태백", "부산"),
    },
)

REGION_FALLBACK_IMAGES = {
    "서울·경기": (
        "img/destination/generated/inje-autumn-lake-v1.png",
        "img/destination/generated/muju-summer-valley-v1.png",
        "img/destination/generated/gurye-seomjin-river-v1.png",
        "img/destination/generated/damyang-metasequoia-road-v1.png",
    ),
    "강원": (
        "img/destination/generated/gangneung-beach-sunrise-v1.png",
        "img/destination/generated/sokcho-seoraksan-autumn-v1.png",
        "img/destination/generated/pyeongchang-sheep-ranch-v1.png",
        "img/destination/generated/inje-birch-forest-v1.png",
    ),
    "충청": (
        "img/destination/generated/boryeong-daecheon-sunset-v1.png",
        "img/destination/generated/inje-naerincheon-valley-v1.png",
        "img/destination/generated/taebaek-cloud-sunrise-v1.png",
        "img/destination/generated/muju-summer-valley-v1.png",
    ),
    "전라": (
        "img/destination/generated/yeosu-islands-sunset-v1.png",
        "img/destination/generated/gurye-sansuyu-village-v1.png",
        "img/destination/generated/muju-deogyusan-snow-v1.png",
        "img/destination/generated/jeongeup-naejangsan-autumn-v1.png",
    ),
    "경상": (
        "img/destination/generated/jinhae-cherry-stream-v1.png",
        "img/destination/generated/andong-hahoe-village-v1.png",
        "img/destination/generated/andong-dosan-seowon-v1.png",
        "img/destination/generated/taebaek-wind-highland-v1.png",
    ),
    "제주": (
        "img/destination/generated/jeju-dol-hareubang-v1.png",
        "img/destination/generated/jeju-sea-v1.png",
        "img/destination/generated/jeju-night-v1.png",
        "img/destination/generated/jeju-sea-v1.png",
    ),
}

TASTE_TILES = (
    {
        "label": "자연",
        "filename": "img/destination/generated/jeju-sea-v1.png",
        "query": "purpose=자연",
        "icon": "leaf",
    },
    {
        "label": "휴양",
        "filename": "img/destination/generated/yeosu-islands-sunset-v1.png",
        "query": "purpose=휴양",
        "icon": "waves",
    },
    {
        "label": "미식",
        "filename": "img/destination/generated/gangneung-seaside-cafe-v1.png",
        "query": "purpose=미식",
        "icon": "utensils",
    },
    {
        "label": "문화",
        "filename": "img/destination/generated/andong-hahoe-village-v1.png",
        "query": "purpose=문화",
        "icon": "landmark",
    },
    {
        "label": "액티비티",
        "filename": "img/destination/generated/pyeongchang-winter-slope-v1.png",
        "query": "purpose=액티비티",
        "icon": "activity",
    },
    {
        "label": "조용한",
        "filename": "img/destination/generated/gurye-mountain-temple-v1.png",
        "query": "atmosphere=조용한",
        "icon": "quiet",
    },
)


def _ordered_destinations(destinations_by_name, names):
    return [
        destinations_by_name[name]
        for name in names
        if name in destinations_by_name
    ]


def _region_groups(destinations):
    groups = []
    for label, fragments in REGION_GROUP_RULES:
        matches = [
            destination
            for destination in destinations
            if any(fragment in destination.region for fragment in fragments)
        ]
        groups.append(
            {
                "label": label,
                "destinations": matches[:4],
                "images": REGION_FALLBACK_IMAGES[label],
            }
        )
    return groups


@main_bp.get("/")
def index():
    """메인 화면에 필요한 여행지 묶음을 한 번의 조회로 구성한다."""
    all_destinations = list(
        db.session.execute(
            db.select(Destination).order_by(Destination.id)
        ).scalars()
    )
    destinations_by_name = {
        destination.name: destination for destination in all_destinations
    }
    companion_groups = [
        {
            "label": group["label"],
            "icon": group["icon"],
            "headline": group["headline"],
            "recommendation_title": group["recommendation_title"],
            "destinations": _ordered_destinations(
                destinations_by_name,
                group["names"],
            ),
        }
        for group in COMPANION_DESTINATION_GROUPS
    ]

    return render_template(
        "main/index.html",
        hero_slides=[
            {
                **slide,
                "destination": destinations_by_name.get(
                    slide["destination_name"]
                ),
            }
            for slide in HERO_SLIDES
        ],
        popular_destinations=_ordered_destinations(
            destinations_by_name,
            POPULAR_DESTINATION_NAMES,
        ),
        region_groups=_region_groups(all_destinations),
        companion_groups=companion_groups,
        fall_destination=destinations_by_name.get(FALL_DESTINATION_NAME),
        taste_tiles=TASTE_TILES,
    )
