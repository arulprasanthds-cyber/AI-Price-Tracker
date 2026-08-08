from app import create_app
from scheduler.scheduler import check_product_prices


def main():
    print("🚀 Price Tracker Worker Started")

    app = create_app()

    try:
        check_product_prices(app)
        print("✅ Price check completed")

    except Exception as e:
        print(f"❌ Worker Error: {e}")


if __name__ == "__main__":
    main()