from app import app
import models  # Import models so they're registered
import routes  # Import routes to register URL handlers

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
