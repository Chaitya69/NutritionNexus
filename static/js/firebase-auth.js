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
    const provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithRedirect(provider);
}

/**
 * Handle the redirect result after Firebase authentication
 */
async function handleRedirectResult() {
    try {
        const result = await firebase.auth().getRedirectResult();
        
        if (result.user) {
            // User is signed in
            const user = result.user;
            
            // Get the ID token
            const idToken = await user.getIdToken();
            
            // Send the token to the server
            const response = await fetch('/auth/firebase/callback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ idToken }),
            });
            
            const data = await response.json();
            
            if (data.success && data.redirect) {
                // Redirect to the dashboard or specified page
                window.location.href = data.redirect;
            } else {
                console.error('Server authentication failed:', data.error);
            }
        }
    } catch (error) {
        console.error('Firebase redirect result error:', error);
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