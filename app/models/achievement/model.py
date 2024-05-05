from app.database import db


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    distance = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('achievements', lazy='dynamic'))
