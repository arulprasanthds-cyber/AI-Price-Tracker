from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from flask_mail import Message

from datetime import datetime

from dashboard import dashboard

from extensions import db, mail

from models import Product, PriceHistory

from scraper.scraper_manager import get_product_details


# =========================================================
# DASHBOARD HOME
# =========================================================

@dashboard.route("/dashboard")
@login_required
def dashboard_home():

    products = Product.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Product.created_at.desc()
    ).all()

    total_products = len(products)

    tracking_products = Product.query.filter_by(
        user_id=current_user.id,
        status="Tracking"
    ).count()

    target_products = Product.query.filter_by(
        user_id=current_user.id,
        status="Target Reached"
    ).count()

    return render_template(
        "dashboard.html",
        products=products,
        total_products=total_products,
        tracking_products=tracking_products,
        target_products=target_products
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@dashboard.route(
    "/add-product",
    methods=["GET", "POST"]
)
@login_required
def add_product():

    if request.method == "POST":

        # =================================================
        # GET FORM DATA
        # =================================================

        product_url = request.form.get(
            "product_url",
            ""
        ).strip()

        target_price = request.form.get(
            "target_price",
            ""
        ).strip()


        # =================================================
        # URL VALIDATION
        # =================================================

        if not product_url:

            flash(
                "❌ Product URL is required.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        # =================================================
        # TARGET PRICE VALIDATION
        # =================================================

        if not target_price:

            flash(
                "❌ Target price is required.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        try:

            target_price_value = float(
                target_price
            )

            if target_price_value <= 0:

                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            flash(
                "❌ Please enter a valid target price.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        # =================================================
        # CHECK DUPLICATE PRODUCT
        # =================================================

        existing_product = Product.query.filter_by(
            user_id=current_user.id,
            product_url=product_url
        ).first()


        if existing_product:

            flash(
                "⚠️ You are already tracking this product.",
                "warning"
            )

            return redirect(
                url_for("dashboard.dashboard_home")
            )


        # =================================================
        # SCRAPE PRODUCT
        # =================================================

        print()
        print("==========================================")
        print("🔍 ADDING NEW PRODUCT")
        print("==========================================")
        print(
            f"🔗 URL: {product_url}"
        )
        print(
            f"🎯 Target: ₹{target_price_value:.2f}"
        )


        try:

            result = get_product_details(
                product_url
            )

        except Exception as e:

            print(
                f"❌ Scraper exception: {e}"
            )

            flash(
                "❌ Unable to read product details from this URL.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        # =================================================
        # SCRAPER RESULT VALIDATION
        # =================================================

        if not result:

            flash(
                "❌ Product scraper returned no data.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        if not result.get("success"):

            error_message = result.get(
                "error",
                "Unable to fetch product details."
            )

            print(
                f"❌ Scraping failed: {error_message}"
            )

            flash(
                f"❌ {error_message}",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        # =================================================
        # GET AUTOMATIC PRODUCT NAME
        # =================================================

        product_name = result.get(
            "product_name"
        )


        if not product_name:

            product_name = "Unknown Product"


        # =================================================
        # GET AUTOMATIC CURRENT PRICE
        # =================================================

        scraped_price = result.get(
            "current_price"
        )


        if scraped_price is None:

            flash(
                "❌ Current product price could not be detected.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        try:

            current_price_value = float(
                scraped_price
            )

        except (
            TypeError,
            ValueError
        ):

            flash(
                "❌ Scraper returned an invalid price.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        if current_price_value <= 0:

            flash(
                "❌ Invalid product price detected.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        # =================================================
        # GET AUTOMATIC PRODUCT IMAGE
        # =================================================

        image_url = result.get(
            "image"
        )


        # =================================================
        # WEBSITE
        # =================================================

        website = result.get(
            "website",
            "unknown"
        )


        # =================================================
        # DETERMINE INITIAL STATUS
        # =================================================

        if current_price_value <= target_price_value:

            product_status = "Target Reached"

        else:

            product_status = "Tracking"


        # =================================================
        # CREATE PRODUCT
        # =================================================

        product = Product(

            user_id=current_user.id,

            product_name=product_name,

            product_url=product_url,

            image_url=image_url,

            current_price=current_price_value,

            target_price=target_price_value,

            price_direction="Same",

            status=product_status,

            last_checked=datetime.utcnow(),

            created_at=datetime.utcnow()

        )


        # =================================================
        # SAVE PRODUCT
        # =================================================

        try:

            db.session.add(product)

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                f"❌ Product database save failed: {e}"
            )

            flash(
                "❌ Could not save the product.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )


        # =================================================
        # FIRST PRICE HISTORY
        # =================================================

        try:

            history = PriceHistory(

                product_id=product.id,

                price=current_price_value,

                checked_at=datetime.utcnow()

            )

            db.session.add(history)

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                f"⚠️ Price history save failed: {e}"
            )


        # =================================================
        # LOG
        # =================================================

        print()
        print("==========================================")
        print("✅ PRODUCT SAVED SUCCESSFULLY")
        print("==========================================")

        print(
            f"👤 User: {current_user.username}"
        )

        print(
            f"🌐 Website: {website.upper()}"
        )

        print(
            f"📦 Product: {product_name}"
        )

        print(
            f"💰 Current Price: "
            f"₹{current_price_value:.2f}"
        )

        print(
            f"🎯 Target Price: "
            f"₹{target_price_value:.2f}"
        )

        print(
            f"📌 Status: {product_status}"
        )

        print("==========================================")


        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        flash(
            "✅ Product added successfully! "
            "Automatic price tracking started.",
            "success"
        )


        return redirect(
            url_for("dashboard.dashboard_home")
        )


    # =====================================================
    # GET REQUEST
    # =====================================================

    return render_template(
        "add_product.html"
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@dashboard.route(
    "/delete-product/<int:id>"
)
@login_required
def delete_product(id):

    product = Product.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()


    if not product:

        flash(
            "❌ Product not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )


    product_name = product.product_name


    # =====================================================
    # DELETE PRICE HISTORY
    # =====================================================

    try:

        PriceHistory.query.filter_by(
            product_id=product.id
        ).delete()

    except Exception as e:

        print(
            f"⚠️ Price history delete error: {e}"
        )


    # =====================================================
    # DELETE PRODUCT
    # =====================================================

    try:

        db.session.delete(product)

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        flash(
            "❌ Could not delete product.",
            "danger"
        )

        print(
            f"❌ Delete error: {e}"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )


    print()
    print(
        f"🗑️ Product deleted: {product_name}"
    )


    flash(
        "🗑️ Product deleted successfully.",
        "success"
    )


    return redirect(
        url_for("dashboard.dashboard_home")
    )


# =========================================================
# PRICE HISTORY
# =========================================================

@dashboard.route(
    "/product-history/<int:id>"
)
@login_required
def product_history(id):

    product = Product.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    history = PriceHistory.query.filter_by(
        product_id=product.id
    ).order_by(
        PriceHistory.checked_at.asc()
    ).all()


    prices = []

    dates = []


    for item in history:

        prices.append(
            float(item.price)
        )

        dates.append(
            item.checked_at.strftime(
                "%d-%m-%Y %H:%M"
            )
        )


    return render_template(

        "price_history.html",

        product=product,

        prices=prices,

        dates=dates

    )


# =========================================================
# TEST EMAIL
# =========================================================

@dashboard.route(
    "/test-email/<int:id>"
)
@login_required
def test_email(id):

    # =====================================================
    # FIND USER'S PRODUCT
    # =====================================================

    product = Product.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()


    if not product:

        flash(
            "❌ Product not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )


    # =====================================================
    # CHECK EMAIL
    # =====================================================

    if not current_user.email:

        flash(
            "❌ Your account email is missing.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )


    # =====================================================
    # SEND TEST EMAIL
    # =====================================================

    try:

        msg = Message(

            subject="🔔 AI Price Tracker - Test Email",

            recipients=[
                current_user.email
            ]

        )


        msg.body = f"""
Hello {current_user.username},

This is a test email from AI Price Tracker.

========================================
PRODUCT DETAILS
========================================

Product Name  : {product.product_name}

Current Price : ₹{product.current_price:.2f}

Target Price  : ₹{product.target_price:.2f}

Status        : {product.status}

Price Direction: {product.price_direction}

========================================

Your email notification system is working successfully.

AI Price Tracker
Automatic Price Monitoring System
"""


        mail.send(msg)


        print()
        print("==========================================")
        print("✅ TEST EMAIL SENT SUCCESSFULLY")
        print(
            f"📧 To: {current_user.email}"
        )
        print(
            f"📦 Product: {product.product_name}"
        )
        print("==========================================")


        flash(
            "📧 Test email sent successfully!",
            "success"
        )


    except Exception as e:

        print()
        print("==========================================")
        print("❌ EMAIL SENDING FAILED")
        print(
            f"❌ Error: {e}"
        )
        print("==========================================")


        flash(
            f"❌ Email sending failed: {e}",
            "danger"
        )


    return redirect(
        url_for("dashboard.dashboard_home")
    )