import json
import re
from functools import lru_cache
from pathlib import Path, PurePosixPath

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app import db
from app.auth_helpers import login_required
from app.models import Accommodation, AccommodationReview, Destination


accommodation_bp = Blueprint("accommodation", __name__)

LOCAL_ACCOMMODATION_IMAGE_PREFIX = "/static/img/accommodation/"
ACCOMMODATION_IMAGE_SUFFIXES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
    ".gif",
}
ACCOMMODATION_DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "accommodations.json"
)


@lru_cache(maxsize=1)
def _accommodation_booking_facts():
    """JSON에 정의된 숙소별 편의·입퇴실 정보를 조회용 사전으로 만든다."""
    with ACCOMMODATION_DATA_PATH.open(encoding="utf-8") as data_file:
        accommodations = json.load(data_file)

    return {
        (item["destination_name"], item["name"]): {
            "wifi_available": item.get("wifi_available", True),
            "parking_available": item.get("parking_available", True),
            "check_in_time": item.get("check_in_time", "15:00"),
            "check_out_time": item.get("check_out_time", "11:00"),
        }
        for item in accommodations
    }


def _booking_facts_for(accommodation):
    destination_name = (
        accommodation.destination.name if accommodation.destination else ""
    )
    return _accommodation_booking_facts().get(
        (destination_name, accommodation.name),
        {
            "wifi_available": True,
            "parking_available": True,
            "check_in_time": "15:00",
            "check_out_time": "11:00",
        },
    )


def _natural_filename_key(path):
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", path.name)
    ]


def _accommodation_gallery(image_url):
    """대표 이미지와 같은 폴더에 있는 로컬 숙소 사진을 순서대로 반환한다."""
    if not image_url or not image_url.startswith(LOCAL_ACCOMMODATION_IMAGE_PREFIX):
        return []

    relative_url = image_url.removeprefix("/static/")
    relative_path = Path(*PurePosixPath(relative_url).parts)
    static_root = Path(current_app.static_folder).resolve()
    image_path = (static_root / relative_path).resolve()

    try:
        image_path.relative_to(static_root)
    except ValueError:
        return []

    if not image_path.is_file():
        return []

    gallery_paths = sorted(
        (
            path
            for path in image_path.parent.iterdir()
            if path.is_file() and path.suffix.casefold() in ACCOMMODATION_IMAGE_SUFFIXES
        ),
        key=_natural_filename_key,
    )
    gallery_urls = [
        f"/static/{path.relative_to(static_root).as_posix()}" for path in gallery_paths
    ]

    # 데이터에 지정된 대표 이미지가 항상 첫 번째로 보이도록 보장한다.
    if image_url in gallery_urls:
        gallery_urls.remove(image_url)
        gallery_urls.insert(0, image_url)

    return gallery_urls


@accommodation_bp.get("", endpoint="list")
def accommodation_list():
    destination_id = request.args.get("destination_id", type=int)
    destination = (
        db.get_or_404(Destination, destination_id)
        if destination_id is not None
        else None
    )
    query = db.select(Accommodation).order_by(Accommodation.id)
    if destination is not None:
        query = query.where(Accommodation.destination_id == destination.id)

    accommodations = list(
        db.session.execute(query).scalars()
    )
    return render_template(
        "accommodation/list.html",
        destination=destination,
        accommodations=accommodations,
    )


@accommodation_bp.get("/<int:id>")
def detail(id):
    accommodation = db.get_or_404(Accommodation, id)
    accommodation_images = _accommodation_gallery(accommodation.image_url)
    reviews = list(
        db.session.execute(
            db.select(AccommodationReview)
            .options(joinedload(AccommodationReview.user))
            .where(AccommodationReview.accommodation_id == accommodation.id)
            .order_by(
                AccommodationReview.created_at.desc(),
                AccommodationReview.id.desc(),
            )
        ).scalars()
    )
    review_average = db.session.scalar(
        db.select(db.func.avg(AccommodationReview.rating)).where(
            AccommodationReview.accommodation_id == accommodation.id
        )
    )
    average_rating = (
        float(review_average)
        if review_average is not None
        else float(accommodation.rating)
        if accommodation.rating is not None
        else None
    )
    can_review = bool(
        g.user
        and not db.session.scalar(
            db.select(AccommodationReview.id).where(
                AccommodationReview.user_id == g.user.id,
                AccommodationReview.accommodation_id == accommodation.id,
            )
        )
    )
    return render_template(
        "accommodation/detail.html",
        accommodation=accommodation,
        accommodation_images=accommodation_images,
        booking_facts=_booking_facts_for(accommodation),
        accommodation_reviews=reviews,
        average_rating=average_rating,
        can_review=can_review,
    )


@accommodation_bp.post("/<int:id>/reviews")
@login_required
def create_review(id):
    accommodation = db.get_or_404(Accommodation, id)
    content = (request.form.get("content") or "").strip()
    try:
        rating = int(request.form.get("rating", ""))
    except (TypeError, ValueError):
        rating = None

    error = None
    if rating is None or not 1 <= rating <= 5:
        error = "평점은 1점부터 5점 사이로 선택해 주세요."
    elif not content:
        error = "숙소 후기 내용을 입력해 주세요."
    elif db.session.scalar(
        db.select(AccommodationReview.id).where(
            AccommodationReview.user_id == g.user.id,
            AccommodationReview.accommodation_id == accommodation.id,
        )
    ):
        error = "이 숙소에는 이미 후기를 작성했습니다."

    if error is None:
        db.session.add(
            AccommodationReview(
                user_id=g.user.id,
                accommodation_id=accommodation.id,
                rating=rating,
                content=content,
            )
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            error = "이 숙소에는 이미 후기를 작성했습니다."

    if error is not None:
        flash(error, "error")

    return redirect(
        url_for("accommodation.detail", id=accommodation.id, _anchor="stay-reviews")
    )
