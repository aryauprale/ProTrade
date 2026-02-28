from flask import Flask, render_template

app = Flask(__name__)

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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        # later I will validate phone/otp and redirect
        return redirect(url_for("verify"))
    return render_template("reset.html")

@app.route("/signup")
def signup():
    return render_template("signup.html", debug_marker="TEMPLATE LOADED")

if __name__ == "__main__":
    app.run(debug=True)