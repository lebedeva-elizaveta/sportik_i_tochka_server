from flask_apscheduler import APScheduler

from app.exceptions.exceptions import InvalidRoleException, NotFoundException
from app.models.achievement.controller import AchievementController
from app.models.base_controller import BaseController
from app.models.premium.controller import PremiumController
from app.models.user.model import User
from app.models.user.schemas import UserCreate
from app.services.image_service import ImageService
from app.services.security_service import EncryptionService
from app.services.statistics_service import StatisticsService
from app.services.user_service import UserService


class UserController(BaseController):
    model = User
    schema = UserCreate

    scheduler = APScheduler()

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
        rating_data, _ = cls.get_rating()
        users = rating_data["users"]

        user_rating = None
        for idx, user_data in enumerate(users):
            if user_data["id"] == user_id:
                user_rating = user_data["rating"]
                break

        response = {
            "name": user.name,
            "image": ImageService.get_uploaded_file_url(user.avatar, 'avatars'),
            "statistics": statistics,
            "achievements": achievements,
            "rating": user_rating
        }
        return response, 200

    @classmethod
    def get_rating(cls):
        users = cls.model.query.all()
        active_users = []
        inactive_users = []

        for user in users:
            role = UserController.get_user_status(user.id)
            user_data = UserService.get_user_data_for_rating(user, role)
            if user_data["total_activities_count"] > 0:
                active_users.append(user_data)
            else:
                inactive_users.append(user_data)

        active_users_sorted = UserService.sort_active_users(active_users)
        base_rating = len(active_users_sorted)

        inactive_users_sorted = UserService.sort_inactive_users(inactive_users, base_rating)

        sorted_list = active_users_sorted + inactive_users_sorted

        return {"users": sorted_list}, 200

    @staticmethod
    def get_premium_statistics(user_id, period):
        user_status = UserController.get_user_status(user_id)
        if user_status != "premium":
            raise InvalidRoleException("User is not premium")
        response = StatisticsService.premium_statistics_count(user_id, period)
        return response, 200

    @staticmethod
    def get_top_user():
        rating_result = UserController.get_rating()
        users = rating_result[0]["users"]
        if users:
            top_user = users[0]
            return top_user
        else:
            raise NotFoundException("No users found")

    @staticmethod
    @scheduler.task('cron', id='give_premium_award', day=1, hour=0, minute=0, timezone='Europe/Moscow')
    def premium_award():
        with UserController.scheduler.app.app_context():
            user = UserController.get_top_user()
            UserService.premium_award(user)

    @classmethod
    def change_password(cls, email, new_password, confirm_password):
        user = cls.get_by_email(email)
        return BaseController.change_password(user, new_password, confirm_password)
