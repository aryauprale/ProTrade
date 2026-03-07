from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "dev"  # change later


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    flash("Login successful!", "success")
    return redirect(url_for("home"))

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


if __name__ == "__main__":
    app.run(debug=True)