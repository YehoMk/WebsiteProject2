from flask import render_template, request, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from .config import *
from .db import *


__all__ = ("index", "rent")


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/rent")
def rent():
    return render_template("rent.html")


@app.route("/register", methods=["POST"])  # Responsible for processing user registration.
def register():
    print("success")
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    password_hash = generate_password_hash(password)
    print(username, email, password_hash)
    user = User(username=username, email=email, password_hash=password_hash)
    try:
        db.session.add(user)
        db.session.commit()
        return "Success"
    except IntegrityError:
        db.session.rollback()
        return "This user already exists try again."
