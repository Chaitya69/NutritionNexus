# Deploying NutriGuide to Render.com

This guide will help you deploy the NutriGuide application to Render.com successfully.

## Pre-deployment Steps

### 1. Ensure Your Code is in a Git Repository

Make sure your application code is in a Git repository (GitHub, GitLab, etc.) as Render deploys from Git.

### 2. Configure Environment Variables

You'll need to set these environment variables in Render's dashboard:

- `FLASK_APP`: main.py
- `FLASK_ENV`: production
- `FIREBASE_API_KEY`: Your Firebase API key
- `FIREBASE_APP_ID`: Your Firebase App ID
- `FIREBASE_PROJECT_ID`: Your Firebase Project ID
- `DATABASE_URL`: Your database connection string (if using a database)

### 3. Update Firebase Configuration

1. Go to your Firebase Console → Authentication → Settings → Authorized domains
2. Add your Render.com domain (example: `your-app-name.onrender.com`)
3. Make sure Google Authentication is enabled in Firebase Console

## Deployment Configuration

### Create a New Web Service on Render

1. Go to render.com and sign in
2. Click on "New +" and select "Web Service"
3. Connect your repository
4. Fill in the following details:
   - **Name**: Choose a name for your service
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`

5. Add the environment variables mentioned above
6. Click "Create Web Service"

## Post-deployment Steps

### 1. Verify Domain Authorization

1. After deployment, check your Render domain
2. Make sure to add it to Firebase Authorized Domains
3. You may need to wait a few minutes for DNS propagation

### 2. Test Authentication

1. Visit your deployed app
2. Try to log in with Google
3. Check the logs in Render dashboard if issues occur

## Troubleshooting

### Common Issues

1. **Firebase Authentication Errors**:
   - Ensure your domain is added to Firebase Authorized Domains
   - Verify all Firebase environment variables are set correctly

2. **Redirect Issues**:
   - Firebase redirection may need to be updated for your production domain
   - Check the browser console for errors

3. **Database Connection Problems**:
   - If using MongoDB, ensure your connection string is properly formatted
   - The app will use in-memory storage if database connection fails

### Connecting a Custom Domain

If you want to use a custom domain:

1. Add your custom domain in Render dashboard
2. Update DNS settings as instructed by Render
3. Add your custom domain to Firebase Authorized Domains