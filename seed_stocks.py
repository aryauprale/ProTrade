import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

stocks = [
    ("Apple Inc.", "AAPL", 78000000, 192, 189, 194, 187),
    ("Tesla Inc.", "TSLA", 32000000, 170, 172, 175, 165),
    ("Nvidia Corp.", "NVDA", 25000000, 925, 910, 940, 905),
    ("Microsoft Corp.", "MSFT", 42000000, 415, 410, 420, 408),
    ("Amazon.com Inc.", "AMZN", 51000000, 182, 179, 185, 178),
    ("Alphabet Inc.", "GOOGL", 26000000, 141, 139, 143, 138),
    ("Meta Platforms", "META", 23000000, 485, 480, 490, 478),
    ("Advanced Micro Devices", "AMD", 30000000, 165, 160, 168, 159),
    ("Intel Corp.", "INTC", 29000000, 42, 41, 44, 40),
    ("Netflix Inc.", "NFLX", 18000000, 610, 600, 620, 598),
    ("Adobe Inc.", "ADBE", 12000000, 525, 520, 530, 515),
    ("Salesforce", "CRM", 15000000, 295, 290, 300, 288),
    ("Uber Technologies", "UBER", 37000000, 72, 70, 74, 69),
    ("Palantir Technologies", "PLTR", 41000000, 26, 25, 27, 24),
    ("Spotify Technology", "SPOT", 9000000, 295, 290, 300, 288),
    ("Snowflake Inc.", "SNOW", 8000000, 190, 185, 195, 183),
    ("Shopify Inc.", "SHOP", 14000000, 85, 83, 88, 82),
    ("PayPal Holdings", "PYPL", 21000000, 67, 66, 69, 65),
]

cursor.executemany("""
INSERT OR IGNORE INTO stocks
(company_name, ticker, total_volume, current_price, opening_price, day_high, day_low)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", stocks)

conn.commit()
conn.close()

print("Stocks added successfully.")