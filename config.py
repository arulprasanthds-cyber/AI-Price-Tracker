import os


class Config:

    # ==========================================
    # Flask Security
    # ==========================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key"
    )


    # ==========================================
    # Database
    # ==========================================

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:

        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:

        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///product_tracker.db"
        )


    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ==========================================
    # Gmail
    # ==========================================

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv("arulprasanthds@gmail.com")
    MAIL_PASSWORD = os.getenv("aidkjidcuxcqvsdu")