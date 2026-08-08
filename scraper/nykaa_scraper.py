import requests
from bs4 import BeautifulSoup



# ======================================
# Nykaa Product Scraper
# ======================================

def get_nykaa_product(url):

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

                "error": "Nykaa page not reachable"

            }



        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )



        # Product Name

        title = soup.find(
            "h1"
        )


        if title:

            product_name = title.text.strip()

        else:

            product_name = "Nykaa Product"



        # Price

        price_tag = soup.find(
            class_="css-1jczs19"
        )


        if price_tag:

            price = price_tag.text.replace(
                "₹",
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
            "Nykaa"

        }




    except Exception as e:


        return {

            "success": False,

            "error":
            str(e)

        }