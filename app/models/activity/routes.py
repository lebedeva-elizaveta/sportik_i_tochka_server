from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.models.activity.controller import ActivityController
from app.models.activity.schemas import ActivityListSchema
from app.decorators import check_authorization, check_role_user

api_activity_bp = Blueprint('activity', __name__)


@api_activity_bp.route('/activities', methods=['POST'])
@check_authorization
@check_role_user
def add_activity(user_id, **kwargs):
    """
    Добавить активность
    """
    activity_data = request.json
    activity_data['user_id'] = user_id
    response, status = ActivityController.add_activity(activity_data)
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
            serialized_response = {
                "success": response["success"],
                "activities": ActivityListSchema().dump({"activities": response["activities"]}),
            }
        except ValidationError:
            raise
    return jsonify(serialized_response), status
