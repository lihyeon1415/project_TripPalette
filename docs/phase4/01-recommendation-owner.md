# 작업자 1 — 맞춤 여행지 추천 전체

담당자: 팀장

작업 브랜치: `kdk`

PR 대상: `develop`

상태: 완료

## 목표

회원의 여행 선호를 한 건의 최신 설정으로 저장하고, 여행지 데이터를 점수화하여 추천 이유와 함께 상위 결과를 제공합니다. 설문·저장·계산·결과 UI·테스트를 한 사람이 끝까지 담당합니다.

## 담당 파일

```text
app/views/recommendation.py
app/recommendation_service.py          # 신규
app/templates/recommendation/survey.html
app/templates/recommendation/result.html
app/templates/main/index.html           # 맞춤 추천 CTA 링크만 수정
app/templates/base.html                 # 마이페이지·푸터 추천 링크만 수정
app/static/css/recommendation.css      # 신규
app/static/js/recommendation.js        # 필요한 경우에만 신규
tests/test_phase4_recommendation.py    # 신규
docs/phase4/
Roadmap.md
```

`UserPreference`와 `Destination` 모델은 이미 있으므로 모델과 Migration은 변경하지 않습니다.

## URL 계약

| Method | URL | 기능 | 권한 |
|---|---|---|---|
| GET | `/recommend/survey` | 저장된 설정을 포함한 설문 표시 | 회원 |
| POST | `/recommend/survey` | 설문 검증 및 저장·수정 | 회원 |
| GET | `/recommend/result` | 점수순 추천 결과 표시 | 회원 |

비회원은 `login_required`를 통해 로그인 화면으로 이동하고 로그인 후 원래 추천 페이지로 복귀합니다.

## 접근 경로

맞춤 추천 설문은 다음 세 곳에서 접근합니다.

1. 메인 페이지 하단 `맞춤 여행지 찾기` CTA
2. 로그인 회원의 마이페이지 메뉴 `맞춤 여행 설정`
3. 공통 푸터의 `맞춤 추천`

세 링크는 모두 `/recommend/survey`로 이동합니다. 비회원이 메인 CTA나 푸터에서 접근하면 로그인 화면으로 이동하고, 로그인 성공 후 설문으로 복귀합니다.

헤더에는 맞춤 추천 메뉴를 새로 만들지 않으며 현재 구성을 그대로 유지합니다.

## 설문 입력 계약

| 필드 | 허용 값 |
|---|---|
| `season` | 봄, 여름, 가을, 겨울 |
| `companion` | 혼자, 연인, 가족, 친구 |
| `purpose` | 자연, 휴양, 문화, 미식, 액티비티 |
| `atmosphere` | 조용한, 낭만적인, 활기찬, 전통적인, 자연친화적 |
| `budget` | 150000, 300000, 500000 |
| `trip_duration` | 1, 2, 3, 4, 5 |

- 모든 항목은 서버에서 허용 값인지 검증합니다.
- 예산과 기간은 정수로 변환한 뒤 검증합니다.
- 최초 제출은 `UserPreference`를 생성합니다.
- 다시 제출하면 같은 사용자의 기존 행을 수정합니다.
- 요청에서 받은 `user_id`를 신뢰하지 않고 `g.user.id`만 사용합니다.

## 추천 규칙

추천 계산은 `app/recommendation_service.py`의 순수 함수로 분리합니다.

| 조건 | 권장 점수 |
|---|---:|
| 계절 일치 또는 여행지가 사계절 | +3 |
| 목적 일치 | +3 |
| 분위기 일치 | +2 |
| 여행지 예산 등급이 선택 예산 이내 | +2 |
| 추천 기간 정확히 일치 | +2 |
| 추천 기간과 1일 차이 | +1 |
| 동행 유형과 목적·분위기 조합 일치 | +1 |

- 총점 내림차순, 동점이면 여행지 ID 오름차순으로 정렬합니다.
- 상위 6개를 기본 결과로 제공합니다.
- 결과마다 실제 일치 조건으로 만든 추천 이유를 최대 3개 표시합니다.
- 설정이 없거나 유효한 일치 결과가 없어도 전체 여행지 중 대체 추천을 제공합니다.
- 추천 대상은 `Destination`이며 숙소를 직접 추천하지 않습니다.

## Template 변수 계약

### `survey.html`

```text
choices          허용 선택지 묶음
form_data        저장값 또는 검증 실패 후 입력값
has_preference   기존 설정 존재 여부
```

### `result.html`

```text
recommendations     추천 결과 목록
preference_summary  사용자가 선택한 조건 요약
fallback_mode       대체 추천 여부
```

추천 결과 항목 구조:

```python
{
    "destination": destination,
    "score": 10,
    "reasons": [
        "가을에 떠나기 좋아요",
        "원하는 자연 여행과 잘 맞아요",
        "3일 일정에 알맞아요",
    ],
}
```

## UI 요구사항

- 한 화면에 질문을 모두 표시하되 질문별 선택 카드로 구분합니다.
- 기존 설정이 있으면 선택 상태를 복원하고 제출 버튼을 `취향 다시 저장하기`로 표시합니다.
- 결과 상단에 선택 조건 요약과 `취향 다시 설정하기` 링크를 둡니다.
- 결과 카드는 승인된 로컬 생성 이미지 또는 정적 Placeholder를 사용합니다.
- 추천 이유는 점수만 표시하지 않고 사람이 이해할 수 있는 문장으로 표시합니다.
- JavaScript가 없어도 Form 제출과 결과 확인이 가능해야 합니다.
- 메인 CTA·마이페이지·푸터 링크만 연결하고 헤더는 수정하지 않습니다.

## 자동 테스트

- 비회원 설문·결과 접근 차단
- 최초 설정 저장
- 재제출 시 기존 설정 수정 및 중복 행 방지
- 허용되지 않은 선택값과 누락값 차단
- 회원별 설정 분리
- 점수와 정렬 순서 검증
- 추천 이유 생성 검증
- 설정 없음·일치 결과 없음의 대체 추천
- 결과에서 여행지 상세 URL 연결
- 여행지가 없는 DB에서도 500 오류가 발생하지 않음

## 금지사항

- 모델·Migration 변경
- 추천 점수를 JavaScript에서만 계산
- 클라이언트의 사용자 ID 신뢰
- 숙소 추천 또는 예약 기능 추가
- 추천 이유 없이 단순 목록만 표시
- 작업자 2·3의 Template 또는 CSS 수정
- 헤더 메뉴 추가 또는 Header Layout 변경

## 완료 기준

로그인 → 설문 입력 → 설정 저장 → 추천 결과 → 여행지 상세 흐름이 동작하고, 설문을 다시 제출하면 기존 설정이 수정되며 모든 자동 테스트가 통과합니다.
