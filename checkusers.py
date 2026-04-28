import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")

columns = cursor.fetchall()

print("\nUsers table columns:\n")

for col in columns:
    print(col[1])   # prints just the column name

conn.close()