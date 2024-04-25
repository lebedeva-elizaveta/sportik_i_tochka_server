from werkzeug.exceptions import NotFound
from app.models.activity.model import Activity
from app.database import db


class ActivityController:
    model = Activity

    def __init__(self, activity_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == activity_id).first()
        if not self.db_entity:
            raise NotFound("Activity not found")

    @classmethod
    def create(cls, data):
        new_activity = cls.model(**data)
        db.session.add(new_activity)
        db.session.commit()
        return new_activity

    @classmethod
    def get_by_id(cls, activity_id):
        activity = db.session.query(cls.model).filter(cls.model.id == activity_id).first()
        if not activity:
            raise NotFound("Activity not found")
        return activity

    @classmethod
    def get_by_user_id(cls, user_id):
        user_activities = db.session.query(cls.model).filter(cls.model.user_id == user_id).all()
        return user_activities
