# ✈️ TripPalette

> 여행지를 먼저 발견하고, 그곳의 숙소까지 연결하는 국내 여행 추천 서비스

TripPalette는 사용자의 여행 조건에 맞는 국내 여행지를 추천하고, 선택한 여행지 주변의 숙소를 연결하여 예약과 모의 결제까지 제공하는 웹 서비스입니다.

사용자가 숙소부터 검색하는 기존 방식과 달리, 자신에게 맞는 여행지를 먼저 발견한 뒤 해당 지역의 숙소를 선택할 수 있도록 설계했습니다.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 프로젝트명 | TripPalette |
| 프로젝트 유형 | 국내 여행지 추천 및 숙소 예약 서비스 |
| 핵심 대상 | 국내 여행지를 탐색하거나 추천받고 싶은 사용자 |
| Backend | Python, Flask |
| Database | MySQL |
| Frontend | HTML5, CSS3, JavaScript |
| Template Engine | Jinja2 |
| 데이터 제공 | 국내 여행지 및 숙소 관련 Open API |
| 협업 도구 | GitHub, Figma 또는 FigJam |

공통 UI를 수정하거나 새 페이지를 구현할 때는 [TripPalette CSS 디자인 가이드](docs/TripPalette-CSS-가이드.md)를 기준으로 작업합니다.

현재 단계별 담당 파일과 병합 순서는 [Phase 3 작업 배정](docs/phase3/README.md)에서 확인합니다.

---

## 2. 핵심 서비스 흐름

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
```

TripPalette의 추천 대상은 `여행지`이며, 예약과 결제의 대상은 `숙소`입니다.

### User Flow

![TripPalette 사용자 이동 동선](docs/images/user-flow.png)

---

## 3. 주요 기능

### 여행지 탐색

- 국내 여행지 검색
- 지역 및 여행 테마 필터
- 여행지 목록 조회
- 여행지 상세정보 조회
- 여행지 리뷰 조회
- 주변 숙소 확인

### 맞춤 여행지 추천

회원이 입력한 다음 조건을 바탕으로 여행지를 추천합니다.

- 여행 계절
- 동행 유형
- 여행 목적
- 선호 분위기
- 예산
- 여행 기간

### 회원 기능

- 이메일 회원가입
- 이메일 로그인
- 로그아웃
- 가입 이메일 찾기
- 비밀번호 재설정
- 여행지 찜
- 여행지 리뷰 작성
- 숙소 예약
- 모의 결제
- 마이페이지 이용

### 마이페이지

- 맞춤 여행지 추천
- 찜한 여행지 확인
- 숙소 예약 내역 확인
- 작성한 여행지 리뷰 확인
- 회원정보 수정

---

## 4. 회원 및 비회원 권한

| 기능 | 비회원 | 회원 |
|---|:---:|:---:|
| 메인 페이지 열람 | ✅ | ✅ |
| 여행지 탐색 | ✅ | ✅ |
| 여행지 목록 및 상세 조회 | ✅ | ✅ |
| 여행지 리뷰 조회 | ✅ | ✅ |
| 숙소 목록 및 상세 조회 | ✅ | ✅ |
| 맞춤 여행지 추천 | ❌ | ✅ |
| 여행지 찜 | ❌ | ✅ |
| 여행지 리뷰 작성 | ❌ | ✅ |
| 숙소 예약 | ❌ | ✅ |
| 모의 결제 | ❌ | ✅ |
| 마이페이지 | ❌ | ✅ |

비회원이 회원 전용 기능을 선택하면 이메일 로그인 또는 회원가입 페이지로 이동합니다.

로그인 완료 후에는 기존에 이용하려던 페이지로 복귀할 수 있도록 구현합니다.

### Use Case Diagram

![TripPalette Use Case Diagram](docs/images/use-case.png)

---

## 5. 기능 운영 기준

### 로그인

별도의 로그인 ID를 사용하지 않고 이메일 주소를 로그인 계정으로 사용합니다.

```text
이메일 + 비밀번호
```

### 찜

찜 기능의 대상은 숙소가 아닌 여행지입니다.

```text
USER → FAVORITE → DESTINATION
```

한 회원은 동일한 여행지를 중복으로 찜할 수 없습니다.

### 리뷰

현재 프로젝트에서는 여행지 리뷰만 운영합니다.

```text
리뷰 대상: 여행지
숙소 리뷰: 구현 범위에서 제외
```

한 회원은 동일한 여행지에 하나의 리뷰만 작성할 수 있습니다.

### 결제

실제 카드사나 PG사와 연결하지 않고 모의 결제로 구현합니다.

```text
숙소 예약
→ 결제수단 선택
→ 모의 결제 처리
→ 예약 및 결제 상태 변경
→ 예약 완료
```

---

## 6. Open API 활용 방식

여행지와 숙소의 상세정보는 국내 관광 관련 Open API에서 가져옵니다.

HTML은 화면의 기본 구조를 제공하고 JavaScript가 데이터를 비동기로 요청하여 화면에 삽입합니다.

```text
사용자
→ JavaScript fetch 요청
→ Flask API
→ 외부 Open API
→ 데이터 가공
→ JSON 응답
→ HTML 화면 업데이트
```

### 역할 구분

| 구성 요소 | 역할 |
|---|---|
| HTML | 데이터를 표시할 기본 화면 구조 |
| CSS | 페이지 및 컴포넌트 디자인 |
| JavaScript | 비동기 요청과 화면 업데이트 |
| Flask | 외부 API 호출, 데이터 가공, 인증 및 DB 처리 |
| MySQL | 회원, 찜, 리뷰, 예약, 결제정보 저장 |
| Open API | 여행지와 숙소의 원본 정보 제공 |

### 비동기 처리 예시

```javascript
async function loadDestinations() {
    const response = await fetch("/api/destinations");
    const destinations = await response.json();

    const destinationList = document.querySelector("#destination-list");

    destinationList.innerHTML = destinations.map((destination) => `
        <article class="destination-card">
            <img
                src="${destination.imageUrl}"
                alt="${destination.name}"
            >

            <h2>${destination.name}</h2>
            <p>${destination.region}</p>

            <a href="/destinations/${destination.id}">
                상세보기
            </a>
        </article>
    `).join("");
}
```

---

## 7. 기술 스택

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square)

### Database

![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)

### Frontend

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

### Collaboration

![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)

---

## 8. 프로젝트 구조

```text
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
├── migrations/
├── instance/
├── config.py
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 9. HTML 템플릿 구성

독립된 페이지 템플릿은 총 20개를 기준으로 합니다.

| 영역 | 개수 |
|---|---:|
| 공통 기본 템플릿 | 1개 |
| 메인 페이지 | 1개 |
| 인증 | 4개 |
| 여행지 | 2개 |
| 숙소 | 2개 |
| 맞춤 추천 | 2개 |
| 예약 및 모의 결제 | 3개 |
| 마이페이지 | 5개 |
| 합계 | 20개 |

반복되는 화면 요소는 컴포넌트로 분리할 수 있습니다.

```text
templates/components/
├── header.html
├── footer.html
├── destination_card.html
├── accommodation_card.html
├── review_item.html
├── pagination.html
└── loading.html
```

---

## 10. 데이터베이스 구성

### 주요 테이블

| 테이블 | 역할 |
|---|---|
| `USER` | 회원정보 |
| `USER_PREFERENCE` | 맞춤 추천 조건 |
| `DESTINATION` | 여행지 정보 |
| `FAVORITE` | 여행지 찜 |
| `REVIEW` | 여행지 리뷰 |
| `ACCOMMODATION` | 여행지 주변 숙소 |
| `RESERVATION` | 숙소 예약정보 |
| `PAYMENT` | 모의 결제정보 |

### ERD

![TripPalette ERD](docs/images/erd.png)

---

## 11. 주요 URL

### 메인 및 여행지

| Method | URL | 기능 |
|---|---|---|
| GET | `/` | 메인 페이지 |
| GET | `/destinations` | 여행지 목록 |
| GET | `/destinations/<id>` | 여행지 상세 및 리뷰 |
| POST | `/destinations/<id>/favorite` | 여행지 찜 |
| POST | `/destinations/<id>/reviews` | 여행지 리뷰 작성 |
| GET | `/destinations/<id>/accommodations` | 여행지 주변 숙소 |

### 숙소

| Method | URL | 기능 |
|---|---|---|
| GET | `/accommodations` | 숙소 목록 |
| GET | `/accommodations/<id>` | 숙소 상세 |
| GET | `/accommodations/<id>/reservation` | 예약 화면 |
| POST | `/accommodations/<id>/reservation` | 예약 생성 |

### 인증

| Method | URL | 기능 |
|---|---|---|
| GET, POST | `/auth/login` | 이메일 로그인 |
| GET, POST | `/auth/signup` | 회원가입 |
| POST | `/auth/logout` | 로그아웃 |
| GET, POST | `/auth/find-email` | 가입 이메일 찾기 |
| GET, POST | `/auth/reset-password` | 비밀번호 재설정 |

### 맞춤 추천

| Method | URL | 기능 |
|---|---|---|
| GET | `/recommend/survey` | 추천 설문 |
| POST | `/recommend/survey` | 추천 설문 저장 |
| GET | `/recommend/result` | 추천 결과 |

### 예약 및 모의 결제

| Method | URL | 기능 |
|---|---|---|
| GET | `/reservations/<id>/payment` | 모의 결제 화면 |
| POST | `/reservations/<id>/payment` | 모의 결제 처리 |
| GET | `/reservations/<id>/complete` | 예약 완료 |

### 마이페이지

| Method | URL | 기능 |
|---|---|---|
| GET | `/mypage` | 마이페이지 |
| GET | `/mypage/favorites` | 찜 목록 |
| GET | `/mypage/reservations` | 예약 내역 |
| GET | `/mypage/reviews` | 작성한 리뷰 |
| GET, POST | `/mypage/profile` | 회원정보 수정 |

---

## 12. 설치 및 실행

### 저장소 복제

```bash
git clone https://github.com/TripPalette/project_TripPalette.git
cd project_TripPalette
```

팀원은 Organization 저장소를 개인 계정으로 Fork한 뒤 개인 Fork 주소를 Clone합니다. 자세한 절차는 [협업 가이드](CONTRIBUTING.md)를 확인해주세요.

### Python 버전

```text
Python 3.12.10
```

### 가상환경 생성

```bash
python -m venv venv
```

### 가상환경 실행

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS 또는 Linux:

```bash
source venv/bin/activate
```

### 패키지 설치

```bash
pip install -r requirements.txt
```

### 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/trippalette
```

### 데이터베이스 마이그레이션

```bash
flask db upgrade
```

초기 마이그레이션 파일이 없는 경우:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 애플리케이션 실행

```bash
python run.py
```

또는:

```bash
flask run
```

기본 접속 주소:

```text
http://127.0.0.1:5000
```

---

## 13. 환경변수 보안

`.env` 파일에는 데이터베이스 비밀번호와 같은 민감한 정보가 포함되므로 GitHub에 업로드하지 않습니다.

`.gitignore`에 다음 항목을 추가합니다.

```gitignore
.env
venv/
__pycache__/
*.pyc
instance/
```

GitHub에는 실제 값이 없는 예시 파일만 공유합니다.

```text
.env.example
```

예시:

```env
SECRET_KEY=
DATABASE_URL=
```

---

## 14. 개발 순서

1. Flask Application Factory 및 Blueprint 구성
2. MySQL 연결 및 Model 작성
3. 공통 Template과 Navigation 구현
4. 회원가입 및 이메일 로그인 구현
5. 여행지 로컬 이미지 연결
6. 여행지 목록 및 상세 구현
7. 여행지 찜 및 리뷰 구현
8. 맞춤 여행지 추천 구현
9. 숙소 상세 및 예약 구현
10. 모의 결제 구현
11. 마이페이지 구현
12. 숙소 목록과 필터 구현
13. 전체 기능 통합 및 테스트

숙소 목록은 여행지와 숙소의 상세 구조가 확정된 후 프로젝트 후반에 구현합니다.

---

## 15. 개발 시 핵심 기준

1. 추천 대상은 여행지입니다.
2. 예약과 모의 결제 대상은 숙소입니다.
3. 찜 대상은 여행지입니다.
4. 리뷰 대상은 여행지입니다.
5. 로그인 계정은 별도 ID가 아닌 이메일입니다.
6. 비밀번호는 조회하지 않고 재설정합니다.
7. 결제는 실제 결제가 아닌 모의 결제입니다.
8. `recommendation.py`와 `templates/recommendation/` 명칭을 통일합니다.
9. 회원 한 명당 하나의 최신 추천 설정을 저장합니다.
10. 예약 한 건당 하나의 최종 모의 결제정보를 저장합니다.
11. Open API 데이터는 비동기로 가져와 HTML에 삽입합니다.
12. URL, View 함수, Template 경로와 ERD 관계를 일치시킵니다.

---

## 16. 향후 확장 기능

- 숙소 목록 필터 고도화
- 여행지 지도 표시
- 숙소 위치 지도 표시
- 여행 일정 생성
- 리뷰 수정 및 삭제
- 예약 취소
- 관리자 페이지
- 실제 결제 시스템 연동
- 사용자 행동 기반 추천 고도화

---

## 17. 프로젝트 문서

프로젝트의 상세 설계는 다음 문서를 기준으로 관리합니다.

- 개발 사양서
- Use Case Diagram
- 사용자 이동 동선
- ERD
- URL 및 폴더 구조도
- 화면 설계서
- API 명세서

기능이나 데이터 구조가 변경되면 코드뿐만 아니라 관련 설계 문서도 함께 수정합니다.

---

## 18. 협업 안내

TripPalette는 GitHub Fork와 Pull Request 방식으로 협업합니다. 기능 브랜치는 `develop`에 통합하고, 검증이 끝난 `develop`만 `main`에 병합합니다.

작업을 시작하기 전에 [협업 가이드](CONTRIBUTING.md)를 확인해주세요.
