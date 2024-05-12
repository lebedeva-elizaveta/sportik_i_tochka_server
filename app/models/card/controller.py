from marshmallow import ValidationError

from app.database import db
from app.exceptions.exceptions import NotFoundException
from app.models.additional_models import User_Card
from app.models.card.schemas import EncryptedCardSchema
from app.models.card.model import Card
from app.models.user.model import User
from app.services.security_service import EncryptionService


class CardController:
    model = Card

    def __init__(self, card_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == card_id).first()
        if not self.db_entity:
            raise NotFoundException("Card not found")

    @classmethod
    def create(cls, data):
        new_card = cls.model(**data)
        db.session.add(new_card)
        db.session.commit()
        return new_card

    @classmethod
    def get_user_cards(cls, user_id):
        user_cards = cls.model.query.join(User_Card).filter(User_Card.user_id == user_id).all()
        card_numbers = [EncryptionService.decrypt_card_number(card.card_number) for card in user_cards]
        card_ids = [card.id for card in user_cards]
        return card_numbers, card_ids, 200

    @classmethod
    def card_exists(cls, card_number):
        card = cls.model.query.filter_by(card_number=card_number).first()
        if card:
            return card
        return False

    @classmethod
    def user_card_exists(cls, card_number, user_id):
        card = cls.model.query.filter_by(card_number=card_number).first()
        user_card = User_Card.query.filter_by(user_id=user_id, card_id=card.id).first()
        if user_card:
            return True
        return False

    @staticmethod
    def is_card_available(user_id, card_data):
        encrypted_data = EncryptionService.encrypt_card_data(card_data)
        card_number = encrypted_data.get("card_number")
        card_id = CardController.card_exists(card_number)
        if card_id:
            if CardController.user_card_exists(card_number, user_id):
                return True
            CardController._add_user_card_data(user_id, card_id)
        else:
            try:
                validate_data = EncryptedCardSchema().load(encrypted_data)
            except ValidationError:
                raise
            new_card = CardController.create(validate_data)
            CardController._add_user_card_data(user_id, new_card.id)
            return True
        return False

    @classmethod
    def _add_user_card_data(cls, user_id, card_id):
        user = User.query.get(user_id)
        card = cls.model.query.get(card_id)
        if not user:
            raise NotFoundException("User not found")
        if not card:
            raise NotFoundException("card not found")
        user_card_data = User_Card(user_id=user_id, card_id=card_id)
        db.session.add(user_card_data)
        db.session.commit()
