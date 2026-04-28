import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
    print("Role column added.")
except Exception as e:
    print("Error:", e)

conn.commit()
conn.close()