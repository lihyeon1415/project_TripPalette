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
    payment_customer_key = db.Column(
        db.String(64),
        nullable=True,
        unique=True,
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
    goods_orders = db.relationship("GoodsOrder", back_populates="user")


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
        default="PAYMENT_PENDING",
        server_default="PAYMENT_PENDING",
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )
    expires_at = db.Column(db.DateTime, nullable=True, index=True)

    user = db.relationship("User", back_populates="reservations")
    accommodation = db.relationship("Accommodation", back_populates="reservations")
    # 예약 한건에는 하나의 최종결제정보만 연결
    payment = db.relationship("Payment", back_populates="reservation", uselist=False)

    # ======================================
    #people_count가 accommodation.capacity 이하인지는
    # 다른 테이블 값을 확인해야 하므로 예약 처리 로직에서 검증한다.
    # ===========================================

class Product(db.Model):
    __tablename__ = "product"
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="ck_product_price_nonnegative"),
        db.CheckConstraint(
            "stock_quantity >= 0",
            name="ck_product_stock_quantity_nonnegative",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    thumbnail_url = db.Column(db.String(255))
    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=True,
        default=db.func.now(),
        onupdate=db.func.now(),
        server_default=db.func.current_timestamp(),
    )

    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )
    categories = db.relationship(
        "ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    order_items = db.relationship("GoodsOrderItem", back_populates="product")


class ProductCategory(db.Model):
    __tablename__ = "product_category"
    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "category",
            name="uq_product_category_product_category",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False,
    )
    category = db.Column(db.String(30), nullable=False, index=True)

    product = db.relationship("Product", back_populates="categories")


class ProductImage(db.Model):
    __tablename__ = "product_image"
    __table_args__ = (
        db.UniqueConstraint(
            "product_id",
            "sort_order",
            name="uq_product_image_product_sort_order",
        ),
        db.CheckConstraint(
            "sort_order >= 0",
            name="ck_product_image_sort_order_nonnegative",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False,
    )
    image_url = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0, server_default="0")

    product = db.relationship("Product", back_populates="images")


class GoodsOrder(db.Model):
    __tablename__ = "goods_order"
    __table_args__ = (
        db.CheckConstraint(
            "items_amount >= 0",
            name="ck_goods_order_items_amount_nonnegative",
        ),
        db.CheckConstraint(
            "shipping_fee >= 0",
            name="ck_goods_order_shipping_fee_nonnegative",
        ),
        db.CheckConstraint(
            "total_amount >= 0",
            name="ck_goods_order_total_amount_nonnegative",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), nullable=False, unique=True)
    # 탈퇴 후에도 거래 기록은 보존하고 회원 연결과 배송 개인정보만 익명화한다.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    recipient_name = db.Column(db.String(50), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    address_detail = db.Column(db.String(255))
    delivery_request = db.Column(db.String(255))
    items_amount = db.Column(db.Integer, nullable=False)
    shipping_fee = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.String(30),
        nullable=False,
        default="PAYMENT_PENDING",
        server_default="PAYMENT_PENDING",
    )
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )
    paid_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="goods_orders")
    items = db.relationship(
        "GoodsOrderItem",
        back_populates="goods_order",
        cascade="all, delete-orphan",
    )
    payment = db.relationship(
        "Payment",
        back_populates="goods_order",
        uselist=False,
    )


class GoodsOrderItem(db.Model):
    __tablename__ = "goods_order_item"
    __table_args__ = (
        db.CheckConstraint(
            "unit_price >= 0",
            name="ck_goods_order_item_unit_price_nonnegative",
        ),
        db.CheckConstraint(
            "quantity >= 1",
            name="ck_goods_order_item_quantity_positive",
        ),
        db.CheckConstraint(
            "subtotal >= 0",
            name="ck_goods_order_item_subtotal_nonnegative",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    goods_order_id = db.Column(
        db.Integer,
        db.ForeignKey("goods_order.id"),
        nullable=False,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False,
    )
    product_name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

    goods_order = db.relationship("GoodsOrder", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")


# 숙소 예약과 굿즈 주문의 테스트 결제정보를 공통으로 저장
class Payment(db.Model):
    __tablename__ = "payment"
    __table_args__ = (
        db.CheckConstraint(
            "(reservation_id IS NOT NULL AND goods_order_id IS NULL) OR "
            "(reservation_id IS NULL AND goods_order_id IS NOT NULL)",
            name="ck_payment_exactly_one_target",
        ),
        db.CheckConstraint(
            "amount >= 0",
            name="ck_payment_amount_nonnegative",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    # 예약 한건당 하나의 최종 결제정보만 허용
    reservation_id = db.Column(
        db.Integer,
        db.ForeignKey("reservation.id"),
        nullable=True,
        unique=True,
    )
    goods_order_id = db.Column(
        db.Integer,
        db.ForeignKey("goods_order.id"),
        nullable=True,
        unique=True,
    )
    merchant_order_id = db.Column(db.String(64), nullable=True, unique=True)
    provider = db.Column(
        db.String(20),
        nullable=False,
        default="TOSS",
        server_default="TOSS",
    )
    payment_key = db.Column(db.String(200), nullable=True, unique=True)
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), nullable=True)
    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="READY",
        server_default="READY",
    )
    requested_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.current_timestamp(),
    )
    # 결제가 성공하기 전에는 NULL이며 성공 시점에만 기록
    paid_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    failure_code = db.Column(db.String(100))
    failure_message = db.Column(db.String(255))
    idempotency_key = db.Column(db.String(64), nullable=True, unique=True)

    reservation = db.relationship("Reservation", back_populates="payment")
    goods_order = db.relationship("GoodsOrder", back_populates="payment")
