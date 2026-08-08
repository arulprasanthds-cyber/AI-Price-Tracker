from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


from auth import auth

from extensions import db

from models import User



# ======================================
# Register
# ======================================

@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard_home"
            )
        )


    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        email = request.form.get(
            "email"
        ).lower()


        password = request.form.get(
            "password"
        )


        confirm_password = request.form.get(
            "confirm_password"
        )


        if password != confirm_password:

            flash(
                "Passwords do not match",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.register"
                )
            )


        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "Email already registered",
                "warning"
            )

            return redirect(
                url_for(
                    "auth.register"
                )
            )


        hashed_password = generate_password_hash(
            password
        )


        user = User(

            username=username,

            email=email,

            password=hashed_password

        )


        db.session.add(
            user
        )

        db.session.commit()


        flash(
            "Registration successful. Login now.",
            "success"
        )


        return redirect(
            url_for(
                "auth.login"
            )
        )


    return render_template(
        "register.html"
    )



# ======================================
# Login
# ======================================

@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard_home"
            )
        )


    if request.method == "POST":

        email = request.form.get(
            "email"
        ).lower()


        password = request.form.get(
            "password"
        )


        user = User.query.filter_by(
            email=email
        ).first()



        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(
                user
            )


            flash(
                "Login successful",
                "success"
            )


            return redirect(
                url_for(
                    "dashboard.dashboard_home"
                )
            )


        flash(
            "Invalid email or password",
            "danger"
        )


    return render_template(
        "login.html"
    )



# ======================================
# Logout
# ======================================

@auth.route("/logout")
@login_required
def logout():


    logout_user()


    flash(
        "Logged out successfully",
        "success"
    )


    return redirect(
        url_for(
            "auth.login"
        )
    )