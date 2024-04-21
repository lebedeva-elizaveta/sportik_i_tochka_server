from flask import Blueprint, request, jsonify
from app.models.activity.controller import ActivityController
from app.models.activity.schemas import ActivityListSchema
from app.models.user.controller import UserController

api_activity_bp = Blueprint('activity', __name__)


@api_activity_bp.route('/add_activity', methods=['POST'])
def add_activity():
    """
    Добавить активность
    """
    try:
        access_token = request.headers.get('Authorization')
        user_id = UserController.get_id_from_access_token(access_token)
        if not user_id:
            return jsonify({"success": False}), 401
        user = UserController.get_by_id(user_id)
        if not user:
            return jsonify({"success": False}), 404
        activity_data = request.json
        activity_data['user_id'] = user_id
        new_activity = ActivityController.create(activity_data)
        return jsonify({
            "success": True,
            "activity_id": new_activity.id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500


@api_activity_bp.route('/get_activities', methods=['GET'])
def get_activities():
    """
    Получить список активностей
    """
    try:
        access_token = request.headers.get('Authorization')
        user_id = UserController.get_id_from_access_token(access_token)
        if not user_id:
            return jsonify({"success": False}), 401
        user = UserController.get_by_id(user_id)
        if not user:
            return jsonify({"success": False}), 404
        try:
            user_activities = ActivityController.get_by_user_id(user.id)
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to retrieve activities: {e}"}), 500
        if not user_activities:
            return jsonify({"success": True, "message": "No activities yet"}), 200
        try:
            activity_list_schema = ActivityListSchema()
            serialized_activities = activity_list_schema.dump({"activities": user_activities})
        except Exception as e:
            return jsonify({"success": False, "error": f"Serialization error: {e}"}), 500
        return jsonify({"success": True, "activities": serialized_activities['activities']}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500
