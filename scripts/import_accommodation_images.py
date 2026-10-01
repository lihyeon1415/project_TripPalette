"""지역/숙소 폴더의 사진을 정적 자산으로 복사하고 시드 경로를 갱신한다."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "app" / "data" / "accommodations.json"
STATIC_ROOT = PROJECT_ROOT / "app" / "static" / "img" / "accommodation"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}

# 전달받은 이미지 폴더의 지역명에는 도명이나 추천 계절이 함께 적힌 경우가 있다.
# 정적 자산 경로와 시드 데이터에는 실제 여행지 이름만 사용한다.
REGION_ALIASES = {
    "강릉(겨울)": "강릉",
    "강원도 정선": "정선",
    "경상남도 거제": "거제",
    "경상북도청송": "청송",
    "경주(사계절)": "경주",
    "담양(가을)": "담양",
    "무주(여름)": "무주",
    "부산(사계절)": "부산",
    "삼척(봄)": "삼척",
    "속초(여름)": "속초",
    "안동(가을)": "안동",
    "인제(겨울)": "인제",
    "전라남도 여수": "여수",
    "전라북도 군산": "군산",
    "정읍(가을)": "정읍",
    "제주(봄)": "제주",
    "사계절 제주": "제주",
    "제주도 서귀포": "서귀포",
    "창원(봄)": "창원 진해",
    "충청남도 보령": "보령",
    "태백(여름)": "태백",
    "평창(겨울)": "평창",
}

# 원본 폴더의 명백한 띄어쓰기/오탈자만 현재 시드의 숙소명에 연결한다.
FOLDER_ALIASES = {
    ("서산", "베니키아호텔"): "베니키아호텔 서산",
    ("영동", "스테이인터뷰"): "영동 스테이인터뷰",
    ("이천", "인트라다호텔"): "이천 인트라다 호텔",
    ("제천", "하운드호텔"): "하운드호텔 제천역",
    ("춘천", "숲펜션"): "춘천숲펜션",
    ("춘천", "에스턴호텔"): "춘천 에스턴호텔",
    ("충주", "서유숙펜션"): "충주 서유숙펜션",
    ("태안", "칸타빌레펜션"): "태안 칸타빌레펜션",
    ("포천", "아도니스호텔"): "포천 아도니스호텔",
    ("포천", "아일랜드펜션"): "포천 아일랜드펜션",
    ("괴산", "그랑둘이펜션"): "괴산 그랑둘이 펜션",
    ("괴산", "농소막펜션"): "농소막펜션&카페",
    ("단양", "단양글램핑"): "단양글램핑&펜션",
    ("목포", "호텔 현대 바이 라한 목포"): "호텔현대 바이 라한 목포",
    ("산청", "휴름산청빌리지"): "휴롬산청빌리지",
    ("양양", "그랑블루글램핑"): "그랑블루글램핑 야영장&펜션",
    ("양주", "그레이캐슬펜션"): "양주 그레이캐슬펜션",
    ("양주", "스톤밸리캠핑장"): "양주스톤밸리캠핑장",
    ("양평", "양평 포레스트렌션"): "양평 포레스트펜션",
    ("연천", "쉬는시간펜션"): "연천 쉬는시간펜션",
    ("연천", "은대리쉼나루펜션"): "연천 은대리 쉼나루 펜션",
    ("연천", "조선로얄패밀리호텔"): "조선 로얄 패밀리 호텔",
    ("원주", "원주센트럴호텔"): "원주 센트럴 호텔",
    ("원주", "원주에코캠프"): "원주 에코캠프",
    ("제주 한림", "결겹"): "곁겹",
    ("인제", "인제 스피디움호텔 & 리조트"): "인제 스피디움 호텔앤리조트",
    ("인제", "인제 스피디움호텔&리조트"): "인제 스피디움 호텔앤리조트",
    ("평창", "휘닉스 리조트 평창"): "휘닉스파크 평창",
    ("홍천", "세이지우드 홍천"): "사가우드 홍천",
    ("홍천", "소노펠리체 빌리지 비발디 파그"): "소노펠리체 빌리지 비발디파크",
    ("거제", "소노캄거재"): "소노캄 거제",
    ("경주", "경주 브루원 리조트"): "블루원 리조트",
    ("경주", "경주앤한옥펜션"): "경주엔한옥펜션",
    ("무주", "랜드글램핑"): "무주 랜드글램핑",
    ("부산", "아난티코드"): "아난티 앳 부산 코브",
    ("부산", "제이스글램핑"): "제이스 스파 글램핑",
    ("부산", "풀마레 풀빌라"): "부산 폴마레펜션",
    ("속초", "씨크루즈호텔"): "씨크루즈호텔 속초",
    ("군산", "버드글래핑"): "버드글램핑",
    ("제주", "씨사이드뷰"): "제주 씨사이드뷰 펜션",
    ("창원 진해", "그랜드 머큐어 앰버서더 창원"): "그랜드 머큐어 앰배서더 창원",
    ("창원 진해", "잔해이터시티호텔"): "진해 인터시티호텔",
    ("태안", "칸타빌레스파펜션"): "칸타빌레펜션",
    ("포천", "늘푸른허브펜션"): "산정호수계곡 늘푸른허브펜션",
}

# 원본 폴더에는 남겨두되 프로젝트에서 사용하지 않을 저화질·오류 이미지를 제외한다.
EXCLUDED_SOURCE_FILENAMES = {
    ("화성", "라마다동탄"): {"1.jpg", "images.jpg"},
}

# 자연 정렬의 첫 파일과 다른 사진을 대표 이미지로 사용할 때 지정한다.
COVER_IMAGE_OVERRIDES = {
    ("화성", "라마다동탄"): "0224y12000cahszww8F28_W_600_0_R5.webp",
}


def normalize_name(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", value.casefold())


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", path.name)]


def resolve_source_root(source: Path) -> Path:
    nested = source / "호텔이미지"
    return nested if nested.is_dir() else source


def import_images(source: Path) -> tuple[int, int, list[str]]:
    source = resolve_source_root(source)
    with DATA_PATH.open(encoding="utf-8") as file:
        accommodations = json.load(file)

    normalized_lookup: dict[tuple[str, str], list[dict]] = {}
    global_normalized_lookup: dict[str, list[dict]] = {}
    exact_lookup: dict[tuple[str, str], dict] = {}
    for item in accommodations:
        region = item["destination_name"].strip()
        name = item["name"].strip()
        exact_lookup[(region, name)] = item
        normalized_lookup.setdefault((region, normalize_name(name)), []).append(item)
        global_normalized_lookup.setdefault(normalize_name(name), []).append(item)

    matched_count = 0
    copied_count = 0
    skipped: list[str] = []

    for region_dir in sorted((path for path in source.iterdir() if path.is_dir()), key=lambda path: path.name):
        source_region = REGION_ALIASES.get(region_dir.name, region_dir.name)
        for lodging_dir in sorted((path for path in region_dir.iterdir() if path.is_dir()), key=lambda path: path.name):
            source_key = (source_region, lodging_dir.name)
            alias = FOLDER_ALIASES.get((source_region, lodging_dir.name))
            if alias:
                item = exact_lookup.get((source_region, alias))
                matches = [item] if item else []
            else:
                matches = normalized_lookup.get(
                    (source_region, normalize_name(lodging_dir.name)),
                    [],
                )
                if not matches:
                    global_matches = global_normalized_lookup.get(
                        normalize_name(lodging_dir.name),
                        [],
                    )
                    if len(global_matches) == 1:
                        matches = global_matches

            if len(matches) != 1:
                reason = "대응 숙소 없음" if not matches else "대응 숙소 중복"
                skipped.append(f"{source_region} / {lodging_dir.name}: {reason}")
                continue

            excluded_filenames = EXCLUDED_SOURCE_FILENAMES.get(source_key, set())
            images = sorted(
                (
                    path
                    for path in lodging_dir.iterdir()
                    if path.is_file() and path.suffix.casefold() in IMAGE_SUFFIXES
                    and path.name not in excluded_filenames
                ),
                key=natural_key,
            )
            if not images:
                skipped.append(f"{source_region} / {lodging_dir.name}: 이미지 없음")
                continue

            item = matches[0]
            target_region = item["destination_name"].strip()
            canonical_name = item["name"].strip()
            target_dir = STATIC_ROOT / target_region / canonical_name
            target_dir.mkdir(parents=True, exist_ok=True)
            for image in images:
                shutil.copy2(image, target_dir / image.name)
                copied_count += 1

            cover_filename = COVER_IMAGE_OVERRIDES.get(source_key, images[0].name)
            cover_image = next(
                (image for image in images if image.name == cover_filename),
                images[0],
            )
            item["image_url"] = (
                f"/static/img/accommodation/{target_region}/{canonical_name}/{cover_image.name}"
            )
            matched_count += 1

    with DATA_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(accommodations, file, ensure_ascii=False, indent=2)
        file.write("\n")

    return matched_count, copied_count, skipped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="지역 폴더를 포함한 호텔 이미지 폴더")
    args = parser.parse_args()

    matched_count, copied_count, skipped = import_images(args.source)
    print(f"연결 숙소: {matched_count}개")
    print(f"복사 이미지: {copied_count}개")
    if skipped:
        print("제외 항목:")
        for message in skipped:
            print(f"- {message}")


if __name__ == "__main__":
    main()
