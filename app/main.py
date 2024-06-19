from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate
from marshmallow import ValidationError

from app.config import settings
from app.exceptions.error_handlers import handle_invalid_token_exception, handle_user_not_found_exception, \
    handle_invalid_role_exception, handle_unavailable_action, handle_validation_error, handle_invalid_action_exception, \
    handle_already_exists_exception, handle_invalid_password_exception, bad_request_error_handler, \
    handle_unprocessable_entity
from app.exceptions.exceptions import InvalidTokenException, NotFoundException, InvalidRoleException, \
    ActionIsNotAvailableException, InvalidActionException, AlreadyExistsException, InvalidPasswordException, \
    UnprocessableEntityException
from app.file_controller import file_bp
from app.models.activity.routes import api_activity_bp
from app.models.admin.routes import api_admin_bp
from app.models.premium.routes import api_premium_bp
from app.models.common_routes import api_bp
from app.models.user.routes import api_user_bp
from app.database import db
from app.models.user.controller import UserController
from app.services.mail_service import mail

app = Flask(__name__)

UserController.scheduler.init_app(app)
UserController.scheduler.start()

app.config['SECRET_KEY'] = settings.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
app.config['MAIL_SERVER'] = settings.mail_server
app.config['MAIL_PORT'] = settings.mail_port
app.config['MAIL_USERNAME'] = settings.mail_username
app.config['MAIL_PASSWORD'] = settings.mail_password
app.config['MAIL_USE_TLS'] = settings.mail_use_tls

mail.init_app(app)
db.init_app(app)

swagger = Swagger(app, template_file='../swagger.yaml')

app.register_blueprint(api_user_bp)
app.register_blueprint(api_admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(api_activity_bp)
app.register_blueprint(api_premium_bp)
app.register_blueprint(file_bp)

migrate = Migrate(app, db)

app.register_error_handler(InvalidTokenException, handle_invalid_token_exception)
app.register_error_handler(NotFoundException, handle_user_not_found_exception)
app.register_error_handler(InvalidRoleException, handle_invalid_role_exception)
app.register_error_handler(ValidationError, handle_validation_error)
app.register_error_handler(400, bad_request_error_handler)
app.register_error_handler(ActionIsNotAvailableException, handle_unavailable_action)
app.register_error_handler(InvalidActionException, handle_invalid_action_exception)
app.register_error_handler(AlreadyExistsException, handle_already_exists_exception)
app.register_error_handler(InvalidPasswordException, handle_invalid_password_exception)
app.register_error_handler(UnprocessableEntityException, handle_unprocessable_entity)


if __name__ == '__main__':
    app.run(debug=True)
with app.app_context():
    db.create_all()
