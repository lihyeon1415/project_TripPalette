import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app import create_app, db
from app.models import (
    Accommodation,
    Destination,
    Product,
    ProductCategory,
    ProductImage,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "app" / "data"
DESTINATIONS_PATH = DATA_DIR / "destinations.json"
ACCOMMODATIONS_PATH = DATA_DIR / "accommodations.json"
PRODUCTS_PATH = DATA_DIR / "products.json"

DESTINATION_REQUIRED_FIELDS = ("name", "region")
ACCOMMODATION_REQUIRED_FIELDS = (
    "destination_name",
    "name",
    "address",
    "price_per_night",
    "capacity",
)
PRODUCT_REQUIRED_FIELDS = (
    "sku",
    "name",
    "price",
    "stock_quantity",
    "categories",
    "images",
    "is_active",
)
PRODUCT_CATEGORIES = {"travel", "daily", "stationery"}


def load_json(path):
    """UTF-8 JSON 배열을 읽고 기본 형식을 검증한다."""
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Seed 파일을 찾을 수 없습니다: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{path.name}의 JSON 형식이 올바르지 않습니다: "
            f"{error.lineno}행 {error.colno}열"
        ) from error

    if not isinstance(data, list):
        raise ValueError(f"{path.name}의 최상위 값은 배열이어야 합니다.")

    return data


def require_fields(item, required_fields, label):
    """필수 필드가 없거나 빈 문자열이면 명확한 오류를 발생시킨다."""
    missing_fields = [
        field
        for field in required_fields
        if field not in item or item[field] is None or item[field] == ""
    ]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(f"{label}의 필수 필드가 비어 있습니다: {missing}")


def positive_integer(value, field, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label}의 {field}는 1 이상의 정수여야 합니다.")
    return value


def nonnegative_integer(value, field, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label}의 {field}는 0 이상의 정수여야 합니다.")
    return value


def optional_rating(value, label):
    if value in (None, ""):
        return None

    try:
        rating = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{label}의 rating은 숫자여야 합니다.") from error

    if rating < 0 or rating > 5:
        raise ValueError(f"{label}의 rating은 0~5 범위여야 합니다.")
    return rating


def validate_destinations(items):
    seen_names = set()
    for index, item in enumerate(items, start=1):
        label = f"여행지 {index}번"
        if not isinstance(item, dict):
            raise ValueError(f"{label} 데이터는 객체여야 합니다.")
        require_fields(item, DESTINATION_REQUIRED_FIELDS, label)

        name = item["name"].strip()
        if name in seen_names:
            raise ValueError(f"여행지명이 중복되었습니다: {name}")
        seen_names.add(name)

        days = item.get("recommended_days")
        if days is not None:
            positive_integer(days, "recommended_days", label)


def validate_accommodations(items, destination_names):
    seen_pairs = set()
    for index, item in enumerate(items, start=1):
        label = f"숙소 {index}번"
        if not isinstance(item, dict):
            raise ValueError(f"{label} 데이터는 객체여야 합니다.")
        require_fields(item, ACCOMMODATION_REQUIRED_FIELDS, label)

        destination_name = item["destination_name"].strip()
        accommodation_name = item["name"].strip()
        if destination_name not in destination_names:
            raise ValueError(
                f"{label}의 연결 여행지가 존재하지 않습니다: {destination_name}"
            )

        pair = (destination_name, accommodation_name)
        if pair in seen_pairs:
            raise ValueError(
                f"동일 여행지의 숙소명이 중복되었습니다: "
                f"{destination_name} / {accommodation_name}"
            )
        seen_pairs.add(pair)

        positive_integer(item["price_per_night"], "price_per_night", label)
        positive_integer(item["capacity"], "capacity", label)
        optional_rating(item.get("rating"), label)

        for field in ("wifi_available", "parking_available"):
            if not isinstance(item.get(field), bool):
                raise ValueError(f"{label}의 {field}는 true 또는 false여야 합니다.")

        for field in ("check_in_time", "check_out_time"):
            if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", item.get(field, "")):
                raise ValueError(f"{label}의 {field}는 HH:MM 형식이어야 합니다.")


def validate_products(items):
    seen_skus = set()
    for index, item in enumerate(items, start=1):
        label = f"상품 {index}번"
        if not isinstance(item, dict):
            raise ValueError(f"{label} 데이터는 객체여야 합니다.")
        require_fields(item, PRODUCT_REQUIRED_FIELDS, label)

        sku = item["sku"].strip()
        if not re.fullmatch(r"[A-Z0-9-]{3,50}", sku):
            raise ValueError(f"{label}의 sku 형식이 올바르지 않습니다: {sku}")
        if sku in seen_skus:
            raise ValueError(f"상품 SKU가 중복되었습니다: {sku}")
        seen_skus.add(sku)

        nonnegative_integer(item["price"], "price", label)
        nonnegative_integer(item["stock_quantity"], "stock_quantity", label)

        if not isinstance(item["is_active"], bool):
            raise ValueError(f"{label}의 is_active는 true 또는 false여야 합니다.")

        categories = item["categories"]
        if not isinstance(categories, list) or not categories:
            raise ValueError(f"{label}의 categories는 하나 이상의 배열이어야 합니다.")
        unknown_categories = set(categories) - PRODUCT_CATEGORIES
        if unknown_categories:
            unknown = ", ".join(sorted(unknown_categories))
            raise ValueError(f"{label}에 허용되지 않은 카테고리가 있습니다: {unknown}")
        if len(categories) != len(set(categories)):
            raise ValueError(f"{label}의 categories가 중복되었습니다.")

        images = item["images"]
        if not isinstance(images, list) or not images:
            raise ValueError(f"{label}의 images는 하나 이상의 배열이어야 합니다.")
        thumbnail_url = item.get("thumbnail_url")
        image_paths = [thumbnail_url, *images]
        for image_path in image_paths:
            if not isinstance(image_path, str) or not image_path.startswith("img/goods/"):
                raise ValueError(f"{label}의 상품 이미지 경로가 올바르지 않습니다.")
            if not (BASE_DIR / "app" / "static" / image_path).is_file():
                raise ValueError(
                    f"{label}의 상품 이미지 파일이 존재하지 않습니다: {image_path}"
                )


def upsert_destinations(items):
    created = 0
    updated = 0

    existing_destinations = {
        destination.name: destination
        for destination in db.session.execute(db.select(Destination)).scalars()
    }

    for item in items:
        name = item["name"].strip()
        destination = existing_destinations.get(name)
        if destination is None:
            destination = Destination(name=name)
            db.session.add(destination)
            existing_destinations[name] = destination
            created += 1
        else:
            updated += 1

        destination.region = item["region"].strip()
        destination.description = item.get("description") or None
        destination.season = item.get("season") or None
        destination.purpose = item.get("purpose") or None
        destination.atmosphere = item.get("atmosphere") or None
        destination.budget_level = item.get("budget_level") or None
        destination.recommended_days = item.get("recommended_days")
        # 여행지 이미지는 승인된 로컬 정적 파일에서만 표시한다.
        destination.image_url = None

    db.session.flush()
    return existing_destinations, created, updated


def upsert_accommodations(items, destinations_by_name):
    created = 0
    updated = 0

    existing_accommodations = {
        (accommodation.destination_id, accommodation.name): accommodation
        for accommodation in db.session.execute(db.select(Accommodation)).scalars()
    }

    for item in items:
        destination_name = item["destination_name"].strip()
        destination = destinations_by_name[destination_name]
        name = item["name"].strip()
        key = (destination.id, name)

        accommodation = existing_accommodations.get(key)
        if accommodation is None:
            accommodation = Accommodation(
                destination_id=destination.id,
                name=name,
            )
            db.session.add(accommodation)
            existing_accommodations[key] = accommodation
            created += 1
        else:
            updated += 1

        accommodation.address = item["address"].strip()
        accommodation.description = item.get("description") or None
        accommodation.price_per_night = item["price_per_night"]
        accommodation.capacity = item["capacity"]
        accommodation.rating = optional_rating(
            item.get("rating"),
            f"숙소 {destination_name} / {name}",
        )
        # 검수된 로컬 숙소 이미지는 시드 데이터의 경로를 그대로 유지한다.
        # 값이 없는 숙소만 사진 준비 중 상태로 표시한다.
        accommodation.image_url = item.get("image_url") or None

    return created, updated


def upsert_products(items):
    created = 0
    updated = 0
    existing_products = {
        product.sku: product
        for product in db.session.execute(db.select(Product)).scalars()
    }

    for item in items:
        sku = item["sku"].strip()
        product = existing_products.get(sku)
        if product is None:
            product = Product(sku=sku)
            db.session.add(product)
            existing_products[sku] = product
            created += 1
        else:
            updated += 1

        product.name = item["name"].strip()
        product.description = item.get("description") or None
        product.price = item["price"]
        product.stock_quantity = item["stock_quantity"]
        product.thumbnail_url = item.get("thumbnail_url") or None
        product.is_active = item["is_active"]

        desired_categories = set(item["categories"])
        existing_categories = {
            category.category: category for category in product.categories
        }
        for category_name, category in existing_categories.items():
            if category_name not in desired_categories:
                db.session.delete(category)
        for category_name in desired_categories - set(existing_categories):
            product.categories.append(ProductCategory(category=category_name))

        desired_images = list(dict.fromkeys(item["images"]))
        existing_images = {image.image_url: image for image in product.images}
        for image_url, image in existing_images.items():
            if image_url not in desired_images:
                db.session.delete(image)
        for sort_order, image_url in enumerate(desired_images):
            image = existing_images.get(image_url)
            if image is None:
                product.images.append(
                    ProductImage(image_url=image_url, sort_order=sort_order)
                )
            else:
                image.sort_order = sort_order

    return created, updated


def seed():
    destinations = load_json(DESTINATIONS_PATH)
    accommodations = load_json(ACCOMMODATIONS_PATH)
    products = load_json(PRODUCTS_PATH)

    validate_destinations(destinations)
    destination_names = {item["name"].strip() for item in destinations}
    validate_accommodations(accommodations, destination_names)
    validate_products(products)

    app = create_app()
    with app.app_context():
        try:
            destinations_by_name, destination_created, destination_updated = (
                upsert_destinations(destinations)
            )
            accommodation_created, accommodation_updated = upsert_accommodations(
                accommodations,
                destinations_by_name,
            )
            product_created, product_updated = upsert_products(products)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print(
            "여행지: "
            f"신규 {destination_created}개, 갱신 {destination_updated}개, "
            f"전체 {db.session.scalar(db.select(db.func.count(Destination.id)))}개"
        )
        print(
            "숙소: "
            f"신규 {accommodation_created}개, 갱신 {accommodation_updated}개, "
            f"전체 {db.session.scalar(db.select(db.func.count(Accommodation.id)))}개"
        )
        print(
            "상품: "
            f"신규 {product_created}개, 갱신 {product_updated}개, "
            f"전체 {db.session.scalar(db.select(db.func.count(Product.id)))}개"
        )


if __name__ == "__main__":
    seed()
