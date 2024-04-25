from datetime import datetime, timedelta
from marshmallow import ValidationError
from app.models.activity.controller import ActivityController
from app.models.admin.schemas import AdminStatisticsSchema
from app.models.premium.model import Premium
from app.models.user.model import User
from app.models.user.schemas import UserStatisticsSchema, UserAverageStatisticsSchema, PremiumStatisticsSchema


class StatisticsService:
    @staticmethod
    def _get_start_date(period_time: str):
        period_dict = {
            'week': 7,
            'month': 30,
            'year': 365,
        }
        if period_time in period_dict:
            return datetime.now() - timedelta(days=period_dict[period_time])
        elif period_time == 'all_time':
            return None
        else:
            raise ValueError(f"Unknown period time: {period_time}")

    @staticmethod
    def user_statistics_count(user_id, period_time):
        user_activities = ActivityController.get_by_user_id(user_id)
        if not user_activities:
            return {
                'total_distance_in_meters': 0,
                'total_time': 0,
                'total_calories': 0,
            }

        start_date = StatisticsService._get_start_date(period_time)

        if start_date:
            activities = [
                activity for activity in user_activities
                if activity.date >= start_date.date()
            ]
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

    @staticmethod
    def user_average_statistics(user_id, total_activities_count):
        if total_activities_count == 0:
            return {
                "avg_speed": 0,
                "average_distance_in_meters": 0,
                "average_time": 0,
                "average_calories": 0,
            }

        statistics = StatisticsService.user_statistics_count(user_id, "all_time")

        total_distance = statistics.get("total_distance_in_meters")
        total_time = statistics.get("total_time")
        total_calories = statistics.get("total_calories")

        avg_speed = round(total_distance / total_time, 2)
        average_distance = round(total_distance / total_activities_count)
        average_time = round(total_time / total_activities_count)
        average_calories = round(total_calories / total_activities_count)

        data = {
            "avg_speed": avg_speed,
            "average_distance_in_meters": average_distance,
            "average_time": average_time,
            "average_calories": average_calories,
        }

        try:
            validated_data = UserAverageStatisticsSchema().load(data)
        except ValidationError as e:
            return {"error": f"Data validation error: {e}"}
        return validated_data

    @staticmethod
    def premium_statistics_count(user_id, period):
        statistics = StatisticsService.user_statistics_count(user_id, period)
        if not statistics:
            return {"success": False, "message": "Statistics not found"}, 404

        total_distance_in_meters = statistics['total_distance_in_meters']
        total_time = statistics['total_time']
        total_calories = statistics['total_calories']
        avg_speed = round(total_distance_in_meters / total_time, 2)

        premium_statistics_response = {
            "total_distance_in_meters": total_distance_in_meters,
            "total_time": total_time,
            "total_calories": total_calories,
            "avg_speed": avg_speed,
            "activities": ActivityController.get_by_user_id(user_id)
        }

        return PremiumStatisticsSchema().dump(premium_statistics_response), 200

    @staticmethod
    def admin_statistics_count(period):
        start_date = StatisticsService._get_start_date(period)
        if start_date is None:
            first_user_registration = User.query.order_by(User.date_of_registration).first()
            start_date = first_user_registration.date_of_registration if first_user_registration else datetime.now()
        end_date = datetime.now()

        total_users = User.query.count()
        graph_data = []
        current_date = start_date

        while current_date <= end_date:
            premium_users_count = Premium.query.filter(
                Premium.start_date <= current_date,
                Premium.end_date >= current_date
            ).count()

            registered_users_count = User.query.filter(User.date_of_registration <= current_date).count()
            non_premium_users_count = registered_users_count - premium_users_count

            graph_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'users_with_premium': premium_users_count,
                'users_without_premium': non_premium_users_count
            })

            current_date += timedelta(days=1)

        admin_statistics_response = {
            'total_users': total_users,
            'premium_users': Premium.query.filter(Premium.end_date >= datetime.now()).count(),
            'graph_data': graph_data
        }

        return AdminStatisticsSchema().dump(admin_statistics_response), 200
