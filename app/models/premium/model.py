from datetime import datetime, timedelta

import pytz

from app.database import db

moscow_tz = pytz.timezone('Europe/Moscow')


class Premium(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow().astimezone(moscow_tz))
    end_date = db.Column(db.DateTime, default=datetime.utcnow().astimezone(moscow_tz) + timedelta(days=30))

    user = db.relationship('User', backref=db.backref('premiums', lazy='dynamic'))
