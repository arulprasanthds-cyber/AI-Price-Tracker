# 🤖 AI Product Price Tracker

An AI-powered product price tracking system built with Flask.

The application allows users to track products, monitor price changes automatically, maintain price history, and receive email alerts when the price drops or reaches the target price.

---

## 🚀 Features

- 👤 Multi-user authentication
- 📦 Add multiple products
- 🔗 Product URL tracking
- 💰 Automatic price monitoring
- 🎯 Target price alerts
- 📉 Price-drop detection
- 📊 Price history
- 📧 Email notifications
- ⏱️ Automatic background scheduler
- 🔐 Environment-based email credentials
- 🌐 Flipkart product scraping
- 🗑️ Product deletion
- 📱 Responsive dashboard

---

## 🛠️ Technologies

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Mail
- APScheduler
- Playwright
- BeautifulSoup
- Requests
- SQLite
- HTML
- CSS
- JavaScript

---

## 📁 Project Structure

```text
product_price_tracker/
│
├── app.py
├── models.py
├── extensions.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
│
├── auth/
│   └── ...
│
├── dashboard/
│   └── ...
│
├── scheduler/
│   └── ...
│
├── scraper/
│   ├── scraper_manager.py
│   └── flipkart_scraper.py
│
├── templates/
│   └── ...
│
└── static/
    └── ...
    