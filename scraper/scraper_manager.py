from urllib.parse import urlparse

def detect_website(url):
    if not url:
        return None

    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return None

    if "amazon." in domain:
        return "amazon"
    elif "flipkart." in domain:
        return "flipkart"
    elif "myntra." in domain:
        return "myntra"
    elif "ajio." in domain:
        return "ajio"
    elif "nykaa." in domain:
        return "nykaa"
    elif "croma." in domain:
        return "croma"

    return None


def get_product_details(url):
    website = detect_website(url)

    if website is None:
        return {
            "success": False,
            "error": "Unsupported or invalid product URL"
        }

    try:
        if website == "amazon":
            from scraper.amazon_scraper import get_amazon_product
            return get_amazon_product(url)

        elif website == "flipkart":
            from scraper.flipkart_scraper import get_flipkart_product
            return get_flipkart_product(url)

        elif website == "myntra":
            from scraper.myntra_scraper import get_myntra_product
            return get_myntra_product(url)

        elif website == "ajio":
            from scraper.ajio_scraper import get_ajio_product
            return get_ajio_product(url)

        elif website == "nykaa":
            from scraper.nykaa_scraper import get_nykaa_product
            return get_nykaa_product(url)

        elif website == "croma":
            from scraper.croma_scraper import get_croma_product
            return get_croma_product(url)

        return {
            "success": False,
            "error": "Website scraper not found"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
