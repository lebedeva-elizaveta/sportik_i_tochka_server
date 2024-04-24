from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from app.models.admin.controller import AdminController
from app.models.admin.schemas import AdminActionModifySchema, AdminGrantPremiumSchema
from app.services.security_service import EncryptionService

api_admin_bp = Blueprint('admin', __name__)


@api_admin_bp.route('/register_admin', methods=['POST'])
def register_admin():
    """
    Зарегистрироваться от лица админа
    """
    email = request.headers.get('email')
    register_data = request.json
    try:
        AdminController.check_email(email)
    except Exception as e:
        return jsonify({"success": False, "error": {e}}), 409
    try:
        register_data['password_hash'] = EncryptionService.generate_password_hash(register_data['password_hash'])
        register_data['email'] = email
        new_admin = AdminController.create(data=register_data)
    except ValidationError as err:
        return jsonify({"success": False, "message": f"Validation error: {err.messages}"}), 400
    if new_admin:
        admin_instance = AdminController(entity_id=new_admin.id)
        access_token = admin_instance.generate_access_token()
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user_id": new_admin.id
        }), 201
    else:
        return jsonify({"success": False, "message": "Failed to create admin"}), 500


@api_admin_bp.route("/admin_actions/modify", methods=["PUT"])
def admin_actions_put():
    """
    Заблокировать/разблокировать, забрать премиум-подписку
    """
    access_token = request.headers.get("Authorization")
    if not access_token:
        return jsonify({"success": False}), 401
    admin_id = AdminController.get_id_from_access_token(access_token)
    if not admin_id:
        return jsonify({"success": False}), 404
    try:
        data = AdminActionModifySchema().load(request.json)
        result, status = AdminController.modify_admin_action_endpoint(admin_id, data)
        return jsonify(result), status
    except ValidationError as ve:
        return jsonify({"success": False, "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500


@api_admin_bp.route('/admin_actions/grant_premium', methods=['POST'])
def admin_actions_post():
    """
    Выдать премиум-подписку
    """
    access_token = request.headers.get("Authorization")
    if not access_token:
        return jsonify({"success": False, "message": "Token missing"}), 401
    admin_id = AdminController.get_id_from_access_token(access_token)
    if not admin_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    try:
        data = AdminGrantPremiumSchema().load(request.json)
        result, status = AdminController.grant_premium_endpoint(admin_id, data['user_id'])
        return jsonify(result), status
    except ValidationError as ve:
        return jsonify({"success": False, "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500


@api_admin_bp.route('/get_admin_profile', methods=['GET'])
def get_user_profile():
    """
    Профиль администратора
    """
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"success": False, "error": "Authorization header missing"}), 401
        return AdminController.get_profile_data(access_token)
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500
