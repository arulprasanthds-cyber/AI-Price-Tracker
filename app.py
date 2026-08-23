import os

from dotenv import load_dotenv

from flask import Flask, redirect

from extensions import db, login_manager, mail


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CREATE APP
# =========================================================

app = Flask(__name__)


# =========================================================
# SECRET KEY
# =========================================================

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "development-secret-key-change-me"
)


# =========================================================
# DATABASE
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///price_tracker.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================================================
# FLASK-MAIL CONFIGURATION
# =========================================================

app.config["MAIL_SERVER"] = os.environ.get(
    "MAIL_SERVER",
    "smtp.gmail.com"
)

app.config["MAIL_PORT"] = int(
    os.environ.get(
        "MAIL_PORT",
        "587"
    )
)

app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.environ.get(
    "MAIL_USERNAME",
    ""
)

app.config["MAIL_PASSWORD"] = os.environ.get(
    "MAIL_PASSWORD",
    ""
)

app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER",
    app.config["MAIL_USERNAME"]
)


# =========================================================
# INITIALIZE EXTENSIONS
# =========================================================

db.init_app(app)

login_manager.init_app(app)

mail.init_app(app)


# =========================================================
# LOGIN MANAGER
# =========================================================

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Please login to continue."
)

login_manager.login_message_category = "warning"


# =========================================================
# USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    from models import User

    try:

        return db.session.get(
            User,
            int(user_id)
        )

    except Exception as e:

        print(
            f"❌ User loader error: {e}"
        )

        return None


# =========================================================
# REGISTER BLUEPRINTS
# =========================================================

from auth import auth
from dashboard import dashboard

app.register_blueprint(auth)

app.register_blueprint(dashboard)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

with app.app_context():

    from models import (
        User,
        Product,
        PriceHistory
    )

    db.create_all()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return redirect("/dashboard")


# =========================================================
# 404 ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    """, 404


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    print()
    print(
        "=========================================="
    )

    print(
        "🚀 AI PRICE TRACKER"
    )

    print(
        "=========================================="
    )

    print(
        "🌐 http://127.0.0.1:5000"
    )

    print(
        "📦 Database: SQLite"
    )

    print(
        "👤 Multi-user system: Enabled"
    )

    print(
        "📧 Email system: Enabled"
    )

    print(
        "⏱️ Automatic tracking: 30 minutes"
    )

    print(
        "=========================================="
    )


    # =====================================================
    # EMAIL CONFIGURATION CHECK
    # =====================================================

    if app.config["MAIL_USERNAME"]:

        print(
            f"📧 Email account: "
            f"{app.config['MAIL_USERNAME']}"
        )

    else:

        print(
            "⚠️ MAIL_USERNAME is not configured."
        )


    if app.config["MAIL_PASSWORD"]:

        print(
            "🔐 Email password: Configured"
        )

    else:

        print(
            "⚠️ MAIL_PASSWORD is not configured."
        )


    print()


    # =====================================================
    # START SCHEDULER
    # =====================================================

    from scheduler.scheduler import start_scheduler


    # Flask debug reloader can create two processes.
    # Start scheduler only in the serving process.

    if (
        not app.debug
        or os.environ.get(
            "WERKZEUG_RUN_MAIN"
        ) == "true"
    ):

        try:

            start_scheduler(app)

        except Exception as e:

            print(
                f"❌ Scheduler startup failed: {e}"
            )


    print()


    # =====================================================
    # RUN FLASK
    # =====================================================

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False

    )