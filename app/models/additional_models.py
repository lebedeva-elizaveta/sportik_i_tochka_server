from datetime import datetime

import pytz
from sqlalchemy import Enum
from sqlalchemy.sql import sqltypes

from app.enum import AdminAction
from app.database import db

moscow_tz = pytz.timezone('Europe/Moscow')


class Admin_User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(Enum(AdminAction), nullable=False)
    timestamp = db.Column(sqltypes.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow().astimezone(moscow_tz))

    admin = db.relationship('Admin', backref=db.backref('admin_user', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('admin_user', lazy='dynamic'))


class User_Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))

    user = db.relationship('User', backref=db.backref('user_card', lazy='dynamic'))
    card = db.relationship('Card', backref=db.backref('user_card', lazy='dynamic'))
