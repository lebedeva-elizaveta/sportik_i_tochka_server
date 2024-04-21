from flask import request, Blueprint, jsonify
from werkzeug.exceptions import NotFound

from app.models.admin.controller import AdminController
from app.models.user.controller import UserController

api_bp = Blueprint('api', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    login_data = request.json
    email = login_data.get('email')
    password = login_data.get('password')

    try:
        admin = AdminController.get_by_email(email)
        return AuthHandler.handle_admin_login(admin, password)
    except NotFound:
        pass

    try:
        user = UserController.get_by_email(email)
        return AuthHandler.handle_user_login(user, password)
    except NotFound:
        pass

    return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404


def handle_user_login(user, password):
    print("User object:", user.__dict__)
    if user.is_blocked:
        return jsonify({"success": False, "error": "USER_BLOCKED"}), 403
    if not UserController.check_password(user.password_hash, password):
        return jsonify({"success": False, "error": "INCORRECT_PASSWORD"}), 401

    role = "premium" if UserController.is_premium(user.id) else "regular"
    return jsonify({
        "success": True,
        "access_token": UserController(entity_id=user.id).generate_access_token(),
        "user_id": user.id,
        "role": role
    }), 200


def handle_admin_login(admin, password):
    if not AdminController.check_password(admin.password_hash, password):
        return jsonify({"success": False, "error": "INCORRECT_PASSWORD"}), 401

    return jsonify({
        "success": True,
        "access_token": AdminController(entity_id=admin.id).generate_access_token(),
        "admin_id": admin.id,
        "role": "admin"
    }), 200
