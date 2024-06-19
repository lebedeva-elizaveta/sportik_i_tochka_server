from functools import wraps
from flask import request

from app.exceptions.exceptions import InvalidTokenException, NotFoundException, InvalidRoleException, \
    AlreadyExistsException
from app.models.admin.controller import AdminController
from app.models.base_controller import BaseController
from app.models.user.controller import UserController


def check_authorization(func):
    """Проверяет переданный в заголовке токен"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        entity_id = BaseController.get_id_from_access_token(access_token)
        if not entity_id:
            raise InvalidTokenException("Invalid token")
        role = BaseController.get_role_from_access_token(access_token)
        if role == "user":
            user = UserController.get_by_id(entity_id)
            if not user:
                raise NotFoundException("User not found")
            kwargs['user_id'] = entity_id
        elif role == "admin":
            admin = AdminController.get_by_id(entity_id)
            if not admin:
                raise NotFoundException("Admin not found")
            kwargs['admin_id'] = entity_id
        kwargs['access_token'] = access_token
        return func(*args, **kwargs)
    return wrapper


def check_role_user(func):
    """Проверяет, что пользователь не явл. администратором"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if not user_id:
            raise InvalidRoleException("Invalid role (must be user)")
        return func(*args, **kwargs)
    return wrapper


def check_role_admin(func):
    """Проверяет, что пользователь явл. администратором"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        admin_id = kwargs.get("admin_id", None)
        if not admin_id:
            raise InvalidRoleException("Invalid role (must be admin)")
        return func(*args, **kwargs)
    return wrapper


def check_unique_email(func):
    """Проверяет, что email не занят"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        email = request.headers.get('email')
        if not email:
            raise ValueError("Email is required")
        if AdminController.check_email(email) or UserController.check_email(email):
            raise AlreadyExistsException("Email is already taken")
        return func(*args, **kwargs)
    return wrapper
