from app.database import db


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_name = db.Column(db.String(255), nullable=False)
    card_number = db.Column(db.String(255), nullable=False, unique=True)
    month = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(255), nullable=False)
    cvv = db.Column(db.String(255), nullable=False)
