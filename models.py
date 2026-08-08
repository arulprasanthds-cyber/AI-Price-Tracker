
from datetime import datetime

from flask_login import UserMixin

from extensions import db


# ==========================================
# USER MODEL
# ==========================================

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # --------------------------------------
    # One User -> Many Products
    # --------------------------------------

    products = db.relationship(
        "Product",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ==========================================
# PRODUCT MODEL
# ==========================================

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------
    # Product belongs to User
    # --------------------------------------

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    product_name = db.Column(
        db.String(200),
        nullable=False
    )

    product_url = db.Column(
        db.String(500),
        nullable=False
    )

    image_url = db.Column(
        db.String(500),
        nullable=True
    )

    current_price = db.Column(
        db.Float,
        nullable=False
    )

    target_price = db.Column(
        db.Float,
        nullable=False
    )

    # --------------------------------------
    # Price Direction
    # --------------------------------------

    price_direction = db.Column(
        db.String(20),
        default="Same",
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Tracking",
        nullable=False
    )

    last_checked = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # --------------------------------------
    # Product -> Many Price History Records
    # --------------------------------------

    price_history = db.relationship(
        "PriceHistory",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ==========================================
# PRICE HISTORY MODEL
# ==========================================

class PriceHistory(db.Model):

    __tablename__ = "price_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    checked_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

