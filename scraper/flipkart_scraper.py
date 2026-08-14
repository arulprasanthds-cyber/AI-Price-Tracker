from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

import re


# =========================================================
# FLIPKART PRODUCT SCRAPER
# =========================================================

def get_flipkart_product(url):

    if not url:

        return {
            "success": False,
            "error": "Flipkart URL is empty"
        }


    browser = None


    try:

        # =================================================
        # START PLAYWRIGHT
        # =================================================

        with sync_playwright() as p:

            print()
            print("🌐 Opening Flipkart...")
            print(f"🔗 URL: {url}")


            browser = p.chromium.launch(
                headless=True
            )


            context = browser.new_context(

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

                locale="en-IN",

                extra_http_headers={
                    "Accept-Language":
                        "en-IN,en;q=0.9"
                }

            )


            page = context.new_page()


            # =================================================
            # OPEN PAGE
            # =================================================

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


            # Give JavaScript time to render
            page.wait_for_timeout(4000)


            # =================================================
            # CHECK PAGE
            # =================================================

            current_url = page.url.lower()


            if "login" in current_url:

                browser.close()

                return {
                    "success": False,
                    "error":
                        "Flipkart redirected to login page"
                }


            # =================================================
            # PAGE TEXT
            # =================================================

            try:

                body_text = page.locator(
                    "body"
                ).inner_text(
                    timeout=10000
                )

            except Exception:

                body_text = ""


            # =================================================
            # PRODUCT NAME
            # =================================================

            product_name = None


            # -----------------------------------------------
            # H1
            # -----------------------------------------------

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


            # -----------------------------------------------
            # TITLE FALLBACK
            # -----------------------------------------------

            if not product_name:

                try:

                    title = page.title()

                    if title:

                        product_name = title.strip()

                except Exception:

                    product_name = None


            # -----------------------------------------------
            # FINAL FALLBACK
            # -----------------------------------------------

            if not product_name:

                product_name = "Flipkart Product"


            print(
                f"📦 Product: {product_name}"
            )


            # =================================================
            # FIND CURRENT PRICE
            # =================================================

            current_price = None


            # -----------------------------------------------
            # METHOD 1: Product section
            # -----------------------------------------------

            product_position = body_text.find(
                product_name
            )


            if product_position >= 0:

                product_section = body_text[
                    product_position:
                    product_position + 2500
                ]

            else:

                product_section = body_text[
                    :5000
                ]


            price_matches = re.findall(

                r"₹\s*([0-9,]+(?:\.[0-9]+)?)",

                product_section

            )


            for price_text in price_matches:

                try:

                    price = float(
                        price_text.replace(
                            ",",
                            ""
                        )
                    )


                    if price > 100:

                        current_price = price

                        break


                except (
                    ValueError,
                    TypeError
                ):

                    continue


            # =================================================
            # METHOD 2: DOM PRICE SEARCH
            # =================================================

            if current_price is None:

                try:

                    currency_elements = page.locator(
                        "text=/₹[0-9,]+/"
                    )


                    count = currency_elements.count()


                    for i in range(
                        min(count, 50)
                    ):

                        try:

                            text = (
                                currency_elements
                                .nth(i)
                                .inner_text(
                                    timeout=1000
                                )
                            )


                            match = re.search(
                                r"₹\s*([0-9,]+)",
                                text
                            )


                            if match:

                                price = float(
                                    match.group(
                                        1
                                    ).replace(
                                        ",",
                                        ""
                                    )
                                )


                                if price > 100:

                                    current_price = price

                                    break


                        except Exception:

                            continue


                except Exception:

                    pass


            # =================================================
            # METHOD 3: META / JSON-LD
            # =================================================

            if current_price is None:

                try:

                    json_ld = page.locator(
                        'script[type="application/ld+json"]'
                    )


                    count = json_ld.count()


                    for i in range(
                        min(count, 20)
                    ):

                        try:

                            text = (
                                json_ld
                                .nth(i)
                                .inner_text(
                                    timeout=1000
                                )
                            )


                            match = re.search(

                                r'"price"\s*:\s*"?('
                                r'[0-9]+(?:\.[0-9]+)?'
                                r')"?' ,

                                text

                            )


                            if match:

                                price = float(
                                    match.group(1)
                                )


                                if price > 100:

                                    current_price = price

                                    break


                        except Exception:

                            continue


                except Exception:

                    pass


            # =================================================
            # PRICE NOT FOUND
            # =================================================

            if current_price is None:

                print(
                    "❌ Flipkart price not detected"
                )


                browser.close()


                return {

                    "success": False,

                    "error":
                        "Flipkart page opened, "
                        "but current price could "
                        "not be detected."

                }


            print(
                f"💰 Current Price: "
                f"₹{current_price:.2f}"
            )


            # =================================================
            # PRODUCT IMAGE
            # =================================================

            image = None


            try:

                image_tag = page.locator(
                    'meta[property="og:image"]'
                ).first


                if image_tag.count() > 0:

                    image = (
                        image_tag
                        .get_attribute(
                            "content"
                        )
                    )


            except Exception:

                image = None


            # =================================================
            # CLOSE BROWSER
            # =================================================

            browser.close()


            # =================================================
            # SUCCESS
            # =================================================

            print(
                "✅ Flipkart product scraped successfully"
            )


            return {

                "success": True,

                "product_name":
                    product_name,

                "current_price":
                    current_price,

                "image":
                    image,

                "website":
                    "flipkart"

            }


    # =========================================================
    # TIMEOUT
    # =========================================================

    except PlaywrightTimeoutError:

        if browser:

            try:

                browser.close()

            except Exception:

                pass


        print(
            "❌ Flipkart page loading timed out"
        )


        return {

            "success": False,

            "error":
                "Flipkart page loading timed out"

        }


    # =========================================================
    # GENERAL ERROR
    # =========================================================

    except Exception as e:

        if browser:

            try:

                browser.close()

            except Exception:

                pass


        print(
            f"❌ Flipkart scraper error: {e}"
        )


        return {

            "success": False,

            "error":
                str(e)

        }