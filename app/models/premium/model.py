from datetime import datetime, timedelta

import pytz
from sqlalchemy.sql import sqltypes

from app.database import db

moscow_tz = pytz.timezone('Europe/Moscow')


class Premium(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_date = db.Column(sqltypes.TIMESTAMP(timezone=True), default=datetime.utcnow().astimezone(moscow_tz))
    end_date = db.Column(sqltypes.TIMESTAMP(timezone=True), default=datetime.utcnow().astimezone(moscow_tz) + timedelta(days=30))

    user = db.relationship('User', backref=db.backref('premiums', lazy='dynamic'))


class Premium_Award(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(sqltypes.TIMESTAMP(timezone=True), default=datetime.utcnow().astimezone(moscow_tz))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref=db.backref('premium_awards', lazy='dynamic'))
