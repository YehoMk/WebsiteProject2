from flask import render_template, request, redirect, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, login_required, logout_user
import os
from werkzeug.utils import secure_filename


from .config import *
from .db import *


__all__ = ("index", "tours", "register_retrieve", "register_process", "login_retrieve", "login_process", "logout")


def allowed_file(filename):
    """
    Checks the validity of an uploaded file. More specifically weather it has an extension and weather this extension is in ALLOWED_EXTENSIONS.
    :param filename:
    :return: filename.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@login.user_loader
def load_user(user_id):
    print(user_id)
    print(User.query.get(int(user_id)))
    return User.query.get(int(user_id))


# The main pages


@app.route("/index")
@app.route("/")
def index():
    """
    The function for the main page of the website.
    :return: template for the main page.
    """
    return render_template("index.html")


@app.route("/tours")
def tours():
    """
    The function for the page with the tours .
    :return: template for the tours page.
    """
    tours = Tour.query.all()
    return render_template("tours.html", tours=tours)


# Admin related pages


@app.route("/add_tours", methods=["GET"])
def add_tours_retrieve():
    """
    :return: HTML with the form for tour creation.
    """
    print(current_user.get_id())
    if current_user.get_id() is None or current_user.id != 1:
        return "Error: this page is available only for admin users."
    return render_template("add_tours.html")


@app.route("/add_tours", methods=["POST"])
def add_tours_process():
    """
    Adds a tour to the database. Adds the image files to the uploads folder. Creates the upload folder if there isn't one yet.
    :return: addTourResultText used in the form.
    """

    # Checks the image and adds it to the upload folder
    file = request.files["image"]
    if file and allowed_file(file.filename):
        if "uploads" not in os.listdir("app/static"):
            os.mkdir("app/static/uploads")
        if os.listdir("app/static/uploads") == []:
            image_id = "1"
        else:
            image_id_list = [int(image.rsplit(".", 1)[0]) for image in os.listdir("app/static/uploads")]
            image_id_list.sort()
            image_id = str(image_id_list[-1] + 1)

        filename = secure_filename(file.filename)
        id_filename = filename.rsplit(".", 1)
        id_filename[0] = image_id
        id_filename = ".".join(id_filename)

        image_path = f"/static/uploads/{id_filename}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], id_filename))

    # Gets the rest of the information and adds it to the database
    title = request.form["title"]
    description = request.form["description"]
    min_price = request.form["minPrice"]
    tour = Tour(title=title, description=description, min_price=min_price, image_path=image_path)
    try:
        db.session.add(tour)
        db.session.commit()
        return "Success"
    except IntegrityError:
        db.session.rollback()
        return "Tour creation error."


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
        return "Incorrect details. Try again."
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
