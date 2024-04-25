from datetime import datetime
from operator import itemgetter

from flask import jsonify
from app.models.achievement.controller import AchievementController
from app.models.achievement.schemas import AchievementSchema
from app.models.base_controller import BaseUser
from app.models.user.model import User
from app.models.user.schemas import UserCreate, UserProfileSchema
from app.models.premium.model import Premium
from app.services.statistics_service import StatisticsService
from app.services.user_service import UserService


class UserController(BaseUser):
    model = User
    schema = UserCreate

    def get_role(self):
        return "user"

    @classmethod
    def premium_or_regular(cls, user_id):
        if not isinstance(user_id, int):
            raise ValueError("user_id must be an integer")
        current_datetime = datetime.utcnow()
        active_premium = Premium.query.filter_by(user_id=user_id).filter(
            Premium.end_date > current_datetime
        ).first()
        if active_premium:
            return "premium"
        return "regular"

    @classmethod
    def get_profile_data(cls, access_token, period):
        user_id = cls.get_id_from_access_token(access_token)
        user = cls.get_by_id(user_id)
        statistics = StatisticsService.user_statistics_count(user_id, period)
        achievements = AchievementController.get_by_user_id(user_id)
        response_data = {
            "name": user.name,
            "image": user.avatar,
            "statistics": statistics,
            "achievements": AchievementSchema(many=True).dump(achievements)
        }
        return jsonify(UserProfileSchema().dump(response_data)), 200

    @classmethod
    def get_rating(cls):
        users = User.query.all()
        list_of_users = []
        for user in users:
            role = UserController.premium_or_regular(user.id)
            list_of_users.append(UserService.get_user_data_for_rating(user, role))
        return sorted(filter(None, list_of_users), key=itemgetter('rating'))
