
from flask_mail import Message

from extensions import mail


# ==========================================
# SEND PRICE ALERT EMAIL
# ==========================================

def send_price_alert(
    email,
    product_name,
    current_price,
    target_price
):

    if not email:
        print("⚠️ Email address not found.")
        return False

    try:

        subject = (
            f"📉 Price Alert - {product_name}"
        )

        body = f"""
Hello,

Good news! 🎉

The price of your tracked product has reached
your target price.

━━━━━━━━━━━━━━━━━━━━━━

📦 Product:
{product_name}

💰 Current Price:
₹{current_price:.2f}

🎯 Target Price:
₹{target_price:.2f}

━━━━━━━━━━━━━━━━━━━━━━

Your AI Price Tracker detected the price change.

Please check the product before the price changes again.

Regards,
AI Price Tracker
"""

        message = Message(
            subject=subject,
            recipients=[email],
            body=body
        )

        mail.send(message)

        print(
            f"📧 Price alert email sent to {email}"
        )

        return True

    except Exception as e:

        print(
            f"❌ Email sending failed: {e}"
        )

        return False

