# TripPalette 최종본 팀 동기화 가이드

기준일: 2026-10-06

## 최종본 구성

- 여행지 탐색·상세·추천
- 숙소 목록·상세·예약
- 회원가입·로그인·찜·리뷰·마이페이지
- 굿즈 상품·상세·장바구니·배송지·주문·주문 상세
- 숙소 예약과 굿즈 주문의 토스페이먼츠 테스트 결제
- 결제 대기 10분 만료와 재고·숙소 날짜 점유 복구
- 자동 테스트 99개
- Migration head: `b4e8c1a7d930`

## GitHub 반영 순서

현재 기능 브랜치는 `feature/goods-cart-checkout`입니다.

```powershell
git switch feature/goods-cart-checkout
git status
python -m unittest discover -s tests -q
git add -A
git diff --cached --check
git commit -m "feat: 굿즈 장바구니와 공통 결제 흐름 완성"
git push -u origin feature/goods-cart-checkout
```

GitHub에서 다음 순서로 Pull Request를 병합합니다.

1. `feature/goods-cart-checkout` → `develop`
2. `develop`에서 테스트와 화면을 최종 확인
3. `develop` → `main`

기능 브랜치를 `main`으로 직접 병합하지 않습니다.

## 기존 팀원의 최종본 적용

Organization 저장소를 `origin`으로 사용하는 경우:

```powershell
git switch main
git fetch origin
git pull --ff-only origin main
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask db upgrade
python seed.py
python -m flask db current
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
python -m flask db upgrade
python seed.py
python -m flask db current
python -m unittest discover -s tests -q
python -m flask run
```

GitHub 웹의 개인 Fork에서는 먼저 `Sync fork` → `Update branch`를 실행해도 됩니다.

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

`.env`의 `DATABASE_URL`, `SECRET_KEY`를 자신의 로컬 환경에 맞게 수정한 뒤 실행합니다.

```powershell
python -m flask db upgrade
python seed.py
python -m flask db current
python -m unittest discover -s tests -q
python -m flask run
```

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
→ Ran 99 tests
→ OK
```
