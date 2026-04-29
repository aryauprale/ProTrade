import sqlite3
from werkzeug.security import generate_password_hash

print("starting db init...")

conn = sqlite3.connect("database.db")
print("connected database")

with open("sql/schema.sql", "r") as f:
    schema = f.read()
print("schema file loaded")

try:
    conn.executescript(schema)
    print("schema executed")

    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("tables:", tables)

# Insert default market settings (only once)
    conn.execute("""
        INSERT OR IGNORE INTO market_settings (id, open_time, close_time)
        VALUES (1, '09:00', '16:00')
    """)
    print("default market settings inserted")


    conn.commit()
    print("database and tables created successfully")

    conn.execute("""
        INSERT OR IGNORE INTO users 
        (first_name, last_name, username, email, phone, password_hash, role, cash_balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
       "Admin",
       "User",
       "admin",
       "admin@protrade.com",
       "0000000000",
       generate_password_hash("admin123"),
       "admin",
        100000
    ))
    print("admin user created")

    conn.commit()
    print("database and tables created successfully")

except Exception as e:
    print("ERROR:", e)

finally:
    conn.close()

