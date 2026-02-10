CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      full_name TEXT NOT NULL,
      username VARCHAR(50) UNIQUE NOT NULL,
      email VARCHAR(50) UNIQUE NOT NULL,
      pass_word VARCHAR(50) NOT NULL,
      role_assign TEXT NOT NULL,
      cash_balance REAL DEFAULT 0,
) ;

CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    total_volume BIGINT NOT NULL DEFAULT 0,
    current_price REAL NOT NULL CHECK (current_price >= 0),
    opening_price REAL NOT NULL CHECK (opening_price >= 0),
    day_high REAL NOT NULL CHECK (day_high >= 0),
    day_low REAL NOT NULL CHECK (day_low >= 0)
);

CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    quantity_owned INTEGER NOT NULL DEFAULT 0 CHECK (quantity_owned >= 0),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE (user_id, stock_id)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,

    type TEXT NOT NULL CHECK (type IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_time REAL NOT NULL CHECK (price_at_time >= 0),

    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);

CREATE TABLE market_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    day_of_the_week INTEGER NOT NULL CHECK (day_of_the_week BETWEEN 0 AND 6),
    open_time TEXT,   
    close_time TEXT,  
    is_open_today INTEGER NOT NULL DEFAULT 1 CHECK (is_open_today IN (0, 1)),
    UNIQUE (day_of_the_week)
);
