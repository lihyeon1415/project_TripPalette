# Phase 5 백엔드 사양서 — 굿즈 주문·장바구니와 토스페이먼츠 테스트 결제

작성일: 2026-10-02
최종 갱신일: 2026-10-07
상태: 구현·자동 테스트·배포 완료
대상 DB: MySQL
결제 환경: 토스페이먼츠 테스트 환경 전용

> 안전 경계: 이 Phase에서는 `test_` 접두사의 테스트 키만 허용한다. 라이브 키, 실제 승인, 실제 출금으로 전환하는 설정과 코드는 구현 범위에서 제외한다.

## 1. 목표와 범위

TripPalette에 숙소 예약 결제와 굿즈 주문 결제를 하나의 결제 서비스로 연결한다. 초기 사양은 바로 구매만 포함했으나 구현 과정에서 회원별 장바구니와 선택 상품 일괄 주문을 추가했고, 굿즈 찜은 만들지 않았다.

```text
숙소 예약 → 결제 → 예약 확정 → 마이페이지 숙소 예약
굿즈 상세 → 바로 구매 또는 장바구니 → 배송지 → 결제 → 마이페이지 굿즈 주문
```

이번 문서는 모델, Migration, Seed, URL, 서버 검증, 토스 테스트 승인·취소, 마이페이지 연결 계약만 정의한다. 프론트엔드 Template·CSS·JavaScript는 팀원의 이미지 초안이 확정된 뒤 구현한다.

### 포함

- 굿즈 목록·상세 조회 백엔드
- 한 상품의 수량을 선택하는 바로 구매
- 주문 당시 상품명·단가 스냅샷
- 수령인·연락처·우편번호·주소·배송 요청사항
- 숙소와 굿즈의 토스페이먼츠 테스트 결제
- 서버 금액 재계산, 성공·실패·취소 상태 저장
- 마이페이지의 숙소 예약·굿즈 주문 조회
- 접근 권한, 중복 승인, 재고 복구 테스트

### 제외

- 굿즈 찜
- 쿠폰·포인트·복합 할인
- 실제 배송사 API·운송장 추적
- 관리자 상품 관리 화면
- 라이브 키와 실제 출금
- 비회원 구매, 정기 결제, 가상계좌, 웹훅

1차 구현은 로그인 회원의 카드 중심 일회성 테스트 결제로 제한한다.

### 테스트 결제의 의미

이번 구현에서 말하는 `결제 URL 테스트`는 고정된 상품 결제 링크를 발급하는 기능이 아니다. 서버가 결제 대기 데이터를 만든 뒤 브라우저에서 토스 테스트 결제창을 열고, 인증 결과가 아래 URL로 돌아오는 흐름을 뜻한다.

```text
TripPalette 결제 화면
→ 토스 테스트 결제창
→ 성공: /payments/success?paymentKey=...&orderId=...&amount=...
→ 실패: /payments/fail?code=...&message=...&orderId=...
```

성공 URL로 돌아온 뒤 테스트 승인 API까지 호출하여 애플리케이션의 예약·주문 상태를 검증한다. 테스트 키를 사용하므로 승인 결과가 성공이어도 실제 카드나 계좌에서 돈은 빠져나가지 않는다.

토스의 별도 `결제 링크` 상품이나 외부에 공유하는 영구 결제 URL은 이번 범위에 포함하지 않는다.

## 2. 현재 구조 검토

현재 프로젝트에는 Flask Blueprint, SQLAlchemy, Flask-Migrate, MySQL, 회원·숙소·예약 모델, 예약 취소와 마이페이지 예약 내역이 있다. `Payment`는 `reservation_id`가 필수인 숙소 전용 1:1 모델이며 `/reservations/<id>/payment`는 실제 승인 API가 없는 안내 화면이다.

따라서 예약과 굿즈 주문 도메인은 분리하고 결제 승인·취소 서비스만 공통으로 사용한다.

## 3. 권장 파일 구조

```text
app/
├─ data/products.json                       # 신규, 굿즈 기준 데이터
├─ services/
│  ├─ __init__.py                           # 신규
│  └─ toss_payment_service.py               # 신규, 외부 승인·취소 API
├─ views/
│  ├─ goods.py                              # 신규, 목록·상세·구매 준비
│  ├─ order.py                              # 신규, 배송지·주문 생성·취소
│  ├─ payment.py                            # 신규, 성공·실패·승인 공통 처리
│  ├─ reservation.py                        # 수정, 결제 전 예약 생성
│  └─ mypage.py                             # 수정, 예약·주문 내역
├─ templates/goods/                         # 디자인 확정 후 구현
├─ templates/order/                         # 디자인 확정 후 구현
├─ templates/payment/                       # 디자인 확정 후 구현
├─ static/js/toss-payment.js                # 디자인 확정 후 구현
├─ models.py                                # 모델 추가·Payment 확장
└─ __init__.py                              # Blueprint 등록

migrations/versions/
└─ <revision>_add_goods_orders_and_toss_payment.py

tests/
├─ test_goods.py
├─ test_goods_order.py
├─ test_payment_flow.py
└─ test_account_withdrawal.py               # 신규 관계 반영
```

## 4. 데이터 모델

### 4.1 User 변경

| 컬럼 | 형식 | 조건 | 용도 |
|---|---|---|---|
| `payment_customer_key` | `VARCHAR(64)` | NULL 허용, UNIQUE | 토스 회원 식별용 무작위 키 |

- 최초 결제 준비 시 UUID 기반 값을 생성해 저장한다.
- 이메일, 전화번호, 자동 증가 `user.id`를 `customerKey`로 사용하지 않는다.
- 브라우저가 전달한 `customerKey`는 신뢰하지 않는다.

### 4.2 Product 신규

테이블명: `product`

| 컬럼 | 형식 | 조건 |
|---|---|---|
| `id` | `INT` | PK |
| `sku` | `VARCHAR(50)` | NOT NULL, UNIQUE |
| `name` | `VARCHAR(120)` | NOT NULL |
| `description` | `TEXT` | NULL 허용 |
| `price` | `INT` | NOT NULL, 0 이상 |
| `stock_quantity` | `INT` | NOT NULL, 0 이상 |
| `thumbnail_url` | `VARCHAR(255)` | NULL 허용 |
| `is_active` | `BOOLEAN` | NOT NULL, 기본값 TRUE |
| `created_at` | `DATETIME` | NOT NULL |
| `updated_at` | `DATETIME` | NULL 허용 |

- 금액은 원 단위 정수로 저장한다.
- 판매 종료 상품은 삭제하지 않고 `is_active = false`로 바꾼다.
- `sku`를 Seed Upsert 식별자로 사용한다.

### 4.3 ProductImage 신규

테이블명: `product_image`

| 컬럼 | 형식 | 조건 |
|---|---|---|
| `id` | `INT` | PK |
| `product_id` | `INT` | FK, NOT NULL |
| `image_url` | `VARCHAR(255)` | NOT NULL |
| `sort_order` | `INT` | NOT NULL, 기본값 0 |

`(product_id, sort_order)`에 UNIQUE 제약조건을 둔다.

### 4.4 GoodsOrder 신규

SQL 예약어와 혼동하지 않도록 클래스명은 `GoodsOrder`, 테이블명은 `goods_order`로 한다.

| 컬럼 | 형식 | 조건 |
|---|---|---|
| `id` | `INT` | PK |
| `order_number` | `VARCHAR(64)` | NOT NULL, UNIQUE |
| `user_id` | `INT` | FK, NULL 허용 |
| `recipient_name` | `VARCHAR(50)` | NOT NULL |
| `recipient_phone` | `VARCHAR(20)` | NOT NULL |
| `postal_code` | `VARCHAR(10)` | NOT NULL |
| `address` | `VARCHAR(255)` | NOT NULL |
| `address_detail` | `VARCHAR(255)` | NULL 허용 |
| `delivery_request` | `VARCHAR(255)` | NULL 허용 |
| `items_amount` | `INT` | NOT NULL, 0 이상 |
| `shipping_fee` | `INT` | NOT NULL, 0 이상 |
| `total_amount` | `INT` | NOT NULL, 0 이상 |
| `status` | `VARCHAR(30)` | NOT NULL |
| `expires_at` | `DATETIME` | NOT NULL |
| `created_at` | `DATETIME` | NOT NULL |
| `paid_at` | `DATETIME` | NULL 허용 |
| `cancelled_at` | `DATETIME` | NULL 허용 |

상태:

```text
PAYMENT_PENDING, PAID, PAYMENT_FAILED, PREPARING, SHIPPED,
DELIVERED, CANCELLED, REFUNDED, EXPIRED
```

배송 주소는 회원정보를 참조하지 않고 주문 시점의 값으로 저장한다. 회원정보 변경이 과거 주문 주소를 바꾸면 안 된다.

회원탈퇴가 확정되면 완료·취소·환불·실패·만료 주문은 거래 기록을 보존하되 `user_id` 연결과 수령인·연락처·배송지 정보를 익명화한다. 결제·배송 진행 중 주문이 있으면 영구 삭제를 보류한다.

### 4.5 GoodsOrderItem 신규

테이블명: `goods_order_item`

| 컬럼 | 형식 | 조건 |
|---|---|---|
| `id` | `INT` | PK |
| `goods_order_id` | `INT` | FK, NOT NULL |
| `product_id` | `INT` | FK, NOT NULL |
| `product_name` | `VARCHAR(120)` | NOT NULL |
| `sku` | `VARCHAR(50)` | NOT NULL |
| `unit_price` | `INT` | NOT NULL, 0 이상 |
| `quantity` | `INT` | NOT NULL, 1 이상 |
| `subtotal` | `INT` | NOT NULL, 0 이상 |

현재는 주문당 상품 한 종류만 허용한다. 그래도 주문 당시 이름·가격 보존을 위해 항목 테이블을 두며 서버가 `subtotal = unit_price × quantity`를 계산한다.

### 4.6 Reservation 변경

| 신규 컬럼 | 형식 | 조건 | 용도 |
|---|---|---|---|
| `expires_at` | `DATETIME` | NULL 허용 | 결제 대기 예약 만료 시각 |

상태:

```text
PAYMENT_PENDING, CONFIRMED, PAYMENT_FAILED, CANCELLED, REFUNDED, EXPIRED
```

- 예약 생성 직후 완료 화면으로 보내지 않는다.
- `PAYMENT_PENDING`으로 생성하고 결제 페이지로 이동한다.
- 결제 대기 시간은 기본 10분이다.
- 만료되지 않은 `PAYMENT_PENDING`과 `CONFIRMED`만 중복 예약 검사 대상이다.
- 승인 성공 뒤에만 `CONFIRMED`가 된다.

### 4.7 Payment 변경

기존 `payment` 테이블을 공통 결제 기록으로 확장한다.

| 컬럼 | 변경 내용 |
|---|---|
| `reservation_id` | NULL 허용, 기존 UNIQUE 유지 |
| `goods_order_id` | 신규 FK, NULL 허용, UNIQUE |
| `merchant_order_id` | 신규 `VARCHAR(64)`, UNIQUE |
| `provider` | 신규 `VARCHAR(20)`, 기본값 `TOSS` |
| `payment_key` | 신규 `VARCHAR(200)`, NULL 허용, UNIQUE |
| `payment_method` | 승인 전 NULL 허용 |
| `payment_status` | 기존 컬럼을 공통 상태로 사용 |
| `requested_at` | 신규 `DATETIME`, NOT NULL |
| `paid_at` | 기존 컬럼 유지 |
| `cancelled_at` | 신규 `DATETIME`, NULL 허용 |
| `failure_code` | 신규 `VARCHAR(100)`, NULL 허용 |
| `failure_message` | 신규 `VARCHAR(255)`, NULL 허용 |
| `idempotency_key` | 신규 `VARCHAR(64)`, NULL 허용, UNIQUE |

상태:

```text
READY, AUTHENTICATED, DONE, FAILED, CANCELLED, PARTIAL_CANCELLED, EXPIRED
```

무결성 규칙:

- `reservation_id`와 `goods_order_id` 중 정확히 하나만 존재한다.
- Payment 금액은 연결된 예약 또는 주문의 서버 계산 금액과 같아야 한다.
- `merchant_order_id`는 토스의 `orderId`와 동일하게 사용한다.
- 기존 개발 DB의 Payment 행을 고려해 신규 문자열 컬럼은 Migration에서 우선 NULL을 허용하지만 신규 결제 로직은 필수로 채운다.

## 5. 관계 구조

```text
User 1 ─ N Reservation 1 ─ 0..1 Payment
User 1 ─ N GoodsOrder  1 ─ 0..1 Payment
Product 1 ─ N ProductImage
GoodsOrder 1 ─ N GoodsOrderItem N ─ 1 Product
```

Payment는 예약 또는 굿즈 주문 중 한 종류에만 연결한다. 승인 결과와 대상 상태는 같은 DB 트랜잭션에서 갱신한다.

## 6. URL 계약

### 굿즈

| Method | URL | 기능 | 권한 |
|---|---|---|---|
| GET | `/goods` | 판매 중 상품 목록 | 전체 |
| GET | `/goods/<int:product_id>` | 상품 상세 | 전체 |
| GET | `/goods/<int:product_id>/checkout` | 수량·배송지 주문서 | 회원 |
| POST | `/goods/<int:product_id>/orders` | 결제 대기 주문 생성 | 회원 |

### 숙소 예약

| Method | URL | 기능 | 권한 |
|---|---|---|---|
| GET, POST | `/reservations/new/<int:accommodation_id>` | 예약 입력·검증 | 회원 |
| GET | `/reservations/<int:id>/payment` | 예약 결제 페이지 | 예약자 |
| GET | `/reservations/<int:id>/complete` | 결제 완료 예약 표시 | 예약자 |
| POST | `/reservations/<int:id>/cancel` | 결제 취소 후 예약 취소 | 예약자 |

### 공통 결제

| Method | URL | 기능 | 권한 |
|---|---|---|---|
| GET | `/payments/<int:payment_id>` | 결제 화면 데이터 | 결제 소유자 |
| GET | `/payments/success` | 인증값 검증·승인 API | 로그인 회원 |
| GET | `/payments/fail` | 인증 실패 반영 | 로그인 회원 |
| POST | `/payments/<int:payment_id>/cancel` | 테스트 결제 취소 | 결제 소유자 |

### 마이페이지

| Method | URL | 기능 | 권한 |
|---|---|---|---|
| GET | `/mypage/reservations` | 숙소 예약 내역 | 회원 |
| GET | `/mypage/orders` | 굿즈 주문 내역 | 회원 |
| GET | `/mypage/orders/<int:order_id>` | 주문·배송·결제 상세 | 주문자 |

마이페이지 메뉴명은 `예약·주문 내역`으로 표시하고 내부에 `숙소 예약`, `굿즈 주문` 탭을 둔다. 기존 예약 URL은 유지한다.

## 7. 토스페이먼츠 테스트 결제 계약

### 적용 방식

- 신규 연동은 JavaScript SDK V2를 사용한다.
- SDK URL은 `https://js.tosspayments.com/v2/standard`이다.
- 별도 요구가 없으므로 주문서에 결제수단 UI를 표시하는 주문서형 결제를 기본으로 한다.
- `widgets()` → `setAmount()` → `renderPaymentMethods()`·`renderAgreement()` → `requestPayment()` 순서로 처리한다.
- 인증 성공 뒤 서버가 승인 API를 호출해야 결제가 완료된다.
- 2024년 자료의 `결제위젯`은 현재 주문서형·결제창형으로 나뉘므로 구버전과 V2를 섞지 않는다.
- `successUrl`과 `failUrl`은 Flask가 `url_for(..., _external=True)`로 생성한 절대 URL을 사용한다.
- 로컬 테스트에서는 현재 실행 주소를 기준으로 `http://127.0.0.1:5000/payments/success`와 `/payments/fail` 형태가 된다.
- 서버가 임의의 토스 결제 URL을 만들어 반환하지 않는다. 결제창 이동과 리다이렉트는 토스 SDK가 담당한다.

### 환경변수

실제 값은 `.env`에만 저장한다.

```dotenv
TOSS_CLIENT_KEY=your_test_client_key
TOSS_SECRET_KEY=your_test_secret_key
TOSS_API_BASE_URL=https://api.tosspayments.com
TOSS_PAYMENT_MODE=test
PAYMENT_PENDING_MINUTES=10
```

`.env.example`에는 이름과 빈 예시만 추가한다. 시크릿 키는 Template, JavaScript, 응답, 로그에 포함하지 않는다. 클라이언트 키만 결제 화면에 전달한다. 사용자가 제공한 문서용 키 문자열도 소스와 사양서에는 복사하지 않는다.

테스트 전용 안전장치:

- 앱 시작 또는 결제 서비스 초기화 시 클라이언트 키와 시크릿 키가 모두 `test_`로 시작하는지 검사한다.
- `TOSS_PAYMENT_MODE`가 `test`가 아니면 결제 요청을 거부한다.
- `live_` 키 또는 `test_`로 시작하지 않는 키가 감지되면 서버 시작 단계에서 명확한 설정 오류를 발생시킨다.
- 라이브 전환용 우회 플래그나 설정값은 이번 Phase에서 만들지 않는다.
- 테스트 환경 여부는 서버 설정과 키 검증으로 강제하며 내부 환경 문구를 결제 UI에 노출하지 않는다.

### 식별자

- 토스 `orderId`는 서버가 생성하고 영문·숫자·`-`, `_`만 사용하며 6~64자 범위로 만든다.
- 예약은 `RES-<UUID>`, 굿즈는 `GOODS-<UUID>` 접두사를 사용한다.
- `customerKey`는 회원별 무작위 UUID 기반 값을 사용한다.

### 결제 준비

서버는 다음 값을 먼저 DB에 저장한 뒤 화면에 제공한다.

```text
payment_id, merchant_order_id, order_name, amount, customer_key,
client_key, success_url, fail_url
```

금액은 상품 DB 또는 숙소 DB를 기준으로 서버가 계산한다.

### 성공 처리

`successUrl`은 `paymentKey`, `orderId`, `amount`를 받는다.

1. 현재 회원이 Payment의 실제 소유자인지 확인한다.
2. `orderId`와 DB의 `merchant_order_id`가 같은지 확인한다.
3. URL 금액과 DB 금액을 비교한다.
4. 승인 API에는 URL 값을 신뢰하지 않고 DB 금액을 사용한다.
5. 서버가 토스 결제 승인 API를 호출한다.
6. HTTP 200과 결제 상태를 확인한다.
7. 한 DB 트랜잭션에서 Payment와 연결 대상을 갱신한다.
8. 예약은 `CONFIRMED`, 굿즈 주문은 `PAID`로 바꾼다.
9. 완료 화면으로 이동한다.

승인 POST에는 UUID 기반 `Idempotency-Key`를 사용하고 DB에 저장해 새로고침과 중복 콜백을 막는다.

### 실패 처리

- `failUrl`은 `code`, `message`, `orderId`를 받는다.
- 실패 URL에서는 승인 API를 호출하지 않는다.
- 소유권과 주문번호를 확인한다.
- Payment와 연결 대상을 `FAILED`/`PAYMENT_FAILED`로 바꾼다.
- 외부 오류 메시지는 그대로 HTML에 출력하지 않는다.
- 사용자가 같은 주문을 다시 결제할 수 있는 경로를 제공한다.

### 취소 처리

1. 소유권과 현재 상태 확인
2. 서버에서 토스 결제 취소 API 호출
3. 성공 응답 확인
4. Payment를 `CANCELLED` 또는 `PARTIAL_CANCELLED`로 변경
5. 예약을 `CANCELLED`, 굿즈 주문을 `CANCELLED` 또는 `REFUNDED`로 변경
6. 굿즈 재고 복구

취소 API가 실패하면 DB의 결제 완료 상태를 유지한다.

## 8. 업무 흐름

### 숙소 예약

```text
숙소 상세 → 날짜·인원 입력 → 서버 검증
→ Reservation(PAYMENT_PENDING, expires_at)
→ Payment(READY) → 토스 테스트 인증 → 서버 승인
→ Payment(DONE) + Reservation(CONFIRMED)
→ 예약 완료 → 마이페이지 숙소 예약
```

- 숙박 금액은 `price_per_night × 숙박일수`로 서버가 계산한다.
- 만료된 대기 예약은 날짜를 점유하지 않는다.
- 완료·취소된 결제의 성공 URL 재접근은 중복 승인하지 않는다.

### 굿즈 바로 구매

```text
상품 상세 → 바로 구매 → 수량·배송지 입력 → 서버 검증
→ GoodsOrder(PAYMENT_PENDING) + GoodsOrderItem 스냅샷
→ Payment(READY) → 토스 테스트 인증 → 서버 승인
→ Payment(DONE) + GoodsOrder(PAID)
→ 주문 완료 → 마이페이지 굿즈 주문
```

검증 규칙:

- 수량은 1~10개이다.
- 활성 상품이며 요청 수량 이하의 재고가 있어야 한다.
- 폼의 상품명·가격·총액은 무시하고 DB로 다시 계산한다.
- 수령인, 전화번호, 우편번호, 기본 주소는 필수다.
- 전화번호와 우편번호는 문자열로 저장하고 서버에서 형식을 검증한다.

재고 정책:

- 주문 생성 시 상품 행을 잠그고 재고를 임시 차감한다.
- 결제 실패·취소·만료 시 수량을 복구한다.
- 결제 성공 시 확보된 재고를 확정한다.
- 상태 전이를 확인해 같은 주문의 재고를 두 번 복구하지 않는다.

## 9. Seed 정책

### Seed 대상

`app/data/products.json`을 추가하고 상품 기준 데이터만 관리한다.

```json
[
  {
    "sku": "PALLY-KEYRING-001",
    "name": "팰리 여행 키링",
    "description": "상품 설명",
    "price": 12000,
    "stock_quantity": 30,
    "thumbnail_url": "img/goods/pally-keyring/main.png",
    "images": [
      "img/goods/pally-keyring/main.png",
      "img/goods/pally-keyring/detail-1.png"
    ],
    "is_active": true
  }
]
```

상품은 `sku` 기준으로 Upsert한다. 팀원이 확정한 상품명·가격·재고·이미지 경로를 이 규격으로 전달한다.

### Seed 제외 대상

다음은 실제 사용자 거래 데이터이므로 Seed가 생성하거나 덮어쓰지 않는다.

- GoodsOrder, GoodsOrderItem, Payment, Reservation, 배송지

### 팀원 실행 원칙

```powershell
python -m flask db upgrade
python seed.py
```

- `db upgrade`는 테이블과 컬럼을 반영한다.
- `seed.py`는 여행지·숙소·상품 기준 데이터를 Upsert한다.
- Migration만 바뀌고 JSON이 바뀌지 않았다면 Seed는 필수가 아니다.
- 상품 JSON이 추가·변경된 Pull에서는 Seed를 한 번 실행한다.
- 반복 실행은 허용하지만 앱 실행 때마다 자동 Seed하지 않는다.
- 현재 Seed는 JSON에서 빠진 행을 DB에서 자동 삭제하지 않는다. 상품 중단은 `is_active: false`로 표현한다.

## 10. Migration 계획

### 예상 파일 수: 1개

이번 변경은 한 담당자가 같은 브랜치에서 하나의 기능 단위로 구현하므로 다음 Migration 하나에 묶는다.

```text
<revision>_add_goods_orders_and_toss_payment.py
```

포함 내용:

1. `user.payment_customer_key`
2. `product`
3. `product_image`
4. `goods_order`
5. `goods_order_item`
6. `reservation.expires_at`
7. `payment` 공통 결제 컬럼 및 NULL 조건 변경
8. FK, UNIQUE, CHECK, INDEX

모델 개수와 Migration 파일 개수는 같지 않으므로 위 변경을 한 파일에서 처리할 수 있다.

두 파일 이상이 필요한 예외:

- 운영 데이터 때문에 Payment 백필과 NOT NULL 전환을 나눌 때
- 첫 Migration 배포 후 추가 스키마 변경이 생겼을 때
- 여러 브랜치에서 Migration을 동시에 생성해 Revision 충돌이 생겼을 때

현재 개발용 MySQL과 기존 Payment 사용량 기준으로는 1개가 적절하다. Migration은 여러 팀원이 동시에 만들지 않는다.

### MySQL 검토 항목

- 현재 MySQL 버전에서 CHECK가 실제 적용되는지 확인한다.
- 생성 순서를 `product → product_image → goods_order → goods_order_item → payment 변경`으로 맞춘다.
- `payment_key`, `merchant_order_id`, `order_number`, `sku`에 인덱스를 둔다.
- 기존 Payment 행 때문에 Upgrade가 실패하지 않도록 신규 결제 식별자는 우선 NULL 허용한다.
- `downgrade()`는 FK와 인덱스를 먼저 제거한다.
- `flask db migrate` 결과를 그대로 사용하지 않고 수동 검토한다.

## 11. 결제 서비스 계약

`app/services/toss_payment_service.py`는 외부 HTTP 통신만 담당하고 Flask View나 DB 모델을 직접 변경하지 않는다.

```python
confirm_payment(payment_key, order_id, amount, idempotency_key)
cancel_payment(payment_key, cancel_reason, idempotency_key)
get_payment(payment_key)
```

필수 처리:

- 시크릿 키 Basic 인증
- 요청 제한시간
- 네트워크·JSON 파싱 오류
- 토스 오류 코드와 사용자 메시지 분리
- 카드정보·인증 헤더 로그 금지
- 테스트 API URL 사용

`requests`를 사용하면 `requirements.txt`에 버전을 고정한다.

## 12. 보안·무결성

- 결제·주문·예약 Route에 `login_required`를 적용한다.
- ID뿐 아니라 `user_id == g.user.id`를 확인한다.
- 모든 금액은 서버에서 계산한다.
- 성공 URL 금액과 DB 금액이 다르면 승인하지 않는다.
- 시크릿 키는 서버에서만 사용한다.
- 승인·취소는 중복 호출에 안전해야 한다.
- POST Form에는 CSRF 보호를 적용한다.
- 현재 Flask-WTF는 설치되어 있지만 전역 CSRF 초기화가 확인되지 않으므로 구현 시 기존 모든 POST Form과 테스트의 영향을 함께 처리한다.
- 배송 주소와 전화번호를 로그에 남기지 않는다.

## 13. 회원탈퇴 연동

현재 `account_deletion.py`는 Payment와 Reservation을 직접 정리하므로 GoodsOrder 추가 시 수정해야 한다.

- 결제 대기·결제 완료·상품 준비·배송 중 주문은 영구 삭제 전에 처리 상태를 확인한다.
- 배송 완료·취소 주문은 수령인·연락처·주소를 익명화한 뒤 회원을 삭제한다.
- Payment → GoodsOrderItem → GoodsOrder 순서로 정리한다.
- 계정 삭제 테스트에 굿즈 주문·결제를 추가한다.

실서비스 전환 시 거래기록 보존과 개인정보 정책은 별도 법률 검토가 필요하다.

## 14. 자동 테스트

### 상품·Seed

- 판매 중 상품만 표시
- 없는 상품 404, 비활성 상품 구매 차단
- Seed 재실행 시 중복 상품·이미지 없음

### 굿즈 주문

- 비회원 차단, 다른 회원 주문 접근 404
- 수량 0·음수·10개 초과·재고 초과 차단
- 클라이언트 가격 변조 무시
- 배송 필수값 검증
- 실패·취소·만료 때 재고 한 번만 복구

### 숙소 결제

- 생성 후 `PAYMENT_PENDING`, 승인 후 `CONFIRMED`
- 금액 불일치 승인 차단
- 만료 예약 날짜 점유 해제
- 다른 회원 결제 접근 404

### 공통 결제

- 승인 성공·실패·네트워크 예외 Mock
- 동일 성공 URL 재호출 시 중복 승인 없음
- 실패 URL에서 승인 API를 호출하지 않음
- 취소 성공 후 상태 변경·취소 실패 시 기존 상태 유지
- 예약 Payment와 굿즈 Payment 대상 분리

자동 테스트는 실제 토스 서버를 호출하지 않고 HTTP 응답을 Mock한다. 수동 통합 테스트에서만 테스트 키를 사용한다.

## 15. 프론트엔드 전달 계약

디자인 확정 전에도 백엔드는 다음 Template 변수를 보장한다.

```text
상품 상세:
  product, product_images, can_purchase

굿즈 주문서:
  product, quantity, unit_price, items_amount,
  shipping_fee, total_amount, form_data

결제 화면:
  payment, target, client_key, customer_key,
  order_name, success_url, fail_url

마이페이지 굿즈 주문:
  orders, active_tab
```

프론트엔드는 표시값을 바꿀 수 있지만 서버 결제 금액에는 영향을 줄 수 없다.

## 16. 구현 순서

진행 표시: `[x]` 완료, `[ ]` 미착수

### 1단계 — 테스트 환경 안전장치

1. [x] `.env.example`과 `Config`에 토스 테스트 설정 추가
2. [x] `test_` 키만 허용하는 검증 추가
3. [x] 라이브 키 거부 테스트 작성

### 2단계 — DB 기반

4. [x] 상품·주문 모델과 기존 Payment 확장
5. [x] Migration 1개 생성
6. [x] 기존 개발 MySQL DB에서 Upgrade/Downgrade/재Upgrade 검증

### 3단계 — 상품 기준 데이터

7. [ ] 팀원에게 상품 JSON 규격 공유
8. [x] `products.json` 추가
9. [x] `sku` 기준 멱등 Seed 확장 및 재실행 검증

### 4단계 — 도메인 백엔드

10. [x] 굿즈 목록·상세 조회
11. [x] 수량·배송지 검증과 바로 구매 주문 생성
12. [x] 재고 임시 차감·실패·만료 복구
13. [x] 숙소 예약을 결제 대기 흐름으로 변경

### 5단계 — 토스 테스트 결제

14. [x] 공통 결제 준비 데이터와 성공·실패 URL 생성
15. [x] 토스 승인·조회·취소 서비스 구현
16. [x] 성공 URL 금액·소유권 검증 후 테스트 승인
17. [x] 실패 URL과 재시도 처리
18. [x] 테스트 결제 취소와 상태·재고 복구

### 6단계 — 프로젝트 연결

19. [x] 마이페이지 예약·주문 조회 연결
20. [x] 회원탈퇴 정리 로직 수정
21. [x] 외부 API Mock 기반 자동 테스트

### 7단계 — 프론트엔드와 수동 검증

22. [x] 팀원 이미지 초안 기준 Template·CSS 구현
23. [x] SDK V2 JavaScript 연결
24. [x] 내부 테스트 환경 문구를 노출하지 않고 공통 결제 디자인 적용
25. [x] 문서용 테스트 키로 결제창 실행과 결제 콜백·승인 흐름 확인
26. [x] 현재 범위 전체 회귀 테스트

## 17. 완료 기준

- Migration 1개로 빈 MySQL DB와 기존 개발 DB가 Upgrade된다.
- `python seed.py` 재실행 시 상품이 중복되지 않는다.
- 상품 상세에서 바로 구매하거나 장바구니의 선택 상품을 한 번에 주문한다.
- 배송지와 주문 당시 상품 정보가 저장된다.
- 숙소와 굿즈가 같은 토스 결제 서비스를 사용한다.
- 테스트 승인 성공 시 숙소는 `CONFIRMED`, 굿즈는 `PAID`가 된다.
- 금액 변조, 다른 회원 접근, 중복 승인, 재고 중복 복구가 차단된다.
- 테스트 결제는 실제 출금되지 않는다.
- `live_` 키를 넣으면 결제 기능이 시작되지 않는다.
- 브라우저에서 토스 테스트 결제창이 열리고 성공·실패 URL로 복귀한다.
- 성공 URL에서 테스트 승인 API가 처리되어도 실제 청구는 발생하지 않는다.
- 마이페이지에서 숙소 예약과 굿즈 주문을 구분해 조회한다.
- 기존 테스트와 신규 테스트가 모두 통과한다.

## 18. 공식 참고 문서

- 토스페이먼츠 주문서형 결제 연동: https://docs.tosspayments.com/guides/v2/payment-widget/integration
- 토스페이먼츠 SDK V2 빠른 참조: https://docs.tosspayments.com/guides/v2/get-started/llms-quick-reference
- 토스페이먼츠 테스트 환경: https://docs.tosspayments.com/guides/v2/get-started/environment
