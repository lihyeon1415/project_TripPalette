# TripPalette 개발 사양서

## 1. 프로젝트 개요

### 1.1 프로젝트명

**TripPalette**

### 1.2 서비스 정의

사용자의 여행 조건에 맞는 국내 여행지를 추천하고, 선택한 여행지 주변의 숙소를 연결하여 예약과 모의 결제까지 제공하는 여행 서비스입니다.

### 1.3 핵심 방향

> 사용자가 숙소부터 검색하는 것이 아니라 자신에게 맞는 여행지를 먼저 발견하고, 해당 여행지의 주변 숙소를 선택할 수 있도록 한다.

### 1.4 핵심 서비스 흐름

```text
여행지 탐색
→ 여행지 목록
→ 여행지 상세
→ 주변 숙소 확인
→ 숙소 목록
→ 숙소 상세
→ 숙소 예약
→ 모의 결제
→ 예약 완료
1.5 기술 스택
구분	기술
Backend	Python, Flask
Database	MySQL
Frontend	HTML5, CSS3, JavaScript
Template Engine	Jinja2
ORM	SQLAlchemy
Migration	Flask-Migrate
Authentication	Session 기반 이메일 로그인
Version Control	Git, GitHub
2. 서비스 범위
2.1 핵심 기능

TripPalette는 다음 기능을 제공합니다.

여행지 탐색 및 검색
여행지 목록 조회
여행지 상세정보 조회
여행지 리뷰 조회
여행지 찜
여행지 리뷰 작성
여행지 기반 주변 숙소 조회
숙소 상세정보 조회
맞춤 여행지 추천
숙소 예약
모의 결제
마이페이지
이메일 기반 회원가입 및 로그인
2.2 리뷰 운영 범위

현재 프로젝트에서는 여행지 리뷰만 운영합니다.

리뷰 대상: 여행지
숙소 리뷰: 현재 구현 범위에서 제외

따라서 숙소 상세 페이지에서는 숙소 사진, 설명, 가격, 수용 인원 등의 정보만 제공합니다.

2.3 결제 운영 범위

실제 카드사나 PG사와 연결하지 않고 모의 결제 기능으로 구현합니다.

모의 결제에서는 다음 정보만 처리합니다.

예약 정보
결제 금액
결제수단
결제 상태
결제 완료 시간
2.4 숙소 목록 구현 범위

숙소 목록 기능은 전체 구조에는 포함하지만 세부 기획과 구현은 프로젝트 후반에 진행합니다.

현재 단계에서는 다음 연결 구조만 확보합니다.

여행지 상세
→ 주변 숙소 보기
→ 숙소 목록
→ 숙소 상세

추후 다음 파일을 연결합니다.

app/templates/accommodation/list.html
3. 사용자 구분 및 권한
3.1 비회원

비회원은 조회 기능을 사용할 수 있습니다.

이용 가능한 기능
메인 페이지 열람
여행지 탐색
여행지 검색 및 필터
여행지 목록 조회
여행지 상세 조회
여행지 리뷰 조회
주변 숙소 조회
숙소 목록 조회
숙소 상세 조회
이메일 로그인
회원가입
가입 이메일 찾기
비밀번호 재설정
이용할 수 없는 기능
맞춤 여행지 추천
여행지 찜
여행지 리뷰 작성
숙소 예약
모의 결제
마이페이지 이용

회원 전용 기능을 선택하면 이메일 로그인 또는 회원가입 화면으로 이동합니다.

3.2 회원

회원은 비회원 기능을 포함하여 다음 기능을 추가로 사용할 수 있습니다.

맞춤 여행지 추천
여행지 찜
여행지 리뷰 작성
숙소 예약
모의 결제
예약 완료 확인
찜 목록 확인
예약 내역 확인
작성한 리뷰 확인
회원정보 수정
4. 인증 정책
4.1 로그인 방식

TripPalette는 별도의 로그인 ID를 사용하지 않고 이메일 주소를 로그인 계정으로 사용합니다.

이메일 + 비밀번호
4.2 이메일 정책
회원 이메일은 중복될 수 없습니다.
USER.email에는 UNIQUE 제약조건을 적용합니다.
로그인 시 이메일과 비밀번호를 입력받습니다.
회원가입 시 동일한 이메일의 존재 여부를 확인합니다.
4.3 가입 이메일 찾기

사용자가 가입한 이메일을 잊은 경우 이름과 전화번호를 이용하여 가입 이메일을 확인합니다.

이름 + 전화번호
→ 회원 확인
→ 가입 이메일 안내
4.4 비밀번호 재설정

기존 비밀번호를 사용자에게 보여주지 않습니다.

이메일 및 사용자 정보 확인
→ 본인 확인
→ 새로운 비밀번호 입력
→ password_hash 갱신

비밀번호는 평문으로 저장하지 않고 해시 처리하여 저장합니다.

4.5 로그아웃

로그아웃은 현재 로그인 세션을 종료하고 메인 페이지로 이동합니다.

5. 전체 사용자 이동 흐름
5.1 비회원 탐색 흐름
메인 페이지
→ 여행지 탐색
→ 여행지 목록
→ 여행지 상세
→ 주변 숙소 보기
→ 숙소 목록
→ 숙소 상세

비회원은 위의 페이지를 로그인 없이 조회할 수 있습니다.

5.2 여행지 찜 흐름

찜 대상은 숙소가 아니라 여행지입니다.

여행지 상세
→ 찜하기 선택
→ 로그인 상태 확인
회원인 경우
여행지 상세
→ 찜하기
→ FAVORITE 저장
→ 찜 상태 표시
비회원인 경우
여행지 상세
→ 찜하기
→ 이메일 로그인 또는 회원가입
→ 로그인 완료
→ 기존 여행지 상세로 복귀
→ 찜하기 실행
5.3 여행지 리뷰 작성 흐름
여행지 상세
→ 여행지 리뷰 작성
→ 로그인 상태 확인
회원인 경우
별점 및 리뷰 내용 입력
→ REVIEW 저장
→ 여행지 상세로 이동
→ 작성한 리뷰 표시
비회원인 경우
여행지 리뷰 작성 선택
→ 이메일 로그인 또는 회원가입
→ 로그인 완료
→ 기존 여행지 상세로 복귀
→ 리뷰 작성
5.4 맞춤 여행지 추천 흐름

맞춤 추천은 회원 전용 기능입니다.

마이페이지
→ 맞춤 여행지 추천
→ 추천 설문
→ 설문 저장
→ 추천 결과
→ 여행지 상세
→ 주변 숙소 보기
→ 숙소 목록
→ 숙소 상세

추천 설문 항목은 다음과 같습니다.

여행 계절
동행 유형
여행 목적
선호 분위기
예산
여행 기간
5.5 숙소 예약 및 모의 결제 흐름
숙소 상세
→ 숙소 예약
→ 로그인 상태 확인
→ 예약정보 입력
→ 예약 생성
→ 모의 결제
→ 예약 완료
→ 마이페이지 예약 내역
예약 입력 정보
체크인 날짜
체크아웃 날짜
인원수
숙소 정보
총 결제 금액
모의 결제 정보
결제 금액
결제수단
결제 상태
결제 완료 시간
6. 화면 구성
6.1 메인 페이지
주요 내용
TripPalette 서비스 소개
인기 여행지
여행지 검색
로그인 및 회원가입
마이페이지 진입
여행지 탐색 진입
URL
GET /
6.2 여행지 목록
주요 내용
여행지 검색
지역 필터
여행 테마 필터
여행지 목록
여행지 카드
여행지 상세 이동
검색 및 필터 기준
지역
계절
여행 목적
분위기
예산 수준
추천 여행 기간
URL
GET /destinations
6.3 여행지 상세
주요 내용
여행지명
지역
대표 이미지
여행지 설명
추천 계절
여행 목적
여행 분위기
예산 수준
추천 여행 기간
여행지 리뷰
여행지 찜
여행지 리뷰 작성
주변 숙소 보기
권한
기능	비회원	회원
여행지 정보 조회	가능	가능
여행지 리뷰 조회	가능	가능
여행지 찜	불가능	가능
여행지 리뷰 작성	불가능	가능
주변 숙소 확인	가능	가능
URL
GET /destinations/<int:id>
6.4 숙소 목록

숙소 목록은 프로젝트 후반에 세부 구현합니다.

예정 기능
선택한 여행지의 주변 숙소 표시
가격 필터
평점 필터
수용 인원 확인
숙소 상세 이동
URL
GET /accommodations
GET /destinations/<int:id>/accommodations
6.5 숙소 상세
주요 내용
숙소명
숙소 주소
숙소 이미지
숙소 설명
1박 가격
수용 가능 인원
평점
숙소 예약 버튼

숙소 리뷰는 현재 구현하지 않습니다.

URL
GET /accommodations/<int:id>
6.6 추천 설문
주요 내용
선호 계절
동행 유형
여행 목적
선호 분위기
예산
여행 기간
권한

회원만 이용할 수 있습니다.

URL
GET /recommend/survey
POST /recommend/survey
6.7 추천 결과
주요 내용
사용자 조건과 일치하는 여행지
여행지 대표 이미지
여행지명
지역
추천 이유
여행지 상세 이동
URL
GET /recommend/result
6.8 숙소 예약
주요 내용
예약 대상 숙소
체크인 날짜
체크아웃 날짜
이용 인원
총금액
예약 생성 버튼
URL
GET /accommodations/<int:id>/reservation
POST /accommodations/<int:id>/reservation
6.9 모의 결제
주요 내용
예약 정보
숙소 정보
결제 금액
결제수단
결제 실행
결제 결과
URL
GET /reservations/<int:id>/payment
POST /reservations/<int:id>/payment
6.10 예약 완료
주요 내용
예약 완료 안내
예약번호
숙소명
체크인 및 체크아웃 날짜
이용 인원
결제 금액
마이페이지 이동
URL
GET /reservations/<int:id>/complete
6.11 마이페이지
메뉴
맞춤 여행지 추천
찜 목록
예약 내역
작성한 리뷰
회원정보 수정
URL
GET /mypage
7. 유스케이스 정의
7.1 공개 기능
유스케이스	비회원	회원
메인 페이지 열람	가능	가능
여행지 탐색	가능	가능
여행지 목록 조회	가능	가능
여행지 상세 조회	가능	가능
여행지 리뷰 조회	가능	가능
숙소 목록 조회	가능	가능
숙소 상세 조회	가능	가능
이메일 로그인	가능	해당 없음
회원가입	가능	해당 없음
가입 이메일 찾기	가능	가능
비밀번호 재설정	가능	가능
7.2 회원 전용 기능
유스케이스	설명
맞춤 여행지 추천	설문 결과를 기반으로 여행지를 추천
추천 설문 입력	사용자의 여행 선호 조건 입력
추천 결과 확인	조건에 맞는 여행지 목록 확인
여행지 찜하기	관심 여행지를 찜 목록에 저장
여행지 리뷰 작성	여행지에 별점과 리뷰 작성
숙소 예약	선택한 숙소의 예약정보 저장
모의 결제	실제 PG 연결 없이 결제 과정 처리
예약 완료 확인	예약 및 결제 결과 확인
마이페이지 이용	사용자 활동과 회원정보 관리
찜 목록 확인	찜한 여행지 확인
예약 내역 확인	사용자의 예약정보 확인
작성한 리뷰 확인	사용자가 작성한 여행지 리뷰 확인
회원정보 수정	이름, 전화번호 등의 정보 수정
8. 데이터베이스 설계
8.1 엔티티 목록
엔티티	역할
USER	회원정보 저장
USER_PREFERENCE	맞춤 추천 설문 저장
DESTINATION	여행지 정보 저장
FAVORITE	사용자의 여행지 찜 저장
REVIEW	사용자의 여행지 리뷰 저장
ACCOMMODATION	여행지 주변 숙소 저장
RESERVATION	숙소 예약정보 저장
PAYMENT	모의 결제정보 저장
8.2 USER

회원정보를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	회원 식별자
email	VARCHAR(100)	UNIQUE, NOT NULL	로그인 이메일
password_hash	VARCHAR(255)	NOT NULL	암호화된 비밀번호
name	VARCHAR(50)	NOT NULL	회원 이름
phone	VARCHAR(20)	NOT NULL	전화번호
created_at	DATETIME	NOT NULL	가입 일시
8.3 USER_PREFERENCE

회원의 맞춤 여행지 추천 조건을 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	선호 설정 식별자
user_id	INT	FK, UNIQUE	회원 식별자
season	VARCHAR(20)		선호 계절
companion	VARCHAR(20)		동행 유형
purpose	VARCHAR(20)		여행 목적
atmosphere	VARCHAR(20)		선호 분위기
budget	INT		여행 예산
trip_duration	INT		여행 기간
updated_at	DATETIME		수정 일시
관계
USER 1 : 1 USER_PREFERENCE

한 명의 사용자는 하나의 최신 추천 설정을 가집니다.

이를 보장하기 위해 USER_PREFERENCE.user_id에 UNIQUE 제약조건을 적용합니다.

8.4 DESTINATION

여행지 정보를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	여행지 식별자
name	VARCHAR(100)	NOT NULL	여행지명
region	VARCHAR(50)	NOT NULL	지역
description	TEXT		여행지 설명
season	VARCHAR(20)		추천 계절
purpose	VARCHAR(20)		여행 목적
atmosphere	VARCHAR(20)		여행 분위기
budget_level	VARCHAR(20)		예산 수준
recommended_days	INT		추천 여행 기간
image_url	VARCHAR(255)		대표 이미지 경로
8.5 FAVORITE

회원이 찜한 여행지를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	찜 식별자
user_id	INT	FK, NOT NULL	회원 식별자
destination_id	INT	FK, NOT NULL	여행지 식별자
created_at	DATETIME	NOT NULL	찜한 일시
중복 방지
UNIQUE(user_id, destination_id)

한 사용자가 동일한 여행지를 중복으로 찜할 수 없도록 합니다.

관계
USER 1 : N FAVORITE
DESTINATION 1 : N FAVORITE
8.6 REVIEW

회원이 작성한 여행지 리뷰를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	리뷰 식별자
user_id	INT	FK, NOT NULL	작성 회원
destination_id	INT	FK, NOT NULL	리뷰 대상 여행지
rating	INT	NOT NULL	여행지 평점
content	TEXT	NOT NULL	리뷰 내용
created_at	DATETIME	NOT NULL	작성 일시
중복 작성 방지
UNIQUE(user_id, destination_id)

현재 사양에서는 한 회원이 하나의 여행지에 하나의 리뷰만 작성할 수 있습니다.

평점 범위
1 <= rating <= 5
관계
USER 1 : N REVIEW
DESTINATION 1 : N REVIEW
8.7 ACCOMMODATION

여행지 주변 숙소 정보를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	숙소 식별자
destination_id	INT	FK, NOT NULL	소속 여행지
name	VARCHAR(100)	NOT NULL	숙소명
address	VARCHAR(255)	NOT NULL	숙소 주소
description	TEXT		숙소 설명
price_per_night	INT	NOT NULL	1박 가격
capacity	INT	NOT NULL	최대 수용 인원
rating	DECIMAL(2,1)		숙소 평점
image_url	VARCHAR(255)		숙소 이미지 경로
관계
DESTINATION 1 : N ACCOMMODATION

하나의 여행지에는 여러 숙소가 연결될 수 있습니다.

8.8 RESERVATION

회원의 숙소 예약정보를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	예약 식별자
user_id	INT	FK, NOT NULL	예약 회원
accommodation_id	INT	FK, NOT NULL	예약 숙소
check_in	DATE	NOT NULL	체크인 날짜
check_out	DATE	NOT NULL	체크아웃 날짜
people_count	INT	NOT NULL	이용 인원
total_price	INT	NOT NULL	총 예약 금액
status	VARCHAR(20)	NOT NULL	예약 상태
created_at	DATETIME	NOT NULL	예약 생성 일시
예약 상태 예시
PENDING
PAID
CANCELLED
검증 조건
check_in < check_out
people_count >= 1
people_count <= accommodation.capacity
total_price >= 0
관계
USER 1 : N RESERVATION
ACCOMMODATION 1 : N RESERVATION
8.9 PAYMENT

예약에 대한 모의 결제정보를 저장합니다.

필드	타입	제약조건	설명
id	INT	PK	결제 식별자
reservation_id	INT	FK, UNIQUE, NOT NULL	예약 식별자
amount	INT	NOT NULL	결제 금액
payment_method	VARCHAR(20)	NOT NULL	결제수단
payment_status	VARCHAR(20)	NOT NULL	결제 상태
paid_at	DATETIME		결제 완료 일시
결제 상태 예시
READY
SUCCESS
FAILED
CANCELLED
관계
RESERVATION 1 : 1 PAYMENT

하나의 예약에는 하나의 최종 모의 결제정보만 저장합니다.

이를 보장하기 위해 PAYMENT.reservation_id에 UNIQUE 제약조건을 적용합니다.

9. 엔티티 관계 요약
USER 1 : 1 USER_PREFERENCE
USER 1 : N FAVORITE
DESTINATION 1 : N FAVORITE
USER 1 : N REVIEW
DESTINATION 1 : N REVIEW
DESTINATION 1 : N ACCOMMODATION
USER 1 : N RESERVATION
ACCOMMODATION 1 : N RESERVATION
RESERVATION 1 : 1 PAYMENT
9.1 핵심 데이터 흐름
USER
├── USER_PREFERENCE
├── FAVORITE ── DESTINATION
├── REVIEW ── DESTINATION
└── RESERVATION ── ACCOMMODATION ── DESTINATION
        └── PAYMENT
10. URL 및 View 매핑
10.1 메인
Method	URL	View 함수	Template
GET	/	main.index()	main/index.html
10.2 여행지
Method	URL	기능	View 함수	Template
GET	/destinations	여행지 목록 및 검색	destination.list()	destination/list.html
GET	/destinations/<int:id>	여행지 상세 및 리뷰 조회	destination.detail(id)	destination/detail.html
POST	/destinations/<int:id>/favorite	여행지 찜	destination.favorite(id)	AJAX 또는 redirect
POST	/destinations/<int:id>/reviews	여행지 리뷰 작성	destination.create_review(id)	AJAX 또는 redirect
GET	/destinations/<int:id>/accommodations	여행지 주변 숙소	accommodation.list_by_destination(id)	accommodation/list.html

accommodation/list.html은 프로젝트 후반에 구현합니다.

10.3 숙소
Method	URL	기능	View 함수	Template
GET	/accommodations	전체 숙소 목록	accommodation.list()	accommodation/list.html
GET	/accommodations/<int:id>	숙소 상세	accommodation.detail(id)	accommodation/detail.html
GET	/accommodations/<int:id>/reservation	예약 화면	reservation.form(id)	reservation/form.html
POST	/accommodations/<int:id>/reservation	예약 생성	reservation.create(id)	redirect

숙소 목록 관련 URL과 Template은 프로젝트 후반에 연결합니다.

10.4 인증
Method	URL	기능	View 함수	Template
GET, POST	/auth/login	이메일 로그인	auth.login()	auth/login.html
GET, POST	/auth/signup	회원가입	auth.signup()	auth/signup.html
POST	/auth/logout	로그아웃	auth.logout()	redirect
GET, POST	/auth/find-email	가입 이메일 찾기	auth.find_email()	auth/find_email.html
GET, POST	/auth/reset-password	비밀번호 재설정	auth.reset_password()	auth/reset_password.html
10.5 맞춤 여행지 추천
Method	URL	기능	View 함수	Template
GET	/recommend/survey	추천 설문	recommendation.survey()	recommendation/survey.html
POST	/recommend/survey	설문 저장	recommendation.save_survey()	redirect
GET	/recommend/result	추천 결과	recommendation.result()	recommendation/result.html

Python 파일과 Template 폴더는 모두 recommendation으로 통일합니다.

views/recommendation.py
templates/recommendation/

URL은 사용자 편의를 위해 /recommend를 사용합니다.

10.6 예약 및 모의 결제
Method	URL	기능	View 함수	Template
POST	/accommodations/<int:id>/reservation	예약 생성	reservation.create(id)	redirect
GET	/reservations/<int:id>/payment	모의 결제 화면	reservation.payment(id)	reservation/payment.html
POST	/reservations/<int:id>/payment	모의 결제 처리	reservation.process_payment(id)	redirect
GET	/reservations/<int:id>/complete	예약 완료	reservation.complete(id)	reservation/complete.html
10.7 마이페이지
Method	URL	기능	View 함수	Template
GET	/mypage	마이페이지 홈	mypage.index()	mypage/index.html
GET	/mypage/favorites	찜 목록	mypage.favorites()	mypage/favorites.html
GET	/mypage/reservations	예약 내역	mypage.reservations()	mypage/reservations.html
GET	/mypage/reviews	작성한 리뷰	mypage.reviews()	mypage/reviews.html
GET, POST	/mypage/profile	회원정보 수정	mypage.profile()	mypage/profile.html
11. Flask 프로젝트 폴더 구조
trippalette/
├── app/
│   ├── __init__.py
│   ├── models.py
│   │
│   ├── views/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── destination.py
│   │   ├── accommodation.py
│   │   ├── recommendation.py
│   │   ├── reservation.py
│   │   └── mypage.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   │
│   │   ├── main/
│   │   │   └── index.html
│   │   │
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── signup.html
│   │   │   ├── find_email.html
│   │   │   └── reset_password.html
│   │   │
│   │   ├── destination/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   │
│   │   ├── accommodation/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   │
│   │   ├── recommendation/
│   │   │   ├── survey.html
│   │   │   └── result.html
│   │   │
│   │   ├── reservation/
│   │   │   ├── form.html
│   │   │   ├── payment.html
│   │   │   └── complete.html
│   │   │
│   │   └── mypage/
│   │       ├── index.html
│   │       ├── favorites.html
│   │       ├── reservations.html
│   │       ├── reviews.html
│   │       └── profile.html
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
│
├── instance/
│   └── trippalette.db
│
├── config.py
├── run.py
└── requirements.txt

실제 운영 데이터베이스로 MySQL을 사용하는 경우 instance/trippalette.db는 개발용 SQLite 파일로만 사용할 수 있습니다.

12. Blueprint 구성

각 기능 영역을 Flask Blueprint로 분리합니다.

Blueprint	담당 기능
main	메인 페이지
auth	회원가입, 이메일 로그인, 로그아웃, 계정 찾기
destination	여행지 목록, 상세, 찜, 리뷰
accommodation	숙소 목록 및 상세
recommendation	추천 설문 및 추천 결과
reservation	예약, 모의 결제, 예약 완료
mypage	찜 목록, 예약 내역, 리뷰, 회원정보
12.1 Blueprint URL Prefix 예시
main_bp = Blueprint("main", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
destination_bp = Blueprint("destination", __name__, url_prefix="/destinations")
accommodation_bp = Blueprint("accommodation", __name__, url_prefix="/accommodations")
recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/recommend")
reservation_bp = Blueprint("reservation", __name__, url_prefix="/reservations")
mypage_bp = Blueprint("mypage", __name__, url_prefix="/mypage")
13. 요청 처리 구조
사용자
→ URL 요청
→ Flask Blueprint
→ View 함수
→ Model 및 Database
→ Jinja2 Template
→ HTML 응답
13.1 조회 요청
GET 요청
→ View 함수
→ Database 조회
→ Template에 데이터 전달
→ 화면 출력
13.2 생성 요청
POST 요청
→ 입력값 검증
→ 로그인 및 권한 확인
→ Database 저장
→ redirect
→ 결과 페이지 출력
14. 핵심 비즈니스 규칙
14.1 여행지 찜
회원만 여행지를 찜할 수 있습니다.
찜 대상은 DESTINATION입니다.
동일한 여행지를 중복으로 찜할 수 없습니다.
이미 찜한 여행지를 다시 선택하면 찜을 해제할 수 있습니다.
14.2 여행지 리뷰
회원만 여행지 리뷰를 작성할 수 있습니다.
리뷰 대상은 DESTINATION입니다.
숙소 리뷰는 현재 구현하지 않습니다.
평점은 1점부터 5점까지만 입력할 수 있습니다.
한 회원은 동일한 여행지에 하나의 리뷰만 작성할 수 있습니다.
14.3 추천 설정
회원 한 명당 하나의 최신 추천 설정을 저장합니다.
설문을 다시 제출하면 기존 설정을 수정합니다.
추천 결과는 여행지 데이터를 대상으로 생성합니다.
숙소를 직접 추천 대상으로 사용하지 않습니다.
14.4 숙소 예약
회원만 숙소를 예약할 수 있습니다.
체크인 날짜는 체크아웃 날짜보다 이전이어야 합니다.
예약 인원은 1명 이상이어야 합니다.
예약 인원은 숙소의 최대 수용 인원을 넘을 수 없습니다.
총금액은 서버에서 계산합니다.
14.5 총 예약 금액
숙박 일수 = 체크아웃 날짜 - 체크인 날짜
총금액 = 숙박 일수 × 숙소의 1박 가격

클라이언트에서 전달한 총금액을 그대로 신뢰하지 않고 서버에서 다시 계산합니다.

14.6 모의 결제
실제 PG사와 연결하지 않습니다.
예약금액과 결제금액이 일치해야 합니다.
결제가 완료되면 PAYMENT.payment_status를 SUCCESS로 변경합니다.
결제가 완료되면 RESERVATION.status를 PAID로 변경합니다.
동일한 예약에 결제정보를 중복 생성하지 않습니다.
15. 입력값 검증
15.1 회원가입
이메일 형식 확인
이메일 중복 확인
비밀번호 길이 확인
비밀번호 확인값 일치 여부
이름 필수 입력
전화번호 형식 확인
15.2 로그인
이메일 존재 여부 확인
비밀번호 해시 검증
로그인 실패 시 구체적인 개인정보를 노출하지 않음

권장 오류 메시지:

이메일 또는 비밀번호가 올바르지 않습니다.
15.3 리뷰
평점 1~5점
리뷰 내용 필수
공백만 입력할 수 없음
로그인 회원 확인
중복 리뷰 확인
15.4 예약
체크인 날짜 필수
체크아웃 날짜 필수
체크인 날짜가 체크아웃 날짜보다 빨라야 함
과거 날짜 예약 제한
인원수 1명 이상
숙소 수용 인원 초과 방지
16. 세션 및 접근 제어
16.1 로그인 세션

로그인이 완료되면 세션에 회원 식별자를 저장합니다.

session["user_id"] = user.id
16.2 회원 전용 페이지

다음 기능은 로그인 여부를 확인해야 합니다.

/recommend/*
/mypage/*
POST /destinations/<id>/favorite
POST /destinations/<id>/reviews
/accommodations/<id>/reservation
/reservations/<id>/payment
/reservations/<id>/complete
16.3 로그인 후 복귀

비회원이 회원 전용 기능을 선택한 경우 로그인 완료 후 원래 접근하려던 페이지나 기능으로 복귀할 수 있도록 합니다.

예시:

/destinations/3
→ 찜하기
→ /auth/login?next=/destinations/3
→ 로그인 완료
→ /destinations/3
17. 데이터 삭제 정책
17.1 여행지 삭제

여행지를 삭제할 경우 다음 데이터에 영향을 줍니다.

여행지 찜
여행지 리뷰
연결된 숙소

초기 프로젝트에서는 관리자 기능을 구현하지 않는다면 직접 삭제 기능을 제공하지 않습니다.

17.2 회원 탈퇴

회원 탈퇴 기능은 현재 핵심 범위에서 제외할 수 있습니다.

추후 구현 시 다음 데이터를 어떻게 처리할지 별도로 결정해야 합니다.

찜
여행지 리뷰
예약 내역
결제 내역
추천 설정
18. 구현 우선순위
1단계 데이터베이스 및 공통 구조
Flask Application Factory 구성
Blueprint 등록
SQLAlchemy 설정
MySQL 연결
Model 작성
Migration 설정
base.html 작성
공통 Header 및 Navigation 작성
2단계 회원 기능
회원가입
이메일 로그인
로그아웃
가입 이메일 찾기
비밀번호 재설정
세션 관리
회원 전용 접근 제어
3단계 여행지 기능
여행지 목록
여행지 검색 및 필터
여행지 상세
여행지 리뷰 조회
여행지 찜
여행지 리뷰 작성
4단계 맞춤 추천
추천 설문
추천 설정 저장
여행지 추천 조건 적용
추천 결과
추천 결과에서 여행지 상세 연결
5단계 숙소 및 예약
숙소 상세
숙소 예약 화면
예약정보 저장
예약금액 계산
모의 결제
예약 완료
6단계 마이페이지
마이페이지 홈
찜 목록
예약 내역
작성한 리뷰
회원정보 수정
7단계 숙소 목록 확장
accommodation/list.html 작성
여행지별 주변 숙소 조회
가격 필터
평점 필터
숙소 상세 연결
8단계 최종 통합
전체 사용자 흐름 확인
회원 및 비회원 권한 확인
URL 연결 확인
데이터 관계 확인
오류 메시지 정리
반응형 UI 확인
예약과 모의 결제 테스트
19. 테스트 항목
19.1 회원 기능
동일한 이메일로 중복 가입할 수 없는가
이메일과 비밀번호로 로그인할 수 있는가
잘못된 비밀번호 입력 시 로그인이 차단되는가
로그아웃 후 회원 전용 페이지에 접근할 수 없는가
가입 이메일 찾기가 정상적으로 동작하는가
비밀번호 재설정 후 새 비밀번호로 로그인할 수 있는가
19.2 여행지 기능
여행지 목록이 출력되는가
지역 및 여행 테마 필터가 동작하는가
여행지 상세정보가 출력되는가
여행지 리뷰가 출력되는가
회원만 여행지를 찜할 수 있는가
동일한 여행지가 중복 찜되지 않는가
회원만 여행지 리뷰를 작성할 수 있는가
동일한 여행지에 리뷰가 중복 작성되지 않는가
19.3 추천 기능
비회원이 추천 설문에 접근하면 로그인으로 이동하는가
추천 설문이 정상적으로 저장되는가
설문을 다시 제출하면 기존 설정이 갱신되는가
사용자 조건에 맞는 여행지가 출력되는가
추천 결과에서 여행지 상세로 이동할 수 있는가
19.4 숙소 및 예약
여행지와 숙소가 정상적으로 연결되는가
숙소 상세정보가 출력되는가
체크인 및 체크아웃 날짜가 검증되는가
수용 인원을 초과한 예약이 차단되는가
서버에서 총금액이 정상적으로 계산되는가
예약정보가 정상적으로 저장되는가
19.5 모의 결제
예약금액과 결제금액이 일치하는가
하나의 예약에 결제정보가 중복 생성되지 않는가
결제 완료 시 PAYMENT 상태가 변경되는가
결제 완료 시 RESERVATION 상태가 변경되는가
예약 완료 화면이 정상적으로 출력되는가
마이페이지 예약 내역에 표시되는가
19.6 마이페이지
로그인 회원의 데이터만 출력되는가
찜한 여행지가 표시되는가
예약 내역이 표시되는가
작성한 여행지 리뷰가 표시되는가
회원정보를 수정할 수 있는가
20. 최종 개발 기준

TripPalette의 모든 기능은 다음 기준을 유지해야 합니다.

추천 대상은 여행지입니다.
예약과 모의 결제 대상은 숙소입니다.
찜 대상은 여행지입니다.
리뷰 대상은 여행지입니다.
로그인 계정은 별도 ID가 아닌 이메일입니다.
비밀번호 찾기는 기존 비밀번호 조회가 아닌 비밀번호 재설정 방식입니다.
결제는 실제 결제가 아닌 모의 결제입니다.
recommendation.py와 templates/recommendation/ 명칭을 통일합니다.
회원 한 명당 하나의 최신 추천 설정을 저장합니다.
예약 한 건당 하나의 최종 모의 결제정보를 저장합니다.
숙소 목록은 프로젝트 후반에 확장합니다.
URL, View 함수, Template 경로와 ERD 관계가 서로 일치해야 합니다.