from operator import itemgetter

from app.exceptions.exceptions import InvalidRoleException
from app.models.achievement.controller import AchievementController
from app.models.base_controller import BaseController
from app.models.premium.controller import PremiumController
from app.models.user.model import User
from app.models.user.schemas import UserCreate
from app.services.security_service import EncryptionService
from app.services.statistics_service import StatisticsService
from app.services.user_service import UserService


class UserController(BaseController):
    model = User
    schema = UserCreate

    def get_role(self):
        return "user"

    @staticmethod
    def register_new_user(data):
        password = data.get('password_hash')
        data['password_hash'] = EncryptionService.generate_password_hash(password)

        new_user = UserController.create(data=data)
        user = UserController(entity_id=new_user.id)

        response = {
            "success": True,
            "access_token": user.generate_access_token(),
            "user_id": new_user.id
        }

        return response, 201

    @staticmethod
    def get_user_status(user_id):
        active_premium = PremiumController.is_active(user_id)
        if active_premium:
            user_status = "premium"
        else:
            user_status = "regular"
        return user_status

    @classmethod
    def get_profile_data(cls, user_id, period):
        user = cls.get_by_id(user_id)
        statistics = StatisticsService.user_statistics_count(user_id, period)
        achievements = AchievementController.get_by_user_id(user_id)
        response = {
            "name": user.name,
            "image": user.avatar,
            "statistics": statistics,
            "achievements": achievements
        }
        return response, 200

    @classmethod
    def get_rating(cls):
        users = User.query.all()
        list_of_users = []
        for user in users:
            role = UserController.get_user_status(user.id)
            list_of_users.append(UserService.get_user_data_for_rating(user, role))
        sorted_list = sorted(filter(None, list_of_users), key=itemgetter('rating'))
        return {"users": sorted_list}, 200

    @staticmethod
    def get_premium_statistics(user_id, period):
        user_status = UserController.get_user_status(user_id)
        if user_status != "premium":
            raise InvalidRoleException("User is not premium")
        response = StatisticsService.premium_statistics_count(user_id, period)
        return response, 200
