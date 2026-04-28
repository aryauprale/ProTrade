from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      username TEXT NOT NULL UNIQUE,
      email TEXT NOT NULL UNIQUE,
      phone TEXT NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user',
      cash_balance REAL NOT NULL DEFAULT 10000,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


init_db()


def normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")


@app.route("/aboutus")
def about():
    return render_template("aboutus.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/test")
def test():
    return "Test route works"


@app.route("/admin/stocks")
def admin_stocks():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    stocks = conn.execute("SELECT * FROM stocks ORDER BY ticker").fetchall()
    conn.close()

    return render_template("admin_stocks.html", stocks=stocks)

def is_market_open():
    today = datetime.now().date()
    weekday = today.weekday()  # Monday = 0, Sunday = 6

    # Block weekends
    if weekday >= 5:
        return False

    conn = get_db()
    holiday = conn.execute(
        "SELECT * FROM market_holidays WHERE holiday_date = ?",
        (str(today),)
    ).fetchone()
    conn.close()

    # Block holidays
    if holiday:
        return False

    return True

@app.route("/admin/prices/update", methods=["POST"])
def update_stock_prices():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    conn = get_db()

    stocks = conn.execute("SELECT id, current_price FROM stocks").fetchall()

    for stock in stocks:
        old_price = stock["current_price"]

        # Random change between -3% and +3%
        change_percent = random.uniform(-0.03, 0.03)
        new_price = old_price * (1 + change_percent)

        # Keep price positive
        new_price = max(new_price, 1)

        conn.execute("""
            UPDATE stocks
            SET 
                current_price = ?,
                day_high = CASE 
                    WHEN ? > day_high THEN ? 
                    ELSE day_high 
                END,
                day_low = CASE 
                    WHEN ? < day_low THEN ? 
                    ELSE day_low 
                END
            WHERE id = ?
        """, (
            new_price,
            new_price, new_price,
            new_price, new_price,
            stock["id"]
        ))

    conn.commit()
    conn.close()

    flash("Stock prices updated.", "success")
    return redirect(url_for("exchange"))

@app.route("/admin/reset-day", methods=["POST"])
def reset_day():
    conn = get_db()

    conn.execute("""
        UPDATE stocks
        SET 
            day_high = current_price,
            day_low = current_price,
            opening_price = current_price
    """)

    conn.commit()
    conn.close()

    flash("New trading day started.", "success")
    return redirect(url_for("admin_market"))

@app.route("/sell/<ticker>", methods=["POST"])
def sell_stock(ticker):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    quantity = request.form.get("quantity", "").strip()

    if not quantity.isdigit() or int(quantity) <= 0:
        flash("Please enter a valid quantity.", "error")
        return redirect(url_for("portfolio"))

    quantity = int(quantity)
    conn = get_db()

    try:
        stock = conn.execute(
            "SELECT id, ticker, company_name, current_price FROM stocks WHERE ticker = ?",
            (ticker,)
        ).fetchone()

        if not stock:
            flash("Stock not found.", "error")
            return redirect(url_for("portfolio"))

        holding = conn.execute(
            "SELECT id, quantity_owned FROM portfolio WHERE user_id = ? AND stock_id = ?",
            (session["user_id"], stock["id"])
        ).fetchone()

        if not holding or holding["quantity_owned"] < quantity:
            flash("You do not own enough shares to sell.", "error")
            return redirect(url_for("portfolio"))

        total_sale = stock["current_price"] * quantity
        new_quantity = holding["quantity_owned"] - quantity

        # Add money back to user
        conn.execute(
            "UPDATE users SET cash_balance = cash_balance + ? WHERE id = ?",
            (total_sale, session["user_id"])
        )

        # Add shares back to stock volume
        conn.execute(
            "UPDATE stocks SET total_volume = total_volume + ? WHERE id = ?",
            (quantity, stock["id"])
        )

        # Update or remove portfolio holding
        if new_quantity == 0:
            conn.execute(
                "DELETE FROM portfolio WHERE id = ?",
                (holding["id"],)
            )
        else:
            conn.execute(
                "UPDATE portfolio SET quantity_owned = ? WHERE id = ?",
                (new_quantity, holding["id"])
            )

        # Add transaction history
        conn.execute("""
            INSERT INTO transactions (user_id, stock_id, type, quantity, price, total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            stock["id"],
            "SELL",
            quantity,
            stock["current_price"],
            total_sale
        ))

        conn.commit()
        flash(f"Successfully sold {quantity} shares of {stock['ticker']}.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error selling stock: {e}", "error")

    finally:
        conn.close()

    return redirect(url_for("portfolio"))

@app.route("/admin/market")
def admin_market():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))
    
    conn = get_db()
    holidays = conn.execute(
        "SELECT * FROM market_holidays ORDER BY holiday_date"
    ).fetchall()
    conn.close()

    
    return render_template("admin_market.html", holidays=holidays)

@app.route("/cash", methods=["POST"])
def cash_transaction():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    action = request.form.get("action")
    amount = request.form.get("amount", "").strip()

    if not amount:
        flash("Enter an amount.", "error")
        return redirect(url_for("profile"))

    amount = float(amount)

    if amount <= 0:
        flash("Amount must be greater than 0.", "error")
        return redirect(url_for("profile"))

    conn = get_db()
    user = conn.execute(
        "SELECT cash_balance FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if action == "withdraw" and user["cash_balance"] < amount:
        conn.close()
        flash("You do not have enough cash to withdraw.", "error")
        return redirect(url_for("profile"))

    if action == "deposit":
        conn.execute(
            "UPDATE users SET cash_balance = cash_balance + ? WHERE id = ?",
            (amount, session["user_id"])
        )
        flash(f"Deposited ${amount:.2f}.", "success")

    elif action == "withdraw":
        conn.execute(
            "UPDATE users SET cash_balance = cash_balance - ? WHERE id = ?",
            (amount, session["user_id"])
        )
        flash(f"Withdrew ${amount:.2f}.", "success")

    conn.commit()
    conn.close()

    return redirect(url_for("profile"))

@app.route("/admin/users")
def admin_users():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    users = conn.execute("""
        SELECT id, first_name, last_name, username, email, role, cash_balance, created_at
        FROM users
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template("admin_users.html", users=users)

@app.route("/admin/logs")
def syslog():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    return render_template("syslog.html")

@app.route("/orders/cancel/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db()

    order = conn.execute("""
        SELECT * FROM orders
        WHERE id = ? AND user_id = ? AND status = 'PENDING'
    """, (order_id, session["user_id"])).fetchone()

    if not order:
        conn.close()
        flash("Order not found or already executed.", "error")
        return redirect(url_for("orders"))

    conn.execute("""
        UPDATE orders
        SET status = 'CANCELLED'
        WHERE id = ?
    """, (order_id,))
    conn.commit()
    conn.close()

    flash("Order cancelled successfully.", "success")
    return redirect(url_for("orders"))

@app.route("/admin/stocks/add", methods=["POST"])
def admin_add_stock():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    company_name = request.form.get("company_name")
    ticker = request.form.get("ticker").upper()
    total_volume = request.form.get("total_volume")
    current_price = request.form.get("current_price")

    conn = get_db()
    conn.execute("""
        INSERT INTO stocks 
        (company_name, ticker, total_volume, current_price, opening_price, day_high, day_low)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company_name,
        ticker,
        total_volume,
        current_price,
        current_price,
        current_price,
        current_price
    ))
    conn.commit()
    conn.close()

    flash("Stock added successfully.", "success")
    return redirect(url_for("admin_stocks"))





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        selected_role = request.form.get("role")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        # 1. Check if user exists
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("login"))

        # 2. Check password
        if not check_password_hash(user["password_hash"], password):
            flash("Incorrect password.", "error")
            return redirect(url_for("login"))

        #  3. ADD YOUR STEP HERE (role check)
        if selected_role != user["role"]:
            flash("That role does not match this account.", "error")
            return redirect(url_for("login"))

        # 4. Set session
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        # 5. Redirect based on role
        if user["role"] == "admin":
            return redirect(url_for("admin2"))

        return redirect(url_for("profile"))

    return render_template("login.html")

@app.route("/exchange")
def exchange():
    conn = get_db()
    stocks = conn.execute("SELECT * FROM stocks").fetchall()
    conn.close()

    return render_template("exchange.html", stocks=stocks)
    
@app.route("/logout")
def logout():
    session.clear()              # remember for remove all session data
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("reset.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    first_name = (request.form.get("first_name") or "").strip()
    last_name = (request.form.get("last_name") or "").strip()
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    phone_raw = (request.form.get("phone") or "").strip()
    phone = normalize_phone(phone_raw)
    password = request.form.get("password") or ""
    terms_ok = request.form.get("terms")

    errors = []

    if not first_name or not last_name:
        errors.append("First and last name are required.")
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if not email or "@" not in email:
        errors.append("Valid email is required.")
    if not phone or len(phone) < 10:
        errors.append("Valid phone number is required (10+ digits).")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if not terms_ok:
        errors.append("You must accept the Terms.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("signup"))

    password_hash = generate_password_hash(password)

    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO users (first_name, last_name, username, email, phone, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, username, email, phone, password_hash))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        flash("That username or email is already in use.", "error")
        return redirect(url_for("signup"))

    flash("Account created! Please log in.", "success")
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    user = conn.execute("""
        SELECT id, first_name, last_name, username, email, phone, role, cash_balance, created_at
        FROM users
        WHERE id = ?
    """, (session["user_id"],)).fetchone()
    conn.close()

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("home"))

    return render_template("profile.html", user=user)

@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    db = get_db()
    rows = db.execute("""
        SELECT 
            t.*,
            s.ticker,
            s.company_name
        FROM transactions t
        JOIN stocks s ON t.stock_id = s.id
        WHERE t.user_id = ?
        ORDER BY t.timestamp DESC
    """, (session["user_id"],)).fetchall()
    db.close()

    return render_template("transactions.html", transactions=rows)

@app.route("/order")
def order():
    ticker = request.args.get("ticker")
    db = get_db()
    stock = None

    if ticker:
        stock = db.execute(
            "SELECT * FROM stocks WHERE ticker = ?",
            (ticker,)
        ).fetchone()

    return render_template("order.html", stock=stock)

@app.route("/portfolio")
def portfolio():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db()

    holdings = conn.execute("""
        SELECT 
            portfolio.quantity_owned,
            stocks.ticker,
            stocks.company_name,
            stocks.current_price,
            (portfolio.quantity_owned * stocks.current_price) AS total_value
        FROM portfolio
        JOIN stocks ON portfolio.stock_id = stocks.id
        WHERE portfolio.user_id = ?
    """, (session["user_id"],)).fetchall()

    user = conn.execute(
        "SELECT cash_balance FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template("portfolio.html", holdings=holdings, user=user)


@app.route("/admin2")
def admin2():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        flash("You do not have permission to access the admin portal.", "error")
        return redirect(url_for("index"))

    return render_template("admin2.html")

@app.route("/order/<ticker>")
def order_stock(ticker):
    conn = get_db()
    stock = conn.execute(
        "SELECT * FROM stocks WHERE ticker = ?",
        (ticker,)
    ).fetchone()
    conn.close()

    if stock is None:
        flash("Stock not found.", "error")
        return redirect(url_for("exchange"))

    return render_template("order.html", stock=stock)

@app.route("/buy/<ticker>", methods=["POST"])
def buy_stock(ticker):
    if "user_id" not in session:
        flash("Login required.", "error")
        return redirect(url_for("login"))

    quantity = int(request.form.get("quantity"))

    conn = get_db()

    stock = conn.execute(
        "SELECT * FROM stocks WHERE ticker = ?",
        (ticker,)
    ).fetchone()

    if not stock:
        conn.close()
        flash("Stock not found.", "error")
        return redirect(url_for("exchange"))

    total = stock["current_price"] * quantity

    # for CREATE ORDER (NOT EXECUTE)
    conn.execute("""
        INSERT INTO orders (user_id, stock_id, type, quantity, price, total, status)
        VALUES (?, ?, 'BUY', ?, ?, ?, 'PENDING')
    """, (
        session["user_id"],
        stock["id"],
        quantity,
        stock["current_price"],
        total
    ))

    conn.commit()
    conn.close()

    flash("Order placed. Waiting for execution.", "success")
    return redirect(url_for("orders"))



@app.route("/admin/holidays/add", methods=["POST"])
def add_holiday():
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    holiday_date = request.form.get("holiday_date")
    reason = request.form.get("reason")

    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO market_holidays (holiday_date, reason) VALUES (?, ?)",
        (holiday_date, reason)
    )
    conn.commit()
    conn.close()

    flash("Market holiday added.", "success")
    return redirect(url_for("admin_market"))


@app.route("/admin/holidays/delete/<int:holiday_id>", methods=["POST"])
def delete_holiday(holiday_id):
    if session.get("role") != "admin":
        flash("Admins only.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM market_holidays WHERE id = ?", (holiday_id,))
    conn.commit()
    conn.close()

    flash("Market holiday removed.", "success")
    return redirect(url_for("admin_market"))



@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    orders = conn.execute("""
        SELECT o.*, s.ticker, s.company_name
        FROM orders o
        JOIN stocks s ON o.stock_id = s.id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template("orders.html", orders=orders)

@app.route("/orders/execute/<int:order_id>", methods=["POST"])
def execute_order(order_id):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    
    if not is_market_open():
        flash("Market is closed. Orders cannot be executed today.", "error")
        return redirect(url_for("orders"))

    conn = get_db()

    order = conn.execute("""
        SELECT o.*, s.ticker, s.current_price, s.total_volume
        FROM orders o
        JOIN stocks s ON o.stock_id = s.id
        WHERE o.id = ? AND o.user_id = ? AND o.status = 'PENDING'
    """, (order_id, session["user_id"])).fetchone()

    if not order:
        conn.close()
        flash("Order not found or already handled.", "error")
        return redirect(url_for("orders"))

    user = conn.execute(
        "SELECT cash_balance FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if order["type"] == "BUY":
        if user["cash_balance"] < order["total"]:
            conn.close()
            flash("Insufficient cash to execute order.", "error")
            return redirect(url_for("orders"))

        if order["total_volume"] < order["quantity"]:
            conn.close()
            flash("Not enough stock volume available.", "error")
            return redirect(url_for("orders"))

        conn.execute(
            "UPDATE users SET cash_balance = cash_balance - ? WHERE id = ?",
            (order["total"], session["user_id"])
        )

        conn.execute(
            "UPDATE stocks SET total_volume = total_volume - ? WHERE id = ?",
            (order["quantity"], order["stock_id"])
        )

        existing = conn.execute(
            "SELECT id FROM portfolio WHERE user_id = ? AND stock_id = ?",
            (session["user_id"], order["stock_id"])
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE portfolio SET quantity_owned = quantity_owned + ? WHERE id = ?",
                (order["quantity"], existing["id"])
            )
        else:
            conn.execute(
                "INSERT INTO portfolio (user_id, stock_id, quantity_owned) VALUES (?, ?, ?)",
                (session["user_id"], order["stock_id"], order["quantity"])
            )

    conn.execute("""
        INSERT INTO transactions (user_id, stock_id, type, quantity, price, total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        order["stock_id"],
        order["type"],
        order["quantity"],
        order["price"],
        order["total"]
    ))

    conn.execute(
        "UPDATE orders SET status = 'EXECUTED' WHERE id = ?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    flash("Order executed successfully.", "success")
    return redirect(url_for("orders"))

if __name__ == "__main__":
    app.run(debug=True)