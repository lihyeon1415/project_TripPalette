"""이미지가 없는 캠핑·글램핑 숙소를 시드 JSON에서 제거한다."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "app" / "data" / "accommodations.json"
OUTDOOR_STAY_PATTERN = re.compile(r"캠핑|글램핑")


def is_target(item: dict) -> bool:
    return not item.get("image_url") and (
        bool(OUTDOOR_STAY_PATTERN.search(item.get("name", "")))
        or "캠핑형 숙소" in (item.get("description") or "")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="대상 확인만 하지 않고 JSON에서 실제로 제거한다.",
    )
    args = parser.parse_args()

    with DATA_PATH.open(encoding="utf-8") as file:
        accommodations = json.load(file)

    targets = [item for item in accommodations if is_target(item)]
    for item in targets:
        print(f"- {item['destination_name']} / {item['name']}")
    print(f"대상 숙소: {len(targets)}개")

    if not args.apply:
        print("확인 모드입니다. 삭제하려면 --apply를 사용하세요.")
        return

    remaining = [item for item in accommodations if not is_target(item)]
    with DATA_PATH.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(remaining, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"삭제 완료: {len(accommodations) - len(remaining)}개")


if __name__ == "__main__":
    main()
