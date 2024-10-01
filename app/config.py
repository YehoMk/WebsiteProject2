from flask import Flask


__all__ = ("app",)

app = Flask(__name__)
app.config["SECRET_KEY"] = "<KEY>"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
