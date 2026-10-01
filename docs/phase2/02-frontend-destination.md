# Phase 2 — 프론트엔드 A: 여행지 목록·상세

담당자: 배정 후 기록

작업 브랜치: `feature/phase2-destination-ui`

PR 대상: `develop`

## 작업 목표

비회원이 여행지를 검색·필터링하고 여행지 상세정보와 기존 리뷰를 확인한 뒤 주변 숙소로 이동할 수 있는 화면을 구현합니다.

## 작업 전 확인 문서

- `docs/phase2/README.md`
- `docs/TripPalette-개발-사양서.md` 6.2~6.3
- `app/models.py`의 `Destination`, `Review`
- 현재 `base.html`과 `style.css`

## 담당 파일

```text
app/templates/destination/list.html
app/templates/destination/detail.html
app/static/css/destination.css
app/static/js/destination.js
```

JavaScript가 필요하지 않다면 `destination.js`는 만들지 않아도 됩니다. 검색과 필터는 기본 HTML GET Form으로 동작해야 합니다.

다음 파일은 수정하지 않습니다.

```text
app/views/
app/models.py
migrations/
app/templates/base.html
app/static/css/style.css
app/templates/accommodation/
app/static/css/accommodation.css
```

## 1. 여행지 목록

사용 변수:

```text
destinations
filters.regions
filters.seasons
filters.purposes
filters.atmospheres
selected_filters
keyword
```

필수 구성:

- 페이지 제목과 안내 문구
- 검색어 입력창
- 지역 Select
- 계절 Select
- 여행 목적 Select
- 분위기 Select
- 검색·필터 적용 버튼
- 필터 초기화 링크
- 검색 결과 개수
- 여행지 카드 목록
- 검색 결과가 없을 때 Empty State

Form 기준:

```html
<form action="{{ url_for('destination.list') }}" method="get">
```

입력 이름:

```text
keyword
region
season
purpose
atmosphere
```

필터 적용 후 선택값과 검색어가 화면에 유지되어야 합니다.

여행지 카드 표시 정보:

- 대표 이미지
- 여행지명
- 지역
- 한 줄 설명
- 계절
- 목적 또는 분위기
- 상세 페이지 링크

데이터 예시를 HTML에 직접 작성하지 않고 `{% for destination in destinations %}`로 출력합니다.

## 2. 여행지 상세

사용 변수:

```text
destination
reviews
accommodations
```

필수 구성:

- 여행지 목록으로 돌아가기
- 대표 이미지
- 여행지명과 지역
- 설명
- 추천 계절
- 여행 목적
- 분위기
- 예산 수준
- 추천 여행 기간
- 기존 리뷰 목록 또는 리뷰 없음 안내
- 주변 숙소 미리보기 또는 `주변 숙소 보기` 버튼

주변 숙소 링크:

```jinja2
{{ url_for('destination.accommodations', id=destination.id) }}
```

리뷰 작성 Form, 찜 버튼과 찜 개수는 Phase 3 기능이므로 구현하지 않습니다.

## 3. 이미지와 빈 값 처리

- `image_url`이 있을 때만 `<img>`를 출력합니다.
- 이미지가 없으면 공통 Placeholder 영역을 표시합니다.
- 모든 이미지에 의미 있는 `alt`를 작성합니다.
- 설명이나 선택 필드가 비어 있어도 `None`이 화면에 표시되지 않게 합니다.
- 리뷰가 없으면 오류가 아니라 안내 문구를 표시합니다.

## 4. 디자인 적용 순서

1. Jinja 반복문과 조건문을 먼저 완성합니다.
2. 검색·필터 값 유지와 링크를 확인합니다.
3. 백엔드 병합 후 실제 DB 데이터로 검증합니다.
4. 마지막에 `destination.css`로 카드와 반응형을 적용합니다.

최종 레이아웃 기준:

- 콘텐츠 최대 폭 `1200px`
- 목록 데스크톱 3열, 태블릿 2열, 모바일 1열
- 카드 간격 약 `24px`
- 모바일 좌우 여백 `20px`
- 목록과 상세 화면의 제목 시작선 통일
- 긴 설명은 카드에서 2~3줄로 제한

공통 컨테이너 자체를 바꾸지 말고 페이지 전용 CSS만 작성합니다. 공통 변경 의견은 PR 설명에 기록합니다.

## 접근성 기준

- 검색 Input에 `<label>` 제공
- Select마다 연결된 Label 제공
- 현재 선택값을 색상만으로 구분하지 않음
- 키보드로 모든 링크와 버튼 접근 가능
- Heading 순서를 `h1 → h2 → h3`로 유지
- 장식 아이콘은 `aria-hidden="true"` 처리

## 금지사항

- 여행지와 리뷰 데이터 하드코딩
- Python View와 모델 수정
- 찜 기능 구현 또는 하트 버튼 표시
- 리뷰 작성 Form 구현
- 인증 여부를 임의로 처리
- CDN UI 프레임워크 추가
- `base.html` 또는 공통 CSS 수정

## 완료 조건

- 여행지 목록이 View의 데이터 개수만큼 출력됩니다.
- 검색·필터 Form이 정확한 Query String을 생성합니다.
- 선택한 검색어와 필터가 요청 후에도 유지됩니다.
- 상세 링크와 주변 숙소 링크가 정확합니다.
- 빈 여행지 목록과 빈 리뷰 상태가 정상적으로 표시됩니다.
- Jinja 오류 없이 목록·상세가 HTTP 200을 반환합니다.
- 375px에서 가로 스크롤이 발생하지 않습니다.

## 확인 명령

```powershell
.\venv\Scripts\Activate.ps1
flask run --port 5001
```

확인 URL:

```text
/destinations
/destinations?keyword=제주
/destinations?region=제주특별자치도&season=봄
/destinations/1
```

## 바이브 코딩용 프롬프트

```text
먼저 docs/phase2/README.md,
docs/phase2/02-frontend-destination.md와 현재 base.html을 읽어줘.

내 담당은 Phase 2 여행지 목록과 상세 프론트엔드다.
View에서 전달하는 destinations, filters, selected_filters, keyword,
destination, reviews, accommodations 변수만 사용해 Jinja 화면을 구현해줘.
검색과 필터는 GET Form으로 만들고 선택값을 유지해줘.

Python, 모델, Migration, base.html, 공통 style.css와 숙소 파일은 수정하지 마.
찜과 리뷰 작성은 Phase 3이므로 구현하지 마.
먼저 화면 구조를 설명하고 기능 연결 후 마지막에 반응형 CSS를 적용해줘.
```
