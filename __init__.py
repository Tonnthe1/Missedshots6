from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
app = Flask(__name__)
app.config.from_object(Config)

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import routes and models to avoid circular imports
        from . import routes, models
        db.create_all()

    return app
