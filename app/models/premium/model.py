from datetime import datetime, timedelta

from database import db


class Premium(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow())
    end_date = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(days=30))

    user = db.relationship('User', backref=db.backref('premiums', lazy='dynamic'))
