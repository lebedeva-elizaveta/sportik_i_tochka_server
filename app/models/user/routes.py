from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.user.controller import UserController
from app.services.security_service import EncryptionService

api_user_bp = Blueprint('user', __name__)


@api_user_bp.route('/register_user', methods=['POST'])
def register_user():
    """
    Регистрация от лица обычного пользователя
    """
    email = request.headers.get('email')
    register_data = request.json
    try:
        UserController.check_email(email)
    except Exception as e:
        return jsonify({"success": False, "error": {e}}), 409
    try:
        register_data['password_hash'] = EncryptionService.generate_password_hash(register_data['password_hash'])
        register_data['email'] = email
        new_user = UserController.create(data=register_data)
    except ValidationError as err:
        return jsonify({"success": False, "message": f"Validation error: {err.messages}"}), 400
    if new_user:
        user_instance = UserController(entity_id=new_user.id)
        access_token = user_instance.generate_access_token()
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user_id": new_user.id
        }), 201
    else:
        return jsonify({"success": False, "message": "Failed to create user"}), 500


@api_user_bp.route('/get_user_profile', methods=['GET'])
def get_user_profile():
    """
    Профиль пользователя
    """
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"success": False, "error": "Authorization header missing"}), 401
        period = request.args.get('period')
        return UserController.get_profile_data(access_token, period)
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500


@api_user_bp.route('/get_rating', methods=['GET'])
def get_rating():
    """
    Получить рейтинг пользователей
    """
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"success": False, "error": "Authorization header missing"}), 401
        return jsonify({"users": UserController.get_rating()}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500

