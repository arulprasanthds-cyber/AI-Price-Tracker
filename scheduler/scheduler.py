from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from flask_mail import Message

from extensions import db, mail
from models import Product, PriceHistory

from scraper.scraper_manager import get_product_details


# =========================================================
# SCHEDULER
# =========================================================

scheduler = BackgroundScheduler()


# =========================================================
# SEND PRICE DROP EMAIL
# =========================================================

def send_price_drop_email(
    owner_email,
    product_name,
    old_price,
    new_price,
    target_price
):

    try:

        # -------------------------------------------------
        # PRICE DROP VALIDATION
        # -------------------------------------------------

        if new_price >= old_price:

            print(
                "ℹ️ No price drop. Email not sent."
            )

            return False


        price_drop = old_price - new_price


        # -------------------------------------------------
        # CREATE EMAIL
        # -------------------------------------------------

        msg = Message(
            subject="🔔 AI Price Tracker - Price Drop Alert",
            recipients=[owner_email]
        )


        msg.body = f"""
Hello,

Good news! 🎉

The price of your tracked product has dropped.

==========================================
        PRICE DROP ALERT
==========================================

Product      : {product_name}

Old Price    : ₹{old_price:.2f}

New Price    : ₹{new_price:.2f}

Price Drop   : ₹{price_drop:.2f}

Target Price : ₹{target_price:.2f}

==========================================

AI Price Tracker
Automatic Price Monitoring System
"""


        # -------------------------------------------------
        # SEND EMAIL
        # -------------------------------------------------

        mail.send(msg)


        print()
        print(
            "=========================================="
        )

        print(
            "📧 PRICE DROP EMAIL SENT"
        )

        print(
            f"📧 To: {owner_email}"
        )

        print(
            f"📦 Product: {product_name}"
        )

        print(
            f"💰 ₹{old_price:.2f} → ₹{new_price:.2f}"
        )

        print(
            f"📉 Price Drop: ₹{price_drop:.2f}"
        )

        print(
            f"🎯 Target: ₹{target_price:.2f}"
        )

        print(
            "=========================================="
        )


        return True


    except Exception as e:

        print()
        print(
            "=========================================="
        )

        print(
            "❌ PRICE DROP EMAIL FAILED"
        )

        print(
            f"📧 To: {owner_email}"
        )

        print(
            f"📦 Product: {product_name}"
        )

        print(
            f"❌ Error: {e}"
        )

        print(
            "=========================================="
        )


        return False


# =========================================================
# CHECK ALL PRODUCT PRICES
# =========================================================

def check_product_prices(app):

    print()
    print(
        "=========================================="
    )

    print(
        "🔄 CHECKING PRODUCT PRICES"
    )

    print(
        f"🕒 Time: "
        f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )

    print(
        "=========================================="
    )


    with app.app_context():

        try:

            # -------------------------------------------------
            # GET ALL PRODUCTS
            # -------------------------------------------------

            products = Product.query.order_by(
                Product.id.asc()
            ).all()


            if not products:

                print(
                    "ℹ️ No products found."
                )

                print(
                    "💡 Add a product from the dashboard."
                )

                return


            print(
                f"📦 Products found: {len(products)}"
            )


            # =================================================
            # CHECK EACH PRODUCT
            # =================================================

            for product in products:

                try:

                    print()
                    print(
                        "------------------------------------------"
                    )

                    print(
                        f"🔍 Checking: "
                        f"{product.product_name}"
                    )

                    print(
                        f"👤 Owner ID: "
                        f"{product.user_id}"
                    )

                    print(
                        "------------------------------------------"
                    )


                    # =========================================
                    # BASIC VALIDATION
                    # =========================================

                    if not product.product_url:

                        print(
                            "⚠️ Product URL missing."
                        )

                        continue


                    if product.current_price is None:

                        print(
                            "⚠️ Current price missing."
                        )

                        continue


                    if product.target_price is None:

                        print(
                            "⚠️ Target price missing."
                        )

                        continue


                    # =========================================
                    # OLD PRICE
                    # =========================================

                    old_price = float(
                        product.current_price
                    )


                    target_price = float(
                        product.target_price
                    )


                    # =========================================
                    # SCRAPE NEW PRODUCT DATA
                    # =========================================

                    try:

                        result = get_product_details(
                            product.product_url
                        )

                    except Exception as scraper_error:

                        print(
                            f"❌ Scraper error: "
                            f"{scraper_error}"
                        )

                        continue


                    if not result:

                        print(
                            "❌ No scraper response."
                        )

                        continue


                    if not result.get("success"):

                        error_message = result.get(
                            "error",
                            "Unknown scraper error"
                        )

                        print(
                            "⚠️ Scraping failed."
                        )

                        print(
                            f"   Reason: "
                            f"{error_message}"
                        )

                        continue


                    # =========================================
                    # NEW PRICE
                    # =========================================

                    scraped_price = result.get(
                        "current_price"
                    )


                    if scraped_price is None:

                        print(
                            "❌ Scraper did not return price."
                        )

                        continue


                    try:

                        new_price = float(
                            scraped_price
                        )

                    except (
                        TypeError,
                        ValueError
                    ):

                        print(
                            f"❌ Invalid scraped price: "
                            f"{scraped_price}"
                        )

                        continue


                    if new_price <= 0:

                        print(
                            f"❌ Invalid price: "
                            f"₹{new_price}"
                        )

                        continue


                    # =========================================
                    # PRICE COMPARISON
                    # =========================================

                    if new_price < old_price:

                        product.price_direction = "Dropped"


                        print(
                            "📉 PRICE DROPPED"
                        )

                        print(
                            f"   Old: ₹{old_price:.2f}"
                        )

                        print(
                            f"   New: ₹{new_price:.2f}"
                        )


                    elif new_price > old_price:

                        product.price_direction = "Increased"


                        print(
                            "📈 PRICE INCREASED"
                        )

                        print(
                            f"   Old: ₹{old_price:.2f}"
                        )

                        print(
                            f"   New: ₹{new_price:.2f}"
                        )


                    else:

                        product.price_direction = "Same"


                        print(
                            "➖ PRICE SAME"
                        )

                        print(
                            f"   Price: ₹{new_price:.2f}"
                        )


                    # =========================================
                    # SAVE PRICE HISTORY
                    # =========================================

                    history = PriceHistory(

                        product_id=product.id,

                        price=new_price,

                        checked_at=datetime.utcnow()

                    )


                    db.session.add(history)


                    # =========================================
                    # UPDATE PRODUCT
                    # =========================================

                    product.current_price = new_price

                    product.last_checked = datetime.utcnow()


                    # =========================================
                    # TARGET PRICE CHECK
                    # =========================================

                    if new_price <= target_price:

                        print()
                        print(
                            "🎯 TARGET PRICE REACHED!"
                        )

                        print(
                            f"   Current: "
                            f"₹{new_price:.2f}"
                        )

                        print(
                            f"   Target : "
                            f"₹{target_price:.2f}"
                        )


                        # -------------------------------------
                        # CHECK PREVIOUS STATUS
                        # -------------------------------------

                        if product.status != "Target Reached":

                            owner = product.owner


                            if owner and owner.email:

                                # ---------------------------------
                                # SEND EMAIL ONLY FOR PRICE DROP
                                # ---------------------------------

                                if new_price < old_price:

                                    email_sent = (
                                        send_price_drop_email(

                                            owner.email,

                                            product.product_name,

                                            old_price,

                                            new_price,

                                            target_price

                                        )
                                    )


                                    if email_sent:

                                        print(
                                            "✅ Target alert email sent."
                                        )

                                    else:

                                        print(
                                            "⚠️ Target alert email failed."
                                        )

                                else:

                                    print(
                                        "ℹ️ Target reached, "
                                        "but price did not drop."
                                    )


                            else:

                                print(
                                    "⚠️ Product owner email missing."
                                )


                        else:

                            print(
                                "ℹ️ Target was already reached."
                            )


                        product.status = "Target Reached"


                    else:

                        product.status = "Tracking"


                    # =========================================
                    # COMMIT DATABASE
                    # =========================================

                    db.session.commit()


                    print()
                    print(
                        "✅ PRODUCT UPDATED"
                    )

                    print(
                        f"📦 {product.product_name}"
                    )

                    print(
                        f"💰 ₹{new_price:.2f}"
                    )

                    print(
                        f"📊 Direction: "
                        f"{product.price_direction}"
                    )

                    print(
                        f"📌 Status: "
                        f"{product.status}"
                    )


                except Exception as product_error:

                    db.session.rollback()


                    print()
                    print(
                        "❌ PRODUCT PROCESSING ERROR"
                    )

                    print(
                        f"📦 {product.product_name}"
                    )

                    print(
                        f"❌ Error: "
                        f"{product_error}"
                    )


                    continue


        except Exception as scheduler_error:

            db.session.rollback()


            print()
            print(
                "❌ SCHEDULER ERROR"
            )

            print(
                f"❌ Error: "
                f"{scheduler_error}"
            )


    print()
    print(
        "=========================================="
    )

    print(
        "🏁 PRICE CHECK COMPLETED"
    )

    print(
        "=========================================="
    )

    print()


# =========================================================
# START SCHEDULER
# =========================================================

def start_scheduler(app):

    # -------------------------------------------------------
    # PREVENT DUPLICATE SCHEDULER
    # -------------------------------------------------------

    if scheduler.running:

        print(
            "ℹ️ Scheduler already running."
        )

        return


    # -------------------------------------------------------
    # REMOVE EXISTING JOB
    # -------------------------------------------------------

    existing_job = scheduler.get_job(
        "price_checker"
    )


    if existing_job:

        scheduler.remove_job(
            "price_checker"
        )


    # -------------------------------------------------------
    # ADD AUTOMATIC PRICE CHECKING JOB
    # -------------------------------------------------------

    scheduler.add_job(

        func=check_product_prices,

        args=[app],

        trigger="interval",

        # -----------------------------------------------
        # CHECK EVERY 30 MINUTES
        # -----------------------------------------------

        minutes=30,

        id="price_checker",

        replace_existing=True,

        max_instances=1,

        coalesce=True,

        misfire_grace_time=120

    )


    # -------------------------------------------------------
    # START SCHEDULER
    # -------------------------------------------------------

    scheduler.start()


    print()
    print(
        "🚀 Automatic Price Tracker Scheduler Started"
    )

    print(
        "⏱️ Price checking interval: 30 minutes"
    )

    print(
        "🔄 24/7 automatic tracking enabled"
    )


    # -------------------------------------------------------
    # FIRST PRICE CHECK
    # -------------------------------------------------------

    try:

        print()
        print(
            "⚡ Running first price check immediately..."
        )

        check_product_prices(app)


    except Exception as e:

        print()
        print(
            "❌ Initial price check failed"
        )

        print(
            f"❌ Error: {e}"
        )