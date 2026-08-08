import sqlite3

db_path = "instance/product_tracker.db"

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE products ADD COLUMN price_direction VARCHAR(50) DEFAULT 'Same'"
    )

    conn.commit()

    print("✅ price_direction column added successfully")

except sqlite3.OperationalError as e:

    if "duplicate column name" in str(e).lower():
        print("ℹ️ price_direction column already exists")
    else:
        print("❌ Database Error:", e)

finally:

    conn.close()