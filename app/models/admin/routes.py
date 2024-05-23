from flask import request, jsonify, Blueprint
from marshmallow import ValidationError

from app.config import AppConfig
from app.decorators import check_authorization, check_role_admin, check_unique_email
from app.models.admin.controller import AdminController
from app.models.admin.schemas import AdminActionModifySchema, AdminGrantPremiumSchema, AdminProfileSchema
from app.models.user.schemas import PremiumStatisticsSchema
from app.services.image_service import ImageService

api_admin_bp = Blueprint('admin', __name__)


@api_admin_bp.route('/admin/register', methods=['POST'])
@check_unique_email
def register_admin():
    """
    Зарегистрироваться от лица админа
    """
    file = request.files['avatar']
    register_data = {
        "email": request.headers.get('email'),
        "password_hash": request.form.get('password_hash'),
        "name": request.form.get('name'),
        "birthday": request.form.get('birthday'),
        "phone": request.form.get('phone'),
        "avatar": ImageService.save_image(file, AppConfig.FOLDER_AVATARS) if file else None
    }
    response, status = AdminController.register_new_admin(register_data)
    return jsonify(response), status


@api_admin_bp.route("/admin/action", methods=["PUT"])
@check_authorization
@check_role_admin
def admin_actions_put(admin_id, **kwargs):
    """
    Заблокировать/разблокировать, забрать премиум-подписку
    """
    data = AdminActionModifySchema().load(request.json)
    result, status = AdminController.modify_admin_action_endpoint(admin_id, data)
    return jsonify(result), status


@api_admin_bp.route('/admin/action', methods=['POST'])
@check_authorization
@check_role_admin
def admin_actions_post(admin_id, **kwargs):
    """
    Выдать премиум-подписку
    """
    data = AdminGrantPremiumSchema().load(request.json)
    result, status = AdminController.grant_premium_endpoint(admin_id, data['user_id'])
    return jsonify(result), status


@api_admin_bp.route('/admin/profile', methods=['GET'])
@check_authorization
@check_role_admin
def get_admin_profile(admin_id, **kwargs):
    """
    Профиль администратора
    """
    response, status = AdminController.get_profile_data(admin_id)
    try:
        serialized_response = AdminProfileSchema().dump(response)
    except ValidationError:
        raise
    return jsonify(serialized_response), status


@api_admin_bp.route('/admin/statistics', methods=['GET'])
@check_authorization
@check_role_admin
def admin_route_statistics(**kwargs):
    """
    Получить статистику админа
    """
    period = request.args.get('period')
    response, status = AdminController.get_admin_statistics(period)
    serialized_response = PremiumStatisticsSchema().dump(response)
    return jsonify(serialized_response), status
