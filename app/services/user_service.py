from datetime import datetime

from sqlalchemy import func

from app.database import db
from app.models.achievement.controller import AchievementController
from app.models.achievement.schemas import AchievementListSchema
from app.models.activity.controller import ActivityController
from app.models.activity.model import Activity
from app.models.user.schemas import UserDataForRatingSchema
from app.services.statistics_service import StatisticsService


class UserService:

    @staticmethod
    def get_user_rating(user_id):
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        users_dist = db.session.query(Activity.user_id, func.sum(Activity.distance_in_meters)). \
            filter(Activity.date >= start_of_month). \
            group_by(Activity.user_id). \
            order_by(func.sum(Activity.distance_in_meters).desc()).all()

        user_place = next(
            (idx + 1 for idx, (uid, _) in enumerate(users_dist) if uid == user_id),
            None
        )
        return user_place

    @staticmethod
    def get_user_data_for_rating(user, role):
        user_achievements = AchievementController.get_by_user_id(user.id)
        total_activities_count = len(ActivityController.get_by_user_id(user.id))
        statistics = StatisticsService.user_statistics_count(user.id, "all_time")
        average_statistics = StatisticsService.user_average_statistics(user.id, total_activities_count)

        user_data = {
            "id": user.id,
            "name": user.name,
            "image": user.avatar,
            "role": role,
            "rating": user.id if total_activities_count == 0 else UserService.get_user_rating(user.id),
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

        return UserDataForRatingSchema().dump(user_data)
