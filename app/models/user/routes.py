from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.decorators import check_authorization, check_role_user, check_unique_email
from app.models.achievement.schemas import AchievementListSchema
from app.models.user.controller import UserController
from app.models.user.schemas import UserProfileSchema, UserStatisticsSchema, PremiumStatisticsSchema

api_user_bp = Blueprint('user', __name__)


@api_user_bp.route('/user/register', methods=['POST'])
@check_unique_email
def register_user():
    """
    Регистрация от лица обычного пользователя
    """
    email = request.headers.get('email')
    register_data = request.json
    register_data['email'] = email
    response, status = UserController.register_new_user(register_data)
    return jsonify(response), status


@api_user_bp.route('/user/profile', methods=['GET'])
@check_authorization
@check_role_user
def get_user_profile(user_id, **kwargs):
    """
    Получить профиль пользователя
    """
    period = request.args.get('period')
    response, status = UserController.get_profile_data(user_id, period)
    try:
        response = {
            "name": response["name"],
            "image": response["image"],
            "statistics": UserStatisticsSchema().dump(response["statistics"]),
            "achievements": AchievementListSchema().dump({"achievements": response["achievements"]})["achievements"]
        }
    except ValidationError:
        raise
    try:
        serialized_response = UserProfileSchema().dump(response)
    except ValidationError:
        raise
    return jsonify(serialized_response), status


@api_user_bp.route('/user/premium/statistics', methods=['GET'])
@check_authorization
@check_role_user
def premium_statistics(user_id, **kwargs):
    """
    Получить премиум-статистику
    """
    period = request.args.get('period')
    response, status = UserController.get_premium_statistics(user_id, period)
    try:
        serialized_response = PremiumStatisticsSchema().dump(response)
    except ValidationError:
        raise
    return jsonify(serialized_response), status
