# 작업자 3 사양서 — 숙소 사진 수집 B

상태: 미착수

권장 브랜치: `assets/accommodation-images-b`

신규 수집 목표: 36개 숙소 대표 이미지

## 담당 지역

| 지역 | 전체 숙소 | 신규 수집 |
|---|---:|---:|
| 강릉 | 3 | 3 |
| 구례 | 3 | 3 |
| 단양 | 3 | 3 |
| 문경 | 3 | 3 |
| 부여 | 3 | 3 |
| 신안 | 3 | 3 |
| 양평 | 3 | 3 |
| 인제 | 3 | 3 |
| 제천 | 3 | 3 |
| 태백 | 3 | 3 |
| 평창 | 3 | 3 |
| 홍천 | 3 | 3 |

## 사진 기준

- 실제 숙소와 일치하는 대표 사진 1장
- 가로형, 최소 1200×800 권장
- JPG 또는 WebP, 가능하면 500KB 이하
- 워터마크, 가격표, 홍보 문구가 크게 박힌 사진 제외
- 사진을 확인할 수 없으면 임의 이미지 대신 `pending`으로 보고

## 저장 경로

```text
app/static/img/accommodation/{여행지명}/{숙소명}/01.jpg
```

## 매핑 산출물

```text
docs/phase4/2026-09-30-accommodation-inline/photo-map-b.json
```

레코드 형식:

```json
{
  "destination_name": "강릉",
  "accommodation_name": "숙소 이름",
  "image_url": "/static/img/accommodation/강릉/숙소 이름/01.jpg",
  "source_url": "원본 출처 URL",
  "status": "ready"
}
```

`app/data/accommodations.json`은 수정하지 않는다.

## 완료 조건

- 신규 대상 36개 전부 처리 또는 미확보 항목을 `pending`으로 명시
- 모든 `ready` 경로에 실제 파일 존재
- 숙소명과 사진 대상이 일치
- 출처 URL 누락 없음
- 담당 지역 밖 파일 수정 없음

