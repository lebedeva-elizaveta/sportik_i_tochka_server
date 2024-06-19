from marshmallow import ValidationError

from app.database import db
from app.exceptions.exceptions import NotFoundException
from app.models.achievement.model import Achievement
from app.models.achievement.schemas import AchievementSchema


class AchievementController:
    model = Achievement

    def __init__(self, achievement_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == achievement_id).first()
        if not self.db_entity:
            raise NotFoundException("Achievement not found")

    @classmethod
    def create(cls, data):
        try:
            validated_data = AchievementSchema().load(data)
        except ValidationError as ve:
            raise
        new_achievement = cls.model(**validated_data)
        db.session.add(new_achievement)
        db.session.commit()
        return new_achievement

    @classmethod
    def get_by_user_id(cls, user_id):
        user_achievements = db.session.query(cls.model).filter(cls.model.user_id == user_id).all()
        return user_achievements
