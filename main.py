from app import app
import models  # Import models so they're registered
import routes  # Import routes to register URL handlers

# Register Firebase authentication blueprint
try:
    from firebase_auth import firebase_bp
    app.register_blueprint(firebase_bp)
    app.logger.info("Firebase authentication blueprint registered")
except ImportError as e:
    app.logger.warning(f"Firebase authentication not available: {str(e)}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
