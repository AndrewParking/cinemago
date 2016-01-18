from schematics.exceptions import ValidationError
from itsdangerous import BadSignature, SignatureExpired
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.restful import Api
from config import config
from .exceptions import (
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    ScrapyServerError,
    bad_request_handler,
    bad_signature_handler,
    unauthorized_handler,
    signature_expired_handler,
    forbidden_handler,
    not_found_handler,
    validation_error_handler,
    scrapy_server_error_handler,
)

db = SQLAlchemy()
mail = Mail()
api = Api()


def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])

    # url import

    from . import routes

    db.init_app(app)
    mail.init_app(app)
    api.init_app(app)

    # blueprints here

    from .seanses import seanses as seanses_blueprint
    app.register_blueprint(seanses_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .scrapy_layer import scrapy_layer as scrapy_layer_blueprint
    app.register_blueprint(scrapy_layer_blueprint)

    # exception handlers registration
    app.errorhandler(BadRequest)(bad_request_handler)
    app.errorhandler(Unauthorized)(unauthorized_handler)
    app.errorhandler(Forbidden)(forbidden_handler)
    app.errorhandler(NotFound)(not_found_handler)
    app.errorhandler(ValidationError)(validation_error_handler)
    app.errorhandler(BadSignature)(bad_signature_handler)
    app.errorhandler(SignatureExpired)(signature_expired_handler)
    app.errorhandler(ScrapyServerError)(scrapy_server_error_handler)

    return app
