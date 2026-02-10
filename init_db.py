import sqlite3 
print("starting db init...")

#connecting (create) database.db
conn = sqlite3.connect('database.db')
print("connected database")

#read schema file
with open('sql/schema.sql', 'r') as f:
    schema = f.read()
print("schema file loaded")

#execute schema file
conn.executescript(schema)
print("schema executed")

conn.commit()
conn.close()

print("database and table created successfully")