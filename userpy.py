import sqlite3

conn = sqlite3.connect("database.db")
conn.execute("ALTER TABLE users ADD COLUMN cash_balance REAL NOT NULL DEFAULT 10000")
conn.commit()
conn.close()

print("cash_balance column added successfully.")