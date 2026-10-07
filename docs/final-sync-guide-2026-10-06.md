# TripPalette 최종본 팀 동기화 가이드

최종 갱신일: 2026-10-07

## 최종본 구성

- 여행지 탐색·상세·추천
- 숙소 목록·상세·예약
- 회원가입·로그인·찜·리뷰·마이페이지
- 굿즈 상품·상세·장바구니·배송지·주문·주문 상세
- 숙소 예약과 굿즈 주문의 토스페이먼츠 테스트 결제
- 결제 대기 10분 만료와 재고·숙소 날짜 점유 복구
- 자동 테스트 106개
- Migration head: `b4e8c1a7d930`
- 최종 `main`: `e43941b` (PR #60)
- Docker Hub: `docker.io/wellerman114/trippalette-flask:main-e43941b`
- Render: <https://trippalette-web.onrender.com>
- Aiven MySQL 8.4 공용 DB와 검증된 TLS 연결

## GitHub 최종 반영 상태

굿즈·장바구니, Docker, Aiven TLS 작업은 각각 기능 브랜치에서 `develop`을 거쳐 `main`으로 승격했습니다.

1. PR #55: `feature/goods-cart-checkout` → `develop`
2. PR #57: `feature/docker-deployment` → `develop`
3. PR #59: `feature/aiven-tls` → `develop`
4. PR #60: `develop` → `main`

최종 `main` 커밋은 `e43941b`입니다. 이후 작업도 기능 브랜치를 `develop`에 병합하고, 검증된 `develop`만 `main`으로 승격합니다.

## 기존 팀원의 최종본 적용

Organization 저장소를 `origin`으로 사용하는 경우:

```powershell
git switch main
git fetch origin
git pull --ff-only origin main
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -q
python -m flask run
```

개인 Fork를 `origin`, Organization 저장소를 `upstream`으로 사용하는 경우:

```powershell
git switch main
git fetch upstream
git pull --ff-only upstream main
git push origin main
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -q
python -m flask run
```

GitHub 웹의 개인 Fork에서는 먼저 `Sync fork` → `Update branch`를 실행해도 됩니다.

개인 로컬 MySQL을 사용하는 경우에만 코드 업데이트 후 다음을 실행합니다.

```powershell
python -m flask db upgrade
python seed.py
python -m flask db current
```

공용 Aiven DB를 사용하는 경우 Migration과 Seed는 대표자가 한 번만 적용합니다. 팀원은 위 세 명령을 반복하지 않고 승인받은 `MYSQL_*` 환경변수와 CA 인증서로 접속합니다.

## 처음 받는 팀원

```powershell
git clone <본인의 Fork 또는 Organization 저장소 URL>
cd project_TripPalette
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

MySQL에 개발 DB를 한 번 생성합니다.

```sql
CREATE DATABASE trippalette
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

`.env`의 `DATABASE_URL`, `SECRET_KEY`를 자신의 로컬 환경에 맞게 수정한 뒤 실행합니다. 공용 Aiven을 사용하는 팀원은 `DATABASE_URL`을 비우고 승인받은 `MYSQL_*` 값과 `MYSQL_SSL_CA`를 설정합니다.

```powershell
python -m flask db upgrade
python seed.py
python -m flask db current
python -m unittest discover -s tests -q
python -m flask run
```

위 명령은 **개인 로컬 MySQL** 기준입니다. 공용 Aiven DB는 대표자가 이미 Migration과 Seed를 적용했으므로 팀원이 각자 `db upgrade`와 `seed.py`를 반복 실행하지 않습니다. 팀원은 애플리케이션 접속과 읽기·쓰기 동작만 검증합니다.

## 토스 테스트 결제 설정

결제 기능까지 확인하려면 각 팀원의 `.env`에 테스트 키를 설정합니다.

```env
TOSS_CLIENT_KEY=test_로_시작하는_클라이언트_키
TOSS_SECRET_KEY=test_로_시작하는_시크릿_키
TOSS_PAYMENT_MODE=test
```

- `.env`는 Git에 올리지 않습니다.
- `live_` 키는 애플리케이션이 거부합니다.
- 키를 설정하지 않아도 일반 페이지는 실행되지만 토스 결제창은 사용할 수 없습니다.

## Migration과 Seed의 역할

Migration은 테이블과 컬럼을 맞춥니다.

- `df817ec37b80`: 굿즈 주문과 공통 결제 구조
- `a91c2d47f6b3`: 장바구니 테이블
- `b4e8c1a7d930`: 만료·취소 주문내역 숨김 컬럼

Seed는 개발용 카탈로그 데이터를 맞춥니다.

- 여행지
- 숙소
- 상품 15개
- 상품 가격과 재고
- 상품 카테고리와 이미지 경로

회원·찜·리뷰·장바구니·예약·주문·결제·배송지는 Seed 대상이 아닙니다.
상품 이미지는 Git으로 함께 내려오므로 팀원이 별도로 이미지를 복사할 필요가 없습니다.

## 금지 사항

- 팀원 각자가 `flask db migrate`를 새로 실행하지 않습니다.
- `flask db init`을 다시 실행하지 않습니다.
- DB 덤프 파일이나 `.env`를 Git으로 공유하지 않습니다.
- `seed.py`보다 먼저 `flask db upgrade`를 실행합니다.
- 기존 변경사항이 있는 작업 폴더에서 무조건 `git pull`하지 말고 먼저 `git status`를 확인합니다.

## 최종 확인 기준

다음 결과가 나오면 동일한 최종본을 받은 상태입니다.

```text
python -m flask db current
→ b4e8c1a7d930 (head)

python -m unittest discover -s tests -q
→ Ran 106 tests
→ OK
```

배포 서비스는 다음 핵심 경로가 HTTP 200인지 확인합니다.

```text
/
/goods
/goods/1
/destinations
/auth/login
/auth/signup
```
