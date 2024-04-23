from flask import request, Blueprint, jsonify
from werkzeug.exceptions import NotFound, Unauthorized

from app.models.admin.controller import AdminController
from app.models.base_controller import BaseUser
from app.models.user.controller import UserController
from app.services.authorization_service import AuthorizationService

api_bp = Blueprint('api', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    """
    Логинимся за любого пользователя
    """
    login_data = request.json
    email = login_data.get("email")
    password = login_data.get("password")
    try:
        admin = AdminController.get_by_email(email)
        return AuthorizationService.handle_admin_login(admin, password)
    except NotFound:
        pass
    try:
        user = UserController.get_by_email(email)
        if user.is_blocked:
            return jsonify({"success": False, "error": "USER_IS_BLOCKED"}), 404
        return AuthorizationService.handle_user_login(user, password)
    except NotFound:
        pass
    return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404


@api_bp.route("/get_current_data", methods=["GET"])
def get_current_data():
    """
    Получаем текущие данные пользователя
    """
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"success": False, "error": "Authorization header missing"}), 401
        user_data = BaseUser.get_current_user_data(access_token)
        return jsonify(user_data), 200
    except Unauthorized as ue:
        return jsonify({"success": False, "error": str(ue)}), 401
    except NotFound as nf:
        return jsonify({"success": False, "error": str(nf)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500


@api_bp.route('/change_current_data', methods=['PUT'])
def change_current_data():
    """
    Меняем данные пользователя
    """
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"success": False, "error": "Authorization header missing"}), 401
        user_data = request.json
        return BaseUser.change_user_data(access_token, user_data)
    except Unauthorized as ue:
        return jsonify({"success": False, "error": str(ue)}), 401
    except NotFound as nf:
        return jsonify({"success": False, "error": str(nf)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500