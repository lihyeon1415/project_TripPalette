from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.auth_helpers import login_required
from app.models import Accommodation, Destination, Favorite, Review


destination_bp = Blueprint("destination", __name__)

FILTER_COLUMNS = {
    "region": Destination.region,
    "season": Destination.season,
    "purpose": Destination.purpose,
    "atmosphere": Destination.atmosphere,
}


def _distinct_values(column):
    """필터 Select에 표시할 빈 값 없는 고유 목록을 반환한다."""
    statement = (
        db.select(column)
        .where(column.is_not(None), column != "")
        .distinct()
        .order_by(column)
    )
    return list(db.session.execute(statement).scalars())


@destination_bp.get("", endpoint="list")
def destination_list():
    keyword = request.args.get("keyword", "").strip()
    selected_filters = {
        name: request.args.get(name, "").strip() for name in FILTER_COLUMNS
    }

    statement = db.select(Destination)
    if keyword:
        search_pattern = f"%{keyword}%"
        statement = statement.where(
            or_(
                Destination.name.ilike(search_pattern),
                Destination.region.ilike(search_pattern),
                Destination.description.ilike(search_pattern),
            )
        )

    for name, column in FILTER_COLUMNS.items():
        selected_value = selected_filters[name]
        if selected_value:
            statement = statement.where(column == selected_value)

    destinations = list(
        db.session.execute(statement.order_by(Destination.id)).scalars()
    )
    filters = {
        "regions": _distinct_values(Destination.region),
        "seasons": _distinct_values(Destination.season),
        "purposes": _distinct_values(Destination.purpose),
        "atmospheres": _distinct_values(Destination.atmosphere),
    }
    favorite_destination_ids = set()
    if g.user is not None:
        favorite_destination_ids = set(
            db.session.execute(
                db.select(Favorite.destination_id).where(
                    Favorite.user_id == g.user.id
                )
            ).scalars()
        )

    return render_template(
        "destination/list.html",
        destinations=destinations,
        filters=filters,
        selected_filters=selected_filters,
        keyword=keyword,
        favorite_destination_ids=favorite_destination_ids,
    )


@destination_bp.get("/<int:id>")
def detail(id):
    destination = db.get_or_404(Destination, id)
    reviews = list(
        db.session.execute(
            db.select(Review)
            .where(Review.destination_id == destination.id)
            .order_by(Review.created_at.desc(), Review.id.desc())
        ).scalars()
    )
    accommodations = list(
        db.session.execute(
            db.select(Accommodation)
            .where(Accommodation.destination_id == destination.id)
            .order_by(Accommodation.id)
            .limit(3)
        ).scalars()
    )
    accommodation_count = db.session.scalar(
        db.select(db.func.count(Accommodation.id)).where(
            Accommodation.destination_id == destination.id
        )
    ) or 0
    is_favorite = False
    can_review = False
    if g.user is not None:
        is_favorite = db.session.scalar(
            db.select(Favorite.id).where(
                Favorite.user_id == g.user.id,
                Favorite.destination_id == destination.id,
            )
        ) is not None
        has_review = db.session.scalar(
            db.select(Review.id).where(
                Review.user_id == g.user.id,
                Review.destination_id == destination.id,
            )
        ) is not None
        can_review = not has_review

    return render_template(
        "destination/detail.html",
        destination=destination,
        reviews=reviews,
        accommodations=accommodations,
        accommodation_count=accommodation_count,
        is_favorite=is_favorite,
        can_review=can_review,
    )


@destination_bp.post("/<int:id>/favorite")
@login_required
def toggle_favorite(id):
    destination = db.get_or_404(Destination, id)
    favorite = db.session.scalar(
        db.select(Favorite).where(
            Favorite.user_id == g.user.id,
            Favorite.destination_id == destination.id,
        )
    )

    if favorite is None:
        db.session.add(
            Favorite(user_id=g.user.id, destination_id=destination.id)
        )
    else:
        db.session.delete(favorite)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("찜 상태를 변경하지 못했습니다. 다시 시도해 주세요.", "error")

    return redirect(url_for("destination.detail", id=destination.id))


@destination_bp.post("/<int:id>/reviews")
@login_required
def create_review(id):
    destination = db.get_or_404(Destination, id)
    content = (request.form.get("content") or "").strip()
    try:
        rating = int(request.form.get("rating", ""))
    except (TypeError, ValueError):
        rating = None

    error = None
    if rating is None or not 1 <= rating <= 5:
        error = "평점은 1점부터 5점 사이로 입력해 주세요."
    elif not content:
        error = "리뷰 내용을 입력해 주세요."
    elif db.session.scalar(
        db.select(Review.id).where(
            Review.user_id == g.user.id,
            Review.destination_id == destination.id,
        )
    ):
        error = "이 여행지에는 이미 리뷰를 작성했습니다."

    if error is None:
        db.session.add(
            Review(
                user_id=g.user.id,
                destination_id=destination.id,
                rating=rating,
                content=content,
            )
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            error = "이 여행지에는 이미 리뷰를 작성했습니다."

    if error is not None:
        flash(error, "error")

    return redirect(url_for("destination.detail", id=destination.id))


@destination_bp.get("/<int:id>/accommodations")
def accommodations(id):
    db.get_or_404(Destination, id)
    return redirect(
        url_for(
            "accommodation.list",
            destination_id=id,
        )
    )
