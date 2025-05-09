"""
Firebase configuration for the application.
These environment variables need to be set:
- FIREBASE_API_KEY: Firebase API key for the web SDK
- FIREBASE_APP_ID: Firebase app ID  
- FIREBASE_PROJECT_ID: Firebase project ID
"""

import os
from flask import current_app


def get_firebase_config():
    """Get Firebase configuration from environment variables."""
    return {
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": f"{os.environ.get('FIREBASE_PROJECT_ID')}.firebaseapp.com",
        "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
        "storageBucket": f"{os.environ.get('FIREBASE_PROJECT_ID')}.appspot.com",
        "appId": os.environ.get("FIREBASE_APP_ID"),
    }


def check_firebase_config():
    """Check if all required Firebase environment variables are set."""
    required_vars = ["FIREBASE_API_KEY", "FIREBASE_APP_ID", "FIREBASE_PROJECT_ID"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        current_app.logger.warning(
            f"Missing Firebase configuration: {', '.join(missing_vars)}"
        )
        return False
    return True