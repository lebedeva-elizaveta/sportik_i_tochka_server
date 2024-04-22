from flask import request, Blueprint, jsonify
from werkzeug.exceptions import NotFound

from app.models.admin.controller import AdminController
from app.models.user.controller import UserController
from app.services.admin_service import AdminService
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
