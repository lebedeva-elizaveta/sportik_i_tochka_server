import os

from app.config import AppConfig
from app.models.achievement.controller import AchievementController
from app.models.activity.controller import ActivityController
from app.services.image_service import ImageService


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

        for name, threshold in AchievementService.ACHIEVEMENT_THRESHOLDS.items():
            if total_distance >= threshold and not AchievementService.has_achievement(achievements, name):
                achievement_image_path = os.path.join(AppConfig.FOLDER_ACHIEVEMENTS, f'achievement_{threshold}.jpg')

                data = {
                    "name": name,
                    "image": ImageService.get_static_file_url(achievement_image_path, 'achievements'),
                    "distance": threshold,
                    "user_id": user_id
                }
                AchievementController.create(data)

    @staticmethod
    def has_achievement(achievements_list, achievement_name):
        return any(achievement.name == achievement_name for achievement in achievements_list)
