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

