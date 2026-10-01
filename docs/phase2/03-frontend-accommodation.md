# Phase 2 — 프론트엔드 B: 숙소 목록·상세·메인 점검

담당자: 배정 후 기록

작업 브랜치: `feature/phase2-accommodation-ui`

PR 대상: `develop`

## 작업 목표

선택한 여행지의 주변 숙소를 확인하고 숙소 상세로 이동할 수 있는 화면을 구현합니다. 기존 메인 페이지가 백엔드 데이터와 정상 연결되는지도 함께 점검합니다.

## 작업 전 확인 문서

- `docs/phase2/README.md`
- `docs/TripPalette-개발-사양서.md` 6.1, 6.4~6.5
- `app/models.py`의 `Destination`, `Accommodation`
- 현재 `main/index.html`, `main.css`, `base.html`

## 담당 파일

```text
app/templates/accommodation/list.html
app/templates/accommodation/detail.html
app/static/css/accommodation.css
app/static/js/accommodation.js
app/templates/main/index.html
app/static/css/main.css
```

JavaScript가 필요하지 않다면 `accommodation.js`는 만들지 않아도 됩니다.

다음 파일은 수정하지 않습니다.

```text
app/views/
app/models.py
migrations/
app/templates/base.html
app/static/css/style.css
app/templates/destination/
app/static/css/destination.css
```

## 1. 주변 숙소 목록

사용 변수:

```text
destination
accommodations
```

`destination`이 존재하면 선택한 여행지 기준의 제목을 표시합니다.

```text
제주 주변 숙소
경주 주변 숙소
```

`destination`이 `None`이면 전체 숙소 목록 제목을 표시합니다.

필수 구성:

- 연결된 여행지 상세로 돌아가기
- 페이지 제목과 안내 문구
- 숙소 결과 개수
- 숙소 카드 목록
- 숙소가 없을 때 Empty State

숙소 카드 표시 정보:

- 대표 이미지
- 숙소명
- 주소
- 1박 가격
- 평점
- 수용 가능 인원
- 숙소 상세 링크

가격 출력 예시:

```jinja2
{{ "{:,}".format(accommodation.price_per_night) }}원
```

예약 버튼, 결제 버튼, 객실 선택 Form은 Phase 5 기능이므로 구현하지 않습니다.

## 2. 숙소 상세

사용 변수:

```text
accommodation
```

`accommodation.destination` 관계를 이용하여 연결된 여행지 정보를 표시합니다.

필수 구성:

- 주변 숙소 목록으로 돌아가기
- 대표 이미지
- 숙소명
- 주소
- 상세 설명
- 1박 가격
- 수용 가능 인원
- 평점
- 연결된 여행지명과 여행지 상세 링크
- 예약 기능이 Phase 5에서 제공된다는 안내

숙소 리뷰는 현재 서비스 범위에 없으므로 별도 리뷰 영역을 만들지 않습니다.

## 3. 메인 페이지 점검

사용 변수:

```text
hero_slides
popular_destinations
```

현재 메인 페이지 구조를 유지하면서 다음만 확인합니다.

- 히어로 정적 이미지 목록이 View의 `hero_slides`로 출력되는지 확인
- 검색 Form이 `/destinations?keyword=...`를 생성하는지 확인
- 인기 여행지 카드가 최대 4개 출력되는지 확인
- 카드가 각 여행지 상세 페이지로 이동하는지 확인
- 데이터가 없을 때 Empty State가 표시되는지 확인
- 비회원 Header에 찜과 마이페이지가 나타나지 않는지 확인

메인 페이지에 새로운 기능이나 임의의 문구를 대량으로 추가하지 않습니다.

## 4. 이미지와 빈 값 처리

- `image_url`이 있을 때만 `<img>`를 출력합니다.
- 이미지가 없으면 공통 Placeholder 영역을 표시합니다.
- 이미지에 숙소명 또는 여행지명이 포함된 `alt`를 제공합니다.
- `rating`이 없으면 `평점 정보 없음`으로 표시합니다.
- 설명이 비어 있어도 `None` 문자열이 노출되지 않아야 합니다.
- 가격과 수용 인원은 숫자 단위를 명확하게 표시합니다.

## 5. 디자인 적용 순서

1. Jinja 변수 출력과 링크를 먼저 완성합니다.
2. 주변 숙소와 전체 숙소의 제목 분기를 확인합니다.
3. 백엔드 병합 후 실제 DB 데이터로 확인합니다.
4. 마지막에 숙소 및 메인 반응형 디자인을 조정합니다.

최종 레이아웃 기준:

- 콘텐츠 최대 폭 `1200px`
- 숙소 목록 데스크톱 3열, 태블릿 2열, 모바일 1열
- 카드 간격 약 `24px`
- 숙소 상세는 이미지와 정보의 2열 구조
- 상세 화면의 좌우 영역 간격 약 `40px`
- 모바일에서는 상세 영역을 1열로 전환
- 모바일 좌우 여백 `20px`

공통 컨테이너와 Header를 직접 변경하지 않고 공통 변경 의견은 PR 설명에 기록합니다.

## 접근성 기준

- 숙소 카드 전체가 링크인 경우 내부에 중복 링크를 만들지 않음
- 이미지에 의미 있는 `alt` 제공
- Heading 순서를 `h1 → h2 → h3`로 유지
- 가격·평점·인원 정보를 색상만으로 구분하지 않음
- 키보드 포커스가 카드와 링크에서 보이도록 유지

## 금지사항

- 숙소 데이터 하드코딩
- Python View와 모델 수정
- 예약 Form 또는 예약 생성 기능 구현
- 실제 결제 및 모의 결제 UI 구현
- 숙소 찜 기능 추가
- 숙소 리뷰 영역 추가
- `base.html`, 공통 CSS 또는 여행지 담당 파일 수정

## 완료 조건

- 주변 숙소 목록에 선택한 여행지의 숙소만 출력됩니다.
- 전체 숙소와 주변 숙소 제목이 올바르게 구분됩니다.
- 가격·평점·인원·주소가 정상 표시됩니다.
- 숙소 카드에서 상세로 이동할 수 있습니다.
- 숙소 상세에서 연결된 여행지로 돌아갈 수 있습니다.
- 데이터 없음과 이미지 없음 상태가 정상 표시됩니다.
- 메인 검색과 여행지 카드 링크가 정상 동작합니다.
- 375px에서 가로 스크롤이 발생하지 않습니다.

## 확인 명령

```powershell
.\venv\Scripts\Activate.ps1
flask run --port 5001
```

확인 URL:

```text
/
/destinations/1/accommodations
/accommodations
/accommodations/1
```

## 바이브 코딩용 프롬프트

```text
먼저 docs/phase2/README.md,
docs/phase2/03-frontend-accommodation.md와 현재 base.html을 읽어줘.

내 담당은 Phase 2 주변 숙소 목록, 숙소 상세와 메인 화면 점검이다.
View에서 전달하는 destination, accommodations, accommodation,
hero_slides, popular_destinations 변수만 사용해 Jinja 화면을 구현해줘.

Python, 모델, Migration, base.html, 공통 style.css와 여행지 담당 파일은 수정하지 마.
예약과 결제는 Phase 5이므로 구현하지 마.
먼저 데이터 출력과 링크를 연결하고 마지막에 1200px 컨테이너 기준으로 반응형 CSS를 정리해줘.
```
