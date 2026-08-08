from flask import Flask, redirect, url_for

from config import Config

from extensions import (
    db,
    login_manager,
    mail
)

# ======================================
# Blueprints
# ======================================

from auth import auth
from dashboard import dashboard

from models import User

from scheduler.scheduler import start_scheduler


# ======================================
# Create Flask App
# ======================================

def create_app():

    app = Flask(__name__)

    # ==================================
    # Config
    # ==================================

    app.config.from_object(Config)

    # ==================================
    # Extensions Initialize
    # ==================================

    db.init_app(app)

    login_manager.init_app(app)

    mail.init_app(app)

    # ==================================
    # Register Blueprints
    # ==================================

    app.register_blueprint(auth)

    app.register_blueprint(dashboard)

    # ==================================
    # Login User Loader
    # ==================================

    @login_manager.user_loader
    def load_user(user_id):

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return None

        return db.session.get(User, user_id)

    # ==================================
    # Home Route
    # ==================================

    @app.route("/")
    def home():

        return redirect(
            url_for("auth.login")
        )

    # ==================================
    # Create Database
    # ==================================

    with app.app_context():

        db.create_all()

    # ==================================
    # Start Scheduler
    # ==================================

    start_scheduler(app)

    

    return app


# ======================================
# Run Application
# ======================================

if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True,
        use_reloader=False
    )

