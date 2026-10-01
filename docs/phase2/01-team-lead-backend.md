# Phase 2 — 팀장: 탐색 백엔드·Seed·통합

담당자: 팀장 (`kdk`)

작업 브랜치: `kdk`

PR 대상: `develop`

## 작업 목표

개발용 JSON을 DB에 적재하고 SQLAlchemy로 메인, 여행지 검색·필터, 여행지 상세, 주변 숙소와 숙소 상세 데이터를 제공합니다. 두 프론트엔드 결과를 통합하여 비회원 탐색 흐름을 완성합니다.

## 작업 전 확인 문서

- `docs/TripPalette-개발-사양서.md` 6.1~6.5
- `docs/phase2/README.md`
- `docs/seed-data-guide.md`
- `README.md`의 URL·ERD·접근 권한 정책
- `CONTRIBUTING.md`

## 담당 파일

```text
app/views/main.py
app/views/destination.py
app/views/accommodation.py
seed.py
tests/test_phase2_routes.py
Roadmap.md
```

다음 공유 파일은 두 프론트엔드 PR 병합 후 최종 통합에서만 수정합니다.

```text
app/templates/base.html
app/static/css/style.css
app/static/js/common.js
```

`app/models.py`와 `migrations/`는 현재 스키마로 구현할 수 없는 문제가 확인되지 않는 한 수정하지 않습니다.

## 1. Seed 명령

루트의 `seed.py`에서 다음 순서로 데이터를 적재합니다.

1. `app/data/destinations.json` 읽기
2. 여행지명으로 중복 확인 후 `Destination` 저장
3. 저장된 여행지명과 ID 매핑 생성
4. `app/data/accommodations.json` 읽기
5. `destination_name`으로 FK 대상 조회 후 `Accommodation` 저장
6. Commit 후 여행지·숙소 개수 출력

필수 조건:

- 여러 번 실행해도 중복 데이터가 생기지 않아야 합니다.
- 필수 필드 누락이나 연결되지 않은 여행지명은 명확한 오류로 중단합니다.
- 실제 DB 비밀번호나 API 키를 코드에 넣지 않습니다.
- 이미지 배열 전체를 DB에 억지로 저장하지 않고 Phase 2에서는 대표 `image_url`을 사용합니다.

## 2. 메인 페이지 조회

현재 `app/views/main.py`의 JSON 직접 조회를 SQLAlchemy 조회로 교체합니다. 히어로 슬라이드는 프로젝트 정적 이미지의 파일명과 대체 텍스트를 View에서 전달합니다.

Template 계약:

```python
render_template(
    "main/index.html",
    hero_slides=hero_slides,
    popular_destinations=popular_destinations,
)
```

- 히어로 슬라이드는 Template에 반복해서 하드코딩하지 않습니다.
- 데이터가 전혀 없어도 HTTP 500이 발생하지 않아야 합니다.
- 인기 여행지는 최대 4개만 전달합니다.

## 3. 여행지 목록·검색·필터

URL:

```text
GET /destinations
```

Query String:

```text
keyword
region
season
purpose
atmosphere
```

검색 범위:

- 여행지명
- 지역
- 설명

필터 규칙:

- 값이 없는 조건은 쿼리에 적용하지 않습니다.
- 여러 조건은 AND로 조합합니다.
- 공백 검색어는 검색 조건에서 제외합니다.
- 잘못된 필터 값은 서버 오류를 내지 않고 결과 없음 또는 기본 목록으로 일관되게 처리합니다.
- 정렬 기준은 우선 `Destination.id ASC`로 고정합니다.

Template 계약:

```python
render_template(
    "destination/list.html",
    destinations=destinations,
    filters={
        "regions": regions,
        "seasons": seasons,
        "purposes": purposes,
        "atmospheres": atmospheres,
    },
    selected_filters=selected_filters,
    keyword=keyword,
)
```

## 4. 여행지 상세·주변 숙소

URL:

```text
GET /destinations/<int:id>
GET /destinations/<int:id>/accommodations
```

여행지 상세 Template 계약:

```python
render_template(
    "destination/detail.html",
    destination=destination,
    reviews=reviews,
    accommodations=accommodations,
)
```

- 존재하지 않는 여행지는 `404`를 반환합니다.
- 리뷰는 조회만 제공하고 작성 기능은 구현하지 않습니다.
- 상세 화면에는 주변 숙소 미리보기 또는 주변 숙소 목록 링크를 제공합니다.
- 주변 숙소 URL에서는 선택한 여행지에 속한 숙소만 조회합니다.

주변 숙소 Template 계약:

```python
render_template(
    "accommodation/list.html",
    destination=destination,
    accommodations=accommodations,
)
```

## 5. 숙소 목록·상세

URL:

```text
GET /accommodations
GET /accommodations/<int:id>
```

- `/accommodations`는 전체 숙소를 표시하되 `destination`에는 `None`을 전달할 수 있습니다.
- 숙소 상세에서 연결된 여행지를 함께 조회할 수 있어야 합니다.
- 존재하지 않는 숙소는 `404`를 반환합니다.

숙소 상세 Template 계약:

```python
render_template(
    "accommodation/detail.html",
    accommodation=accommodation,
)
```

## 6. 통합과 최종 디자인

두 프론트엔드 PR을 병합한 뒤에만 공유 레이아웃을 조정합니다.

- 공통 컨테이너 최대 폭 `1200px`
- 데스크톱 기본 좌우 여백 `32px` 이상
- 태블릿 `32px`, 모바일 `20px`
- 목록 화면 데스크톱 3열, 태블릿 2열, 모바일 1열
- Header, 본문, Footer의 좌우 정렬선 통일
- 375px 화면에서 가로 스크롤 금지

## 작업 순서

1. 프론트엔드에 Template 변수 계약을 공유합니다.
2. 멱등성 Seed 명령을 작성하고 DB에 데이터를 넣습니다.
3. 메인 페이지 조회를 ORM으로 전환합니다.
4. 여행지 검색·필터와 상세 조회를 구현합니다.
5. 주변 숙소와 숙소 상세 조회를 구현합니다.
6. 백엔드 테스트를 완료하고 PR을 먼저 병합합니다.
7. 두 프론트엔드 PR을 순서대로 통합합니다.
8. 마지막에 공통 디자인과 반응형을 통일합니다.
9. 전체 탐색 흐름을 검증하고 Roadmap을 갱신합니다.

## 금지사항

- 실제 결제 API 또는 실제 결제 처리
- 로그인 세션과 회원 기능 선행 구현
- 찜·리뷰 작성·예약 생성 구현
- JSON과 DB를 동시에 운영 데이터 원본으로 사용
- 프론트엔드 담당 파일을 사전 협의 없이 수정
- 필터마다 별도 URL 생성

## 완료 조건

- Seed 명령을 두 번 실행해도 데이터 개수가 증가하지 않습니다.
- 메인과 여행지·숙소 화면이 DB 데이터를 표시합니다.
- 검색 및 네 가지 필터가 단독·조합 조건으로 동작합니다.
- 여행지에서 연결된 숙소만 확인할 수 있습니다.
- 잘못된 여행지·숙소 ID가 404를 반환합니다.
- 전체 GET 라우트가 예상 상태 코드를 반환합니다.
- 프론트엔드 두 PR과 충돌 없이 통합됩니다.

## 테스트 예시

```powershell
.\venv\Scripts\Activate.ps1
python seed.py
python seed.py
flask routes
python -m unittest discover -s tests -v
flask run --port 5001
```

수동 확인 URL:

```text
/?keyword=제주
/destinations?keyword=바다
/destinations?region=강원특별자치도&season=겨울
/destinations/1
/destinations/1/accommodations
/accommodations/1
```

## 바이브 코딩용 프롬프트

```text
먼저 docs/TripPalette-개발-사양서.md 6.1~6.5,
docs/phase2/README.md와 docs/phase2/01-team-lead-backend.md를 읽어줘.

현재 작업은 Phase 2 여행지 탐색 백엔드와 통합이다.
JSON Seed를 멱등성 있게 DB에 적재하고, SQLAlchemy로 메인·여행지·숙소를 조회해줘.
여행지 검색과 region, season, purpose, atmosphere 필터를 GET Query String으로 구현해줘.
Template 변수 이름은 사양서의 계약을 그대로 지켜줘.

인증, 찜 저장, 리뷰 작성, 추천, 예약, 결제는 구현하지 마.
프론트엔드 Template과 전용 CSS는 수정하지 말고,
먼저 변경 파일과 쿼리 설계를 설명한 뒤 구현 및 테스트 결과를 정리해줘.
```
