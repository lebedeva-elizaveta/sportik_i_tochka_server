from app.exceptions.exceptions import InvalidPasswordException, InvalidRoleException, NotFoundException
from app.models.admin.controller import AdminController
from app.models.user.controller import UserController


class AuthorizationService:

    @staticmethod
    def login(data):
        email = data.get("email")
        password = data.get("password")
        admin = AdminController.get_by_email(email)
        if admin:
            return AuthorizationService.handle_admin_login(admin, password)
        else:
            user = UserController.get_by_email(email)
            if not user:
                raise NotFoundException("User does not exist")
            elif user.is_blocked:
                raise InvalidRoleException("User is blocked")
            return AuthorizationService.handle_user_login(user, password)

    @staticmethod
    def handle_admin_login(admin, password):
        if not AdminController.check_password(admin.password_hash, password):
            raise InvalidPasswordException("Incorrect password")
        result = {
            "success": True,
            "access_token": AdminController(entity_id=admin.id).generate_access_token(),
            "user_id": admin.id,
            "role": "admin",
        }
        return result

    @staticmethod
    def handle_user_login(user, password):
        if user.is_blocked:
            raise InvalidRoleException("User is blocked")
        if not UserController.check_password(user.password_hash, password):
            raise InvalidPasswordException("Incorrect password")
        role = UserController.get_user_status(user.id)
        result = {
            "success": True,
            "access_token": UserController(entity_id=user.id).generate_access_token(),
            "user_id": user.id,
            "role": role,
        }
        return result
