import requests
from bs4 import BeautifulSoup



# ======================================
# Amazon Product Scraper
# ======================================

def get_amazon_product(url):

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

                "error": "Amazon page not reachable"

            }



        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )



        # Product Name

        title = soup.find(
            "span",
            id="productTitle"
        )


        if title:

            product_name = title.text.strip()

        else:

            product_name = "Unknown Product"




        # Price

        price = None


        price_tag = soup.find(
            "span",
            class_="a-price-whole"
        )


        if price_tag:

            price = price_tag.text.replace(
                ",",
                ""
            ).strip()



        if price:

            current_price = float(price)

        else:

            current_price = 0




        # Image

        image = None


        image_tag = soup.find(
            "img",
            id="landingImage"
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
            "Amazon"


        }




    except Exception as e:


        return {


            "success": False,


            "error":
            str(e)


        }