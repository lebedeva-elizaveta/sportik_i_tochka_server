import os

from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate
from api_routes import api_bp
from models import db

app = Flask(__name__)
swagger = Swagger(app, template_file='swagger.yaml')

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    db_url = 'postgresql://postgres:1234@localhost/sportik_i_tochka'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)
