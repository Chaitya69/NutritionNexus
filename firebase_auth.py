"""
Firebase authentication module for the application.
Handles user authentication with Firebase.
"""

import json
from flask import Blueprint, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user
import firebase_admin
from firebase_admin import auth, credentials
import pyrebase

from models import User
from firebase_config import get_firebase_config, check_firebase_config

# Use a shorter name for firebase_admin.auth
firebase_auth = auth

# Initialize blueprint
firebase_bp = Blueprint('firebase_auth', __name__, url_prefix='/auth/firebase')

# Initialize Firebase Admin SDK - Would be initialized with service account key
# Since we don't have a service account key file yet, we'll initialize it when needed
firebase_admin_initialized = False
firebase_app = None


def initialize_firebase_admin():
    """Initialize Firebase Admin SDK if not already initialized."""
    global firebase_admin_initialized, firebase_app
    if not firebase_admin_initialized:
        try:
            # Try to initialize with application default credentials
            # This is a placeholder and should be replaced with actual credentials
            firebase_app = firebase_admin.initialize_app()
            firebase_admin_initialized = True
            current_app.logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise


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
        return jsonify({
            "error": "Firebase configuration is incomplete. Please set the required environment variables."
        }), 500
    
    try:
        # Get the ID token from the request
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({
                "success": False,
                "error": "No ID token provided"
            }), 400
        
        # Initialize Firebase Admin SDK if not already initialized
        initialize_firebase_admin()
        
        # Verify the ID token
        decoded_token = firebase_auth.verify_id_token(id_token)
        
        # Get user from Firebase
        firebase_user = firebase_auth.get_user(decoded_token['uid'])
        
        # Check if user exists in our database
        user = User.get_by_email(firebase_user.email)
        
        if not user:
            # Create a new user
            user = User.create_firebase_user({
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'username': firebase_user.display_name or firebase_user.email.split('@')[0],
                'display_name': firebase_user.display_name
            })
        
        # Log in the user
        login_user(user)
        
        return jsonify({
            "success": True,
            "redirect": url_for('dashboard')
        })
    
    except Exception as e:
        current_app.logger.error(f"Firebase authentication error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400