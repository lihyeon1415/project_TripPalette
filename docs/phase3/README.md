# Phase 3 작업 배정

Phase 3의 목표는 이메일 기반 인증과 회원별 여행지 찜·리뷰·마이페이지 기능을 완성하는 것입니다. 현재 인원 2명을 기준으로 백엔드와 프론트엔드의 담당 파일을 분리합니다.

## 시작 조건

- Phase 2 변경사항을 먼저 `develop`과 `main`에 병합합니다.
- 두 사람 모두 병합된 최신 `develop`에서 Phase 3 작업을 시작합니다.
- 설계 기준은 `docs/TripPalette-개발-사양서.md` 3장, 4장, 5.2~5.3, 6.11, 7장을 따릅니다.
- UI는 [`docs/TripPalette-CSS-가이드.md`](../TripPalette-CSS-가이드.md)를 따릅니다.
- 기존 `User`, `Favorite`, `Review` 모델로 구현하며 Phase 3에서는 Migration을 만들지 않습니다.

## 역할 배정

| 담당 | 역할 | 작업 문서 | 브랜치 |
|---|---|---|---|
| 팀장 | 인증·회원 기능 백엔드, 테스트, 통합 | [01-team-lead-auth-backend.md](01-team-lead-auth-backend.md) | `kdk` |
| 프론트엔드 | 인증·마이페이지·찜·리뷰 UI | [02-frontend-auth-mypage.md](02-frontend-auth-mypage.md) | `feature/phase3-user-ui` |

## 포함 범위

- 이메일 회원가입·로그인·로그아웃
- 로그인 후 원래 페이지 복귀
- 이름·전화번호를 이용한 가입 이메일 찾기
- 사용자 정보 확인 후 비밀번호 재설정
- 로그인 상태에 따른 Header와 마이페이지 드롭다운 분기
- 여행지 찜 추가·해제
- 여행지 리뷰 작성
- 마이페이지 요약·찜 목록·작성 리뷰 목록
- 이름·전화번호 수정

## 제외 범위

- 소셜 로그인과 실제 이메일·SMS 인증
- 메일 발송 기반 비밀번호 재설정 토큰
- 맞춤 추천 저장과 결과 계산
- 숙소 예약과 모의 결제
- 예약 내역의 실제 데이터 구현
- 리뷰 수정·삭제와 관리자 기능

## URL 계약

| 기능 | Method | URL | 비회원 접근 |
|---|---|---|---|
| 회원가입 | `GET`, `POST` | `/auth/signup` | 가능 |
| 로그인 | `GET`, `POST` | `/auth/login` | 가능 |
| 로그아웃 | `POST` | `/auth/logout` | 불가능 |
| 이메일 찾기 | `GET`, `POST` | `/auth/find-email` | 가능 |
| 비밀번호 재설정 | `GET`, `POST` | `/auth/reset-password` | 가능 |
| 여행지 찜 전환 | `POST` | `/destinations/<id>/favorite` | 로그인으로 이동 |
| 여행지 리뷰 작성 | `POST` | `/destinations/<id>/reviews` | 로그인으로 이동 |
| 마이페이지 진입 | `GET` | `/mypage` | 로그인 후 찜 목록으로 이동 |
| 찜 목록 | `GET` | `/mypage/favorites` | 로그인으로 이동 |
| 작성 리뷰 | `GET` | `/mypage/reviews` | 로그인으로 이동 |
| 회원정보 수정 | `GET`, `POST` | `/mypage/profile` | 로그인으로 이동 |

상태 변경은 반드시 `POST`로 처리합니다. 로그아웃·찜·리뷰·회원정보 수정에 `GET`을 사용하지 않습니다.

## Template 변수 계약

| Template | 변수 |
|---|---|
| `base.html` | `g.user` |
| `auth/login.html` | `next_url`, `form_data` |
| `auth/signup.html` | `form_data` |
| `auth/find_email.html` | `found_email`, `form_data` |
| `auth/reset_password.html` | `form_data` |
| `destination/detail.html` | 기존 변수 + `is_favorite`, `can_review` |
| `mypage/favorites.html` | `favorites` |
| `mypage/reviews.html` | `reviews` |
| `mypage/profile.html` | `user` |

## 인증·보안 기준

- 로그인 계정은 이메일입니다.
- 이메일은 공백 제거와 소문자 정규화를 적용합니다.
- 비밀번호 원문을 DB, 로그, Flash, Template에 남기지 않습니다.
- Werkzeug의 `generate_password_hash()`와 `check_password_hash()`를 사용합니다.
- 로그인 성공 시 세션을 초기화한 뒤 `user_id`를 저장합니다.
- 로그아웃 시 세션을 삭제합니다.
- `next` 이동은 현재 서비스 내부 경로만 허용합니다.
- 로그인 실패 메시지로 이메일 존재 여부를 구분하지 않습니다.
- 다른 사용자의 찜·리뷰·프로필을 조회하거나 수정할 수 없어야 합니다.
- 실제 서비스 수준의 이메일 소유 인증은 범위가 아니며 개발용 본인 확인 흐름만 구현합니다.

## 파일 충돌 방지

### 팀장 전용

```text
app/auth_helpers.py
app/views/auth.py
app/views/destination.py
app/views/mypage.py
tests/test_phase3_auth.py
tests/test_phase3_user_features.py
Roadmap.md
```

### 프론트엔드 전용

```text
app/templates/base.html
app/templates/auth/login.html
app/templates/auth/signup.html
app/templates/auth/find_email.html
app/templates/auth/reset_password.html
app/templates/destination/detail.html
app/templates/mypage/index.html
app/templates/mypage/favorites.html
app/templates/mypage/reviews.html
app/templates/mypage/profile.html
app/static/css/auth.css
app/static/css/mypage.css
app/static/css/destination.css
app/static/js/auth.js
```

`app/models.py`, `app/__init__.py`, `migrations/`, `requirements.txt` 변경이 필요하면 먼저 팀장과 합의합니다.

## 병합 순서

1. Phase 2를 `main`까지 병합하고 기준점을 확정합니다.
2. 팀장이 View·세션·검증·테스트를 구현합니다.
3. 팀장 백엔드를 `develop`에 먼저 병합합니다.
4. 프론트엔드가 최신 `develop`을 반영합니다.
5. 프론트엔드가 실제 변수로 화면을 검증한 뒤 PR을 생성합니다.
6. 팀장이 비회원·회원 시나리오와 사용자별 데이터 분리를 통합 검증합니다.
7. `develop → main` PR로 Phase 3를 마감합니다.

## 완료 기준

- 회원가입 시 비밀번호 해시만 저장됩니다.
- 중복 이메일 가입이 차단됩니다.
- 로그인·로그아웃과 안전한 원래 페이지 복귀가 동작합니다.
- 모든 마이페이지 URL은 비회원 접근을 차단합니다.
- 회원별 찜과 리뷰 데이터가 섞이지 않습니다.
- 같은 여행지의 중복 찜·중복 리뷰가 차단됩니다.
- 리뷰 평점은 1~5만 허용됩니다.
- Header가 로그인 상태에 따라 달라지고 마이페이지 메뉴에서 찜·리뷰·프로필로 이동합니다.
- Phase 3 테스트와 기존 Phase 2 테스트가 모두 통과합니다.
