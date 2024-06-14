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
    response, status = CardController.get_user_cards(user_id)
    if isinstance(response, list):
        serialized_response = CardDataSchema(many=True).dump(response)
        return jsonify(serialized_response), status
    else:
        return jsonify(response), status


@api_premium_bp.route('/premium', methods=['POST'])
@check_authorization
@check_role_user
def buy_premium(user_id, **kwargs):
    """
    Купить премиум
    """
    card_data = request.json
    card_data = CardDataSchema().load(card_data)
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
