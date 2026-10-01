# 작업자 2 — 여행지 상세 페이지 고도화

작업 브랜치: `hyh`

PR 대상: `develop`

상태: 완료

병합 이력: 원본 PR #36, `develop` 교정 PR #38, `main` 교정 PR #39

## 목표

이미 구현된 여행지 상세 데이터와 회원 기능을 유지하면서 사진·여행 정보·찜·리뷰·주변 숙소를 하나의 자연스러운 탐색 흐름으로 재구성합니다.

## 담당 파일

```text
app/templates/destination/detail.html
app/static/css/destination-detail.css    # 신규
```

기존 `destination.css`는 여행지 목록과 공유되므로 수정하지 않고 상세 전용 CSS를 추가합니다. `detail.html`에서 기존 CSS 다음에 상세 전용 CSS를 불러옵니다.

## 기존 URL과 Form 계약

| 기능 | Method | URL |
|---|---|---|
| 여행지 상세 | GET | `/destinations/<id>` |
| 찜 추가·해제 | POST | `/destinations/<id>/favorite` |
| 리뷰 작성 | POST | `/destinations/<id>/reviews` |
| 주변 숙소 | GET | `/destinations/<id>/accommodations` |

리뷰 Form 필드:

```text
rating     1~5 정수
content    공백이 아닌 리뷰 내용
```

## Template 변수 계약

```text
destination       여행지 정보
reviews           최신순 리뷰 목록
accommodations    주변 숙소 최대 3개
is_favorite       현재 회원의 찜 여부
can_review        현재 회원의 리뷰 작성 가능 여부
g.user            로그인 사용자 또는 None
destination_media 생성 이미지와 갤러리 정보
```

Python View와 변수명은 변경하지 않습니다.

## 화면 구성

### 1. 상단 Hero와 갤러리

- 여행지명, 지역, 소개를 사진 위 또는 인접 영역에 배치합니다.
- 생성 이미지가 있는 지역은 3장 갤러리를 유지합니다.
- 첫 이미지를 크게, 나머지 두 이미지를 보조 이미지로 구성합니다.
- 생성 이미지가 없으면 외부 요청 없이 여행지명 기반 Placeholder를 표시합니다.
- 이미지 실패 시 여행지명 기반 Placeholder가 표시되어야 합니다.

### 2. 여행 정보

다음 값이 있을 때만 카드 또는 태그로 표시합니다.

```text
season
purpose
atmosphere
budget_level
recommended_days
```

값이 없는 항목 때문에 빈 카드가 생기지 않아야 합니다.

### 3. 찜

- 회원은 `is_favorite`에 따라 `찜하기`와 `찜 해제` 상태를 구분합니다.
- 상태 변경은 반드시 POST Form을 사용합니다.
- 비회원은 로그인 링크를 표시하고 `next`에 현재 상세 경로를 전달합니다.
- JavaScript가 없어도 기능이 동작해야 합니다.

### 4. 리뷰

- 리뷰 작성자는 이름, 평점, 내용, 작성일을 확인할 수 있게 구성합니다.
- `g.user`가 있고 `can_review=True`일 때만 작성 Form을 표시합니다.
- 이미 리뷰를 작성한 회원에게 중복 작성 Form을 표시하지 않습니다.
- 비회원에게는 로그인 안내를 제공합니다.
- 리뷰가 없으면 명확한 Empty State를 표시합니다.

### 5. 주변 숙소

- `accommodations` 최대 3개를 카드로 표시합니다.
- 숙소명, 주소, 평점, 최대 인원, 1박 가격을 사용합니다.
- 카드는 `/accommodations/<id>` 상세로 이동합니다.
- 전체보기는 `/destinations/<id>/accommodations`로 이동합니다.
- 숙소가 없으면 준비 중 안내를 표시합니다.

## 반응형·접근성

- 최대 콘텐츠 폭은 1200px입니다.
- 데스크톱 갤러리 2열 구성을 모바일에서는 1열로 변경합니다.
- 375px에서 가로 스크롤이 없어야 합니다.
- 모든 이미지에 내용에 맞는 `alt`를 제공합니다.
- Form Control에는 Label 또는 접근 가능한 이름을 제공합니다.
- Heading 순서는 `h1 → h2 → h3`을 유지합니다.
- Hover 확대는 이미지 영역 안에서만 일어나고 Layout을 밀지 않아야 합니다.

## 현재 확인된 정리 항목

- Template 첫 줄 앞의 불필요한 `담` 문자를 제거합니다.
- 백엔드에서 이미 전달하는 찜·리뷰 작성 변수와 주변 숙소 3개를 화면에 연결합니다.
- 기존 생성 이미지 파일과 경로 이름을 변경하지 않습니다.

## 금지사항

- `app/views/destination.py`, 모델, Migration 수정
- 여행지 목록 화면 스타일 변경
- 숙소 찜·숙소 리뷰 기능 추가
- 리뷰 수정·삭제 기능 추가
- 임의 데이터 또는 이미지 URL 하드코딩
- Phase 4 추천 로직 또는 Phase 5 예약 기능 구현

## 완료 기준

비회원과 회원 상태에서 상세 화면이 정상 표시되고, 갤러리·여행 정보·찜·리뷰·주변 숙소 이동이 기존 백엔드 계약대로 동작하며 모바일 레이아웃이 깨지지 않습니다.
