# Phase 4 작업 배정 — 3인 구성

> 2026-09-30 후속 4인 작업은 [여행지 상세·숙소 인라인 작업 브리핑](2026-09-30-accommodation-inline/README.md)을 기준으로 진행합니다.

상태: 전체 완료

최종 갱신일: 2026-10-07

> 이 문서는 Phase 4 당시의 작업 배정과 통합 계약을 기록한 문서입니다. 맞춤 추천, 여행지 상세, 숙소 목록·상세는 이후 통합·고도화까지 완료되어 `main`에 반영됐습니다.

Phase 4의 핵심 기능은 한 사람이 설문부터 추천 결과까지 전담합니다. 나머지 두 사람은 이미 데이터가 연결된 여행지 상세와 숙소 화면을 각각 고도화합니다. 세 작업은 담당 파일을 분리하여 동시에 진행합니다.

## 역할 배정

| 작업자 | 역할 | 작업 문서 | 브랜치 | 상태 |
|---|---|---|---|---|
| 작업자 1(팀장) | 맞춤 여행지 추천 전체·테스트·통합 | [01-recommendation-owner.md](01-recommendation-owner.md) | `kdk` | 완료 |
| 작업자 2 | 여행지 상세 페이지 고도화 | [02-destination-detail.md](02-destination-detail.md) | `hyh` | 완료 |
| 작업자 3 | 숙소 목록·상세 페이지 고도화 | [03-accommodation-pages.md](03-accommodation-pages.md) | `feature/accommodation-ui` | 완료 |

## 시작 조건

- 세 작업자 모두 최신 `develop`을 반영하고 작업을 시작합니다.
- 작업 시작 당시 맞춤 추천과 숙소 화면은 미착수였고, 여행지 상세는 PR #36 이후 PR #38·#39에서 기능 계약을 교정했습니다. 현재 세 작업은 모두 병합 완료 상태입니다.
- 모델, Migration, 공통 Layout 변경이 필요하면 구현 전에 팀장과 합의합니다.
- 공통 기준은 [`TripPalette-개발-사양서.md`](../TripPalette-개발-사양서.md)와 [`TripPalette-CSS-가이드.md`](../TripPalette-CSS-가이드.md)를 따릅니다.

## 공통 금지사항

- 담당자가 아닌 사람의 전용 파일 수정
- 실제 값이 포함된 `.env` 또는 API Key 커밋
- 새로운 모델이나 Migration 임의 추가
- 기존 URL, Form 필드명, Template 변수 임의 변경
- 맞춤 추천 접근 경로는 메인 CTA·마이페이지·푸터만 사용하며 헤더는 변경하지 않음
- Phase 5 예약·결제 기능 선행 구현
- 기능이 없는 버튼을 정상 동작하는 것처럼 표시
- 기존 메인·여행지 목록 디자인을 함께 수정하여 작업 범위 확대

## 파일 소유권

```text
작업자 1
  app/views/recommendation.py
  app/recommendation_service.py
  app/templates/recommendation/
  app/static/css/recommendation.css
  app/static/js/recommendation.js
  tests/test_phase4_recommendation.py

작업자 2
  app/templates/destination/detail.html
  app/static/css/destination-detail.css

작업자 3
  app/templates/accommodation/list.html
  app/templates/accommodation/detail.html
  app/static/css/accommodation.css
```

다음 공통 파일은 팀장만 수정합니다.

```text
app/templates/base.html
app/models.py
app/__init__.py
Roadmap.md
docs/phase4/
```

## 병합 순서

1. 각자 최신 `develop`에서 담당 브랜치를 준비합니다.
2. 작업자 2와 3은 기존 View 계약만 사용하여 화면을 구현합니다.
3. 작업자 1은 추천 백엔드·화면·테스트를 한 브랜치에서 완성합니다.
4. 여행지 상세 PR을 `develop`에 병합합니다.
5. 숙소 페이지 PR을 `develop`에 병합합니다.
6. 작업자 1이 최신 `develop`을 반영하고 추천 기능 PR을 병합합니다.
7. 전체 테스트와 비회원·회원 사용자 흐름을 통합 검증합니다.
8. 완료 항목만 `Roadmap.md`에서 체크합니다.
9. `develop → main` PR로 최종 승격합니다.

## 통합 완료 기준

- 회원이 설문을 저장하고 설명 가능한 여행지 추천을 받습니다.
- 여행지 상세에서 사진·정보·찜·리뷰·주변 숙소 흐름이 자연스럽게 이어집니다.
- 숙소 목록에서 상세로 이동하고 실제 DB 정보가 표시됩니다.
- 빈 데이터와 이미지 실패 상황에서도 레이아웃이 깨지지 않습니다.
- 375px 모바일부터 1200px 데스크톱까지 가로 스크롤이 없습니다.
- 기존 Phase 2·3 테스트와 새 Phase 4 테스트가 모두 통과합니다.
