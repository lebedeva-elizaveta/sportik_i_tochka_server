from flask import request, Blueprint, jsonify, session
from marshmallow import ValidationError

from app.config import AppConfig
from app.decorators import check_authorization
from app.exceptions.exceptions import NotFoundException, InvalidRoleException
from app.models.admin.controller import AdminController
from app.models.base_controller import BaseController
from app.models.common_schemas import EntityGetSchema, LoginResponseSchema, LoginRequestSchema, EntityUpdateSchema
from app.models.user.controller import UserController
from app.models.user.schemas import UserDataForRatingSchema
from app.services.authorization_service import AuthorizationService
from app.services.image_service import ImageService
from app.services.mail_service import send_email

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
        serialized_response = EntityGetSchema().dump(response)
    except ValidationError:
        raise
    return jsonify(serialized_response), status


@api_bp.route('/data', methods=['PUT'])
@check_authorization
def change_current_data(access_token, **kwargs):
    """
    Меняем данные пользователя
    """
    file = request.files.get('image')
    schema = EntityUpdateSchema()
    try:
        user_data = schema.load(request.form.to_dict())
    except ValidationError:
        raise
    if file:
        try:
            avatar_path = ImageService.save_image(file, AppConfig.FOLDER_AVATARS)
            user_data['avatar'] = avatar_path
        except ValueError:
            raise
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


@api_bp.route('/password', methods=['POST'])
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
        session['admin_email'] = email
    session['user_email'] = email
    confirmation_code = send_email(email)
    session['confirmation_code'] = confirmation_code
    return jsonify({
        "message": "Code sent to email"
    }), 200


@api_bp.route('/password/confirm', methods=['POST'])
def confirm_code():
    new_code = request.json
    stored_code = session.get('confirmation_code')
    if new_code == stored_code:
        session.pop('confirmation_code', None)
        return jsonify({
            "success": True
        }), 200
    else:
        session.pop('confirmation_code', None)
        raise InvalidRoleException("Отказано в доступе")


@api_bp.route('/password/change', methods=['PUT'])
def get_new_password():
    user_email = session.get('user_email')
    admin_email = session.get('admin_email')
    data = request.json
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")
    if user_email is not None:
        response, status = UserController.change_password(user_email, new_password, confirm_password)
    else:
        response, status = AdminController.change_password(admin_email, new_password, confirm_password)
    session.pop('user', None)
    session.pop('admin', None)
    return jsonify(response), status
