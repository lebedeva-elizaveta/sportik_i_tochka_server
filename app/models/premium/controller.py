from datetime import datetime, timedelta

import pytz

from app.exceptions.exceptions import NotFoundException, ActionIsNotAvailableException
from app.models.card.controller import CardController
from app.models.premium.model import Premium, Premium_Award
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

    @staticmethod
    def create_premium_award(user_id):
        award = Premium_Award(user_id=user_id)
        db.session.add(award)
        db.session.commit()
        return award

    @classmethod
    def get_active_premium(cls, user_id):
        premium = cls.model.query.filter(
            cls.model.user_id == user_id,
            cls.model.start_date <= datetime.utcnow().astimezone(moscow_tz),
            cls.model.end_date >= datetime.utcnow().astimezone(moscow_tz),
        ).first()
        return premium

    @staticmethod
    def get_premium_award(user_id):
        now = datetime.utcnow().astimezone(moscow_tz)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (start_of_month + timedelta(days=32)).replace(day=1)
        end_of_month = next_month - timedelta(microseconds=1)

        award = Premium_Award.query.filter(
            Premium_Award.user_id == user_id,
            Premium_Award.timestamp >= start_of_month,
            Premium_Award.timestamp <= end_of_month,
        ).first()

        return award

    @staticmethod
    def is_active(user_id):
        premium = PremiumController.get_active_premium(user_id)
        return premium is not None

    @staticmethod
    def buy_premium(user_id, card_data):
        if PremiumController.is_active(user_id):
            raise ActionIsNotAvailableException("User is already premium")
        CardController.add_card(user_id, card_data)
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

    @classmethod
    def extend_premium(cls, premium_id, new_end_date):
        premium = cls.model.query.filter_by(id=premium_id).first()
        if not premium:
            raise NotFoundException("Premium not found")
        premium.end_date = new_end_date
        db.session.commit()
        return premium
