from marshmallow import ValidationError
from werkzeug.exceptions import NotFound
from app.database import db
from app.models.card.schemas import CardData
from app.models.card.model import Card
from app.services.security_service import EncryptionService


class CardController:
    model = Card

    def __init__(self, card_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == card_id).first()
        if not self.db_entity:
            raise NotFound("Card not found")

    @classmethod
    def create(cls, data):
        new_card = cls.model(**data)
        db.session.add(new_card)
        db.session.commit()
        return new_card

    @staticmethod
    def validate_card_data(card_data):
        try:
            validated_data = CardData().load(card_data)
            return validated_data
        except ValidationError as ve:
            raise ve

    @staticmethod
    def card_exists(card_number):
        card = db.session.query(Card).filter_by(card_number=card_number).first()
        return card is not None

    @staticmethod
    def is_card_available(card_data):
        try:
            validated_data = CardController.validate_card_data(card_data)
        except ValidationError:
            return False
        if CardController.card_exists(validated_data["card_number"]):
            return True
        CardController.create(EncryptionService.encrypt_card_data(validated_data))
        return True
