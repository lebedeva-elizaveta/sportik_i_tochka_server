import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from flask import jsonify
from werkzeug.exceptions import NotFound
from app.config import settings, ALGORITHM
import jwt
from app.database import db
from app.models.common_schemas import UserDataSchema
from app.services.common_service import CommonService


class BaseUser:
    model = None

    def __init__(self, entity_id):
        self.db_entity = db.session.query(self.model).filter(self.model.id == entity_id).first()
        if not self.db_entity:
            raise NotFound()

    @classmethod
    def create(cls, data):
        validated_data = cls.schema().load(data)
        user = cls.model(**validated_data)
        db.session.add(user)
        db.session.commit()
        return user

    def get_role(self):
        return None

    @classmethod
    def get_by_email(cls, email: str):
        user = db.session.query(cls.model).filter(cls.model.email == email).first()
        if not user:
            raise NotFound()
        return user

    @classmethod
    def get_by_id(cls, id: int):
        user = db.session.query(cls.model).filter(cls.model.id == id).first()
        if not user:
            raise NotFound()
        return user

    @classmethod
    def check_email(cls, email: str):
        user = db.session.query(cls.model).filter(cls.model.email == email).first()
        if user:
            raise jsonify({"error": "Already existis"})

    def generate_access_token(self):
        role = self.get_role()
        access_token = jwt.encode(payload={'sub': self.db_entity.id, 'role': role},
                                  key=settings.secret_key,
                                  algorithm=ALGORITHM)
        return access_token

    @classmethod
    def check_password(cls, hashed_password, password):
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = base64.urlsafe_b64decode(hashed_password.encode('utf-8') + b'=')
        algorithm = hashes.SHA256()
        digest = hashes.Hash(algorithm, backend=default_backend())
        digest.update(password_bytes)
        hashed_input_password = digest.finalize()
        return hashed_password_bytes == hashed_input_password

    @classmethod
    def get_id_from_access_token(cls, access_token):
        if access_token is None:
            return None
        if 'Bearer' not in access_token:
            return None
        clear_token = access_token.replace('Bearer ', '')
        try:
            payload = jwt.decode(jwt=clear_token, key=settings.secret_key, algorithms=[ALGORITHM])
            if 'sub' not in payload or payload['sub'] is None:
                return None
            return payload['sub']
        except jwt.exceptions.InvalidTokenError as e:
            print("JWT Decode Error:", e)
            return None

    @classmethod
    def get_role_from_access_token(cls, access_token):
        if access_token is None:
            return None
        if 'Bearer' not in access_token:
            return None
        clear_token = access_token.replace('Bearer ', '')
        try:
            payload = jwt.decode(jwt=clear_token, key=settings.secret_key, algorithms=[ALGORITHM])
            if 'role' not in payload or payload['role'] is None:
                return None
            return payload['role']
        except jwt.exceptions.InvalidTokenError as e:
            print("JWT Decode Error:", e)
            return None

    @classmethod
    def get_current_user_data(cls, access_token):
        user_id = cls.get_id_from_access_token(access_token)
        user_role = cls.get_role_from_access_token(access_token)
        user_data = CommonService.get_current_data(user_id, user_role)
        return UserDataSchema().dump(user_data)
