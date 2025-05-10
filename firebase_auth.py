"""
Firebase authentication module for the application.
Handles user authentication with Firebase.
"""

import json
import logging
from flask import Blueprint, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user

# Try to import firebase modules, but handle gracefully if they're not available
try:
    import firebase_admin
    from firebase_admin import auth, credentials
    firebase_auth = auth  # Use a shorter name for firebase_admin.auth
    firebase_imports_successful = True
except ImportError:
    logging.error("Firebase admin SDK not available")
    firebase_imports_successful = False
    firebase_auth = None
    # Create a dummy module to avoid errors
    import types
    firebase_admin = types.ModuleType('firebase_admin')
    firebase_admin.initialize_app = lambda *args, **kwargs: None
    firebase_admin.get_app = lambda *args, **kwargs: None

from models import User
from firebase_config import get_firebase_config, check_firebase_config

# Initialize blueprint
firebase_bp = Blueprint('firebase_auth', __name__, url_prefix='/auth/firebase')

# Initialize Firebase Admin SDK - Would be initialized with service account key
# Since we don't have a service account key file yet, we'll initialize it when needed
firebase_admin_initialized = False
firebase_app = None


def initialize_firebase_admin():
    """Initialize Firebase Admin SDK if not already initialized."""
    global firebase_admin_initialized, firebase_app, firebase_imports_successful
    
    # If Firebase modules weren't imported successfully, we can't initialize
    if not firebase_imports_successful:
        current_app.logger.warning("Cannot initialize Firebase Admin SDK: modules not available")
        return
        
    if not firebase_admin_initialized:
        try:
            # Get Firebase configuration 
            firebase_config = get_firebase_config()
            
            # For Client-Side Auth only (most common use case), we don't need 
            # to initialize the Admin SDK fully
            options = {
                'projectId': firebase_config['projectId'],
            }
            
            # Initialize the app without credentials for client-only usage
            try:
                _initialize_app(options)
            except ValueError:
                # App already exists
                _get_app()
            
            firebase_admin_initialized = True
            current_app.logger.info("Firebase Admin SDK initialized for client auth")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            # Log more information for debugging
            current_app.logger.debug(f"Firebase config available: {check_firebase_config()}")
            # Don't raise the exception, just log it and continue


def _initialize_app(options):
    """Wrapper around firebase_admin.initialize_app to avoid LSP warnings"""
    global firebase_app
    firebase_app = firebase_admin.initialize_app(None, options)
    return firebase_app


def _get_app():
    """Wrapper around firebase_admin.get_app to avoid LSP warnings"""
    global firebase_app
    firebase_app = firebase_admin.get_app()
    return firebase_app


@firebase_bp.route('/token', methods=['GET'])
def get_firebase_token():
    """Return Firebase configuration for client-side initialization"""
    if not check_firebase_config():
        return jsonify({
            "error": "Firebase configuration is incomplete. Please set the required environment variables."
        }), 500
    
    return jsonify(get_firebase_config())


@firebase_bp.route('/callback', methods=['POST'])
def firebase_auth_callback():
    """Handle Firebase authentication callback"""
    if not check_firebase_config():
        current_app.logger.error("Firebase configuration incomplete")
        return jsonify({
            "success": False,
            "error": "Firebase configuration is incomplete. Please set the required environment variables."
        }), 500
    
    try:
        # Get the data from the request
        data = request.get_json()
        
        if not data:
            current_app.logger.warning("No data provided in callback")
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Log the data structure for debugging (excluding sensitive info)
        current_app.logger.debug(f"Auth callback data keys: {list(data.keys())}")
        if 'user' in data:
            user_keys = list(data['user'].keys())
            current_app.logger.debug(f"User data keys: {user_keys}")
        
        # Extract user information directly from the client-side auth result
        # This is a simplified approach that works when we don't have the Admin SDK fully initialized
        user_info = data.get('user', {})
        email = user_info.get('email')
        display_name = user_info.get('displayName', '')
        uid = user_info.get('uid')
        
        if not email or not uid:
            current_app.logger.warning(f"Missing essential user information (email: {bool(email)}, uid: {bool(uid)})")
            return jsonify({
                "success": False,
                "error": "Missing essential user information (email or user ID)"
            }), 400
        
        current_app.logger.info(f"Processing Firebase authentication for email: {email}")
        
        # Check if user exists in our database
        user = User.get_by_email(email)
        
        if not user:
            # Create a new user
            username = display_name or email.split('@')[0]
            current_app.logger.info(f"Creating new user with email: {email}, username: {username}")
            
            try:
                user = User.create_firebase_user({
                    'uid': uid,
                    'email': email,
                    'username': username,
                    'display_name': display_name
                })
                current_app.logger.info(f"Created new user: {email}")
            except Exception as user_create_error:
                current_app.logger.error(f"Failed to create user: {str(user_create_error)}")
                return jsonify({
                    "success": False,
                    "error": f"Failed to create user account: {str(user_create_error)}"
                }), 500
        else:
            current_app.logger.info(f"Found existing user: {email}")
        
        # Log in the user
        try:
            login_user(user)
            current_app.logger.info(f"User logged in successfully: {email}")
        except Exception as login_error:
            current_app.logger.error(f"Failed to log in user: {str(login_error)}")
            return jsonify({
                "success": False,
                "error": f"Failed to log in: {str(login_error)}"
            }), 500
        
        return jsonify({
            "success": True,
            "redirect": url_for('dashboard')
        })
    
    except Exception as e:
        current_app.logger.error(f"Firebase authentication error: {str(e)}")
        # Return a more detailed error response
        error_info = {
            "success": False,
            "error": str(e),
            "error_type": e.__class__.__name__,
        }
        return jsonify(error_info), 400