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

    @staticmethod
    def card_exists(card_number):
        card = db.session.query(Card).filter_by(card_number=card_number).first()
        print(card_number)
        if card:
            print("card exist")
            return True
        print("card does not exist")
        return False

    @staticmethod
    def is_card_available(user_id, card_data):
        encrypted_data = EncryptionService.encrypt_card_data(card_data)
        if CardController.card_exists(encrypted_data.get("card_number")):
            return True
        else:
            try:
                validate_data = EncryptedCardSchema().load(encrypted_data)
            except ValidationError:
                raise
            new_card = CardController.create(validate_data)
            CardController._add_user_card_data(user_id, new_card.id)
            return True

    @staticmethod
    def _add_user_card_data(user_id, card_id):
        user = User.query.get(user_id)
        card = Card.query.get(card_id)
        if not user:
            raise NotFoundException("User not found")
        if not card:
            raise NotFoundException("card not found")
        user_card_data = User_Card(user_id=user_id, card_id=card_id)
        db.session.add(user_card_data)
        db.session.commit()
