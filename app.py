import os
import logging
from datetime import datetime

from flask import Flask
from flask_pymongo import PyMongo
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
try:
    mongo = PyMongo(app)
    mongo.db.users.find_one({})  # Test the connection
    app.logger.info("MongoDB connection established successfully")
except Exception as e:
    app.logger.error(f"MongoDB connection error: {str(e)}")
    app.logger.warning("Using in-memory data storage as MongoDB fallback")
    
    # Create in-memory storage for development/testing
    class MemoryStorage:
        def __init__(self):
            self.db = type('obj', (object,), {
                'users': [],
                'nutrition_recommendations': []
            })
    
    mongo = MemoryStorage()

# Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

# Note: We're NOT importing models or routes here to avoid circular imports
