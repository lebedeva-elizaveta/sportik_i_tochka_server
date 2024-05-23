import base64
import jwt

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from marshmallow import ValidationError

from app.config import AppConfig, settings
from app.database import db
from app.exceptions.exceptions import NotFoundException, InvalidTokenException, UnprocessableEntityException
from app.services.common_service import CommonService
from app.services.security_service import EncryptionService


class BaseController:
    model = None
    schema = None

    def __init__(self, entity_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == entity_id).first()
        if not self.db_entity:
            raise NotFoundException("Пользователь или админ не найден")

    def get_role(self):
        return None

    @classmethod
    def create(cls, data):
        try:
            validated_data = cls.schema().load(data)
        except ValidationError:
            raise
        entity = cls.model(**validated_data)
        db.session.add(entity)
        db.session.commit()
        return entity

    @classmethod
    def get_by_email(cls, email):
        entity = db.session.query(cls.model).filter(cls.model.email == email).first()
        return entity

    @classmethod
    def get_by_id(cls, entity_id):
        entity = db.session.query(cls.model).filter(cls.model.id == entity_id).first()
        return entity

    @classmethod
    def check_email(cls, email):
        entity = db.session.query(cls.model).filter(cls.model.email == email).first()
        if entity:
            return True
        else:
            return False

    @classmethod
    def get_current_entity_data(cls, access_token):
        entity_id = cls.get_id_from_access_token(access_token)
        entity_role = cls.get_role_from_access_token(access_token)
        entity_data = CommonService.get_current_data(entity_id, entity_role)
        return entity_data, 200

    @classmethod
    def change_entity_data(cls, access_token, personal_data):
        entity_id = cls.get_id_from_access_token(access_token)
        entity_role = cls.get_role_from_access_token(access_token)
        entity_data = CommonService.change_user_data(entity_id, entity_role, personal_data)
        return entity_data, 200

    def generate_access_token(self):
        role = self.get_role()
        access_token = jwt.encode(payload={'sub': self.db_entity.id, 'role': role},
                                  key=settings.secret_key,
                                  algorithm=AppConfig.ALGORITHM)
        return access_token

    @staticmethod
    def check_password(hashed_password, password):
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = base64.urlsafe_b64decode(hashed_password.encode('utf-8') + b'=')
        algorithm = hashes.SHA256()
        digest = hashes.Hash(algorithm, backend=default_backend())
        digest.update(password_bytes)
        hashed_input_password = digest.finalize()
        return hashed_password_bytes == hashed_input_password

    @staticmethod
    def is_access_token_valid(access_token):
        if access_token is None:
            raise InvalidTokenException("No token provided")
        if 'Bearer' not in access_token:
            raise InvalidTokenException("Token must be a Bearer token")

        token = access_token.replace('Bearer ', '').strip()

        try:
            jwt.decode(token, key=settings.secret_key, algorithms=AppConfig.ALGORITHM)
        except jwt.DecodeError:
            raise InvalidTokenException("Invalid token format")
        except jwt.InvalidTokenError:
            raise InvalidTokenException("Invalid token")
        return True

    @staticmethod
    def get_payload_from_access_token(access_token):
        if BaseController.is_access_token_valid(access_token):
            clear_token = access_token.replace('Bearer ', '')

            payload = jwt.decode(jwt=clear_token, key=settings.secret_key, algorithms=[AppConfig.ALGORITHM])

            return payload

    @staticmethod
    def get_id_from_access_token(access_token):
        payload = BaseController.get_payload_from_access_token(access_token)
        if 'sub' not in payload or payload['sub'] is None:
            raise InvalidTokenException("Invalid token")
        return payload['sub']

    @staticmethod
    def get_role_from_access_token(access_token):
        payload = BaseController.get_payload_from_access_token(access_token)
        if 'role' not in payload or payload['role'] is None:
            raise InvalidTokenException("Invalid token")
        return payload['role']

    @staticmethod
    def change_password(entity, new_password, confirm_password):
        if new_password != confirm_password:
            raise UnprocessableEntityException("Passwords do not match")
        hashed_password = EncryptionService.generate_password_hash(new_password)
        entity.password_hash = hashed_password
        db.session.commit()
        return {"success": True}, 200
