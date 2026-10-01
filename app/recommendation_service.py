"""설명 가능한 여행지 추천 점수를 계산하는 순수 함수 모음."""

SEASON_ALL_YEAR = "사계절"

BUDGET_LIMITS = {
    "저렴": 150000,
    "보통": 300000,
    "높음": 500000,
}

COMPANION_MATCHES = {
    "혼자": {
        "purposes": {"자연", "문화", "미식"},
        "atmospheres": {"조용한", "자연친화적"},
    },
    "연인": {
        "purposes": {"휴양", "미식", "문화"},
        "atmospheres": {"낭만적인", "조용한"},
    },
    "가족": {
        "purposes": {"자연", "휴양", "문화"},
        "atmospheres": {"전통적인", "자연친화적", "조용한"},
    },
    "친구": {
        "purposes": {"액티비티", "미식"},
        "atmospheres": {"활기찬", "낭만적인"},
    },
}


def _companion_matches(destination, companion):
    rule = COMPANION_MATCHES.get(companion)
    if not rule:
        return False
    return (
        destination.purpose in rule["purposes"]
        or destination.atmosphere in rule["atmospheres"]
    )


def score_destination(destination, preference):
    """여행지 한 곳의 점수와 실제 일치 조건에 따른 설명을 반환한다."""
    score = 0
    reasons = []

    if destination.season in {preference.season, SEASON_ALL_YEAR}:
        score += 3
        reasons.append(
            "어느 계절에도 떠나기 좋아요"
            if destination.season == SEASON_ALL_YEAR
            else f"{preference.season}에 떠나기 좋아요"
        )

    if destination.purpose == preference.purpose:
        score += 3
        reasons.append(f"원하는 {preference.purpose} 여행과 잘 맞아요")

    if destination.atmosphere == preference.atmosphere:
        score += 2
        reasons.append(f"{preference.atmosphere} 분위기를 즐길 수 있어요")

    destination_budget = BUDGET_LIMITS.get(destination.budget_level)
    if destination_budget is not None and destination_budget <= preference.budget:
        score += 2
        reasons.append("선택한 예산 안에서 계획하기 좋아요")

    if destination.recommended_days == preference.trip_duration:
        score += 2
        reasons.append(f"{preference.trip_duration}일 일정에 알맞아요")
    elif (
        destination.recommended_days is not None
        and abs(destination.recommended_days - preference.trip_duration) == 1
    ):
        score += 1
        reasons.append("선택한 일정과 비슷하게 다녀오기 좋아요")

    if _companion_matches(destination, preference.companion):
        score += 1
        reasons.append(f"{preference.companion} 여행에 잘 어울려요")

    return score, reasons[:3]


def recommend_destinations(destinations, preference, limit=6):
    """점수순 추천과 대체 추천 여부를 반환한다."""
    ordered_destinations = sorted(destinations, key=lambda item: item.id)
    if preference is None:
        return [
            {"destination": item, "score": 0, "reasons": ["먼저 둘러보기 좋은 여행지예요"]}
            for item in ordered_destinations[:limit]
        ], True

    scored = []
    for destination in ordered_destinations:
        score, reasons = score_destination(destination, preference)
        if score > 0:
            scored.append(
                {
                    "destination": destination,
                    "score": score,
                    "reasons": reasons,
                }
            )

    if not scored:
        return [
            {"destination": item, "score": 0, "reasons": ["새로운 취향을 발견하기 좋은 여행지예요"]}
            for item in ordered_destinations[:limit]
        ], True

    scored.sort(key=lambda item: (-item["score"], item["destination"].id))
    return scored[:limit], False
