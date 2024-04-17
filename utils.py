import base64

import jwt
from flask import jsonify
from jwt import decode
from config import SECRET_KEY, AES_KEY, AES_IV
from logic_achievements import get_achievement
from logic_rating import get_user_rating
from logic_statistics import user_statistics_count, user_average_statistics
from models import User, Premium, Admin, Admin_User, db, Admin_Premium, Card, Activity, Achievement
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from datetime import datetime, timedelta


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


def get_id_from_access_token(new_access_token):
    if new_access_token is None:
        return None
    if 'Bearer' not in new_access_token:
        return None
    clear_token = new_access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    if payload['sub'] is None or payload['role'] is None:
        return None
    return payload['sub']


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


def get_role(id):
    if is_premium(id):
        role = "premium"
    else:
        role = "regular"
    return role


def add_card_and_buy(card_data):
    card_name = card_data['card_name']
    card_number = card_data['card_number']
    month = str(card_data['month'])
    year = str(card_data['year'])
    cvv = str(card_data['cvv'])

    encrypted_card_number = encrypt_data(AES_KEY, AES_IV, card_number.encode())
    encrypted_month = encrypt_data(AES_KEY, AES_IV, month.encode())
    encrypted_year = encrypt_data(AES_KEY, AES_IV, year.encode())
    encrypted_cvv = encrypt_data(AES_KEY, AES_IV, cvv.encode())

    existing_card = Card.query.filter_by(card_number_hash=encrypted_card_number.hex()).first()
    if existing_card:
        if existing_card.month_hash == encrypted_month.hex() and existing_card.year_hash == encrypted_year.hex() \
                and existing_card.cvv_hash == encrypted_cvv.hex():
            return jsonify({
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=30)})
    else:
        new_card = Card(
            card_name=card_name,
            card_number_hash=encrypted_card_number.hex(),
            month_hash=encrypted_month.hex(),
            year_hash=encrypted_year.hex(),
            cvv_hash=encrypted_cvv.hex()
        )
        db.session.add(new_card)
        db.session.commit()
        return jsonify({
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=30)})


def get_user_data(user):
    total_activities_count = Activity.query.filter_by(user_id=user.id).count()
    if total_activities_count == 0:
        return None
    user_achievements = Achievement.query.filter_by(user_id=user.id).all()
    list_of_achievements = [{"id": a.id, "name": a.name, "image": a.image, "distance": a.distance} for a in user_achievements]
    statistics = user_statistics_count(user.id, "all_time")
    average_statistics = user_average_statistics(user.id)
    if not statistics or not average_statistics:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "image": user.avatar,
        "role": get_role(user.id),
        "rating": get_user_rating(user.id),
        "total_activities_count": total_activities_count,
        "total_distance_in_meters": statistics['total_distance_in_meters'],
        "total_time": statistics['total_time'],
        "total_calories": statistics['total_calories'],
        "avg_speed": average_statistics['avg_speed'],
        "average_distance_in_meters": average_statistics['average_distance_in_meters'],
        "average_time": average_statistics['average_time'],
        "average_calories": average_statistics['average_calories'],
        "achievements": list_of_achievements
    }


def handle_user_login(user, password):
    if user.is_blocked:
        return jsonify({"success": False, "error": "USER_BLOCKED"}), 403
    if not check_password(user.password_hash, password):
        return jsonify({"success": False, "error": "INCORRECT_PASSWORD"}), 401
    role = "premium" if is_premium(user.id) else "regular"
    return jsonify({
        "success": True,
        "access_token": generate_access_token(user),
        "user_id": user.id,
        "role": role
    }), 200


def handle_admin_login(admin, password):
    if not check_password(admin.password_hash, password):
        return jsonify({"success": False, "error": "INCORRECT_PASSWORD"}), 401
    return jsonify({
        "success": True,
        "access_token": generate_access_token(admin),
        "admin_id": admin.id,
        "role": "admin"
    }), 200


def generate_access_token(entity):
    if isinstance(entity, User):
        role = 'user'
    elif isinstance(entity, Admin):
        role = 'admin'
    else:
        return None

    access_token = jwt.encode(payload={'sub': entity.id, 'role': role}, key=SECRET_KEY, algorithm='HS256')
    return access_token


def create_activity(user, activity_data):
    new_activity = Activity(
        user_id=user.id,
        duration=activity_data['duration'],
        distance=activity_data['distance_in_meters'],
        calories=activity_data['calories_burned'],
        speed=activity_data['avg_speed'],
        date=activity_data['date'],
        image=activity_data['image'],
        type=activity_data['activity_type']
    )
    db.session.add(new_activity)
    db.session.commit()
    get_achievement(user.id)
    db.session.commit()
    return new_activity
