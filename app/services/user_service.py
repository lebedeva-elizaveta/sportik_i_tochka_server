from datetime import datetime, timedelta

import pytz

from sqlalchemy import func

from app.database import db
from app.models.achievement.controller import AchievementController
from app.models.achievement.schemas import AchievementListSchema
from app.models.activity.model import Activity
from app.models.premium.controller import PremiumController
from app.services.image_service import ImageService
from app.services.statistics_service import StatisticsService

moscow_tz = pytz.timezone('Europe/Moscow')


class UserService:

    @staticmethod
    def get_user_distance(user_id):
        start_of_month = datetime.now().astimezone(moscow_tz).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        user_dist = db.session.query(func.sum(Activity.distance_in_meters)). \
            filter(Activity.date >= start_of_month). \
            filter(Activity.user_id == user_id). \
            group_by(Activity.user_id). \
            first()
        return user_dist[0] if user_dist else 0

    @staticmethod
    def get_user_data_for_rating(user, role):
        user_achievements = AchievementController.get_by_user_id(user.id)
        total_activities_count = UserService.get_user_distance(user.id)
        statistics = StatisticsService.user_statistics_count(user.id, "all_time")
        average_statistics = StatisticsService.user_average_statistics(user.id, total_activities_count)
        user_data = {
            "id": user.id,
            "name": user.name,
            "image": ImageService.get_static_file_url(user.avatar, 'avatars') if user.avatar is not None else None,
            "role": role,
            "is_blocked": user.is_blocked,
            "total_activities_count": total_activities_count,
            "total_distance_in_meters": statistics.get("total_distance_in_meters"),
            "total_time": statistics.get("total_time"),
            "total_calories": statistics.get("total_calories"),
            "avg_speed": average_statistics.get("avg_speed"),
            "average_distance_in_meters": average_statistics.get("average_distance_in_meters"),
            "average_time": average_statistics.get("average_time"),
            "average_calories": average_statistics.get("average_calories"),
            "achievements": AchievementListSchema().dump({"achievements": user_achievements}).get("achievements"),
        }
        return user_data

    @staticmethod
    def sort_active_users(users):
        sorted_users = sorted(users, key=lambda u: u["total_distance_in_meters"], reverse=True)

        for idx, user in enumerate(sorted_users):
            user["rating"] = idx + 1

        return sorted_users

    @staticmethod
    def sort_inactive_users(users, base_rating):
        sorted_users = sorted(users, key=lambda u: u["id"])

        for idx, user in enumerate(sorted_users):
            user["rating"] = base_rating + idx + 1

        return sorted_users

    @staticmethod
    def premium_award(user):
        user_id = user.get('id')
        if not PremiumController.get_premium_award(user_id):
            if not PremiumController.is_active(user_id):
                PremiumController.create(user_id)
                PremiumController.create_premium_award(user_id)
            else:
                premium = PremiumController.get_active_premium(user_id)
                if premium:
                    new_end_date = premium.end_date + timedelta(days=30)
                    PremiumController.extend_premium(premium.id, new_end_date)
