
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

from datetime import datetime

from dashboard import dashboard

from extensions import db

from models import Product, PriceHistory

from scraper.scraper_manager import get_product_details


# ==========================================
# Dashboard Home
# ==========================================

@dashboard.route("/dashboard")
@login_required
def dashboard_home():

    # Only show products belonging to logged-in user
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


# ==========================================
# Add Product
# ==========================================

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


        # --------------------------------------
        # Validate Required Fields
        # --------------------------------------

        if not product_name:
            flash(
                "Product name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "dashboard.add_product"
                )
            )


        if not product_url:
            flash(
                "Product URL is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "dashboard.add_product"
                )
            )


        if not target_price:
            flash(
                "Target price is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "dashboard.add_product"
                )
            )


        # --------------------------------------
        # Convert Target Price
        # --------------------------------------

        try:

            target_price_value = float(
                target_price
            )

            if target_price_value <= 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid target price.",
                "danger"
            )

            return redirect(
                url_for(
                    "dashboard.add_product"
                )
            )


        # --------------------------------------
        # Try to Fetch Product Details
        # --------------------------------------

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


        # --------------------------------------
        # Determine Current Price
        # --------------------------------------

        if scraped_price is not None:

            try:

                current_price_value = float(
                    scraped_price
                )

            except (TypeError, ValueError):

                current_price_value = None

        else:

            current_price_value = None


        # --------------------------------------
        # Fallback to Manual Price
        # --------------------------------------

        if current_price_value is None:

            if not current_price:

                flash(
                    "Could not fetch product price. "
                    "Please enter current price manually.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "dashboard.add_product"
                    )
                )

            try:

                current_price_value = float(
                    current_price
                )

                if current_price_value <= 0:
                    raise ValueError

            except ValueError:

                flash(
                    "Please enter a valid current price.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "dashboard.add_product"
                    )
                )


        # --------------------------------------
        # Use Scraped Product Name
        # --------------------------------------

        final_product_name = (
            scraped_name
            if scraped_name
            else product_name
        )


        # --------------------------------------
        # Create Product
        # --------------------------------------

        product = Product(

            user_id=current_user.id,

            product_name=final_product_name,

            product_url=product_url,

            image_url=image_url,

            current_price=current_price_value,

            target_price=target_price_value,

            status=(
                "Target Reached"
                if current_price_value <= target_price_value
                else "Tracking"
            ),

            price_direction="Same",

            last_checked=datetime.utcnow(),

            created_at=datetime.utcnow()

        )


        db.session.add(
            product
        )

        db.session.commit()


        # --------------------------------------
        # First Price History Record
        # --------------------------------------

        price_history = PriceHistory(

            product_id=product.id,

            price=current_price_value,

            checked_at=datetime.utcnow()

        )

        db.session.add(
            price_history
        )

        db.session.commit()


        flash(
            "✅ Product Added Successfully!",
            "success"
        )


        return redirect(
            url_for(
                "dashboard.dashboard_home"
            )
        )


    return render_template(
        "add_product.html"
    )


# ==========================================
# Delete Product
# ==========================================

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
            url_for(
                "dashboard.dashboard_home"
            )
        )


    db.session.delete(
        product
    )

    db.session.commit()


    flash(
        "🗑️ Product Deleted Successfully.",
        "success"
    )


    return redirect(
        url_for(
            "dashboard.dashboard_home"
        )
    )


# ==========================================
# Price History Graph
# ==========================================

@dashboard.route(
    "/product-history/<int:id>"
)
@login_required
def product_history(id):

    # Make sure product belongs to current user
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

