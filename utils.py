import base64

from flask import jsonify
from jwt import decode
from config import SECRET_KEY
from models import User, Premium, Admin, Admin_User, db, Admin_Premium
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from datetime import datetime


def check_email(email):
    existing_user = User.query.filter_by(email=email).first()
    existing_admin = Admin.query.filter_by(email=email).first()
    if existing_user or existing_admin:
        return False
    else:
        return True


def generate_password_hash(password):
    password_bytes = password.encode('utf-8')
    algorithm = hashes.SHA256()
    digest = hashes.Hash(algorithm, backend=default_backend())
    digest.update(password_bytes)
    hashed_password = digest.finalize()
    hashed_password_b64 = urlsafe_b64encode(hashed_password).rstrip(b'=').decode('utf-8')
    return hashed_password_b64


def check_access_token(new_access_token):
    if new_access_token is None:
        return False
    if 'Bearer' not in new_access_token:
        return False
    clear_token = new_access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    if payload['sub'] is None or payload['role'] is None:
        return False
    return True


def check_password(hashed_password, password):
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = base64.urlsafe_b64decode(hashed_password.encode('utf-8') + b'=')
    algorithm = hashes.SHA256()
    digest = hashes.Hash(algorithm, backend=default_backend())
    digest.update(password_bytes)
    hashed_input_password = digest.finalize()
    return hashed_password_bytes == hashed_input_password


def is_premium(user_id):
    current_datetime = datetime.utcnow()
    active_premium = Premium.query.filter_by(user_id=user_id).filter(Premium.end_date > current_datetime).first()
    return active_premium is not None


def encrypt_data(key, iv, data):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext


def add_admin_user_data(admin_id, user_id, action):
    admin = Admin.query.get(admin_id)
    user = User.query.get(user_id)
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    admin_user_data = Admin_User(admin_id=admin_id, user_id=user_id, action=action)
    db.session.add(admin_user_data)
    db.session.commit()

    return jsonify({"success": True}), 201


def add_admin_premium_data(admin_id, premium_id, action):
    admin = Admin.query.get(admin_id)
    premium = Premium.query.get(premium_id)
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    if not premium:
        return jsonify({"success": False, "message": "Premium not found"}), 404
    admin_premium_data = Admin_Premium(admin_id=admin_id, premium_id=premium_id, action=action)
    db.session.add(admin_premium_data)
    db.session.commit()

    return jsonify({"success": True}), 201
