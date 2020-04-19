import os

from flask import Flask
from flask_assets import Environment
from flask_compress import Compress
from flask_login import LoginManager
from flask_mail import Mail
from flask_rq import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from pymongo import MongoClient

from app.assets import app_css, app_js, vendor_css, vendor_js
from config import config as Config

from flasgger import Swagger

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()

# TODO: Find a way to refer configuration from Config instead of using os.getenv for consistency
# TODO: Research if PyMongo helps creating mongo instance with the same pattern as other extensions
MONGO_USER = os.getenv('MONGO_USER')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')
MONGO_ATLAS_DOMAIN = os.getenv('MONGO_ATLAS_DOMAIN')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
client_credential = "mongodb+srv://%s:%s@%s" % (
    MONGO_USER, MONGO_PASSWORD, MONGO_ATLAS_DOMAIN
)
client = MongoClient(client_credential)
mongo_db = client[MONGO_DATABASE]

db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'


def create_app(config):
    app = Flask(__name__)
    swagger = Swagger(app)
    config_name = config

    if not isinstance(config, str):
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app.config.from_object(Config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it

    Config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    RQ(app)

    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    assets_env = Environment(app)
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir, path))
    assets_env.url_expire = True

    assets_env.register('app_css', app_css)
    assets_env.register('app_js', app_js)
    assets_env.register('vendor_css', vendor_css)
    assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .walk import walk as walk_blueprint
    app.register_blueprint(walk_blueprint, url_prefix='/walk')

    return app
