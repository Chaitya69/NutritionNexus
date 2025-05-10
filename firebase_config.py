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
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    return {
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": f"{project_id}.firebaseapp.com",
        "projectId": project_id,
        "storageBucket": f"{project_id}.appspot.com",
        "appId": os.environ.get("FIREBASE_APP_ID"),
        "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID", ""), # Optional
        # Add these for more compatibility
        "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""), # Optional
        "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", ""), # Optional
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