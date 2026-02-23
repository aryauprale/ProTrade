from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")

@app.route("/aboutus")
def about():
    return render_template("aboutus.html")


if __name__ == "__main__":
    app.run(debug=True)