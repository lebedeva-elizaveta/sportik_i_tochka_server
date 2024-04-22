from app.models.admin.model import Admin
from app.models.admin.schemas import AdminCreate
from app.models.base_controller import BaseUser
from app.services.admin_service import AdminService


class AdminController(BaseUser):
    model = Admin
    schema = AdminCreate

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
