# NutriGuide - Nutrition Awareness and Recommendation System

A Flask-based nutrition awareness platform that provides personalized dietary insights through a ChatGPT-like interface.

## Features

- User authentication (traditional and Firebase Google login)
- Personalized nutrition recommendations based on user profile
- Food nutrition information lookup
- Simple, clean UI with blue and green theme

## Prerequisites

- Python 3.9 or higher
- MongoDB (optional, app has in-memory fallback)
- Firebase project (for Google authentication)

## Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/nutrition-recommendation.git
cd nutrition-recommendation
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with:

```
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_APP_ID=your_firebase_app_id
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use an existing one
3. Add a web app to your project
4. Enable Google authentication
5. Add `localhost` to authorized domains
6. Copy API keys to your `.env` file

### 5. Run the Application

```bash
flask run
```

Or:

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

### 6. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## Running in VS Code

1. Install the Python extension in VS Code
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables in `.env` file
6. Run with VS Code debugger:
   - Create a launch configuration for Flask
   - Or run from terminal within VS Code

## Deployment

For deployment instructions, see [render-deploy-guide.md](render-deploy-guide.md).

## Firebase Authentication Setup

1. Create a project in [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication and Google sign-in method
3. Add your domain to Authorized Domains list
4. Configure OAuth consent screen in Google Cloud Console
5. Copy Firebase configuration values to environment variables

## Project Structure

- `main.py`: Application entry point
- `app.py`: Flask application setup
- `models.py`: Data models and user management
- `forms.py`: Form definitions using Flask-WTF
- `routes.py`: URL route handlers
- `utils.py`: Utility functions and helpers
- `firebase_auth.py`: Firebase authentication integration
- `firebase_config.py`: Firebase configuration management
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)

## Technology Stack

- Backend: Flask, Python
- Authentication: Flask-Login, Firebase Authentication
- Database: MongoDB with in-memory fallback
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Deployment: Compatible with Render, Heroku, etc.