import os
import base64
from models import Activity, Achievement, db


def get_achievement(user_id):
    activities = Activity.query.filter_by(user_id=user_id).all()
    achievements = Achievement.query.filter_by(user_id=user_id).all()
    total_distance = sum(activity.distance for activity in activities) / 1000
    if total_distance >= 50:
        if not has_achievement(achievements, "50km_distance"):
            image_path = os.path.join('achievements', 'achievement_50.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(user_id, "50km_distance", image_base64, 50)
    if total_distance >= 100:
        if not has_achievement(achievements, "100km_distance"):
            image_path = os.path.join('achievements', 'achievement_100.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(user_id, "100km_distance", image_base64, 100)
    if total_distance >= 250:
        if not has_achievement(achievements, "250km_distance"):
            image_path = os.path.join('achievements', 'achievement_250.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(user_id, "250km_distance", image_base64, 250)
    if total_distance >= 500:
        if not has_achievement(achievements, "500km_distance"):
            image_path = os.path.join('achievements', 'achievement_500.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(user_id, "500km_distance", image_base64, 500)
    if total_distance >= 1000:
        if not has_achievement(achievements, "1000km_distance"):
            image_path = os.path.join('achievements', 'achievement_1000.jpg')
            image_base64 = image_to_base64(image_path)
            create_achievement(user_id, "1000km_distance", image_base64, 1000)


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
    with open(image_path, 'rb') as image_file:
        base64_data = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_data
