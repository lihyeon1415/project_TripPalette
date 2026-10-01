# Phase 2 작업 배정

Phase 2의 목표는 비회원이 메인 페이지에서 여행지를 검색하고, 여행지 상세와 주변 숙소를 거쳐 숙소 상세까지 탐색할 수 있는 MVP를 완성하는 것입니다.

목표 완료일: `2026-09-23`

## 공통 기준

- 기준 브랜치: `develop`
- PR 대상: `TripPalette/project_TripPalette`의 `develop`
- 설계 기준: `docs/TripPalette-개발-사양서.md` 6.1~6.5
- CSS 기준: [`docs/TripPalette-CSS-가이드.md`](../TripPalette-CSS-가이드.md)
- 협업 기준: `CONTRIBUTING.md`
- 담당 파일 밖의 변경이 필요하면 먼저 팀장에게 알립니다.
- 페이지에 여행지나 숙소 데이터를 하드코딩하지 않고 View가 전달한 값을 사용합니다.
- 기능과 페이지 이동을 먼저 완성하고 시각 디자인은 마지막 통합 단계에서 다듬습니다.
- `.env`, API 키, DB 접속정보, 로컬 DB는 커밋하지 않습니다.

## 역할 배정

| 담당 | 역할 | 작업 문서 | 브랜치 |
|---|---|---|---|
| 팀장 | 백엔드·Seed·통합 | [01-team-lead-backend.md](01-team-lead-backend.md) | `kdk` |
| 프론트엔드 A | 여행지 목록·상세 | [02-frontend-destination.md](02-frontend-destination.md) | `feature/phase2-destination-ui` |
| 프론트엔드 B | 숙소 목록·상세·메인 점검 | [03-frontend-accommodation.md](03-frontend-accommodation.md) | `feature/phase2-accommodation-ui` |

실제 담당자 이름과 GitHub ID는 작업 시작 전에 각 문서의 `담당자` 항목에 기록합니다.

## 작업 시작

Fork를 사용하는 팀원은 원본 저장소를 `upstream`으로 등록한 상태에서 시작합니다.

```bash
git fetch upstream
git switch develop
git merge upstream/develop
git push origin develop
git switch -c <담당-브랜치>
```

팀장은 기존 `kdk` 브랜치를 최신 `develop`과 맞춥니다.

```bash
git switch kdk
git fetch origin
git merge origin/develop
```

## URL과 Template 계약

| 화면 | URL | Template | 핵심 변수 |
|---|---|---|---|
| 메인 | `GET /` | `main/index.html` | `hero_slides`, `popular_destinations` |
| 여행지 목록 | `GET /destinations` | `destination/list.html` | `destinations`, `filters`, `selected_filters`, `keyword` |
| 여행지 상세 | `GET /destinations/<id>` | `destination/detail.html` | `destination`, `reviews`, `accommodations` |
| 주변 숙소 | `GET /destinations/<id>/accommodations` | `accommodation/list.html` | `destination`, `accommodations` |
| 숙소 전체 목록 | `GET /accommodations` | `accommodation/list.html` | `destination`, `accommodations` |
| 숙소 상세 | `GET /accommodations/<id>` | `accommodation/detail.html` | `accommodation` |

검색과 필터는 GET Query String을 사용합니다.

```text
keyword
region
season
purpose
atmosphere
```

`budget_level`, `recommended_days`는 필수 기능을 완료한 후 추가할 수 있습니다.

## 파일 충돌 방지

- 팀장만 `app/views/*.py`, `seed.py`, 테스트 코드를 수정합니다.
- 프론트엔드 A만 여행지 Template과 여행지 전용 CSS·JS를 수정합니다.
- 프론트엔드 B만 숙소 Template, 숙소 전용 CSS·JS, 메인 전용 파일을 수정합니다.
- `base.html`, `style.css`, `common.js`는 기능 개발 중 수정하지 않습니다.
- 공통 레이아웃 변경은 두 프론트엔드 PR을 병합한 후 팀장이 최종 반영합니다.
- `models.py`와 Migration 변경이 필요하면 독립 작업으로 분리하고 팀장 승인을 받습니다.

## 디자인 적용 순서

1. Jinja 변수 출력과 링크 이동을 완성합니다.
2. 검색·필터와 빈 결과 화면을 연결합니다.
3. 여행지에서 주변 숙소로 이어지는 전체 흐름을 검증합니다.
4. 마지막으로 카드, 글꼴, 색상, 여백과 반응형을 통일합니다.

최종 공통 레이아웃 기준은 다음과 같습니다.

색상과 컴포넌트의 세부 기준은 [`TripPalette-CSS-가이드.md`](../TripPalette-CSS-가이드.md)를 따릅니다.

- 데스크톱 콘텐츠 최대 폭: `1200px`
- 데스크톱 기본 좌우 여백: `32px` 이상
- 태블릿 좌우 여백: `32px`
- 모바일 좌우 여백: `20px`
- 여행지·숙소 목록: 데스크톱 3열, 태블릿 2열, 모바일 1열
- 배경 영역은 전체 폭을 사용할 수 있지만 텍스트와 UI는 공통 컨테이너에 정렬

## 병합 순서

1. 팀장 백엔드와 Template 변수 계약 확정
2. 세 담당자가 각 브랜치에서 병렬 작업
3. 팀장 백엔드 PR 병합
4. 프론트엔드 A가 최신 `develop` 반영 후 검증·PR 병합
5. 프론트엔드 B가 최신 `develop` 반영 후 검증·PR 병합
6. 팀장이 공통 디자인과 전체 탐색 흐름 통합
7. `develop`에서 최종 검증 후 `main` 대상 Phase 2 PR 생성

## Phase 2 제외 범위

- 회원가입·로그인·로그아웃 처리
- 찜 저장과 해제
- 리뷰 작성·수정·삭제
- 맞춤 추천 계산
- 예약 생성
- 실제 결제 및 모의 결제
- 마이페이지 데이터 조회

리뷰는 여행지 상세에서 기존 리뷰를 조회하는 영역만 준비하며, 리뷰 작성은 Phase 3에서 구현합니다.

## Phase 2 완료 기준

```text
메인
→ 여행지 검색·필터
→ 여행지 목록
→ 여행지 상세
→ 주변 숙소 목록
→ 숙소 상세
```

- 위 흐름을 비회원으로 이동할 수 있습니다.
- 검색과 네 가지 필터를 조합할 수 있습니다.
- 데이터가 없을 때 빈 결과 화면이 표시됩니다.
- 존재하지 않는 여행지·숙소 ID는 404를 반환합니다.
- 모든 Template이 `base.html`을 상속합니다.
- 데스크톱·태블릿·모바일에서 가로 스크롤이 생기지 않습니다.
- 전체 GET 라우트와 정적 파일이 정상 응답합니다.
