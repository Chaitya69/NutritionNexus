/**
 * Firebase Authentication Integration
 * This file handles client-side authentication with Firebase
 */

// Firebase configuration - Will be loaded dynamically from the server
let firebaseConfig = null;

// Initialize Firebase when the document is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Fetch Firebase configuration from server
        const response = await fetch('/auth/firebase/token');
        if (!response.ok) {
            console.error('Failed to load Firebase configuration');
            return;
        }
        
        firebaseConfig = await response.json();
        
        // Log the configuration (without sensitive data) for debugging
        console.log('Firebase configuration loaded successfully:', {
            authDomain: firebaseConfig.authDomain,
            projectId: firebaseConfig.projectId,
            hasApiKey: !!firebaseConfig.apiKey,
            hasAppId: !!firebaseConfig.appId
        });
        
        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);
        
        // Set up UI elements
        setupFirebaseUI();
        
        // Check for redirect result
        handleRedirectResult();
        
    } catch (error) {
        console.error('Firebase initialization error:', error);
    }
});

/**
 * Set up Firebase UI elements
 */
function setupFirebaseUI() {
    const loginWithGoogleBtn = document.getElementById('login-with-google');
    if (loginWithGoogleBtn) {
        loginWithGoogleBtn.addEventListener('click', signInWithGoogle);
    }
    
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', signOut);
    }
}

/**
 * Sign in with Google using Firebase
 */
function signInWithGoogle() {
    const errorElement = document.getElementById('firebase-error');
    if (errorElement) {
        errorElement.style.display = 'none';
    }

    try {
        const provider = new firebase.auth.GoogleAuthProvider();
        
        // Add scopes for permissions
        provider.addScope('email');
        provider.addScope('profile');
        
        // Set custom parameters
        provider.setCustomParameters({
            prompt: 'select_account'
        });
        
        // Log info before redirect
        console.log('Starting Google sign-in redirect...');
        console.log('Auth domain:', firebaseConfig.authDomain);
        
        // Start sign in process
        firebase.auth().signInWithRedirect(provider)
            .catch(error => {
                console.error('Immediate redirect error:', error);
                if (errorElement) {
                    errorElement.textContent = 'Sign-in error: ' + error.message;
                    errorElement.style.display = 'block';
                }
            });
    } catch (error) {
        console.error('Failed to initialize Google sign-in:', error);
        if (errorElement) {
            errorElement.textContent = 'Failed to start sign-in: ' + error.message;
            errorElement.style.display = 'block';
        }
    }
}

/**
 * Handle the redirect result after Firebase authentication
 */
async function handleRedirectResult() {
    try {
        console.log('Checking Firebase redirect result...');
        const result = await firebase.auth().getRedirectResult();
        
        if (result.user) {
            // User is signed in
            console.log('Firebase user authenticated, sending to server...');
            const user = result.user;
            
            // Extract user information to send to server
            const userData = {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName,
                photoURL: user.photoURL
            };
            
            // Log the user data for debugging (without sensitive information)
            console.log('User authenticated:', {
                uid: userData.uid ? 'present' : 'missing',
                email: userData.email ? 'present' : 'missing',
                displayName: userData.displayName || 'not provided',
                photoAvailable: !!userData.photoURL
            });
            
            // Send user data to the server
            const response = await fetch('/auth/firebase/callback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user: userData }),
            });
            
            const data = await response.json();
            
            if (data.success && data.redirect) {
                // Redirect to the dashboard or specified page
                console.log('Redirecting to:', data.redirect);
                window.location.href = data.redirect;
            } else {
                console.error('Server authentication failed:', data.error);
                // Display error to user
                const errorElement = document.getElementById('firebase-error');
                if (errorElement) {
                    errorElement.textContent = 'Authentication failed: ' + (data.error || 'Unknown error');
                    errorElement.style.display = 'block';
                }
            }
        }
    } catch (error) {
        console.error('Firebase redirect result error:', error);
        
        // Display detailed error to user
        const errorElement = document.getElementById('firebase-error');
        if (errorElement) {
            let errorMessage = 'Authentication error: ' + error.message;
            
            // Provide more helpful messages for common Firebase errors
            if (error.code) {
                switch (error.code) {
                    case 'auth/unauthorized-domain':
                        errorMessage = 'Error: This domain is not authorized for Firebase authentication. Please add your domain to the Firebase Console under Authentication > Settings > Authorized Domains.';
                        break;
                    case 'auth/operation-not-allowed':
                        errorMessage = 'Error: Google authentication is not enabled in the Firebase Console. Please enable it under Authentication > Sign-in Methods.';
                        break;
                    case 'auth/popup-blocked':
                        errorMessage = 'Error: Authentication popup was blocked. Please allow popups for this website.';
                        break;
                    case 'auth/cancelled-popup-request':
                        errorMessage = 'Authentication was cancelled.';
                        break;
                    case 'auth/network-request-failed':
                        errorMessage = 'Network error. Please check your internet connection and try again.';
                        break;
                }
            }
            
            errorElement.textContent = errorMessage;
            errorElement.style.display = 'block';
            
            // Add a link to the Firebase test page for debugging
            if (error.code === 'auth/unauthorized-domain') {
                const testLink = document.createElement('a');
                testLink.href = '/firebase_test';
                testLink.textContent = 'Run Firebase Configuration Test';
                testLink.className = 'btn btn-sm btn-outline-primary mt-2';
                errorElement.appendChild(document.createElement('br'));
                errorElement.appendChild(testLink);
            }
        }
    }
}

/**
 * Sign out from Firebase
 */
function signOut() {
    firebase.auth().signOut().then(() => {
        // Sign-out successful, redirect to logout URL
        window.location.href = '/logout';
    }).catch((error) => {
        console.error('Sign out error:', error);
    });
}