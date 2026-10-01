# TripPalette 개발용 Seed Data 안내

## 구성

- `app/data/destinations.json`: 여행지 68개
- `app/data/accommodations.json`: 지역별 숙소 3~7개, 총 277개

계절별 여행지 수는 다음과 같습니다.

| 계절 | 여행지 수 |
|---|---:|
| 봄 | 10 |
| 여름 | 8 |
| 가을 | 13 |
| 겨울 | 4 |
| 사계절 | 33 |

모든 여행지 이름은 중복되지 않으며, 모든 숙소의 `destination_name`은
`destinations.json`의 `name`과 정확하게 일치합니다.

## 지역 자료 반영 기준

`계절별 장소 및 숙소 추가 반영안 .xlsx`의 기존 지역 숙소와 신규 지역을
JSON 데이터에 병합했습니다.

- 기존 여행지와 이름이 겹치는 지역은 중복 생성하지 않고 숙소만 병합했습니다.
- 양주·연천·이천 등 기존 JSON에 없던 26개 여행지를 새로 추가했습니다.
- 엑셀에 제시된 숙소는 기존 숙소를 보존하면서 이름이 겹치지 않는 항목을
  모두 추가했습니다.
- `가평균`은 `가평`으로, 시·군 접미사는 프로젝트의 여행지 이름 형식에
  맞춰 제거했습니다.
- 기존에 검증해 교체한 `오유원`, `맑은물리조트`, `포라이즌글램핑`,
  `더 클래식 바이 호텔원`, `그랜드 머큐어 앰배서더 창원`은 엑셀의
  예전 이름으로 되돌리지 않았습니다.
- 행정구역 표기는 `강원특별자치도`, `전북특별자치도`,
  `제주특별자치도`처럼 현재 명칭으로 통일했습니다.
- 제주 지역은 이름 충돌을 피하고 위치를 분명히 하기 위해 `제주 조천`,
  `제주 애월`, `서귀포`, `제주 한림`, `제주 구좌`, `제주 남원`으로
  구분했습니다.

## 가격 기준

기존 `price_per_night`은 공식 사이트와 국내외 숙박 가격 비교 사이트에서
확인한 공개 가격, 최저가 또는 평균가를 참고해 정한 개발용 1박 대표가격입니다.
엑셀에 새로 추가된 숙소는 가격 정보가 없으므로 숙소 유형별 개발용 기준가를
적용했습니다.

- 호텔·여관: 90,000원 / 기준 2인
- 펜션·한옥·스테이 등: 110,000원 / 기준 4인
- 캠핑·글램핑·카라반: 140,000원 / 기준 4인
- 리조트·리솜·휴양 빌리지: 150,000원 / 기준 4인

- 성수기·비수기, 평일·주말, 객실 등급은 구분하지 않습니다.
- 원 단위 정수로 저장합니다.
- 할인, 세금, 조식과 부대시설 포함 여부를 별도로 계산하지 않습니다.
- 공개 가격을 명확히 확인하기 어려운 일부 소규모 펜션과 호텔은 같은 지역의
  유사 숙소 공개 가격을 참고해 대표가격을 정했습니다.
- 실시간 예약 가격이나 최종 결제 금액으로 사용하지 않습니다.
- 실제 PG사, 카드사 또는 숙소 예약 시스템과 연결하지 않습니다.

이 데이터는 개발·화면·테스트용이며 실제 판매 정보가 아닙니다.

## 평점과 이미지

- 평점은 시점에 따라 달라지므로 `rating`을 `null`로 저장합니다.
- 출처와 사용 권한이 확인된 이미지를 확보하기 전까지 `image_url`은 `null`로 저장합니다.
- 개인정보, 실제 예약정보, 결제정보를 포함하지 않습니다.

## 주요 가격 확인 출처

가격은 조회일과 객실 조건에 따라 달라질 수 있습니다.

- 창원 진해 김해공항 호텔 브라운도트: https://nol.yanolja.com/stay/domestic/1000101230
- 창원 그랜드시티호텔: https://nol.yanolja.com/stay/domestic/10059700
- 삼척 씨티앤고펜션: https://rev.yapen.co.kr/externalV2?ypIdx=27330
- 쏠비치 삼척: https://kr.hotels.com/ho625826/ssolbichi-samcheog-samcheog-hangug/
- 소노캄 여수: https://www.expedia.co.kr/Suncheon-Hotels-Sono-Calm-Yeosu.h5699310.Hotel-Information
- 씨크루즈호텔 속초: https://www.hotelscombined.co.kr/Hotel/Sea_Cruise_Hotel.htm
- 롯데리조트 속초: https://www.lotteresort.com/main/ko/reservation/room-list?urlLang=ko
- 무주 나오스펜션: https://kr.hotels.com/ho1456368544/muju-naoseupensyeon-muju-hangug/
- 무주 하늘길캠핑장: https://www.gocamping.or.kr/bsite/camp/info/read.do?c_no=101358
- 태백호텔: https://www.hotelscombined.co.kr/Hotel/Taebaek_Hotel.htm
- 보령 지역 숙소: https://www.hotelscombined.co.kr/Place/Boryeong.htm
- 안동 전통리조트 구름에: https://www.waug.com/ko/accommodations/31214
- 순천 에코그라드호텔: https://www.hotelscombined.co.kr/Hotel/Ecograd_Hotel.htm
- 라카이 샌드파인: https://lakaisandpine.com/package
- 라한셀렉트 경주: https://lahanhotels.com/gyeongju/ko/main.do
- 아난티 앳 부산 코브: https://ananti.kr/ko/busan
- 포천 지역 숙소: https://www.hotelscombined.co.kr/Place/Pocheon.htm
- 쏠비치 양양 등 양양 지역 숙소: https://kr.trip.com/hotels/yangyang-osan-ri-beach/hotels-c6430m60881709/
- 제천 지역 숙소: https://www.hotelscombined.co.kr/Place/Jecheon.htm
- 소노문 단양: https://kr.hotels.com/ho370556/sonomun-dan-yang-gu-daemyeonglijoteu-dan-yang-dan-yang-hangug/
- 켄싱턴리조트 충주: https://www.kensington.co.kr/rcj/room_info/detail?idx=201
- 라한호텔 포항: https://lahanhotels.com/pohang/ko/main.do
- 청송 한옥호텔 안: https://booking.kakao.com/detail/accommodation/285202
- 소노벨 청송: https://www.hotelscombined.co.kr/Hotel/Sono_Belle_Cheongsong.htm
- 주왕산 온천관광호텔: https://nol.yanolja.com/stay/domestic/10041107
- 바다호텔: https://nol.yanolja.com/stay/domestic/10045714
- 남해 스포츠파크 호텔: https://www.hotelscombined.co.kr/Hotel/Namhae_Sportpark_Hotel.htm
- 남해 지역 숙소: https://www.traveloka.com/ko-kr/hotel/south-korea/landmark/namhae-sports-park-91744080058754
- 에코랜드 호텔: https://www.kayak.co.kr/%EC%A0%9C%EC%A3%BC%EC%8B%9C-%ED%98%B8%ED%85%94-%EC%97%90%EC%BD%94%EB%9E%9C%EB%93%9C-%ED%98%B8%ED%85%94.8651584.ksp
- 유니호텔 제주: https://www.jeju.to/CS/Goods/Lodge/detail.aspx?cid=9760
- 켄싱턴리조트 서귀포: https://kensington.co.kr/rsw/room_info/detail?idx=193

## JSON 검증

PowerShell에서 다음 명령으로 JSON 문법을 확인합니다.

```powershell
.\venv\Scripts\python.exe -m json.tool app\data\destinations.json
.\venv\Scripts\python.exe -m json.tool app\data\accommodations.json
```

추가 검증 항목은 다음과 같습니다.

- 여행지 이름 중복 여부
- 계절별 여행지 개수
- 여행지별 숙소가 정확히 3개인지 여부
- 숙소가 참조하는 여행지가 존재하는지 여부
- 가격과 수용 인원이 양의 정수인지 여부
- 허용된 계절·목적·분위기·예산 값만 사용하는지 여부

## Seed 적용 순서

1. `destinations.json`을 읽어 여행지를 먼저 저장합니다.
2. 여행지 이름으로 기존 데이터를 확인해 중복 삽입을 방지합니다.
3. `accommodations.json`을 읽습니다.
4. `destination_name`으로 저장된 여행지를 조회합니다.
5. 여행지와 숙소 이름 조합으로 기존 숙소를 확인해 중복 삽입을 방지합니다.
6. 여러 번 실행해도 같은 결과가 나오도록 구현합니다.
