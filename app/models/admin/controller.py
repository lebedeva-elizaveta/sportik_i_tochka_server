from flask import jsonify

from app.models.admin.model import Admin
from app.models.admin.schemas import AdminCreate, AdminProfileSchema
from app.models.base_controller import BaseUser
from app.services.admin_service import AdminService
from app.services.statistics_service import StatisticsService


class AdminController(BaseUser):
    model = Admin
    schema = AdminCreate

    def get_role(self):
        return "admin"

    @staticmethod
    def modify_admin_action_endpoint(admin_id, data):
        try:
            admin = AdminService()
            result, status = admin.modify_admin_action(admin_id, data)
            return result, status
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {e}"}, 500

    @staticmethod
    def grant_premium_endpoint(admin_id, user_id):
        try:
            admin = AdminService()
            result, status = admin.grant_premium_admin_action(admin_id, user_id)
            return result, status
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {e}"}, 500

    @classmethod
    def get_profile_data(cls, access_token):
        admin_id = cls.get_id_from_access_token(access_token)
        admin = cls.get_by_id(admin_id)
        response_data = {
            "name": admin.name,
            "image": admin.avatar,
        }
        return jsonify(AdminProfileSchema().dump(response_data)), 200

    @classmethod
    def get_admin_statistics(cls, access_token, period):
        try:
            if BaseUser.get_role_from_access_token(access_token) != "admin":
                # TODO exception
                raise "RoleError"
            return StatisticsService.admin_statistics_count(period)
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {e}"}, 500
