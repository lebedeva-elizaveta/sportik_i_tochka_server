import io
from datetime import datetime, timedelta
from PIL import Image
import os
import base64
from models import Activity, Achievement, db


def user_statistics_count(id, period_time):
    if period_time == 'week':
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period_time == 'month':
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif period_time == 'year':
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    elif period_time == 'all_time':
        latest_activity = Activity.query.filter(Activity.user_id == id).order_by(Activity.timestamp.desc()).first()
        if latest_activity:
            start_date = latest_activity.date
        else:
            return None
    else:
        return None

    activities = Activity.query.filter(Activity.user_id == id, Activity.date >= start_date).all()

    total_distance = sum(activity.distance for activity in activities)
    total_time = sum(activity.duration for activity in activities)
    total_calories = sum(activity.calories for activity in activities)

    return {
        'total_distance_in_meters': total_distance,
        'total_time': total_time,
        'total_calories': total_calories
    }


def get_achievement(id):
    activities = Activity.query.filter_by(user_id=id).all()
    achievements = Achievement.query.filter_by(user_id=id).all()
    total_distance = sum(activity.distance for activity in activities) / 1000
    if total_distance >= 50:
        if not has_achievement(achievements, "50km_distance"):
            image_path = os.path.join('achievements', 'achievement_50.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(id, "50km_distance", image_base64, 50)
    if total_distance >= 100:
        if not has_achievement(achievements, "100km_distance"):
            image_path = os.path.join('achievements', 'achievement_100.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(id, "100km_distance", image_base64, 100)
    if total_distance >= 250:
        if not has_achievement(achievements, "250km_distance"):
            image_path = os.path.join('achievements', 'achievement_250.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(id, "250km_distance", image_base64, 250)
    if total_distance >= 500:
        if not has_achievement(achievements, "500km_distance"):
            image_path = os.path.join('achievements', 'achievement_500.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(id, "500km_distance", image_base64, 500)
    if total_distance >= 1000:
        if not has_achievement(achievements, "1000km_distance"):
            image_path = os.path.join('achievements', 'achievement_1000.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(id, "1000km_distance", image_base64, 1000)


def has_achievement(achievements_list, achievement_name):
    for achievement in achievements_list:
        if achievement.name == achievement_name:
            return True
    return False


def create_achievement(user_id, name, image, distance):
    new_achievement = Achievement(
        user_id=user_id,
        name=name,
        image=image,
        distance=distance
    )
    db.session.add(new_achievement)
    db.session.commit()


def image_to_base64(image_path):
    with Image.open(image_path) as img:
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format=img.format)
        base64_data = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')
    return base64_data
