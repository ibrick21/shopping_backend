import sqlite3

connection = sqlite3.connect("shop.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    product TEXT,
    price INTEGER,
    quantity INTEGER,
    status TEXT
)
""")

cursor.execute(
    """
    UPDATE orders
    SET status = ?
    WHERE status = ?
    """,
    ("pending", "PENDING")
)

connection.commit()
connection.close()

