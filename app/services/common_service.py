from werkzeug.exceptions import Unauthorized, NotFound

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
