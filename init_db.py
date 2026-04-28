import sqlite3

print("starting db init...")

conn = sqlite3.connect("database.db")
print("connected database")

with open("sql/schema.sql", "r") as f:
    schema = f.read()
print("schema file loaded")

try:
    conn.executescript(schema)
    print("schema executed")


    conn.commit()
    print("database and tables created successfully")

except Exception as e:
    print("ERROR:", e)

finally:
    conn.close()