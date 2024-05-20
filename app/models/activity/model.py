from sqlalchemy import Enum
from app.enum import ActivityType
from app.database import db


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False)
    distance_in_meters = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    avg_speed = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    image = db.Column(db.String, nullable=False)
    activity_type = db.Column(Enum(ActivityType), nullable=False)

    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
