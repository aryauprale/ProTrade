from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html", page_css="style1.css")

@app.route("/aboutus")
def about():
    return render_template("aboutus.html", page_css="style1.css")





























if __name__ == '__main__':
    app.run(debug=True)