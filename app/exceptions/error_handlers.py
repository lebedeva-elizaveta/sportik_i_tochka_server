from flask import jsonify, Flask
from marshmallow import ValidationError

from app.exceptions.exceptions import InvalidTokenException, NotFoundException, InvalidRoleException, \
    InvalidActionException, ActionIsNotAvailableException, AlreadyExistsException, InvalidPasswordException

app = Flask(__name__)


@app.errorhandler(InvalidActionException)
def handle_invalid_action_exception(error):
    """Возвращает 400 с сообщением о некорректном действии"""
    return jsonify({"success": False, "error": str(error)}), 400


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Возвращает 400 для ошибок валидации"""
    return jsonify({
        "success": False,
        "error": "Validation error",
        "details": error.messages
    }), 400


@app.errorhandler(400)
def bad_request_error_handler(**kwargs):
    """Возвращает 400 при некорректном JSON"""
    return jsonify({
        "success": False,
        "error": "Bad request",
        "message": "Invalid JSON"
    }), 400


@app.errorhandler(InvalidTokenException)
def handle_invalid_token_exception(error):
    """Возвращает 401 с сообщением Invalid token"""
    return jsonify({"success": False, "error": str(error)}), 401


@app.errorhandler(InvalidPasswordException)
def handle_invalid_password_exception(error):
    """Возвращает 401 с сообщением Incorrect password"""
    return jsonify({"success": False, "error": str(error)}), 401


@app.errorhandler(InvalidRoleException)
def handle_invalid_role_exception(error):
    """Возвращает 403 с сообщением"""
    return jsonify({"success": False, "error": str(error)}), 403


@app.errorhandler(NotFoundException)
def handle_user_not_found_exception(error):
    """Возвращает 404 с сообщением *кто-то или что-то* not found"""
    return jsonify({"success": False, "error": str(error)}), 404


@app.errorhandler(ActionIsNotAvailableException)
def handle_unavailable_action(error):
    """Возвращает 409 с сообщением о том, что вызвало конфликт"""
    return jsonify({"success": False, "error": str(error)}), 409


@app.errorhandler(AlreadyExistsException)
def handle_already_exists_exception(error):
    """Возвращает 409 с сообщением о том, что нарушило требование уникальности"""
    return jsonify({"free": False, "error": str(error)}), 409
