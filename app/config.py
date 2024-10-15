from flask import Flask
from flask_login import LoginManager


__all__ = ("app", "login", "ALLOWED_EXTENSIONS", "UPLOAD_FOLDER")


UPLOAD_FOLDER = "C:/Users/user/PycharmProjects/WebsiteProject2/app/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


app = Flask(__name__)
app.config["SECRET_KEY"] = "<KEY>"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

login = LoginManager(app)
