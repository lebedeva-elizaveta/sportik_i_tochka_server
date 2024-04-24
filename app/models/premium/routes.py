from flask import Blueprint, request, jsonify

from app.models.premium.controller import PremiumController
from app.models.user.controller import UserController

api_premium_bp = Blueprint('premium', __name__)


@api_premium_bp.route('/buy_premium', methods=['POST'])
def buy_premium():
    """
    Купить премиум
    """
    try:
        access_token = request.headers.get('Authorization')
        user_id = UserController.get_id_from_access_token(access_token)
        if not user_id:
            return jsonify({"success": False}), 401
        user = UserController.get_by_id(user_id)
        if not user:
            return jsonify({"success": False}), 404
        try:
            card_data = request.json
            result, status = PremiumController.buy_premium(user_id, card_data)
            return jsonify(result), status
        except Exception as e:
            return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500


@api_premium_bp.route('/cancel_premium', methods=['PUT'])
def cancel_premium():
    """
    Отменить премиум
    """
    try:
        access_token = request.headers.get('Authorization')
        user_id = UserController.get_id_from_access_token(access_token)
        if not user_id:
            return jsonify({"success": False}), 401
        user = UserController.get_by_id(user_id)
        if not user:
            return jsonify({"success": False}), 404
        return PremiumController.cancel_premium(user_id)
    except Exception as e:
        return jsonify({"success": False, "error": f"An unexpected error occurred: {e}"}), 500
