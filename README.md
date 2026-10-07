# TripPalette

> 여행지를 발견하고, 숙소를 예약하고, 여행 굿즈까지 준비하는 국내 여행 큐레이션 플랫폼

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.4-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-linux%2Famd64-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?logo=render&logoColor=black)](https://trippalette-web.onrender.com)

## 바로가기

- 배포 서비스: [https://trippalette-web.onrender.com](https://trippalette-web.onrender.com)
- 개발 로드맵: [Roadmap.md](Roadmap.md)
- 팀 협업 규칙: [CONTRIBUTING.md](CONTRIBUTING.md)
- Docker·배포 가이드: [docs/docker-deployment-guide.md](docs/docker-deployment-guide.md)
- Migration·Seed 동기화: [docs/final-sync-guide-2026-10-06.md](docs/final-sync-guide-2026-10-06.md)

> Render Free 서비스는 일정 시간 요청이 없으면 휴면 상태가 되므로 첫 접속이 늦을 수 있습니다. 결제는 토스페이먼츠 테스트 환경만 사용하며 실제 금액은 청구되지 않습니다.

---

## 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 개발 기간 | 2026.09.18 ~ 2026.10.07 |
| 구성 | 3인 팀 프로젝트 |
| 담당 역할 | 팀장 · 백엔드 · 데이터 모델링 · 기능 통합 · 배포 |
| 서비스 | 여행지 탐색·추천, 숙소 예약, 여행 굿즈 주문 |
| Backend | Python 3.12, Flask, SQLAlchemy, Flask-Migrate |
| Frontend | Jinja2, HTML5, CSS3, JavaScript |
| Database | Aiven MySQL 8.4, TLS 연결 |
| Payment | 토스페이먼츠 SDK V2·승인 API 테스트 환경 |
| Deployment | Docker Hub → Render Web Service |

TripPalette는 숙소부터 검색하는 방식에서 벗어나 사용자가 자신의 취향에 맞는 **여행지를 먼저 발견**하도록 설계했습니다. 여행지 탐색과 추천에서 숙소 예약으로 이어지고, 같은 서비스 안에서 여행 굿즈도 주문할 수 있습니다.

운영 데이터는 외부 API를 런타임에 호출하지 않고 검수된 JSON Seed를 MySQL에 반영합니다. 회원·찜·리뷰·장바구니·예약·주문·결제 데이터는 공용 Aiven MySQL에 저장되므로 배포된 서비스의 사용자들이 같은 리뷰와 상품 재고를 공유합니다.

---

## 해결하고자 한 문제

- 여행지를 정하지 못한 사용자는 숙소 검색부터 시작하기 어렵습니다.
- 여행지 추천, 숙소 예약, 여행 준비 상품 구매가 서로 분리되어 있습니다.
- 예약과 상품 주문은 같은 결제 흐름을 사용하지만 재고와 날짜 점유 규칙은 서로 다릅니다.
- 팀 개발에서는 스키마와 기본 데이터가 각 PC마다 달라지기 쉽습니다.

TripPalette는 이를 다음과 같이 해결했습니다.

1. 조건 기반 여행지 추천과 탐색을 출발점으로 구성했습니다.
2. 여행지 → 주변 숙소 → 예약 → 결제를 하나의 흐름으로 연결했습니다.
3. 굿즈 카탈로그·장바구니·배송지·주문 기능을 같은 회원 영역에 통합했습니다.
4. 숙소와 굿즈가 공통 `Payment` 모델과 결제 위젯을 사용하도록 구성했습니다.
5. Migration과 멱등 Seed를 분리해 모든 환경의 스키마와 기준 데이터를 재현할 수 있게 했습니다.

---

## 서비스 흐름

```text
여행 흐름
메인 → 여행지 검색·필터 → 여행지 상세 → 주변 숙소 → 숙소 상세
     → 예약 생성(PAYMENT_PENDING) → 결제 승인 → 예약 확정(CONFIRMED)

굿즈 흐름
굿즈 목록 → 상품 상세 → 바로 구매 또는 장바구니 → 배송지 입력
         → 주문 생성(PAYMENT_PENDING) → 결제 승인 → 주문 완료(PAID)
```

```mermaid
flowchart TD
    HOME[메인] --> DEST[여행지 탐색]
    HOME --> REC[맞춤 추천]
    DEST --> DEST_DETAIL[여행지 상세]
    REC --> DEST_DETAIL
    DEST_DETAIL --> STAY[주변 숙소]
    STAY --> RESERVE[예약·결제]
    HOME --> GOODS[굿즈]
    GOODS --> CART[장바구니·배송지]
    CART --> PAY[주문·결제]
    RESERVE --> MY[마이페이지]
    PAY --> MY
```

---

## 주요 기능

### 여행지 탐색과 추천

- 여행지 이름 검색과 지역·계절·목적·분위기 필터
- 69개 여행지와 252개 숙소 Seed 데이터
- 여행지 상세 갤러리, 찜, 평점·리뷰, 주변 숙소 연결
- 계절·동행·목적·분위기·예산·기간을 반영한 설명 가능한 추천
- 조건이 부족할 때 대체 추천 제공

### 숙소와 예약

- 숙소 목록·상세·이미지 갤러리
- 숙소 평점·리뷰 작성과 마이페이지 삭제
- 날짜·인원·중복 예약 검증과 서버 측 금액 계산
- 예약 생성 후 10분간 결제 대기
- 결제 성공 시 `CONFIRMED`, 실패·만료 시 날짜 점유 해제
- 예약 내역 조회와 결제 완료 후 취소 처리

### 굿즈와 장바구니

- 여행소품·일상소품·문구/기록 카테고리와 상품 15개
- 상품 상세, 바로 구매, 장바구니 수량 변경·선택 삭제
- 바로 구매와 장바구니가 공유하는 배송지 입력 모달
- 서버에서 가격·배송비·재고를 다시 계산하여 변조 차단
- 주문 생성 시 재고 임시 차감, 실패·만료·취소 시 한 번만 복구
- 주문 내역·상세·취소, 만료·취소 항목 숨김

### 인증과 마이페이지

- 이메일 회원가입·로그인·로그아웃
- 가입 이메일 찾기와 비밀번호 재설정
- 로그인 후 원래 페이지로 안전하게 복귀
- 회원별 찜·리뷰·예약·장바구니·주문 데이터 분리
- 프로필 수정과 유예기간 기반 회원탈퇴·철회
- 탈퇴 시 거래 기록은 유지하고 회원 연결·배송 개인정보를 정리

### 토스페이먼츠 테스트 결제

- SDK V2 결제창과 서버 승인·조회·취소 API 연결
- 숙소 예약과 굿즈 주문의 공통 결제 프레임
- 서버 저장 금액과 콜백 금액 비교
- 소유권 검증, 중복 승인 차단, Idempotency Key 적용
- `test_` 키만 허용하며 `live_` 키 또는 비테스트 모드로 실행 차단

---

## 시스템 구조

```mermaid
flowchart LR
    U[Browser] -->|HTTPS| R[Render Web Service]
    R --> F[Flask / Gunicorn]
    F --> J[Jinja2 · CSS · JavaScript]
    F --> S[Service Layer]
    S -->|SQLAlchemy + verified TLS| A[(Aiven MySQL)]
    S -->|SDK V2 · Confirm/Cancel API| T[Toss Payments Test]
    D[Docker Hub<br/>linux/amd64 image] --> R
    M[Alembic Migration] --> A
    E[Idempotent JSON Seed] --> A
```

### 배포 구성

| 구성 | 적용 내용 |
|---|---|
| Docker | `python:3.12-slim-bookworm`, 비루트 사용자, Gunicorn |
| Image | `docker.io/wellerman114/trippalette-flask:main-e43941b` |
| Web | Render Free, Singapore, `https://trippalette-web.onrender.com` |
| DB | Aiven MySQL 8.4, CA 체인·호스트 이름 검증 |
| Secret | Render 환경변수와 `/etc/secrets/aiven-ca.pem` Secret File |
| Release | `feature → develop → main → Docker Hub → Render` |

---

## 핵심 설계와 문제 해결

### 1. 예약과 상품 주문의 공통 결제 모델

`Payment`가 `Reservation` 또는 `GoodsOrder` 중 정확히 하나만 참조하도록 DB 제약과 서비스 검증을 적용했습니다. 결제 준비·승인·실패·취소는 공통 서비스에서 처리하고, 성공 이후의 상태 변경만 대상별로 분기했습니다.

### 2. 결제 대기 중 자원 점유와 복구

- 예약은 10분 동안 날짜를 임시 점유합니다.
- 굿즈 주문은 생성 트랜잭션에서 상품 행을 잠그고 재고를 차감합니다.
- 실패·만료·취소 시 예약 날짜 또는 상품 재고를 해제합니다.
- 상태 전이를 검사하여 새로고침이나 중복 콜백으로 재고가 두 번 복구되지 않게 했습니다.

### 3. 서버 중심의 결제 보안

브라우저가 보낸 상품명·가격·결제 금액을 신뢰하지 않습니다. 상품과 숙소 가격은 DB에서 다시 조회하고 결제 승인 직전에 저장 금액과 토스 콜백 금액을 비교합니다. 결제 키는 서버에서만 사용하며 로그와 템플릿에 노출하지 않습니다.

### 4. 재현 가능한 DB 동기화

- `migrations/`: 테이블·컬럼·제약조건의 버전 관리
- `seed.py`: 여행지·숙소·상품 기준 데이터의 멱등 Upsert
- Seed 제외: 회원, 찜, 리뷰, 장바구니, 예약, 주문, 결제, 배송지

현재 Migration head는 `b4e8c1a7d930`입니다.

### 5. 안전한 공용 MySQL 연결

Aiven 접속값을 개별 환경변수로 받아 비밀번호 URL 인코딩 문제를 없앴습니다. Aiven 연결에는 CA 파일을 필수로 요구하며 인증서 체인과 서버 호스트 이름을 모두 검증합니다. 인증서나 경로가 잘못되면 애플리케이션 시작 단계에서 실패합니다.

### 6. 이미지 품질을 유지한 배포 최적화

PNG 327개를 `oxipng --nx`로 무손실 재압축하고 디코딩된 픽셀을 전수 비교했습니다.

- 정적 PNG: `843,970,575` → `783,754,223` bytes
- 절감량: `60,216,352` bytes (`7.13%`)
- 픽셀 검증: `327/327`, 불일치 `0`

---

## 데이터 모델

총 15개 SQLAlchemy 모델을 사용합니다.

| 영역 | 모델 |
|---|---|
| 회원·추천 | `User`, `UserPreference` |
| 여행지 | `Destination`, `Favorite`, `Review` |
| 숙소 | `Accommodation`, `AccommodationReview`, `Reservation` |
| 굿즈 | `Product`, `ProductCategory`, `ProductImage`, `CartItem` |
| 주문·결제 | `GoodsOrder`, `GoodsOrderItem`, `Payment` |

```mermaid
erDiagram
    USER ||--o| USER_PREFERENCE : has
    USER ||--o{ FAVORITE : saves
    DESTINATION ||--o{ FAVORITE : receives
    USER ||--o{ REVIEW : writes
    DESTINATION ||--o{ REVIEW : receives
    DESTINATION ||--o{ ACCOMMODATION : contains
    USER ||--o{ ACCOMMODATION_REVIEW : writes
    ACCOMMODATION ||--o{ ACCOMMODATION_REVIEW : receives
    USER ||--o{ RESERVATION : creates
    ACCOMMODATION ||--o{ RESERVATION : booked
    USER ||--o{ CART_ITEM : owns
    PRODUCT ||--o{ CART_ITEM : contained
    PRODUCT ||--o{ PRODUCT_CATEGORY : classified
    PRODUCT ||--o{ PRODUCT_IMAGE : shows
    USER ||--o{ GOODS_ORDER : creates
    GOODS_ORDER ||--|{ GOODS_ORDER_ITEM : contains
    PRODUCT ||--o{ GOODS_ORDER_ITEM : snapshots
    RESERVATION ||--o| PAYMENT : paid_by
    GOODS_ORDER ||--o| PAYMENT : paid_by
```

---

## 담당 작업

팀장으로서 백엔드 구현뿐 아니라 작업 분배, 인터페이스 계약, PR 통합, 릴리스와 배포까지 담당했습니다.

| Phase | 담당 내용 |
|---|---|
| Phase 0 | Organization 저장소와 브랜치 전략 수립, PR 규칙·보안 기준·협업 문서 작성 |
| Phase 1 | SQLAlchemy 모델·제약조건 설계, 초기 Migration, Seed 구조, Blueprint 통합 |
| Phase 2 | 여행지·숙소 DB 조회, 검색·필터·상세 라우트, Seed와 프론트엔드 데이터 계약 통합 |
| Phase 3 | 인증·세션·회원 기능 백엔드, 사용자별 찜·리뷰·마이페이지 분리, 자동 테스트 |
| Phase 4 | 맞춤 추천 로직·결과 설명·테스트 전담, 여행지·숙소 UI 작업 통합과 회귀 수정 |
| Phase 5 | 예약·굿즈·장바구니·배송지·주문·재고·만료 처리, 토스 테스트 결제 공통화 |
| Phase 6 | 전역 UI 통합, 106개 회귀 테스트, PNG 무손실 최적화, Docker·Aiven·Render 배포 |

GitHub 작업은 기능 브랜치를 `develop`에 검증·병합하고, 검증된 `develop`만 `main`으로 승격하는 방식으로 진행했습니다. 충돌 수정과 팀원 결과물의 실제 데이터 연결도 팀장 통합 단계에서 처리했습니다.

---

## 구현 규모와 검증

| 항목 | 결과 |
|---|---:|
| SQLAlchemy 모델 | 15개 |
| 애플리케이션 라우트 | 49개 |
| Jinja 템플릿 | 32개 |
| 여행지 Seed | 69개 |
| 숙소 Seed | 252개 |
| 굿즈 Seed | 15개 |
| PNG 정적 자산 | 327개 |
| 자동 테스트 | 106개 통과 |
| Migration head | `b4e8c1a7d930` |

테스트 범위는 인증, 사용자별 권한, 추천, 여행지·숙소 리뷰, 예약, 굿즈, 장바구니, 재고, 결제 승인·실패·취소, 회원탈퇴, DB·결제 설정을 포함합니다. 외부 토스 API는 자동 테스트에서 Mock 처리합니다.

```powershell
python -m unittest discover -s tests -q
# Ran 106 tests
# OK
```

배포 후 `/`, `/goods`, `/goods/1`, `/destinations`, `/auth/login`, `/auth/signup`을 확인했으며 모두 HTTP 200으로 응답했습니다.

---

## 프로젝트 구조

```text
TripPalette/
├── app/
│   ├── data/                 # 여행지·숙소·상품 JSON Seed
│   ├── services/             # 결제·굿즈 주문 도메인 서비스
│   ├── static/               # CSS, JavaScript, 로컬 이미지
│   ├── templates/            # 화면 및 공통 결제·배송지 컴포넌트
│   ├── views/                # 11개 Blueprint 모듈
│   ├── account_deletion.py
│   ├── models.py
│   └── recommendation_service.py
├── migrations/              # Alembic 스키마 이력
├── tests/                   # unittest 자동 테스트
├── docs/                    # 설계·협업·배포 문서
├── config.py
├── seed.py
├── gunicorn.conf.py
├── Dockerfile
└── run.py
```

---

## 로컬 실행

### 1. 설치

```powershell
git clone https://github.com/TripPalette/project_TripPalette.git
cd project_TripPalette
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### 2. 환경변수

로컬 MySQL은 `DATABASE_URL`을 사용할 수 있습니다.

```dotenv
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=로컬용_랜덤값
DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/trippalette?charset=utf8mb4
TOSS_CLIENT_KEY=test_로_시작하는_클라이언트_키
TOSS_SECRET_KEY=test_로_시작하는_시크릿_키
TOSS_PAYMENT_MODE=test
```

Aiven은 `DATABASE_URL`을 비우고 `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_SSL_CA`를 설정합니다. 실제 `.env`, DB 비밀번호, 토스 키, CA 인증서는 Git에 커밋하지 않습니다.

### 3. DB와 실행

```powershell
python -m flask db upgrade
python seed.py
python -m flask db current
python -m unittest discover -s tests -q
python -m flask run
```

기존 Migration을 사용하므로 `flask db init`이나 임의의 `flask db migrate`를 실행하지 않습니다. 공용 Aiven DB의 Migration과 Seed는 대표자 한 명만 수행합니다.

---

## 현재 제한과 다음 단계

- 토스페이먼츠 테스트 환경만 지원하며 실제 결제는 차단되어 있습니다.
- Render Free의 휴면 전환으로 첫 요청에 지연이 생길 수 있습니다.
- 이메일·SMS 소유 인증과 소셜 로그인은 구현 범위에 포함하지 않았습니다.
- 상품 배송 상태 관리와 관리자 화면은 후속 작업입니다.
- PNG는 무손실 최적화까지만 적용했으며 WebP/AVIF·목록 썸네일 분리는 후속 성능 과제입니다.
- 실제 운영 전에는 유료 인프라, 백업·모니터링, 개인정보·전자상거래 정책 검토가 필요합니다.

---

## 관련 문서

- [개발 사양서](docs/TripPalette-개발-사양서.md)
- [CSS 디자인 가이드](docs/TripPalette-CSS-가이드.md)
- [굿즈·토스 테스트 결제 사양서](docs/phase5/2026-10-02-goods-and-toss-test-payment-backend-spec.md)
- [Seed 데이터 가이드](docs/seed-data-guide.md)
- [Aiven·Docker·Render 배포 가이드](docs/docker-deployment-guide.md)
