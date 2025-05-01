import os
import logging
from datetime import datetime

from flask import Flask
from flask_pymongo import PyMongo  # Note the correct capitalization
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure MongoDB
app.config["MONGO_URI"] = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/nutrition_app")
mongo = PyMongo(app)

# Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

# Import models to register user loader with login_manager
import models  # noqa: F401

# Import routes after app is created to avoid circular imports
from routes import *  # noqa: F401, E402