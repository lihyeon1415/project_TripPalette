from app import db

# 회원 계정 정보를 저장하는 모델, 이메일을 로그인 계정으로사용 ,중복가입 x
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),
                       nullable=False,
                        unique=True,
                        )
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )
    withdrawal_requested_at = db.Column(db.DateTime, nullable=True)
    scheduled_deletion_at = db.Column(
        db.DateTime,
        nullable=True,
        index=True,
    )

    preference = db.relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
    )
    favorites = db.relationship("Favorite", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")
    accommodation_reviews = db.relationship(
        "AccommodationReview",
        back_populates="user",
    )
    reservations = db.relationship("Reservation", back_populates="user")


# 회원의 맞춤 여행지 추천 조건 저장 모델 , 한명당 하나의 최신 설정만 저장, id당 unique 제약조건적으로 1:1 관계
class UserPreference(db.Model):
    __tablename__ = "user_preference"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )
    season = db.Column(db.String(20))
    companion = db.Column(db.String(20))
    purpose = db.Column(db.String(20))
    atmosphere = db.Column(db.String(20))
    budget = db.Column(db.Integer)
    trip_duration = db.Column(db.Integer)

    # 추천 조건이 변경될 떄마다 마지막 수정시각을 갱신
    updated_at = db.Column(
        db.DateTime,
        default=db.func.now(),
        onupdate=db.func.now(),
        server_default=db.func.current_timestamp(),
    )

    user = db.relationship("User", back_populates="preference")

# 추천 및 탐색 대상이 되는 국내 여행지 정보를 저장하는 모델
class Destination(db.Model):
    __tablename__ = "destination"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    season = db.Column(db.String(20))
    purpose = db.Column(db.String(20))
    atmosphere = db.Column(db.String(20))
    budget_level = db.Column(db.String(20))
    recommended_days = db.Column(db.Integer)
    image_url = db.Column(db.String(255))

    favorites = db.relationship("Favorite", back_populates="destination")
    reviews = db.relationship("Review", back_populates="destination")
    accommodations = db.relationship("Accommodation", back_populates="destination")



# 회원이 찜한 여행지를 저장하는 연결 모델 , 동일한 회원이 같은 여행지를 중복으로 찜하지 못하도록 id와 destination_id에 복합 unique제약조건을 적용
class Favorite(db.Model):
    __tablename__ = "favorite"

    # 회원별 동일 여행지의 중복찜 방지
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "destination_id",
            name="uq_favorite_user_destination",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("destination.id"),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )

    user = db.relationship("User", back_populates="favorites")
    destination = db.relationship("Destination", back_populates="favorites")


# 회원이 여행지에 작성한 리뷰와 평점을 저장하는 모델
class Review(db.Model):
    __tablename__ = "review"
    __table_args__ = (

        # 동일 회원의 동일 여행지 중복 리뷰 방지
        db.UniqueConstraint(
            "user_id",
            "destination_id",
            name="uq_review_user_destination",
        ),
        db.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_review_rating_range",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("destination.id"),
        nullable=False,
    )
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )

    user = db.relationship("User", back_populates="reviews")
    destination = db.relationship("Destination", back_populates="reviews")


# 여행지 주변의 숙소 정보를 저장
# destination = 추천 탐색 찜 리뷰 대상
# Accommmodation = 예약 대상
class Accommodation(db.Model):
    __tablename__ = "accommodation"

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(
        db.Integer,
        db.ForeignKey("destination.id"),
        nullable=False,
    )
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price_per_night = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Numeric(2, 1))
    image_url = db.Column(db.String(255))

    destination = db.relationship("Destination", back_populates="accommodations")
    reservations = db.relationship("Reservation", back_populates="accommodation")
    reviews = db.relationship(
        "AccommodationReview",
        back_populates="accommodation",
    )


class AccommodationReview(db.Model):
    __tablename__ = "accommodation_review"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "accommodation_id",
            name="uq_accommodation_review_user_accommodation",
        ),
        db.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_accommodation_review_rating_range",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    accommodation_id = db.Column(
        db.Integer,
        db.ForeignKey("accommodation.id"),
        nullable=False,
    )
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )

    user = db.relationship("User", back_populates="accommodation_reviews")
    accommodation = db.relationship("Accommodation", back_populates="reviews")


# 회원의 숙소 예약 정보를 저장하는 모델

class Reservation(db.Model):
    __tablename__ = "reservation"
    __table_args__ = (

        # 체크인은 체크아웃보다 먼저
        db.CheckConstraint(
            "check_in < check_out",
            name="ck_reservation_date_range",
        ),

        # 최소 예약 인원은 1명
        db.CheckConstraint(
            "people_count >= 1",
            name="ck_reservation_people_count_positive",
        ),

        # 총예약 금액은 음수 x
        db.CheckConstraint(
            "total_price >= 0",
            name="ck_reservation_total_price_nonnegative",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    accommodation_id = db.Column(
        db.Integer,
        db.ForeignKey("accommodation.id"),
        nullable=False,
    )
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    people_count = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )

    user = db.relationship("User", back_populates="reservations")
    accommodation = db.relationship("Accommodation", back_populates="reservations")
    # 예약 한건에는 하나의 최종결제정보만 연결
    payment = db.relationship("Payment", back_populates="reservation", uselist=False)

    # ======================================
    #people_count가 accommodation.capacity 이하인지는
    # 다른 테이블 값을 확인해야 하므로 예약 처리 로직에서 검증한다.
    # ===========================================

# 숙소 예약에 대한 모의 결제정보를 저장
class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)

    # 예약 한건당 하나의 최종 결제정보만 허용
    reservation_id = db.Column(
        db.Integer,
        db.ForeignKey("reservation.id"),
        nullable=False,
        unique=True,
    )
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="READY",
        server_default="READY",
    )
    # 결졔가 성공하기 전에는 NUll이며 성공 시점에만 기록
    paid_at = db.Column(db.DateTime)

    reservation = db.relationship("Reservation", back_populates="payment")
