# Phase 3 — 팀장: 인증·회원 기능 백엔드·통합

담당자: 팀장 (`kdk`)

작업 브랜치: `kdk`

PR 대상: `develop`

## 목표

Flask 세션과 기존 모델을 사용하여 이메일 인증, 여행지 찜·리뷰, 마이페이지 데이터를 구현하고 회원별 데이터 격리를 자동 테스트합니다.

## 담당 파일

```text
app/auth_helpers.py
app/views/auth.py
app/views/destination.py
app/views/mypage.py
tests/test_phase3_auth.py
tests/test_phase3_user_features.py
Roadmap.md
```

Template, 페이지 CSS, `base.html`은 프론트엔드 담당자가 수정합니다.

## 1. 인증 공통 도구

`app/auth_helpers.py`에 다음 기능을 둡니다.

- 세션의 `user_id`로 현재 사용자 조회
- `g.user` 설정
- `login_required` Decorator
- 내부 경로만 허용하는 안전한 `next` 검증
- 비회원 접근 시 `/auth/login?next=...`로 이동

외부 도메인, `//example.com`, 잘못된 Scheme이 포함된 `next`는 허용하지 않습니다.

## 2. 회원가입

입력값:

```text
email
password
password_confirm
name
phone
```

처리 순서:

1. 문자열 공백 제거와 이메일 소문자 정규화
2. 필수값·이메일 형식 검증
3. 비밀번호 확인과 최소 길이 검증
4. 중복 이메일 확인
5. `generate_password_hash()` 적용
6. `User` 저장 후 로그인 화면 이동

## 3. 로그인·로그아웃

- 이메일과 비밀번호가 모두 일치할 때만 로그인합니다.
- 성공 시 기존 세션을 초기화하고 `user_id`를 저장합니다.
- 안전한 `next`가 있으면 해당 내부 페이지로 복귀합니다.
- 실패 메시지는 계정 존재 여부를 구분하지 않습니다.
- 로그아웃은 `POST`만 허용하고 세션을 삭제합니다.

## 4. 이메일 찾기·비밀번호 재설정

```text
이메일 찾기: name + phone → 가입 이메일 표시
비밀번호 재설정: email + name + phone + 새 비밀번호 + 확인
```

기존 비밀번호를 표시하거나 복호화하지 않습니다. 실제 이메일·SMS 인증은 구현하지 않습니다.

## 5. 여행지 찜

```text
POST /destinations/<int:id>/favorite
```

- 로그인 필수이며 대상은 여행지입니다.
- 찜이 없으면 생성하고 이미 있으면 삭제하는 Toggle 방식입니다.
- 처리 후 해당 여행지 상세로 이동합니다.
- 상세 Template에 `is_favorite`를 전달합니다.

## 6. 여행지 리뷰 작성

```text
POST /destinations/<int:id>/reviews
```

- 로그인 필수입니다.
- `rating`은 정수 1~5만 허용합니다.
- `content`는 공백만 입력할 수 없습니다.
- 한 사용자는 같은 여행지에 리뷰를 한 번만 작성합니다.
- 상세 Template에 `can_review`를 전달합니다.
- 리뷰 수정·삭제는 구현하지 않습니다.

## 7. 마이페이지

```text
GET /mypage              → /mypage/favorites Redirect
GET /mypage/favorites
GET /mypage/reviews
GET, POST /mypage/profile
```

- 모든 URL에 `login_required`를 적용합니다.
- 별도 마이페이지 홈은 만들지 않고 `/mypage`를 찜 목록으로 이동시킵니다.
- 찜·리뷰 목록은 현재 사용자의 데이터만 조회합니다.
- 프로필은 이름과 전화번호만 수정합니다.
- 이메일은 로그인 계정이므로 Phase 3에서 수정하지 않습니다.
- 예약 내역의 실제 조회는 Phase 5에서 구현합니다.

## 8. 자동 테스트

`tests/test_phase3_auth.py`:

- 회원가입 성공·중복 이메일 실패·비밀번호 해시
- 로그인 성공·실패·로그아웃
- 내부 `next` 복귀와 외부 URL 차단
- 이메일 찾기
- 비밀번호 재설정 후 새 비밀번호 로그인

`tests/test_phase3_user_features.py`:

- 비회원 마이페이지 차단
- 찜 추가·해제와 사용자별 격리
- 리뷰 평점·빈 내용 검증과 중복 차단
- 마이페이지 진입 Redirect·찜 목록·작성 리뷰 목록
- 이름·전화번호 수정
- 존재하지 않는 여행지 404

기존 `tests/test_phase2_routes.py`도 함께 실행합니다.

## 금지사항

- 평문 비밀번호 저장
- 실제 이메일·SMS 인증을 구현했다고 표현
- 숙소 찜 또는 숙소 리뷰 추가
- 맞춤 추천·예약·결제 선행 구현
- 외부 URL로 `next` Redirect
- 다른 사용자의 데이터 ID를 요청값만 믿고 수정
- 불필요한 모델·Migration 변경

## 작업 순서

1. 인증 Helper와 현재 사용자 로딩
2. 회원가입
3. 로그인·로그아웃·원래 페이지 복귀
4. 이메일 찾기·비밀번호 재설정
5. 마이페이지 보호와 사용자 조회
6. 여행지 찜
7. 여행지 리뷰 작성
8. 프로필 수정
9. 자동 테스트
10. 프론트엔드 변수 계약 확인과 통합
