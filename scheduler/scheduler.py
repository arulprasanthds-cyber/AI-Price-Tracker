from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from extensions import db
from models import Product, PriceHistory

from scraper.scraper_manager import get_product_details
from alerts.email_alert import send_price_alert


# ==========================================
# Scheduler
# ==========================================

scheduler = BackgroundScheduler()


# ==========================================
# Check Product Prices
# ==========================================

def check_product_prices(app):

    print("🔄 Checking product prices...")

    with app.app_context():

        products = Product.query.all()

        if not products:
            print("ℹ️ No products found.")
            return

        for product in products:

            try:

                # ==================================
                # Product URL Check
                # ==================================

                if not product.product_url:

                    print(
                        f"⚠️ No URL: "
                        f"{product.product_name}"
                    )

                    continue


                # ==================================
                # Store Old Price
                # ==================================

                old_price = product.current_price


                # ==================================
                # Fetch New Price
                # ==================================

                result = get_product_details(
                    product.product_url
                )

                if not result or not result.get("success"):

                    error_message = (
                        result.get(
                            "error",
                            "Unknown scraper error"
                        )
                        if result
                        else
                        "No response from scraper"
                    )

                    print(
                        f"⚠️ Could not fetch: "
                        f"{product.product_name}"
                    )

                    print(
                        f"❌ Reason: "
                        f"{error_message}"
                    )

                    continue


                # ==================================
                # Price Check
                # ==================================

                if "current_price" not in result:

                    print(
                        f"❌ Price missing: "
                        f"{product.product_name}"
                    )

                    continue


                new_price = float(
                    result["current_price"]
                )


                if new_price <= 0:

                    print(
                        f"❌ Invalid price: "
                        f"{product.product_name}"
                    )

                    continue


                # ==================================
                # PRICE DIRECTION
                # ==================================

                if new_price < old_price:

                    product.price_direction = "Dropped"

                    print(
                        f"📉 Price Dropped: "
                        f"₹{old_price:.2f} → "
                        f"₹{new_price:.2f}"
                    )


                elif new_price > old_price:

                    product.price_direction = "Increased"

                    print(
                        f"📈 Price Increased: "
                        f"₹{old_price:.2f} → "
                        f"₹{new_price:.2f}"
                    )


                else:

                    product.price_direction = "Same"

                    print(
                        f"➖ Price Same: "
                        f"₹{new_price:.2f}"
                    )


                # ==================================
                # Save Price History
                # ==================================

                history = PriceHistory(
                    product_id=product.id,
                    price=new_price
                )

                db.session.add(history)


                # ==================================
                # Update Product
                # ==================================

                product.current_price = new_price

                product.last_checked = datetime.utcnow()


                # ==================================
                # Target Price Check
                # ==================================

                if new_price <= product.target_price:

                    if product.status != "Target Reached":

                        try:

                            if (
                                product.owner
                                and product.owner.email
                            ):

                                email_sent = send_price_alert(

                                    product.owner.email,

                                    product.product_name,

                                    new_price,

                                    product.target_price

                                )

                                if email_sent:

                                    print(
                                        f"📧 Alert sent: "
                                        f"{product.product_name}"
                                    )

                                else:

                                    print(
                                        f"⚠️ Email failed: "
                                        f"{product.product_name}"
                                    )

                        except Exception as mail_error:

                            print(
                                f"❌ Email Error "
                                f"({product.product_name}): "
                                f"{mail_error}"
                            )


                    product.status = "Target Reached"


                else:

                    product.status = "Tracking"


                # ==================================
                # Save Database
                # ==================================

                db.session.commit()


                print(
                    f"✅ Updated: "
                    f"{product.product_name} "
                    f"₹{new_price:.2f} "
                    f"[{product.price_direction}]"
                )


            except Exception as e:

                db.session.rollback()

                print(
                    f"❌ Product Error "
                    f"({product.product_name}): "
                    f"{e}"
                )


# ==========================================
# Start Scheduler
# ==========================================

def start_scheduler(app):

    if scheduler.running:

        print(
            "ℹ️ Scheduler already running."
        )

        return


    scheduler.add_job(

        func=check_product_prices,

        args=[app],

        trigger="interval",

        minutes=1,

        id="price_checker",

        replace_existing=True,

        max_instances=1

    )


    scheduler.start()

    print("🚀 Scheduler Started")