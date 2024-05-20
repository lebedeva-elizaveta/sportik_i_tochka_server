from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.config import FOLDER_ACTIVITIES
from app.models.activity.controller import ActivityController
from app.models.activity.schemas import ActivitySchema
from app.decorators import check_authorization, check_role_user
from app.services.achievement_service import AchievementService
from app.services.image_service import save_image

api_activity_bp = Blueprint('activity', __name__)


@api_activity_bp.route('/activities', methods=['POST'])
@check_authorization
@check_role_user
def add_activity(user_id, **kwargs):
    """
    Добавить активность
    """
    file = request.files['image']
    activity_data = {"activity_type": request.form.get("activity_type"),
                     "date": request.form.get("date"),
                     "avg_speed": float(request.form.get("avg_speed")),
                     "distance_in_meters": int(request.form.get("distance_in_meters")),
                     "duration": int(request.form.get("duration")),
                     "calories_burned": int(request.form.get("calories_burned")),
                     "image": save_image(file, FOLDER_ACTIVITIES),
                     "user_id": user_id}
    response, status = ActivityController.add_activity(activity_data)
    AchievementService.get_achievement(user_id)
    return jsonify(response), status


@api_activity_bp.route('/activities', methods=['GET'])
@check_authorization
@check_role_user
def get_activities(user_id, **kwargs):
    """
    Получить список активностей
    """
    response, status = ActivityController.get_activities(user_id)
    if "message" in response:
        return jsonify(response), status
    else:
        try:
            serialized_response = ActivitySchema(many=True).dump(response)
        except ValidationError:
            raise
    return jsonify(serialized_response), status
