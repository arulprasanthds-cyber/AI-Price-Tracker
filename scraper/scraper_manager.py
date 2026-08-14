from urllib.parse import urlparse


# =========================================================
# SUPPORTED WEBSITES
# =========================================================

SUPPORTED_WEBSITES = {
    "amazon": "amazon",
    "flipkart": "flipkart",
    "myntra": "myntra",
    "ajio": "ajio",
    "nykaa": "nykaa",
    "croma": "croma",
}


# =========================================================
# DETECT WEBSITE
# =========================================================

def detect_website(url):

    if not url:
        return None

    try:

        parsed_url = urlparse(
            url.strip()
        )

        domain = parsed_url.netloc.lower()

        # Remove www.
        domain = domain.replace(
            "www.",
            ""
        )

    except Exception:

        return None


    for website in SUPPORTED_WEBSITES:

        if website in domain:

            return website


    return None


# =========================================================
# VALIDATE PRODUCT URL
# =========================================================

def validate_product_url(url):

    if not url:

        return False

    try:

        parsed_url = urlparse(
            url.strip()
        )

        if parsed_url.scheme not in (
            "http",
            "https"
        ):

            return False

        if not parsed_url.netloc:

            return False

        return True

    except Exception:

        return False


# =========================================================
# GET PRODUCT DETAILS
# =========================================================

def get_product_details(url):

    # -------------------------------------------------------
    # URL VALIDATION
    # -------------------------------------------------------

    if not validate_product_url(url):

        return {
            "success": False,
            "error": "Invalid product URL"
        }


    # -------------------------------------------------------
    # WEBSITE DETECTION
    # -------------------------------------------------------

    website = detect_website(url)


    if website is None:

        return {
            "success": False,
            "error": (
                "Unsupported website. "
                "Supported websites: "
                "Amazon, Flipkart, Myntra, "
                "AJIO, Nykaa and Croma."
            )
        }


    print()
    print(
        "------------------------------------------"
    )

    print(
        f"🌐 Website detected: "
        f"{website.upper()}"
    )

    print(
        f"🔗 URL: {url}"
    )

    print(
        "------------------------------------------"
    )


    # -------------------------------------------------------
    # SELECT SCRAPER
    # -------------------------------------------------------

    try:

        if website == "amazon":

            from scraper.amazon_scraper import (
                get_amazon_product
            )

            result = get_amazon_product(url)


        elif website == "flipkart":

            from scraper.flipkart_scraper import (
                get_flipkart_product
            )

            result = get_flipkart_product(url)


        elif website == "myntra":

            from scraper.myntra_scraper import (
                get_myntra_product
            )

            result = get_myntra_product(url)


        elif website == "ajio":

            from scraper.ajio_scraper import (
                get_ajio_product
            )

            result = get_ajio_product(url)


        elif website == "nykaa":

            from scraper.nykaa_scraper import (
                get_nykaa_product
            )

            result = get_nykaa_product(url)


        elif website == "croma":

            from scraper.croma_scraper import (
                get_croma_product
            )

            result = get_croma_product(url)


        else:

            return {
                "success": False,
                "error": "Scraper not available"
            }


    except ImportError as e:

        print(
            f"❌ Scraper import error: {e}"
        )

        return {
            "success": False,
            "error": (
                f"{website} scraper is not available"
            )
        }


    except Exception as e:

        print(
            f"❌ Scraper execution error: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }


    # -------------------------------------------------------
    # VALIDATE SCRAPER RESULT
    # -------------------------------------------------------

    if not result:

        return {
            "success": False,
            "error": (
                f"{website} scraper returned no data"
            )
        }


    if not isinstance(result, dict):

        return {
            "success": False,
            "error": (
                f"{website} scraper returned "
                "invalid response"
            )
        }


    # -------------------------------------------------------
    # SCRAPER FAILED
    # -------------------------------------------------------

    if not result.get("success"):

        return {
            "success": False,
            "error": result.get(
                "error",
                f"{website} scraping failed"
            )
        }


    # -------------------------------------------------------
    # GET PRICE
    # -------------------------------------------------------

    current_price = result.get(
        "current_price"
    )


    if current_price is None:

        return {
            "success": False,
            "error": (
                f"{website} scraper "
                "did not return current price"
            )
        }


    try:

        current_price = float(
            current_price
        )

    except (
        TypeError,
        ValueError
    ):

        return {
            "success": False,
            "error": (
                "Scraper returned invalid price"
            )
        }


    if current_price <= 0:

        return {
            "success": False,
            "error": (
                "Scraper returned invalid price"
            )
        }


    # -------------------------------------------------------
    # NORMALIZE RESULT
    # -------------------------------------------------------

    product_name = result.get(
        "product_name"
    )

    image = result.get(
        "image"
    )


    normalized_result = {

        "success": True,

        "website": website,

        "product_name": (
            product_name
            if product_name
            else "Unknown Product"
        ),

        "current_price": current_price,

        "image": image,

        "url": url

    }


    # -------------------------------------------------------
    # SUCCESS LOG
    # -------------------------------------------------------

    print()
    print(
        "✅ PRODUCT SCRAPED SUCCESSFULLY"
    )

    print(
        f"🌐 Website: "
        f"{website.upper()}"
    )

    print(
        f"📦 Product: "
        f"{normalized_result['product_name']}"
    )

    print(
        f"💰 Price: "
        f"₹{current_price:.2f}"
    )

    print(
        "------------------------------------------"
    )


    return normalized_result