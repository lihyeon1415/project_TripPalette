# 작업자 1 사양서 — 여행지 상세·숙소 상세 통합

상태: 진행 중 — 여행지 상세 UI·인라인 숙소·기존 경로 리다이렉트 완료, 숙소 상세 후속 작업 예정

역할: UI 구현, 라우팅 정리, 데이터 통합, 테스트 및 최종 병합

권장 브랜치: `feature/destination-stay-inline`

## 구현 목표

별도 주변 숙소 페이지를 거치지 않고 여행지 상세에서 해당 여행지의 숙소 3곳을 직접 확인하게 한다. 카드 선택 시 숙소 상세로 이동한다.

## 담당 파일

```text
app/views/destination.py
app/templates/destination/detail.html
app/templates/accommodation/detail.html
app/static/css/destination-detail.css
app/static/css/accommodation.css
app/data/accommodations.json
seed.py
tests/
```

필요한 경우 `app/templates/accommodation/list.html`은 전역 목록 동작을 보존하는 범위에서만 수정한다.

## 여행지 상세 요구사항

### View

- `destination.detail`에서 현재처럼 해당 여행지 숙소를 조회한다.
- 데이터에는 여행지별 숙소가 3개이므로 세 항목을 모두 전달한다.
- 숙소 정렬은 `Accommodation.id` 오름차순으로 고정한다.
- Template 계약은 `accommodations`를 유지한다.

### Template

- 기존 `주변 숙소 보기` 버튼을 제거한다.
- 섹션 ID를 `nearby-accommodations`로 지정한다.
- 숙소 3개를 카드로 직접 렌더링한다.
- 각 카드 전체를 `accommodation.detail`에 연결한다.
- 카드에는 대표 이미지, 숙소명, 여행지/주소, 1박 가격만 표시한다.
- 외부 이미지 URL은 렌더링하지 않고 `/static/`으로 시작하는 경로만 허용한다.
- 이미지가 없거나 로드 실패 시 공통 placeholder를 표시한다.
- 숙소가 없으면 빈 상태 문구만 표시하고 잘못된 버튼을 만들지 않는다.

### 반응형

```text
1200px 이상: 3열
768px 이상: 2열
767px 이하: 1열
```

## 기존 여행지별 숙소 페이지 처리

삭제 대상 사용자 흐름:

```text
/destinations/<id>/accommodations
```

해당 라우트를 즉시 404로 만들지 말고 다음 주소로 리다이렉트한다.

```text
/destinations/<id>#nearby-accommodations
```

다음 위치의 `destination.accommodations` 링크도 여행지 상세 앵커로 교체한다.

- 숙소 상세 breadcrumb
- `주변 숙소 전체 보기`
- `전체 N곳 보기`

전역 숙소 목록 `/accommodations`는 삭제하지 않는다.

## 숙소 상세 요구사항

첫 화면에서 다음 정보가 명확히 보여야 한다.

- 대표 이미지
- 숙소 이름
- 여행지명
- 주소
- 1박 가격
- 원래 여행지 상세로 돌아가는 링크

같은 여행지의 다른 숙소는 최대 2개만 하단에 표시한다. 표시 정보는 이미지, 이름, 지역, 가격으로 제한한다.

오늘 범위에서 제거하거나 추가하지 않을 항목:

- 임의 평점
- 임의 후기
- 예약 가능해 보이는 활성 버튼
- 결제 기능
- 존재하지 않는 이미지 API 호출
- 숙소 다중 이미지 슬라이더

## 사진 데이터 통합

사진 담당자의 다음 파일을 순서대로 검수한다.

```text
photo-map-a.json
photo-map-b.json
photo-map-c.json
```

검수 항목:

- `destination_name`이 현재 여행지 데이터와 일치하는가
- `accommodation_name`이 현재 숙소 데이터와 일치하는가
- `image_url` 파일이 실제 존재하는가
- 외부 URL이 아닌 `/static/` 경로인가
- 담당 영역이 중복되지 않았는가

검수 후에만 `app/data/accommodations.json`의 `image_url`을 갱신한다.

## Seed 필수 수정

현재 `seed.py`는 숙소 이미지 경로를 강제로 지운다.

```python
accommodation.image_url = None
```

이를 JSON의 로컬 이미지 경로만 보존하도록 변경한다. 외부 URL은 저장하지 않는다.

예상 정책:

```python
image_url = item.get("image_url") or None
accommodation.image_url = (
    image_url if image_url and image_url.startswith("/static/") else None
)
```

## 테스트 요구사항

- 여행지 상세 응답에 해당 여행지 숙소 3개가 표시된다.
- 여행지 상세에 `destination.accommodations` 링크가 남지 않는다.
- 기존 여행지별 숙소 URL은 `#nearby-accommodations`로 리다이렉트된다.
- 각 숙소 카드가 정확한 숙소 상세 URL을 가진다.
- 외부 이미지 URL은 목록과 상세 HTML에 출력되지 않는다.
- 로컬 이미지 URL은 정상 출력된다.
- 이미지가 없는 숙소는 placeholder를 표시한다.
- `seed.py` 실행 시 로컬 이미지 경로가 유지된다.
- 기존 로그인, 찜, 리뷰, 설문 테스트가 회귀하지 않는다.

## 완료 보고 형식

```text
- 수정 파일
- 제거한 기존 이동 경로
- 추가한 숙소 카드 동작
- 사진 연결 개수 / 누락 개수
- 테스트 실행 결과
- 남은 제한사항
```

