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
# SEND TARGET PRICE EMAIL
# =========================================================

def send_target_price_email(
    owner_email,
    product_name,
    old_price,
    new_price,
    target_price
):

    try:

        msg = Message(
            subject="🎯 AI Price Tracker - Target Price Reached",
            recipients=[owner_email]
        )

        msg.body = f"""
Hello,

Good news! 🎉

The target price for your tracked product has been reached.

==========================================
        TARGET PRICE REACHED
==========================================

Product       : {product_name}

Previous Price: ₹{old_price:.2f}

Current Price : ₹{new_price:.2f}

Target Price  : ₹{target_price:.2f}

==========================================

Your target price has been reached.

AI Price Tracker
Automatic Price Monitoring System
"""

        mail.send(msg)

        print()
        print("==========================================")
        print("📧 TARGET PRICE EMAIL SENT")
        print(f"📧 To: {owner_email}")
        print(f"📦 Product: {product_name}")
        print(f"💰 Old: ₹{old_price:.2f}")
        print(f"💰 New: ₹{new_price:.2f}")
        print(f"🎯 Target: ₹{target_price:.2f}")
        print("==========================================")

        return True

    except Exception as e:

        print()
        print("==========================================")
        print("❌ TARGET PRICE EMAIL FAILED")
        print(f"📧 To: {owner_email}")
        print(f"📦 Product: {product_name}")
        print(f"❌ Error: {e}")
        print("==========================================")

        return False


# =========================================================
# CHECK ALL PRODUCT PRICES
# =========================================================

def check_product_prices(app):

    print()
    print("==========================================")
    print("🔄 CHECKING PRODUCT PRICES")
    print(
        f"🕒 Time: "
        f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )
    print("==========================================")


    with app.app_context():

        try:

            # -------------------------------------------------
            # GET ALL PRODUCTS
            # -------------------------------------------------

            products = Product.query.order_by(
                Product.id.asc()
            ).all()


            if not products:

                print("ℹ️ No products found.")
                print("💡 Add a product from the dashboard.")

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
                    print("------------------------------------------")
                    print(
                        f"🔍 Checking: "
                        f"{product.product_name}"
                    )
                    print(
                        f"👤 Owner ID: "
                        f"{product.user_id}"
                    )
                    print("------------------------------------------")


                    # =========================================
                    # VALIDATION
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
                    # OLD PRICE / TARGET PRICE
                    # =========================================

                    old_price = float(
                        product.current_price
                    )

                    target_price = float(
                        product.target_price
                    )


                    # =========================================
                    # SCRAPE PRODUCT
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


                    # =========================================
                    # VALIDATE SCRAPER RESULT
                    # =========================================

                    if not result:

                        print(
                            "❌ No scraper response."
                        )

                        continue


                    if not result.get("success"):

                        print(
                            "⚠️ Scraping failed."
                        )

                        print(
                            f"   Reason: "
                            f"{result.get('error', 'Unknown error')}"
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
                    # PRICE DIRECTION
                    # =========================================

                    if new_price < old_price:

                        product.price_direction = "Dropped"

                        print()
                        print("📉 PRICE DROPPED")
                        print(
                            f"   Old: ₹{old_price:.2f}"
                        )
                        print(
                            f"   New: ₹{new_price:.2f}"
                        )


                    elif new_price > old_price:

                        product.price_direction = "Increased"

                        print()
                        print("📈 PRICE INCREASED")
                        print(
                            f"   Old: ₹{old_price:.2f}"
                        )
                        print(
                            f"   New: ₹{new_price:.2f}"
                        )


                    else:

                        product.price_direction = "Same"

                        print()
                        print("➖ PRICE SAME")
                        print(
                            f"   Price: ₹{new_price:.2f}"
                        )


                    # =========================================
                    # TARGET PRICE CHECK
                    # =========================================

                    target_reached_now = (
                        new_price <= target_price
                        and old_price > target_price
                    )


                    already_reached = (
                        old_price <= target_price
                    )


                    if new_price <= target_price:

                        product.status = "Target Reached"

                        print()
                        print("🎯 TARGET PRICE REACHED!")
                        print(
                            f"   Current: "
                            f"₹{new_price:.2f}"
                        )
                        print(
                            f"   Target : "
                            f"₹{target_price:.2f}"
                        )

                    else:

                        product.status = "Tracking"

                        print()
                        print("⏳ TARGET NOT REACHED")
                        print(
                            f"   Current: "
                            f"₹{new_price:.2f}"
                        )
                        print(
                            f"   Target : "
                            f"₹{target_price:.2f}"
                        )


                    # =========================================
                    # TARGET EMAIL
                    # =========================================
                    #
                    # Email ONLY when price crosses target
                    # for the first time.
                    #
                    # Example:
                    #
                    # ₹55,000 → ₹49,999
                    # Target ₹50,000
                    #
                    # Email YES
                    #
                    # Next check:
                    # ₹49,999 → ₹49,500
                    #
                    # Email NO
                    #
                    # =========================================

                    if target_reached_now and not already_reached:

                        owner = product.owner


                        if owner and owner.email:

                            email_sent = (
                                send_target_price_email(

                                    owner.email,

                                    product.product_name,

                                    old_price,

                                    new_price,

                                    target_price

                                )
                            )


                            if email_sent:

                                print(
                                    "✅ Target price "
                                    "email sent."
                                )

                            else:

                                print(
                                    "⚠️ Target price "
                                    "email failed."
                                )


                        else:

                            print(
                                "⚠️ Product owner "
                                "email missing."
                            )


                    else:

                        if new_price <= target_price:

                            print(
                                "ℹ️ Target already reached. "
                                "Email not repeated."
                            )

                        else:

                            print(
                                "ℹ️ Target not reached. "
                                "No target email."
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
                    # UPDATE IMAGE IF AVAILABLE
                    # =========================================

                    scraped_image = result.get("image")


                    if scraped_image:

                        product.image_url = scraped_image


                    # =========================================
                    # UPDATE PRODUCT NAME IF AVAILABLE
                    # =========================================

                    scraped_name = result.get(
                        "product_name"
                    )


                    if (
                        scraped_name
                        and scraped_name != "Unknown Product"
                    ):

                        product.product_name = scraped_name


                    # =========================================
                    # COMMIT
                    # =========================================

                    db.session.commit()


                    # =========================================
                    # SUCCESS LOG
                    # =========================================

                    print()
                    print("✅ PRODUCT UPDATED")
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
            print("❌ SCHEDULER ERROR")
            print(
                f"❌ Error: "
                f"{scheduler_error}"
            )


    print()
    print("==========================================")
    print("🏁 PRICE CHECK COMPLETED")
    print("==========================================")
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
    # ADD JOB
    # -------------------------------------------------------

    scheduler.add_job(

        func=check_product_prices,

        args=[app],

        trigger="interval",

        minutes=30,

        id="price_checker",

        replace_existing=True,

        max_instances=1,

        coalesce=True,

        misfire_grace_time=120

    )


    # -------------------------------------------------------
    # START
    # -------------------------------------------------------

    scheduler.start()


    print()
    print(
        "=========================================="
    )

    print(
        "🚀 Automatic Price Tracker Scheduler Started"
    )

    print(
        "⏱️ Price checking interval: 30 minutes"
    )

    print(
        "🔄 Automatic tracking enabled"
    )

    print(
        "📧 Target-price email alerts enabled"
    )

    print(
        "=========================================="
    )


    # -------------------------------------------------------
    # FIRST CHECK
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