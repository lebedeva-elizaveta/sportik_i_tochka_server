from flask import request, Blueprint, jsonify
from marshmallow import ValidationError

from app.config import FOLDER_AVATARS
from app.decorators import check_authorization
from app.exceptions.exceptions import NotFoundException
from app.models.admin.controller import AdminController
from app.models.base_controller import BaseController
from app.models.common_schemas import EntityDataSchema, LoginResponseSchema, LoginRequestSchema
from app.models.user.controller import UserController
from app.models.user.schemas import UserDataForRatingSchema
from app.services.authorization_service import AuthorizationService
from app.services.image_service import save_image

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
    file = request.files['image']
    user_data = {
        "name": request.form.get('name'),
        "birthday": request.form.get('birthday'),
        "phone": request.form.get('phone'),
        "weight": int(request.form.get('weight')),
        "avatar": save_image(file, FOLDER_AVATARS)
    }
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


@api_bp.route('/password', methods=['PUT'])
def change_password():
    """
    Восстановить пароль
    """
    email = request.headers.get("email")
    user = UserController.get_by_email(email)
    if not user:
        admin = AdminController.get_by_email(email)
        if not admin:
            raise NotFoundException("User not found")
    data = request.json
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if user:
        response, status = UserController.change_password(email, new_password, confirm_password)
    else:
        response, status = AdminController.change_password(email, new_password, confirm_password)
    return jsonify(response), status
