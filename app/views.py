from .config import app

from flask import render_template


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/rent")
def rent():
    return render_template("rent.html")
