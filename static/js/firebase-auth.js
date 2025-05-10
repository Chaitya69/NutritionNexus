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
        
        // Update sign-in status
        const signInMethodElement = document.createElement('div');
        signInMethodElement.className = 'alert alert-info mt-2';
        signInMethodElement.textContent = 'Attempting authentication...';
        
        if (errorElement) {
            errorElement.innerHTML = '';
            errorElement.appendChild(signInMethodElement);
            errorElement.style.display = 'block';
        }
        
        // Try popup first (works better on some browsers)
        console.log('Attempting Google sign-in with popup...');
        console.log('Auth domain:', firebaseConfig.authDomain);
        
        // Try using popup first (often works better)
        firebase.auth().signInWithPopup(provider)
            .then((result) => {
                console.log('Popup sign-in successful!');
                // This is handled by our redirect handler
                signInMethodElement.textContent = 'Authentication successful! Redirecting...';
                signInMethodElement.className = 'alert alert-success mt-2';
            })
            .catch((error) => {
                console.log('Popup sign-in failed, trying redirect...', error.code);
                
                // Show status update
                signInMethodElement.textContent = 'Popup authentication failed. Trying redirect method...';
                
                // Check specific errors
                if (error.code === 'auth/popup-blocked' || error.code === 'auth/popup-closed-by-user') {
                    // If popup is blocked, try redirect method instead
                    console.log('Starting Google sign-in redirect instead...');
                    firebase.auth().signInWithRedirect(provider)
                        .catch(redirectError => {
                            console.error('Redirect error:', redirectError);
                            if (errorElement) {
                                errorElement.innerHTML = `
                                    <div class="alert alert-danger">
                                        <p><strong>Authentication Error:</strong> ${redirectError.message}</p>
                                        <p>Code: ${redirectError.code || 'unknown'}</p>
                                        <hr>
                                        <p>Please make sure your domain is authorized in Firebase.</p>
                                        <a href="/firebase_test" class="btn btn-sm btn-outline-primary">
                                            Run Firebase Configuration Test
                                        </a>
                                    </div>
                                `;
                            }
                        });
                } else if (error.code === 'auth/unauthorized-domain') {
                    // Unauthorized domain is a common issue
                    if (errorElement) {
                        const domain = window.location.hostname;
                        errorElement.innerHTML = `
                            <div class="alert alert-danger">
                                <p><strong>Domain Not Authorized:</strong> ${error.message}</p>
                                <hr>
                                <p>Your domain <code>${domain}</code> must be added to Firebase.</p>
                                <p>Go to Firebase Console → Authentication → Settings → Authorized Domains</p>
                                <a href="/firebase_test" class="btn btn-sm btn-outline-primary">
                                    Run Firebase Configuration Test
                                </a>
                            </div>
                        `;
                    }
                } else {
                    // Other errors
                    if (errorElement) {
                        errorElement.innerHTML = `
                            <div class="alert alert-danger">
                                <p><strong>Authentication Error:</strong> ${error.message}</p>
                                <p>Code: ${error.code || 'unknown'}</p>
                            </div>
                        `;
                    }
                }
            });
    } catch (error) {
        console.error('Failed to initialize Google sign-in:', error);
        if (errorElement) {
            errorElement.innerHTML = `
                <div class="alert alert-danger">
                    <p><strong>Initialization Error:</strong> ${error.message}</p>
                </div>
            `;
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