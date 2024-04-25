from app.models.admin.controller import AdminController
from app.models.common_schemas import LoginResponseSchema
from app.models.user.controller import UserController


class AuthorizationService:
    @staticmethod
    def handle_admin_login(admin, password):
        if not AdminController.check_password(admin.password_hash, password):
            return {"success": False, "error": "INCORRECT_PASSWORD"}, 401
        result = {
            "success": True,
            "access_token": AdminController(entity_id=admin.id).generate_access_token(),
            "user_id": admin.id,
            "role": "admin",
        }
        schema = LoginResponseSchema()
        return schema.dump(result), 200

    @staticmethod
    def handle_user_login(user, password):
        if user.is_blocked:
            return {"success": False, "error": "USER_BLOCKED"}, 403
        if not UserController.check_password(user.password_hash, password):
            return {"success": False, "error": "INCORRECT_PASSWORD"}, 401
        role = UserController.premium_or_regular(user.id)
        result = {
            "success": True,
            "access_token": UserController(entity_id=user.id).generate_access_token(),
            "user_id": user.id,
            "role": role,
        }

        schema = LoginResponseSchema()
        return schema.dump(result), 200
