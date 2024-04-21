from datetime import datetime, timedelta

from models import Activity, User, Premium


def user_statistics_count(user_id, period_time):
    if period_time == 'week':
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period_time == 'month':
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif period_time == 'year':
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    elif period_time == 'all_time':
        start_date = None
    else:
        return None
    if start_date:
        activities = Activity.query.filter(Activity.user_id == user_id, Activity.date >= start_date).all()
    else:
        activities = Activity.query.filter_by(user_id=user_id).all()
    total_distance = sum(activity.distance for activity in activities)
    total_time = sum(activity.duration for activity in activities)
    total_calories = sum(activity.calories for activity in activities)

    return {
        'total_distance_in_meters': total_distance,
        'total_time': total_time,
        'total_calories': total_calories
    }


def user_average_statistics(user_id):
    statistics = user_statistics_count(user_id, "all_time")
    total_distance = statistics['total_distance_in_meters']
    total_time = statistics['total_time']
    total_calories = statistics['total_calories']

    activities = Activity.query.filter_by(user_id=user_id).all()

    activities_count = len(activities)
    if activities_count == 0:
        return None

    avg_speed = round(total_distance / total_time, 2)
    average_distance = round(total_distance / activities_count)
    average_time = round(total_time / activities_count)
    average_calories = round(total_calories / activities_count)

    return {
        'avg_speed': avg_speed,
        'average_distance_in_meters': average_distance,
        'average_time': average_time,
        'average_calories': average_calories
    }


def admin_statistics(period_time):
    total_users = User.query.count()
    premium_users = Premium.query.filter(Premium.end_date >= datetime.now()).count()
    start_date = None
    if period_time == 'week':
        start_date = datetime.now().date() - timedelta(days=7)
    elif period_time == 'month':
        start_date = datetime.now().date() - timedelta(days=30)
    elif period_time == 'year':
        start_date = datetime.now().date() - timedelta(days=365)
    elif period_time == 'all_time':
        first_user_registration = User.query.order_by(User.date_of_registration).first()
        start_date = first_user_registration.date_of_registration if first_user_registration else datetime.now().date()
    graph_data = []
    while start_date <= datetime.now().date():
        premium_users_count = Premium.query.filter(Premium.start_date <= start_date, Premium.end_date >= start_date).count()
        non_premium_users_count = total_users - premium_users_count
        graph_data.append({
            'date': start_date.strftime('%Y-%m-%d'),
            'users_with_premium': premium_users_count,
            'users_without_premium': non_premium_users_count
        })
        start_date += timedelta(days=1)
    return {
        'total_users': total_users,
        'premium_users': premium_users,
        'graph_data': graph_data
    }
