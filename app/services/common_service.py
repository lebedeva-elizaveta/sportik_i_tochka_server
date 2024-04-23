from flask import jsonify
from werkzeug.exceptions import Unauthorized, NotFound

from app.database import db
from app.models.admin.model import Admin
from app.models.user.model import User


class CommonService:

    @staticmethod
    def get_current_data(id, role):
        if not id:
            raise Unauthorized("Invalid access token")
        if role == 'user':
            user = User.query.filter_by(id=id).first()
        elif role == 'admin':
            user = Admin.query.filter_by(id=id).first()
        else:
            raise Unauthorized("Unknown role")
        if not user:
            raise NotFound("Entity not found")
        user_data = {
            "id": user.id,
            "name": user.name,
            "image": user.avatar,
            "phone": user.phone,
            "birthday": user.birthday,
        }
        if hasattr(user, "weight"):
            user_data["weight"] = user.weight
        return user_data

    @staticmethod
    def change_user_data(id, role, personal_data):
        if not id:
            raise Unauthorized("Invalid access token")
        if role == 'user':
            user = User.query.filter_by(id=id).first()
        elif role == 'admin':
            user = Admin.query.filter_by(id=id).first()
        else:
            raise Unauthorized("Unknown role")
        if not user:
            raise NotFound("Entity not found")
        user.name = personal_data.get('name', user.name)
        user.avatar = personal_data.get('image', user.avatar)
        user.phone = personal_data.get('phone', user.phone)
        user.birthday = personal_data.get('birthday', user.birthday)
        if hasattr(user, "weight"):
            user.weight = personal_data.get('weight', user.weight)
        db.session.commit()
        return jsonify({"success": True}), 200
