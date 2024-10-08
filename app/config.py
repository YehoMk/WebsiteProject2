from flask import Flask
from flask_login import LoginManager


__all__ = ("app", "login")


app = Flask(__name__)
app.config["SECRET_KEY"] = "<KEY>"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"


login = LoginManager(app)
