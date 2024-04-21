from datetime import datetime

from app.models.base_controller import BaseUser
from app.models.user.model import User
from app.models.user.schemas import UserCreate
from app.models.premium.model import Premium


class UserController(BaseUser):
    model = User
    schema = UserCreate

    @classmethod
    def is_premium(cls, user_id):
        if not isinstance(user_id, int):
            raise ValueError("user_id must be an integer")

        current_datetime = datetime.utcnow()

        active_premium = Premium.query.filter_by(user_id=user_id).filter(
            Premium.end_date > current_datetime
        ).first()

        return active_premium is not None
