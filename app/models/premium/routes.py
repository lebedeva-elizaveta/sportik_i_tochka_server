from flask import Blueprint, request, jsonify

from app.decorators import check_authorization, check_role_user
from app.models.card.controller import CardController
from app.models.card.schemas import CardDataSchema
from app.models.premium.controller import PremiumController

api_premium_bp = Blueprint('premium', __name__)


@api_premium_bp.route('/premium', methods=['GET'])
@check_authorization
@check_role_user
def get_cards(user_id, **kwargs):
    """
    Пользователь видит все свои карты перед покупкой
    """
    card_numbers, card_ids, status = CardController.get_user_cards(user_id)
    if card_numbers:
        return jsonify({
            "card_numbers": card_numbers,
            "card_ids": card_ids
        }), status
    else:
        return jsonify({
            "success": True,
            "message": "No cards yet"
        }), 200


@api_premium_bp.route('/premium', methods=['POST'])
@check_authorization
@check_role_user
def buy_premium(user_id, **kwargs):
    """
    Купить премиум
    """
    card_data = {}
    card_id = request.json.get("card_id")
    if card_id:
        card_data["card_id"] = card_id
    else:
        card_data = CardDataSchema().load(request.json)
    result, status = PremiumController.buy_premium(user_id, card_data)
    return jsonify(result), status


@api_premium_bp.route('/premium/cancel', methods=['PUT'])
@check_authorization
@check_role_user
def cancel_premium(user_id, **kwargs):
    """
    Отменить премиум
    """
    result, status = PremiumController.cancel_premium(user_id)
    return jsonify(result), status
