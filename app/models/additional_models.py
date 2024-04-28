from datetime import datetime

import pytz
from sqlalchemy import Enum
from app.enum import AdminPremiumAction, AdminUserAction
from app.database import db

moscow_tz = pytz.timezone('Europe/Moscow')


class Admin_User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(Enum(AdminUserAction), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().astimezone(moscow_tz))

    admin = db.relationship('Admin', backref=db.backref('admin_user', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('admin_user', lazy='dynamic'))


class Admin_Premium(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    premium_id = db.Column(db.Integer, db.ForeignKey('premium.id'))
    action = db.Column(Enum(AdminPremiumAction), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().astimezone(moscow_tz))

    admin = db.relationship('Admin', backref=db.backref('admin_premium', lazy='dynamic'))
    premium = db.relationship('Premium', backref=db.backref('admin_premium', lazy='dynamic'))


class User_Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))

    user = db.relationship('User', backref=db.backref('user_card', lazy='dynamic'))
    card = db.relationship('Card', backref=db.backref('user_card', lazy='dynamic'))
