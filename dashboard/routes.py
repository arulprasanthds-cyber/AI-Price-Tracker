
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

        product_name = request.form.get(
            "product_name",
            ""
        ).strip()

        product_url = request.form.get(
            "product_url",
            ""
        ).strip()

        current_price = request.form.get(
            "current_price",
            ""
        ).strip()

        target_price = request.form.get(
            "target_price",
            ""
        ).strip()

        # =================================================
        # VALIDATION
        # =================================================

        if not product_name:

            flash(
                "Product name is required.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )

        if not product_url:

            flash(
                "Product URL is required.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )

        if not target_price:

            flash(
                "Target price is required.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )

        # =================================================
        # TARGET PRICE
        # =================================================

        try:

            target_price_value = float(
                target_price
            )

            if target_price_value <= 0:
                raise ValueError

        except (ValueError, TypeError):

            flash(
                "Please enter a valid target price.",
                "danger"
            )

            return redirect(
                url_for("dashboard.add_product")
            )

        # =================================================
        # SCRAPE PRODUCT
        # =================================================

        scraped_price = None
        image_url = None
        scraped_name = None

        try:

            result = get_product_details(
                product_url
            )

            if result and result.get("success"):

                scraped_price = result.get(
                    "current_price"
                )

                image_url = result.get(
                    "image"
                )

                scraped_name = result.get(
                    "product_name"
                )

        except Exception as e:

            print(
                f"⚠️ Product scraping error: {e}"
            )

        # =================================================
        # CURRENT PRICE
        # =================================================

        current_price_value = None

        if scraped_price is not None:

            try:

                current_price_value = float(
                    scraped_price
                )

                if current_price_value <= 0:
                    current_price_value = None

            except (
                TypeError,
                ValueError
            ):

                current_price_value = None

        # =================================================
        # MANUAL PRICE FALLBACK
        # =================================================

        if current_price_value is None:

            if not current_price:

                flash(
                    "Could not fetch product price. "
                    "Please enter current price manually.",
                    "danger"
                )

                return redirect(
                    url_for("dashboard.add_product")
                )

            try:

                current_price_value = float(
                    current_price
                )

                if current_price_value <= 0:
                    raise ValueError

            except (
                ValueError,
                TypeError
            ):

                flash(
                    "Please enter a valid current price.",
                    "danger"
                )

                return redirect(
                    url_for("dashboard.add_product")
                )

        # =================================================
        # PRODUCT NAME
        # =================================================

        final_product_name = (
            scraped_name
            if scraped_name
            else product_name
        )

        # =================================================
        # PRODUCT STATUS
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
            product_name=final_product_name,
            product_url=product_url,
            image_url=image_url,
            current_price=current_price_value,
            target_price=target_price_value,
            price_direction="Same",
            status=product_status,
            last_checked=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        db.session.add(product)

        db.session.commit()

        # =================================================
        # FIRST PRICE HISTORY
        # =================================================

        history = PriceHistory(
            product_id=product.id,
            price=current_price_value,
            checked_at=datetime.utcnow()
        )

        db.session.add(history)

        db.session.commit()

        print(
            f"✅ Product saved permanently: "
            f"{final_product_name}"
        )

        print(
            f"👤 Owner: {current_user.email}"
        )

        flash(
            "✅ Product added and saved successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )

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
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )

    product_name = product.product_name

    # Delete price history
    PriceHistory.query.filter_by(
        product_id=product.id
    ).delete()

    # Delete product
    db.session.delete(product)

    db.session.commit()

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
    # FIND USER'S OWN PRODUCT
    # =====================================================

    product = Product.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard_home")
        )

    # =====================================================
    # SEND EMAIL
    # =====================================================

    try:

        msg = Message(
            subject="AI Price Tracker - Test Email",
            recipients=[
                current_user.email
            ]
        )

        msg.body = f"""
Hello {current_user.username},

This is a test email from AI Price Tracker.

----------------------------------------
PRODUCT DETAILS
----------------------------------------

Product Name : {product.product_name}
Current Price: ₹{product.current_price}
Target Price : ₹{product.target_price}
Status       : {product.status}

----------------------------------------

Your email notification system is working successfully.

AI Price Tracker
"""

        mail.send(msg)

        print(
            "=========================================="
        )

        print(
            "✅ TEST EMAIL SENT SUCCESSFULLY"
        )

        print(
            f"📧 To: {current_user.email}"
        )

        print(
            f"📦 Product: {product.product_name}"
        )

        print(
            "=========================================="
        )

        flash(
            "📧 Test email sent successfully!",
            "success"
        )

    except Exception as e:

        print(
            "=========================================="
        )

        print(
            "❌ EMAIL SENDING FAILED"
        )

        print(
            f"❌ Error: {e}"
        )

        print(
            "=========================================="
        )

        flash(
            f"❌ Email sending failed: {e}",
            "danger"
        )

    return redirect(
        url_for("dashboard.dashboard_home")
    )
