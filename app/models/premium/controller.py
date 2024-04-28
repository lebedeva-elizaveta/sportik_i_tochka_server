from datetime import datetime

import pytz

from app.exceptions.exceptions import NotFoundException, InvalidActionException, ActionIsNotAvailableException
from app.models.card.controller import CardController
from app.models.premium.model import Premium
from app.database import db

moscow_tz = pytz.timezone('Europe/Moscow')


class PremiumController:
    model = Premium

    def __init__(self, premium_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == premium_id).first()
        if not self.db_entity:
            raise NotFoundException("Premium not found")

    @classmethod
    def create(cls, user_id):
        premium = cls.model(user_id=user_id)
        db.session.add(premium)
        db.session.commit()
        return premium

    @classmethod
    def get_active_premium(cls, user_id):
        premium = cls.model.query.filter(
            cls.model.user_id == user_id,
            cls.model.start_date <= datetime.utcnow().astimezone(moscow_tz),
            cls.model.end_date >= datetime.utcnow().astimezone(moscow_tz),
        ).first()
        return premium

    @staticmethod
    def is_active(user_id):
        premium = PremiumController.get_active_premium(user_id)
        return premium is not None

    @staticmethod
    def buy_premium(user_id, card_data):
        if PremiumController.is_active(user_id):
            raise ActionIsNotAvailableException("User is already premium")
        is_premium_available = CardController.is_card_available(user_id, card_data)
        if not is_premium_available:
            raise InvalidActionException("Invalid action")
        new_premium = PremiumController.create(user_id)
        result = {
            "success": True,
            "timestamp": new_premium.start_date
        }
        return result, 201

    @staticmethod
    def cancel_premium(user_id):
        if not PremiumController.is_active(user_id):
            raise ActionIsNotAvailableException("User is not premium")
        premium = PremiumController.get_active_premium(user_id)
        premium.end_date = datetime.utcnow().astimezone(moscow_tz)
        db.session.commit()
        result = {
            "success": True
        }
        return result, 200
