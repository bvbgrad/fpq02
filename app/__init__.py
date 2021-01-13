""" """

from flask_bootstrap import Bootstrap
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment

import os

from config import Config
import app.utils6L.utils6L as utils
import logging

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = ('Please log in to access this page.')
bootstrap = Bootstrap()
moment = Moment()

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

@utils.log_wrap
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix='/errors')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    logger.info("Flask application initialized")
    logger.debug(app.url_map)

    return app

from app import models