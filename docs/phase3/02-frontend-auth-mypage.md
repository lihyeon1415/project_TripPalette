# Phase 3 — 프론트엔드: 인증·마이페이지·찜·리뷰 UI

담당자: 프론트엔드 담당자

작업 브랜치: `feature/phase3-user-ui`

PR 대상: `develop`

## 목표

팀장 백엔드가 제공하는 변수를 이용해 로그인 상태별 Header, 인증 Form, 여행지 찜·리뷰, 마이페이지 화면을 구현합니다.

## 담당 파일

```text
app/templates/base.html
app/templates/auth/login.html
app/templates/auth/signup.html
app/templates/auth/find_email.html
app/templates/auth/reset_password.html
app/templates/destination/detail.html
app/templates/mypage/favorites.html
app/templates/mypage/reviews.html
app/templates/mypage/profile.html
app/static/css/auth.css
app/static/css/mypage.css
app/static/css/destination.css
app/static/js/auth.js
```

Python View, 모델, Migration, 테스트 파일은 수정하지 않습니다.

## 1. 로그인 상태별 Header

`g.user`를 기준으로 분기합니다.

```text
비회원: 여행지 | 맞춤추천 | 로그인 | 회원가입
회원: 여행지 | 맞춤추천 | 마이페이지 메뉴 | 로그아웃
```

- 로그아웃은 `method="post"` Form으로 작성합니다.
- 마이페이지 버튼은 찜한 여행지·작성한 리뷰·회원정보 수정 메뉴를 엽니다.
- 별도의 마이페이지 홈 화면은 만들지 않습니다.
- 모바일 메뉴에서도 같은 권한 분기를 유지합니다.

## 2. 인증 화면

모든 Form에 `method="post"`와 정확한 `action`을 작성합니다.

### 로그인

`email`, `password`, `next`를 전송합니다. 비밀번호 입력값은 다시 화면에 출력하지 않습니다.

### 회원가입

`email`, `password`, `password_confirm`, `name`, `phone`을 전송합니다. Input마다 Label과 `autocomplete`을 작성합니다.

### 이메일 찾기

`name`, `phone`을 전송하고 결과가 있으면 `found_email`을 별도 영역에 표시합니다.

### 비밀번호 재설정

`email`, `name`, `phone`, `new_password`, `new_password_confirm`을 전송합니다. 기존 비밀번호를 표시하는 UI는 만들지 않습니다.

## 3. 여행지 찜·리뷰

`destination/detail.html`에만 추가합니다.

- 회원은 `is_favorite`에 따라 찜하기·찜 해제를 표시합니다.
- 비회원은 원래 페이지를 `next`로 포함한 로그인 링크를 표시합니다.
- 숙소 화면에는 찜 버튼을 추가하지 않습니다.
- 기존 리뷰 목록은 유지합니다.
- 로그인하고 `can_review=True`인 회원에게 평점 1~5와 내용 Form을 표시합니다.
- 이미 리뷰를 쓴 회원에게 중복 Form을 표시하지 않습니다.

## 4. 마이페이지

### 마이페이지 메뉴

- Header의 마이페이지 아이콘은 페이지 이동 대신 메뉴를 엽니다.
- 메뉴에서 찜 목록·리뷰 목록·회원정보 수정으로 이동합니다.
- `/mypage` 직접 접근은 찜 목록으로 이동합니다.

### 찜 목록

- `favorites`를 반복하여 여행지 이미지·이름·지역·설명 표시
- 여행지 상세 이동과 Empty State 제공

### 작성 리뷰

- `reviews`를 반복하여 여행지명·평점·내용·작성일 표시
- 여행지 상세 이동과 Empty State 제공

### 프로필

- 이메일은 읽기 전용
- 이름과 전화번호만 수정 Form 제공
- 비밀번호 변경 Form과 혼합하지 않음

## 5. CSS와 반응형

- [`TripPalette-CSS-가이드.md`](../TripPalette-CSS-가이드.md)를 따릅니다.
- 인증 Form 최대 폭은 약 `520px`입니다.
- 카드 목록은 데스크톱 3열, 태블릿 2열, 모바일 1열입니다.
- `375px`에서 가로 스크롤이 없어야 합니다.
- Form 제출은 JavaScript가 없어도 동작해야 합니다.

## 접근성

- Input과 Label의 `for`·`id`를 일치시킵니다.
- 오류 Flash는 `role="alert"`, 일반 안내는 `role="status"`로 제공합니다.
- 아이콘 버튼에는 `aria-label`을 제공합니다.
- Heading 순서는 `h1 → h2 → h3`를 유지합니다.

## 금지사항

- 사용자·찜·리뷰 데이터 하드코딩
- Python View 또는 모델 수정
- 숙소 찜·숙소 리뷰 UI 추가
- 실제 이메일 인증 화면 추가
- 맞춤 추천·예약·결제 UI 선행 구현
- CSS 가이드와 다른 새로운 주색 추가

## 완료 조건

- 비회원과 회원 Header가 정확히 구분되고 마이페이지 메뉴가 동작합니다.
- 모든 인증 Form이 백엔드 입력 이름과 일치합니다.
- 여행지 상세의 찜·리뷰 상태가 변수에 따라 달라집니다.
- 마이페이지에 현재 사용자의 데이터만 표시됩니다.
- 빈 목록에 Empty State가 있습니다.
- 데스크톱·태블릿·모바일에서 정상 표시됩니다.

## 작업 순서

1. 팀장 백엔드의 Template 변수 계약 확인
2. 로그인·회원가입 Form
3. 이메일 찾기·비밀번호 재설정 Form
4. 로그인 상태별 Header
5. 여행지 찜·리뷰 UI
6. 마이페이지 메뉴·찜·리뷰·프로필
7. 페이지별 CSS와 모바일 확인
8. 최신 `develop` 반영 후 전체 화면 검증
