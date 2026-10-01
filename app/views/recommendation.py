from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from app import db
from app.auth_helpers import login_required
from app.models import Destination, UserPreference
from app.recommendation_service import recommend_destinations

recommendation_bp = Blueprint("recommendation", __name__)

CHOICES = {
    "season": ("봄", "여름", "가을", "겨울"),
    "companion": ("혼자", "연인", "가족", "친구"),
    "purpose": ("자연", "휴양", "문화", "미식", "액티비티"),
    "atmosphere": ("조용한", "낭만적인", "활기찬", "전통적인", "자연친화적"),
    "budget": (
        (150000, "15만원 이하"),
        (300000, "30만원 이하"),
        (500000, "50만원 이하"),
        (1000000, "50만원 이상"),
    ),
    "trip_duration": (
        (1, "당일"),
        (2, "1박 2일"),
        (3, "2박 3일"),
        (4, "3박 4일"),
        (5, "4박 5일"),
    ),
}


def _preference_form_data(preference):
    if preference is None:
        return {}
    return {
        "season": preference.season,
        "companion": preference.companion,
        "purpose": preference.purpose,
        "atmosphere": preference.atmosphere,
        "budget": str(preference.budget),
        "trip_duration": str(preference.trip_duration),
    }


def _validate_form(form):
    form_data = {
        field: (form.get(field) or "").strip()
        for field in CHOICES
    }
    allowed = {
        "season": set(CHOICES["season"]),
        "companion": set(CHOICES["companion"]),
        "purpose": set(CHOICES["purpose"]),
        "atmosphere": set(CHOICES["atmosphere"]),
        "budget": {str(value) for value, _ in CHOICES["budget"]},
        "trip_duration": {str(value) for value, _ in CHOICES["trip_duration"]},
    }
    errors = [field for field, value in form_data.items() if value not in allowed[field]]
    return form_data, errors


@recommendation_bp.route("/survey", methods=("GET", "POST"))
@login_required
def survey():
    preference = db.session.scalar(
        db.select(UserPreference).where(UserPreference.user_id == g.user.id)
    )

    if request.method == "POST":
        form_data, errors = _validate_form(request.form)
        if errors:
            flash("모든 질문에서 하나씩 선택해주세요.", "error")
            return render_template(
                "recommendation/survey.html",
                choices=CHOICES,
                form_data=form_data,
                has_preference=preference is not None,
            ), 400

        if preference is None:
            preference = UserPreference(user_id=g.user.id)
            db.session.add(preference)

        preference.season = form_data["season"]
        preference.companion = form_data["companion"]
        preference.purpose = form_data["purpose"]
        preference.atmosphere = form_data["atmosphere"]
        preference.budget = int(form_data["budget"])
        preference.trip_duration = int(form_data["trip_duration"])
        db.session.commit()
        return redirect(url_for("recommendation.result"))

    return render_template(
        "recommendation/survey.html",
        choices=CHOICES,
        form_data=_preference_form_data(preference),
        has_preference=preference is not None,
    )


@recommendation_bp.get("/result")
@login_required
def result():
    preference = db.session.scalar(
        db.select(UserPreference).where(UserPreference.user_id == g.user.id)
    )
    destinations = list(
        db.session.execute(
            db.select(Destination).order_by(Destination.id)
        ).scalars()
    )
    recommendations, fallback_mode = recommend_destinations(
        destinations,
        preference,
    )
    return render_template(
        "recommendation/result.html",
        recommendations=recommendations,
        preference_summary=_preference_form_data(preference),
        budget_labels={str(value): label for value, label in CHOICES["budget"]},
        fallback_mode=fallback_mode,
    )
