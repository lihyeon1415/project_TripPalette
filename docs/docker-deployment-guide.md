# TripPalette Flask Docker 이미지 가이드

## 이미지 구성

- 대상 플랫폼: `linux/amd64`
- 기본 이미지: `python:3.12-slim-bookworm`
- WSGI 서버: Gunicorn
- 실행 사용자: 비루트 `app` 사용자
- 기본 포트: `8000` (`PORT` 환경변수로 변경 가능)
- 데이터베이스: 이미지에 포함하지 않고 `DATABASE_URL`로 외부 MySQL 연결

회원, 리뷰, 예약, 주문 데이터나 `.env` 비밀정보는 이미지에 포함하지 않는다.

## Aiven MySQL TLS 연결

Aiven MySQL 주소를 `DATABASE_URL`에 사용하면 애플리케이션은
`MYSQL_SSL_CA`를 필수로 요구한다. CA 체인과 서버 호스트 이름을 모두
검증하므로 인증서가 없거나 경로가 잘못되면 서버 시작 단계에서 중단된다.

로컬 환경에서는 Aiven Console에서 받은 프로젝트 CA를 Git에서 제외되는
`instance/aiven-ca.pem`에 저장한다.

```dotenv
DATABASE_URL=
MYSQL_HOST=HOST
MYSQL_PORT=PORT
MYSQL_DATABASE=trippalette
MYSQL_USER=trippalette_app
MYSQL_PASSWORD=PASSWORD
MYSQL_SSL_CA=instance/aiven-ca.pem
```

Render에서는 인증서 전체를 `aiven-ca.pem` Secret File로 등록하고 환경변수에
컨테이너 내부 경로를 지정한다.

```text
MYSQL_SSL_CA=/etc/secrets/aiven-ca.pem
```

개별 환경변수를 사용하면 비밀번호의 예약 문자를 URL 인코딩할 필요가 없다.
기존 `DATABASE_URL`과 개별 MySQL 환경변수가 모두 있으면 `DATABASE_URL`을
우선한다. Aiven의 원본 Service URI, 비밀번호, API 토큰, `.env`는 Git에
커밋하지 않는다.

## 로컬 빌드

PowerShell에서 Git 커밋 해시와 릴리스 이름을 지정해 빌드한다.

```powershell
docker build `
  --platform linux/amd64 `
  --tag trippalette-flask:local `
  --build-arg APP_VERSION=local `
  --build-arg VCS_REF=unknown `
  .
```

현재 PNG 자산은 `oxipng`의 변환 비활성화 옵션(`--nx`)으로 무손실
재압축한다. 해상도, 색상 모드, 디코딩된 픽셀이 변경되지 않았는지는
`scripts/verify_png_pixels.py`로 원본과 비교한다.

2026-10-06 기준 327개 PNG를 전수 비교한 결과는 다음과 같다.

- PNG 합계: `843,970,575` → `783,754,223` bytes
- 절감량: `60,216,352` bytes (`7.13%`)
- 픽셀 검증: `checked=327`, `mismatches=0`
- 로컬 Docker 이미지: `2,194,159,423` → `2,080,360,523` bytes

이 최적화는 PNG 컨테이너의 압축 방식과 부가 메타데이터만 정리한다. 화면에
표시되는 해상도·색상·픽셀은 바뀌지 않는다. 더 큰 절감을 위해 WebP/AVIF 또는
손실 압축을 적용하는 작업은 화질 및 브라우저 표시 검토가 필요하므로 별도로
진행한다.

## 로컬 실행

컨테이너에서 호스트 PC의 MySQL에 연결할 때는 `localhost` 대신
`host.docker.internal`을 사용한다.

```powershell
docker run --rm `
  --name trippalette-flask `
  --publish 5000:8000 `
  --env SECRET_KEY=로컬용랜덤값 `
  --env DATABASE_URL='mysql+pymysql://username:password@host.docker.internal:3306/trippalette?charset=utf8mb4' `
  --env MYSQL_SSL_CA=/run/secrets/aiven-ca.pem `
  --volume 'D:\TripPalette\instance\aiven-ca.pem:/run/secrets/aiven-ca.pem:ro' `
  --env TOSS_PAYMENT_MODE=test `
  --env TOSS_CLIENT_KEY=test_클라이언트키 `
  --env TOSS_SECRET_KEY=test_시크릿키 `
  trippalette-flask:local
```

## Docker Hub 업로드

Docker Hub에 `trippalette-flask` 저장소를 만든 후 액세스 토큰으로 로그인한다.
계정 비밀번호나 토큰은 명령 기록 또는 Git에 남기지 않는다.

```powershell
docker login --username DOCKERHUB_USERNAME
```

릴리스 태그와 커밋 태그를 함께 만든다. `latest`만 사용하지 않는다.

```powershell
docker tag trippalette-flask:local DOCKERHUB_USERNAME/trippalette-flask:v1.0.0
docker tag trippalette-flask:local DOCKERHUB_USERNAME/trippalette-flask:COMMIT_SHA

docker push DOCKERHUB_USERNAME/trippalette-flask:v1.0.0
docker push DOCKERHUB_USERNAME/trippalette-flask:COMMIT_SHA
```

팀원별 Render 서비스는 모두 동일한 버전 태그 또는 이미지 digest를 사용한다.

```text
docker.io/DOCKERHUB_USERNAME/trippalette-flask:v1.0.0
```

## 공용 Aiven DB 최초 초기화

Migration과 Seed는 팀 대표가 한 번만 실행한다. 모든 Render 컨테이너의 시작
명령에 Migration이나 Seed를 넣지 않는다.

```powershell
docker run --rm `
  --env-file .env.deploy `
  --entrypoint python `
  DOCKERHUB_USERNAME/trippalette-flask:v1.0.0 `
  -m flask db upgrade

docker run --rm `
  --env-file .env.deploy `
  --entrypoint python `
  DOCKERHUB_USERNAME/trippalette-flask:v1.0.0 `
  seed.py
```

`.env.deploy`는 Git에 올리지 않으며 작업 완료 후 안전하게 보관하거나 삭제한다.
`seed.py`는 최초 초기화 또는 승인된 기본 데이터 변경 때만 실행한다.

## Render 배포

1. `New` → `Web Service`를 선택한다.
2. Source에서 `Existing Image`를 선택한다.
3. Docker Hub의 고정 버전 태그 또는 digest를 입력한다.
4. Free 인스턴스를 선택한다.
5. `DATABASE_URL`, `SECRET_KEY`, Toss 테스트 키를 환경변수로 등록한다.
6. 배포 후 `/`, 로그인, 리뷰, 예약, 주문, 테스트 결제를 확인한다.

Docker Hub 이미지가 갱신되어도 이미지 기반 Render 서비스는 자동 재배포되지
않는다. 공용 DB Migration을 먼저 한 번 수행하고 대표 서비스를 검증한 다음,
팀원들이 같은 이미지 버전을 수동 배포한다.

## 이후 릴리스 순서

```text
feature → develop → main
→ 테스트
→ linux/amd64 이미지 빌드
→ Docker Hub에 고정 태그로 Push
→ Aiven 백업 및 Migration 1회
→ 대표 Render 수동 배포·검증
→ 나머지 팀원 Render에 동일 이미지 수동 배포
```
