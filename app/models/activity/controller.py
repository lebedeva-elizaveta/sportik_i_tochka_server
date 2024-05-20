from marshmallow import ValidationError

from app.exceptions.exceptions import NotFoundException
from app.models.activity.model import Activity
from app.database import db
from app.models.activity.schemas import ActivitySchema
from app.services.image_service import uploaded_file


class ActivityController:
    model = Activity

    def __init__(self, activity_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == activity_id).first()
        if not self.db_entity:
            raise NotFoundException("Activity not found")

    @classmethod
    def create(cls, data):
        try:
            validated_data = ActivitySchema().load(data)
        except ValidationError:
            raise
        new_activity = cls.model(**validated_data)
        db.session.add(new_activity)
        db.session.commit()
        return new_activity

    @classmethod
    def get_by_id(cls, activity_id):
        activity = db.session.query(cls.model).filter(cls.model.id == activity_id).first()
        if not activity:
            raise NotFoundException("Activity not found")
        return activity

    @classmethod
    def get_by_user_id(cls, user_id):
        user_activities = db.session.query(cls.model).filter(cls.model.user_id == user_id).all()
        return user_activities

    @staticmethod
    def add_activity(activity_data):
        new_activity = ActivityController.create(activity_data)
        return {
                   "success": True,
                   "activity_id": new_activity.id
               }, 201

    @staticmethod
    def get_activities(user_id):
        user_activities = ActivityController.get_by_user_id(user_id)
        if not user_activities:
            return {
                       "success": True,
                       "message": "No activities yet"
                   }, 200
        else:
            for activity in user_activities:
                activity.image = uploaded_file(activity.image, 'images/activities')
            return user_activities, 200
