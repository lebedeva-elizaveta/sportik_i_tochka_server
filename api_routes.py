from datetime import datetime
from operator import itemgetter

from flask import jsonify, request
from jwt import decode
from logic_statistics import user_statistics_count, admin_statistics

from models import db, User, Admin, Activity, Premium, Achievement
from config import SECRET_KEY
import jwt
from utils import check_email, is_premium, \
    add_admin_premium_data, add_admin_user_data, get_id_from_access_token, get_user_data, \
    handle_user_login, handle_admin_login, create_activity, encrypt_card_data, find_existing_card, \
    validate_card, create_premium, create_new_card_and_premium, create_user, create_admin, get_all_activities
from flask import Blueprint

api_bp = Blueprint('api', __name__)


@api_bp.route('/register_user', methods=['POST'])
def register_user():
    email = request.headers.get('email')
    register_data = request.json
    email_is_free = check_email(email)
    if not email_is_free:
        return jsonify({"free": False}), 409
    new_user = create_user(register_data, email)
    access_token = jwt.encode(payload={'sub': new_user.id, 'role': 'user'}, key=SECRET_KEY, algorithm='HS256')
    return jsonify({
        "success": True,
        "access_token": access_token,
        "user_id": new_user.id
    }), 201


@api_bp.route('/register_admin', methods=['POST'])
def register_admin():
    email = request.headers.get('email')
    register_data = request.json
    email_is_free = check_email(email)
    if not email_is_free:
        return jsonify({"free": False}), 409
    new_admin = create_admin(register_data, email)
    access_token = jwt.encode(payload={'sub': new_admin.id, 'role': 'admin'}, key=SECRET_KEY, algorithm='HS256')
    return jsonify({
        "success": True,
        "access_token": access_token,
        "admin_id": new_admin.id
    }), 201


@api_bp.route('/login', methods=['POST'])
def login():
    login_data = request.json
    email = login_data.get('email')
    password = login_data.get('password')
    user = User.query.filter_by(email=email).first()
    if user:
        return handle_user_login(user, password)
    admin = Admin.query.filter_by(email=email).first()
    if admin:
        return handle_admin_login(admin, password)
    return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404


@api_bp.route('/add_activity', methods=['POST'])
def add_activity():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False}), 404
    activity_data = request.json
    new_activity = create_activity(user, activity_data)
    return jsonify({
        "success": True,
        "activity_id": new_activity.id
    }), 201


@api_bp.route('/get_activities', methods=['GET'])
def get_activities():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False}), 404
    user_activities = Activity.query.filter_by(user_id=user_id).all()
    if not user_activities:
        return jsonify({"success": True, "message": "No activities yet"}), 200
    list_of_activities = []
    list_of_activities = get_all_activities(list_of_activities, user_activities)
    return jsonify({"success": True, "activities": list_of_activities}), 200


@api_bp.route('/admin_actions/modify', methods=['PUT'])
def admin_actions_put():
    access_token = request.headers.get('Authorization')
    admin_id = get_id_from_access_token(access_token)
    if not admin_id:
        return jsonify({"success": False}), 401
    admin = Admin.query.filter_by(id=admin_id).first()
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404

    request_data = request.json
    user_id = request_data['user_id']
    action = request_data['action']
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if action == "block":
        user.is_blocked = True
        add_admin_user_data(admin_id, user_id, action)
        db.session.commit()
        return jsonify({"success": True, "action": "block"})
    elif action == "unblock":
        user.is_blocked = False
        add_admin_user_data(admin_id, user_id, action)
        db.session.commit()
        return jsonify({"success": True, "action": "unblock"})
    elif action == "revoke_premium":
        premium = Premium.query.filter(
            Premium.user_id == user_id,
            Premium.start_date <= datetime.utcnow(),
            Premium.end_date >= datetime.utcnow()
        ).order_by(
            Premium.start_date.desc(), Premium.end_date.desc()
        ).first()
        premium.end_date = datetime.utcnow()
        add_admin_premium_data(admin_id, premium.id, action)
        db.session.commit()
        return jsonify({"success": True, "action": "revoke_premium"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400


@api_bp.route('/admin_actions/grant_premium', methods=['POST'])
def admin_actions_post():
    access_token = request.headers.get('Authorization')
    admin_id = get_id_from_access_token(access_token)
    if not admin_id:
        return jsonify({"success": False}), 401
    admin = Admin.query.filter_by(id=admin_id).first()
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    request_data = request.json
    user_id = request_data['user_id']
    action = request_data['action']
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if action == "grant_premium":
        new_premium = create_premium(user_id)
        add_admin_premium_data(admin_id, new_premium.id, action)
        return jsonify({"success": True, "action": "grant_premium"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400


@api_bp.route('/buy_premium', methods=['POST'])
def buy_premium():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False}), 404

    card_data = request.json

    encrypt_card = encrypt_card_data(card_data)
    card_name = encrypt_card['card_name']
    encrypted_card_number = encrypt_card['card_number']
    encrypted_month = encrypt_card['month']
    encrypted_year = encrypt_card['year']
    encrypted_cvv = encrypt_card['cvv']

    existing_card = find_existing_card(encrypted_card_number)
    if existing_card and validate_card(existing_card, encrypted_month, encrypted_year, encrypted_cvv):
        new_premium = create_premium(user_id)
        start_date = new_premium.start_date
    else:
        create_new_card_and_premium(card_name, encrypted_card_number, encrypted_month, encrypted_year, encrypted_cvv,
                                    user_id)
        start_date = datetime.utcnow()

    return jsonify({"success": True, "timestamp": start_date}), 201


@api_bp.route('/get_current_data', methods=['GET'])
def get_current_data():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    clear_token = access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    role = payload['role']
    entity_id = payload['sub']
    if role == 'user':
        entity = User.query.get(entity_id)
    elif role == 'admin':
        entity = Admin.query.get(entity_id)
    else:
        return jsonify({"success": False}), 403
    if not entity:
        return jsonify({"success": False}), 404

    response_data = {
        "id": entity_id,
        "name": entity.name,
        "image": entity.avatar,
        "phone": entity.phone,
        "birthday": entity.birthday.strftime('%Y-%m-%d')
    }

    if role == 'user':
        response_data["weight"] = entity.weight

    return jsonify(response_data), 200


@api_bp.route('/change_current_data', methods=['PUT'])
def change_current_data():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401

    clear_token = access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    role = payload['role']
    if role not in ['user', 'admin']:
        return jsonify({"success": False}), 403

    if role == 'user':
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        user_data = request.json
        user.name = user_data.get('name', user.name)
        user.avatar = user_data.get('image', user.avatar)
        user.phone = user_data.get('phone', user.phone)
        user.birthday = user_data.get('birthday', user.birthday)
        user.weight = user_data.get('weight', user.weight)
        db.session.commit()
    elif role == 'admin':
        admin = Admin.query.get(user_id)
        if not admin:
            return jsonify({"success": False, "message": "Admin not found"}), 404
        admin_data = request.json
        admin.email = admin_data.get('email', admin.email)
        admin.password_hash = admin_data.get('password_hash', admin.password_hash)
        admin.name = admin_data.get('name', admin.name)
        admin.avatar = admin_data.get('image', admin.avatar)
        admin.phone = admin_data.get('phone', admin.phone)
        admin.birthday = admin_data.get('birthday', admin.birthday)
        db.session.commit()

    return jsonify({"success": True}), 200


@api_bp.route('/cancel_premium', methods=['PUT'])
def cancel_premium():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False}), 404
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


@api_bp.route('/get_user_profile', methods=['GET'])
def get_user_profile():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False}), 404
    period = request.args.get('period')
    statistics = user_statistics_count(user_id, period)
    if not statistics:
        return jsonify({"success": False, "message": "Statistics not found"}), 404
    user_achievements = Achievement.query.filter_by(user_id=user_id).all()
    list_of_achievements = []
    for achievement in user_achievements:
        achievement_data = {
            "id": achievement.id,
            "name": achievement.name,
            "image": achievement.image,
            "distance": achievement.distance
        }
        list_of_achievements.append(achievement_data)
    return jsonify({
        "name": user.name,
        "image": user.avatar,
        "statistics": statistics,
        "achievements": list_of_achievements
    }), 200


@api_bp.route('/get_rating', methods=['GET'])
def get_rating():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    users = User.query.all()
    if not users:
        return jsonify({"success": True, "message": "No users yet"}), 404
    sorted_users = sorted(filter(None, (get_user_data(u) for u in users)), key=itemgetter('rating'))
    return jsonify({"users": sorted_users}), 200


@api_bp.route('/premium_statistics', methods=['GET'])
def premium_statistics():
    access_token = request.headers.get('Authorization')
    user_id = get_id_from_access_token(access_token)
    if not user_id:
        return jsonify({"success": False}), 401
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if not is_premium(user.id):
        return jsonify({"success": False, "message": "User is not premium"}), 403
    period = request.args.get('period')
    statistics = user_statistics_count(user.id, period)
    if not statistics:
        return jsonify({"success": False, "message": "Statistics not found"}), 404
    total_distance_in_meters = statistics['total_distance_in_meters']
    total_time = statistics['total_time']
    total_calories = statistics['total_calories']
    avg_speed = round(total_distance_in_meters/total_time, 2)
    user_activities = Activity.query.filter_by(user_id=user.id).all()
    if not user_activities:
        return jsonify({"success": True, "message": "No activities yet"}), 200
    list_of_activities = []
    for activity in user_activities:
        activity_data = {
            "id": activity.id,
            "activity_type": activity.type,
            "image": activity.image,
            "date": activity.date.strftime('%Y-%m-%d'),
            "avg_speed": activity.speed,
            "distance_in_meters": activity.distance,
            "duration": activity.duration,
            "calories_burned": activity.calories
        }
        list_of_activities.append(activity_data)
    return jsonify({
        "total_distance_in_meters": total_distance_in_meters,
        "total_time": total_time,
        "total_calories": total_calories,
        "avg_speed": avg_speed,
        "activities": list_of_activities
    }), 200


@api_bp.route('/admin_route_statistics', methods=['GET'])
def admin_route_statistics():
    access_token = request.headers.get('Authorization')
    admin_id = get_id_from_access_token(access_token)
    if not admin_id:
        return jsonify({"success": False}), 401
    admin = Admin.query.filter_by(id=admin_id).first()
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    period = request.args.get('period')
    admin_data_statistics = admin_statistics(period)
    if not admin_data_statistics:
        return jsonify({"success": False, "message": "Statistics not found"}), 404
    return jsonify(admin_data_statistics)
