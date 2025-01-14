from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from src.models import db


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object("src.config.Config")
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    api = Api(app)
    JWTManager(app)

    from src.routes.auth import auth
    from src.routes.decisions import decisions

    api.register_blueprint(auth)
    api.register_blueprint(decisions)

    return app
