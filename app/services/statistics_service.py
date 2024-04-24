from datetime import datetime, timedelta
from app.models.activity.controller import ActivityController
from app.models.user.schemas import UserStatisticsSchema


class StatisticsService:
    @staticmethod
    def _get_start_date(period_time: str):
        period_dict = {
            'week': 7,
            'month': 30,
            'year': 365,
        }
        if period_time in period_dict:
            return (datetime.now() - timedelta(days=period_dict[period_time])).strftime('%Y-%m-%d')
        elif period_time == 'all_time':
            return None
        else:
            raise ValueError(f"Unknown period time: {period_time}")

    @staticmethod
    def user_statistics_count(user_id, period_time):
        start_date = StatisticsService._get_start_date(period_time)
        user_activities = ActivityController.get_by_user_id(user_id)
        if start_date:
            activities = [activity for activity in user_activities if activity.date >= start_date]
        else:
            activities = user_activities
        total_distance = sum(activity.distance_in_meters for activity in activities)
        total_time = sum(activity.duration for activity in activities)
        total_calories = sum(activity.calories_burned for activity in activities)
        data = {
            'total_distance_in_meters': total_distance,
            'total_time': total_time,
            'total_calories': total_calories,
        }
        return UserStatisticsSchema().load(data)
