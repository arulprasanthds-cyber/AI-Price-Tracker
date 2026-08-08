import requests
from bs4 import BeautifulSoup



# ======================================
# Myntra Product Scraper
# ======================================

def get_myntra_product(url):

    try:

        headers = {

            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

        }


        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )


        if response.status_code != 200:

            return {

                "success": False,

                "error": "Myntra page not reachable"

            }



        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )



        # Product Name

        title = soup.find(
            "h1",
            class_="pdp-title"
        )


        brand = soup.find(
            "h1",
            class_="pdp-name"
        )



        if brand and title:

            product_name = (
                brand.text.strip()
                + " "
                + title.text.strip()
            )

        else:

            product_name = "Myntra Product"



        # Price

        price_tag = soup.find(
            "span",
            class_="pdp-price"
        )


        if price_tag:

            price = price_tag.text.replace(
                "Rs.",
                ""
            ).replace(
                ",",
                ""
            ).strip()


            current_price = float(price)

        else:

            current_price = 0



        # Image

        image = None


        image_tag = soup.find(
            "img"
        )


        if image_tag:

            image = image_tag.get(
                "src"
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
            "Myntra"

        }



    except Exception as e:


        return {


            "success": False,


            "error":
            str(e)

        }