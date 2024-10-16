from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_login import UserMixin

from .config import *


__all__ = ("db", "migrate", "User", "Tour")


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)


class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String)
    description = db.Column(db.String(120), nullable=False)
    min_price = db.Column(db.Integer, nullable=False)
