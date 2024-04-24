from datetime import datetime

from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound

from app.models.card.controller import CardController
from app.models.premium.model import Premium
from app.database import db


class PremiumController:
    model = Premium

    def __init__(self, premium_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == premium_id).first()
        if not self.db_entity:
            raise NotFound("Premium not found")

    @classmethod
    def create(cls, user_id):
        premium = cls.model(user_id=user_id)
        db.session.add(premium)
        db.session.commit()
        return premium

    @staticmethod
    def buy_premium(user_id, card_data):
        try:
            is_premium_available = CardController.is_card_available(card_data)
            if not is_premium_available:
                return {"success": False}, 405
            new_premium = PremiumController.create(user_id)
            return {"success": True, "timestamp": new_premium.start_date}, 201
        except ValidationError as ve:
            return {"success": False, "errors": ve.messages}, 400
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

    @staticmethod
    def cancel_premium(user_id):
        premium = Premium.query.filter(
            Premium.user_id == user_id,
            Premium.start_date <= datetime.utcnow(),
            Premium.end_date >= datetime.utcnow()
        ).order_by(
            Premium.start_date.desc(), Premium.end_date.desc()
        ).first()
        premium.end_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True}), 200
