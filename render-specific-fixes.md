# Render.com Deployment Fixes

Some specific adjustments may be needed for your Firebase authentication to work correctly on Render.com.

## 1. Port Configuration

Render dynamically assigns a port through the PORT environment variable. Update your startup command to:

```
gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app
```

## 2. Firebase Redirect URI Fix

If you're experiencing issues with Firebase authentication after deployment, add the following JavaScript fix to your login page to handle the different domain:

```javascript
// Add this to your firebase-auth.js file
document.addEventListener('DOMContentLoaded', function() {
    // Fix for redirect URLs in production
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Get the production hostname for Firebase auth
        const productionDomain = window.location.hostname;
        console.log('Using production domain for Firebase auth:', productionDomain);
        
        // You might need to update your authDomain if using custom domain
        if (typeof firebaseConfig !== 'undefined' && firebaseConfig !== null) {
            console.log('Original authDomain:', firebaseConfig.authDomain);
        }
    }
});
```

## 3. Update the firebase_config.py File

You may need to modify the authDomain to use your Render domain in production:

```python
def get_firebase_config():
    """Get Firebase configuration from environment variables."""
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    
    # Check if running on Render
    on_render = os.environ.get("RENDER") == "true"
    render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    
    # Default auth domain
    auth_domain = f"{project_id}.firebaseapp.com"
    
    # If on Render and we have a hostname, consider using that instead
    # Note: This might not be necessary, but can help with certain configurations
    # Only enable if you're having redirect issues
    # if on_render and render_hostname:
    #     auth_domain = render_hostname
    
    return {
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": auth_domain,
        "projectId": project_id,
        "storageBucket": f"{project_id}.appspot.com",
        "appId": os.environ.get("FIREBASE_APP_ID"),
    }
```

## 4. Add a Procfile for Render

Create a file named `Procfile` (no extension) at the root of your project:

```
web: gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app
```

## 5. CORS Configuration for Render

If you're experiencing CORS issues, add Flask-CORS to your application:

```python
# In app.py
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

Install Flask-CORS in requirements.txt.

## 6. Debug Environment on Render

Add this to your main route to debug environment variables:

```python
@app.route('/debug-env')
def debug_env():
    if app.debug:  # Only show in debug mode
        env_vars = {k: v for k, v in os.environ.items() 
                   if not k.lower().contains('key') and not k.lower().contains('secret')}
        return jsonify(env_vars)
    return "Not available in production"
```

## 7. Database Configuration

For MongoDB, ensure your connection string is updated for production:

```python
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/nutrition")
```

## 8. Testing Deployment

After deployment:

1. Check your Render logs for any errors
2. Test the regular email/password login first
3. Then test the Firebase Google authentication
4. If Firebase auth fails, use the Firebase test page to debug