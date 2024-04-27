from flask import request, Blueprint, jsonify
from marshmallow import ValidationError

from app.decorators import check_authorization
from app.models.base_controller import BaseController
from app.models.common_schemas import EntityDataSchema, LoginResponseSchema, LoginRequestSchema
from app.models.user.controller import UserController
from app.models.user.schemas import UserDataForRatingSchema
from app.services.authorization_service import AuthorizationService

api_bp = Blueprint('api', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    """
    Логинимся за любого пользователя
    """
    data = request.json
    try:
        validated_data = LoginRequestSchema().load(data)
    except ValidationError:
        raise
    response = AuthorizationService.login(validated_data)
    try:
        serialized_response = LoginResponseSchema().dump(response)
    except ValidationError:
        raise
    return jsonify(serialized_response), 200


@api_bp.route('/data', methods=["GET"])
@check_authorization
def get_current_data(access_token, **kwargs):
    """
    Получаем текущие данные пользователя
    """
    response, status = BaseController.get_current_entity_data(access_token)
    try:
        serialized_response = EntityDataSchema().dump(response)
    except ValidationError:
        raise
    return jsonify(serialized_response), status


@api_bp.route('/data', methods=['PUT'])
@check_authorization
def change_current_data(access_token, **kwargs):
    """
    Меняем данные пользователя
    """
    user_data = request.json
    response, status = BaseController.change_entity_data(access_token, user_data)
    return jsonify(response), status


@api_bp.route('/rating', methods=['GET'])
@check_authorization
def get_rating(**kwargs):
    """
    Получить рейтинг пользователей
    """
    response, status = UserController.get_rating()
    try:
        serialized_response = {
            "users": UserDataForRatingSchema(many=True).dump(response["users"])
        }
    except ValidationError:
        raise
    return jsonify(serialized_response), status
