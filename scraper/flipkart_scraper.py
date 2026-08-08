from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re


# ======================================
# Flipkart Product Scraper
# ======================================

def get_flipkart_product(url):

    if not url:
        return {
            "success": False,
            "error": "Flipkart URL is empty"
        }

    browser = None

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page(
                viewport={
                    "width": 1366,
                    "height": 768
                },
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                ),
                locale="en-IN"
            )

            print("🌐 Opening Flipkart...")

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            if response:

                print(
                    f"🔎 Flipkart HTTP Status: "
                    f"{response.status}"
                )

            page.wait_for_timeout(5000)


            # ======================================
            # Get Complete Page Text
            # ======================================

            body_text = page.locator(
                "body"
            ).inner_text(
                timeout=10000
            )


            # ======================================
            # Product Name
            # ======================================

            product_name = None


            try:

                h1 = page.locator(
                    "h1"
                ).first

                if h1.count() > 0:

                    product_name = h1.inner_text(
                        timeout=3000
                    ).strip()

            except Exception:

                product_name = None


            # Fallback
            if not product_name:

                title = page.title()

                if title:

                    product_name = title.strip()


            if not product_name:

                product_name = "Flipkart Product"


            print(
                f"📦 Product: {product_name}"
            )


            # ======================================
            # Find Product Price
            # ======================================

            current_price = None


            # Find product name inside page text
            product_position = body_text.find(
                product_name
            )


            if product_position >= 0:

                product_section = body_text[
                    product_position:
                    product_position + 1500
                ]

            else:

                product_section = body_text[
                    :3000
                ]


            # Find ₹ price
            price_matches = re.findall(
                r"₹\s*([0-9,]+(?:\.[0-9]+)?)",
                product_section
            )


            if price_matches:

                for price_text in price_matches:

                    try:

                        price = float(
                            price_text.replace(
                                ",",
                                ""
                            )
                        )

                        # Ignore unrealistic values
                        if price > 100:

                            current_price = price

                            break

                    except ValueError:

                        continue


            # ======================================
            # Alternative: Search DOM currency text
            # ======================================

            if current_price is None:

                currency_elements = page.locator(
                    "text=/₹[0-9,]+/"
                )

                count = currency_elements.count()

                for i in range(
                    min(count, 30)
                ):

                    try:

                        text = currency_elements.nth(
                            i
                        ).inner_text(
                            timeout=1000
                        )

                        match = re.search(
                            r"₹\s*([0-9,]+)",
                            text
                        )

                        if match:

                            price = float(
                                match.group(1).replace(
                                    ",",
                                    ""
                                )
                            )

                            if price > 100:

                                current_price = price

                                break

                    except Exception:

                        continue


            # ======================================
            # Price Not Found
            # ======================================

            if current_price is None:

                print(
                    "❌ Flipkart price not detected"
                )

                browser.close()

                return {
                    "success": False,
                    "error": (
                        "Flipkart page opened, "
                        "but current product price "
                        "could not be detected."
                    )
                }


            print(
                f"💰 Current Price: ₹{current_price}"
            )


            # ======================================
            # Product Image
            # ======================================

            image = None

            try:

                image_tag = page.locator(
                    'meta[property="og:image"]'
                ).first

                if image_tag.count() > 0:

                    image = image_tag.get_attribute(
                        "content"
                    )

            except Exception:

                image = None


            # ======================================
            # Close Browser
            # ======================================

            browser.close()


            # ======================================
            # Return Result
            # ======================================

            return {

                "success": True,

                "product_name":
                    product_name,

                "current_price":
                    current_price,

                "image":
                    image,

                "website":
                    "Flipkart"

            }


    except PlaywrightTimeoutError:

        if browser:

            try:
                browser.close()
            except Exception:
                pass

        return {

            "success": False,

            "error":
                "Flipkart page loading timed out"

        }


    except Exception as e:

        if browser:

            try:
                browser.close()
            except Exception:
                pass

        return {

            "success": False,

            "error":
                str(e)

        }
