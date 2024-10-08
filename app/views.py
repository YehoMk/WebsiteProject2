from flask import render_template, request, redirect, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, login_required, logout_user

from .config import *
from .db import *


__all__ = ("index", "rent", "register_retrieve", "register_process", "login_retrieve", "login_process", "logout")


@login.user_loader
def load_user(user_id):
    print(user_id)
    print(User.query.get(int(user_id)))
    return User.query.get(int(user_id))


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/rent")
def rent():
    return render_template("rent.html")


# Account management


@app.route("/register", methods=["GET"])
def register_retrieve():
    """
    :return: HTML with register content needed for the accountModal.
    """
    return render_template("register_and_profile.html")


@app.route("/register", methods=["POST"])
def register_process():
    """
    Processes user registration.
    :return: resultText used in the accountModal.
    """
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
        return "This user already exists. Try again."


@app.route("/login", methods=["GET"])
def login_retrieve():
    """
    :return: HTML with login content needed for the accountModal.
    """
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_process():
    """
    Processes user login.
    :return: resultText used in the accountModal.
    """
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    print(username, password)
    print(user)
    if user is None or not check_password_hash(user.password_hash, password):
        return "This user already exists. Try again."
    login_user(user, remember=True)
    return "Success"


@app.route("/logout")
@login_required
def logout():
    """
    Logs the user out.
    :return: redirect for the main page.
    """
    logout_user()
    return redirect(url_for("index"))
