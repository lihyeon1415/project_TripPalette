# 2026-09-30 여행지 상세·숙소 작업 브리핑

상태: 진행 중 — 여행지 상세 UI와 주변 숙소 인라인 전환 완료

작업 인원: 4명

## 오늘의 목표

여행지 상세 화면에서 주변 숙소 3곳을 즉시 확인하고, 각 카드에서 숙소 상세로 이동할 수 있게 한다. 기존 여행지별 주변 숙소 목록 페이지는 사용자 흐름에서 제거한다.

```text
여행지 상세
  └─ 주변 숙소 카드 3개
       └─ 숙소 상세
```

전역 숙소 목록 `/accommodations`와 숙소 상세 `/accommodations/<id>`는 유지한다. 기존 `/destinations/<id>/accommodations`는 북마크 호환을 위해 여행지 상세의 `#nearby-accommodations`로 리다이렉트한다.

## 현재 데이터 기준

- 여행지 42개
- 숙소 126개, 여행지별 3개
- 로컬 대표 이미지 연결 19개
- 대표 이미지 미연결 107개
- 오늘은 기존 `Accommodation.image_url`만 사용하므로 모델 및 Migration을 추가하지 않는다.
- 숙소별 다중 이미지 갤러리는 `AccommodationImage` 모델이 필요한 후속 작업으로 분리한다.

## 역할 배정

| 작업자 | 담당 | 신규 사진 목표 | 문서 | 상태 |
|---|---|---:|---|---|
| 작업자 1(통합 담당) | 여행지 상세·숙소 상세·라우팅·데이터 통합·테스트 | - | [01-ui-integration.md](01-ui-integration.md) | 진행 중 |
| 작업자 2(사진 A) | 담당 지역 숙소 사진 수집 및 출처 기록 | 35개 | [02-photo-collector-a.md](02-photo-collector-a.md) | 미착수 |
| 작업자 3(사진 B) | 담당 지역 숙소 사진 수집 및 출처 기록 | 36개 | [03-photo-collector-b.md](03-photo-collector-b.md) | 미착수 |
| 작업자 4(사진 C) | 담당 지역 숙소 사진 수집 및 출처 기록 | 36개 | [04-photo-collector-c.md](04-photo-collector-c.md) | 미착수 |

## 공통 데이터 계약

숙소 카드와 상세 화면에 표시할 정보는 다음으로 제한한다.

- 숙소 이름
- 대표 이미지
- 여행지명 또는 주소
- 1박 가격

오늘 범위에서 평점, 수용 인원, 임의 후기, 예약 및 결제 기능은 추가하지 않는다.

사진 경로는 아래 규칙을 사용한다.

```text
app/static/img/accommodation/{여행지명}/{숙소명}/01.jpg
```

매핑 레코드는 숙소 ID 대신 `destination_name`과 `accommodation_name`으로 식별한다.

```json
{
  "destination_name": "강릉",
  "accommodation_name": "숙소 이름",
  "image_url": "/static/img/accommodation/강릉/숙소 이름/01.jpg",
  "source_url": "원본 출처 URL"
}
```

## 충돌 방지 규칙

- 사진 담당자는 `app/data/accommodations.json`, `seed.py`, View, Template, CSS를 수정하지 않는다.
- 사진 담당자는 자신의 이미지 폴더와 자신의 `photo-map-*.json`만 커밋한다.
- 통합 담당자만 세 매핑 파일을 검수하고 `accommodations.json`에 반영한다.
- 외부 URL을 `image_url`에 직접 저장하지 않는다.
- 실제 숙소인지 확인되지 않은 사진과 워터마크 이미지는 사용하지 않는다.
- 공통 파일 수정이 필요하면 먼저 통합 담당자에게 알린다.

## 권장 브랜치

```text
작업자 1: feature/destination-stay-inline
작업자 2: assets/accommodation-images-a
작업자 3: assets/accommodation-images-b
작업자 4: assets/accommodation-images-c
```

## 병합 순서

1. 사진 A 브랜치를 통합 브랜치에 병합한다.
2. 사진 B 브랜치를 병합한다.
3. 사진 C 브랜치를 병합한다.
4. 통합 담당자가 세 매핑을 검수해 `accommodations.json`에 반영한다.
5. 여행지 상세 및 숙소 상세 UI를 완성한다.
6. `seed.py`가 로컬 이미지 경로를 DB에 보존하도록 수정한다.
7. 전체 테스트 및 반응형 화면을 검증한다.
8. 통합 브랜치를 `develop`에 PR로 병합한다.
9. 최종 검증 후 `develop → main`으로 승격한다.

## 전체 완료 조건

- 여행지 상세에서 주변 숙소 3개가 직접 표시된다.
- 주변 숙소 전용 페이지로 이동하는 버튼이 없다.
- 기존 주변 숙소 URL은 여행지 상세 숙소 섹션으로 리다이렉트된다.
- 숙소 카드에서 숙소 상세로 이동한다.
- 숙소 상세에서 대표 사진, 지역, 주소, 가격을 확인할 수 있다.
- 외부 이미지 URL이 화면에 출력되지 않는다.
- 이미지가 없거나 로드에 실패해도 placeholder가 표시된다.
- `python seed.py` 실행 뒤에도 로컬 이미지 경로가 유지된다.
- 모바일 1열, 태블릿 2열, 데스크톱 3열이 정상 표시된다.
- 전체 자동 테스트가 통과한다.

