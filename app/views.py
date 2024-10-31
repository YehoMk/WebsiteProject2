from flask import render_template, request, redirect, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, NoResultFound
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
    index_selector = "border-bottom border-light border-2"
    return render_template("index.html", index_selector=index_selector)


@app.route("/tours")
def tours():
    """
    The function for the page with the tours. The selector variable contains needed bootstrap styling.
    :return: template for the tours page.
    """
    if current_user.get_id() is None:
        return "Error: You must login to view this page."
    tours = Tour.query.all()
    tours_selector = "border-bottom border-light border-2"
    return render_template("tours.html", tours=tours, tours_selector=tours_selector)


# tours processing

@app.route("/tours/modal/<int:tour_id>", methods=["GET"])
def tours_modal_retrieve(tour_id):
    """
    Renders the "book tour" page and form within the tourModal.
    :param tour_id: The id of the tour that was selected for booking.
    """
    tour = Tour.query.filter_by(id=tour_id).one()
    return render_template("tours_modal.html", tour=tour)


@app.route("/tours/modal/<int:tour_id>", methods=["POST"])
def tours_modal_process(tour_id):
    """
    Books the tour by making an instance of the Booking database model. Calculates the price depending on the form data.
    :param tour_id: The id of the tour that was selected for booking.
    """
    people_value = int(request.form["people"])
    days_value = int(request.form["days"])
    food_value = request.form["food"]

    for element in [element for element in str(people_value)]:
        if element not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return "Error: People value should be a number."
    if not (1 <= people_value <= 4):
        return "Error: People value should be between 1 and 4"

    for element in [element for element in str(people_value)]:
        if element not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return "Error: Days value should be a number."
    if not (1 <= days_value <= 30):
        return "Error: Days value should be between 1 and 30"

    if food_value not in ["noFood", "breakfasts", "allInclusive"]:
        return "Error: Incorrect food value."

    if people_value == 1:
        people_percent = 0
    elif people_value == 2:
        people_percent = 10
    elif people_value == 3:
        people_percent = 20
    elif people_value == 4:
        people_percent = 30

    if 1 <= days_value <= 3:
        days_percent = 0
    elif 4 <= days_value <= 7:
        days_percent = 15
    elif 7 <= days_value <= 15:
        days_percent = 30
    elif 15 <= days_value <= 30:
        days_percent = 40

    if food_value == "noFood":
        food_percent = 0
    elif food_value == "breakfasts":
        food_percent = 15
    elif food_value == "allInclusive":
        food_percent = 30

    total_percent = people_percent + days_percent + food_percent
    tour = Tour.query.filter_by(id=tour_id).one()
    price = int((tour.max_price - tour.min_price) * total_percent/100 + tour.min_price)
    print(price)

    booking = Booking(user_id=int(current_user.id), tour_id=tour_id, people_value=people_value, days_value=days_value, food_value=food_value, price=price)
    try:
        db.session.add(booking)
        db.session.commit()
        return "Success"
    except IntegrityError:
        db.session.rollback()
        return "Booking error."


# Admin related pages


@app.route("/tours_manage", methods=["GET"])
def tours_manage_retrieve():
    """
    Renders the admin panel.
    """
    if current_user.get_id() is None or current_user.id != 1:
        return "Error: this page is available only for admin users."
    return render_template("admin_tours.html")


@app.route("/tours_manage/add_tours", methods=["GET"])
def tours_add_retrieve():
    """
    Renders the "add tour" form within the AdminModal.
    """
    print(current_user.get_id())
    return render_template("admin_tours_add.html")


@app.route("/tours_manage/add_tours", methods=["POST"])
def tours_add_process():
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
    max_price = request.form["maxPrice"]

    if len(title) > 20:
        return "Error: The title can't have more than 20 characters."
    if len(description) > 800:
        return "Error: The description can't have more than 800 characters."

    tour = Tour(title=title, description=description, min_price=min_price, max_price=max_price, image_path=image_path)

    try:
        db.session.add(tour)
        db.session.commit()
        return "Success"
    except IntegrityError:
        db.session.rollback()
        return "Tour creation error."


@app.route("/tours_manage/edit_tours", methods=["GET"])
def tours_edit_retrieve():
    """
    Renders the "edit tour" selection within the AdminModal.
    """
    tours = Tour.query.all()
    return render_template("admin_tours_edit.html", tours=tours)


@app.route("/tours_manage/edit_tours/<int:tour_id>", methods=["GET"])
def tours_edit_form_retrieve(tour_id):
    """
    Renders the "edit tour" form within the AdminModal.
    :param tour_id: The id of the tour that was selected for editing.
    """
    return render_template("admin_tours_edit_form.html", tour_id=tour_id)


@app.route("/tours_manage/edit_tours/<int:tour_id>", methods=["POST"])
def tours_edit_form_process(tour_id):
    """
    Edits an already existing tour in the database. Adds the image files to the uploads folder. Creates the upload folder if there isn't one yet.
    :param tour_id: The id of the tour that was selected for editing.
    :return: editTourResultText used in the form.
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
    max_price = request.form["maxPrice"]
    tour = Tour.query.filter_by(id=tour_id).one()

    if len(title) > 20:
        return "Error: The title can't have more than 20 characters."
    if len(description) > 800:
        return "Error: The description can't have more than 800 characters."

    try:
        tour.title = title
        tour.image_path = image_path
        tour.description = description
        tour.min_price = min_price
        tour.max_price = max_price
        db.session.commit()
        return "Success"
    except IntegrityError:
        db.session.rollback()
        return "Tour creation error."



@app.route("/tours_manage/delete_tours", methods=["GET"])
def tours_delete_retrieve():
    """
    Renders the "delete tour" selection within the AdminModal.
    """
    tours = Tour.query.all()
    return render_template("admin_tours_delete.html", tours=tours)


@app.route("/tours_manage/delete_tours/<int:tour_id>", methods=["POST"])
def tours_delete_process(tour_id):
    """
    :param tour_id: The id of the tour that was selected for deletion.
    :return: tour_id that is displayed in the selection.
    """
    tour = Tour.query.filter_by(id=tour_id).one()
    db.session.delete(tour)
    db.session.commit()
    return f"Deleted {[tour_id]}"


# Account management


@app.route("/profile", methods=["GET"])
def profile():
    """
    :return: HTML with profile content needed for the accountModal.
    """
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    bookings_full_data = []
    for booking in bookings:
        booking_dict = dict()

        booking_dict["tour_id"] = booking.tour_id
        booking_dict["people_value"] = booking.people_value
        booking_dict["days_value"] = booking.days_value
        booking_dict["food_value"] = booking.food_value
        booking_dict["price"] = booking.price

        try:
            tour = Tour.query.filter_by(id=booking.tour_id).one()
        except NoResultFound:
            booking_dict["tour_title"] = "[deleted tour]"
            booking_dict["tour_image_path"] = "/"
        else:
            booking_dict["tour_title"] = tour.title
            booking_dict["tour_image_path"] = tour.image_path


        bookings_full_data.append(booking_dict)

    return render_template("profile.html", bookings_full_data=bookings_full_data)


@app.route("/register", methods=["GET"])
def register_retrieve():
    """
    :return: HTML with register content needed for the accountModal.
    """
    return render_template("register.html")


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
    response = make_response("success")
    response.headers["HX-Trigger"] = "makeAccountButtonProfile"
    return response


@app.route("/login_profile_button", methods=["GET"])
def login_profile_button_retrieve():
    """
    :return: HTML with the profile button needed for the accountModal after the user logs in.
    """
    return render_template("profile_button.html")


@app.route("/logout")
@login_required
def logout():
    """
    Logs the user out.
    :return: redirect for the main page.
    """
    logout_user()
    return redirect(url_for("index"))
