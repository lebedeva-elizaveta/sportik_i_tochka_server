from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate

from app.config import settings
from app.models.activity.routes import api_activity_bp
from app.models.admin.routes import api_admin_bp
from app.models.premium.routes import api_premium_bp
from app.models.common_routes import api_bp

from app.models.user.routes import api_user_bp
from app.database import db

from app.models.additional_models import User_Card
from app.models.card.model import  Card

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
db.init_app(app)

swagger = Swagger(app, template_file='../swagger.yaml')
app.register_blueprint(api_user_bp)
app.register_blueprint(api_admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(api_activity_bp)
app.register_blueprint(api_premium_bp)
migrate = Migrate(app, db)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

