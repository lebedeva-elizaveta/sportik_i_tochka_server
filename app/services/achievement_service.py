import base64
import os

from app.models.achievement.controller import AchievementController
from app.models.activity.controller import ActivityController


class AchievementService:
    ACHIEVEMENT_THRESHOLDS = {
        "50km_distance": 50,
        "100km_distance": 100,
        "250km_distance": 250,
        "500km_distance": 500,
        "1000km_distance": 1000,
    }

    @staticmethod
    def get_achievement(user_id):
        activities = ActivityController.get_by_user_id(user_id)
        achievements = AchievementController.get_by_user_id(user_id)

        total_distance = sum(activity.distance_in_meters for activity in activities) / 1000

        def has_achievement(achievements_list, achievement_name):
            return any(achievement.name == achievement_name for achievement in achievements_list)

        for name, threshold in AchievementService.ACHIEVEMENT_THRESHOLDS.items():
            if total_distance >= threshold and not has_achievement(achievements, name):
                with open(os.path.join('app', 'models', 'achievement', 'achievements',
                                       f'achievement_{threshold}.jpg'), 'rb') as image_file:
                    image_binary = image_file.read()

                image_base64 = base64.b64encode(image_binary).decode('utf-8')

                data = {
                    "name": name,
                    "image": image_base64,
                    "distance": threshold,
                    "user_id": user_id
                }
                AchievementController.create(data)
