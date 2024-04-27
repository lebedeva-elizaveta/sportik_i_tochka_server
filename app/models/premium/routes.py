from flask import Blueprint, request, jsonify

from app.decorators import check_authorization, check_role_user
from app.models.card.schemas import CardDataSchema
from app.models.premium.controller import PremiumController

api_premium_bp = Blueprint('premium', __name__)


@api_premium_bp.route('/premium', methods=['POST'])
@check_authorization
@check_role_user
def buy_premium(user_id, **kwargs):
    """
    Купить премиум
    """
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
