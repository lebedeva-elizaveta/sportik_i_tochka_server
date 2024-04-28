from datetime import datetime

import pytz

from app.database import db


moscow_tz = pytz.timezone('Europe/Moscow')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.Text, nullable=True)
    date_of_registration = db.Column(db.DateTime, default=datetime.now().astimezone(moscow_tz))
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
