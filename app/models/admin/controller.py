from app.models.admin.model import Admin
from app.models.admin.schemas import AdminCreate
from app.models.base_controller import BaseController
from app.services.admin_service import AdminService
from app.services.security_service import EncryptionService
from app.services.statistics_service import StatisticsService


class AdminController(BaseController):
    model = Admin
    schema = AdminCreate

    def get_role(self):
        return "admin"

    @staticmethod
    def register_new_admin(data):
        password = data.get('password_hash')
        data['password_hash'] = EncryptionService.generate_password_hash(password)

        new_admin = AdminController.create(data=data)
        admin = AdminController(entity_id=new_admin.id)

        response = {
            "success": True,
            "access_token": admin.generate_access_token(),
            "user_id": new_admin.id
        }

        return response, 201

    @staticmethod
    def modify_admin_action_endpoint(admin_id, data):
        admin = AdminService()
        response = admin.modify_admin_action(admin_id, data)
        return response, 200

    @staticmethod
    def grant_premium_endpoint(admin_id, user_id):
        admin = AdminService()
        response = admin.grant_premium_admin_action(admin_id, user_id)
        return response, 200

    @classmethod
    def get_profile_data(cls, admin_id):
        admin = cls.get_by_id(admin_id)
        response = {
            "name": admin.name,
            "image": admin.avatar,
        }
        return response, 200

    @classmethod
    def get_admin_statistics(cls, period):
        response = StatisticsService.admin_statistics_count(period)
        return response, 200
