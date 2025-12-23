# auth_handler.py - Firebase Auth SDK integration for Streamlit

import streamlit as st
import json
from firebase_manager import is_signed_in, get_current_user, migrate_guest_data_to_user

# Firebase configuration
FIREBASE_API_KEY = st.secrets.get("FIREBASE_WEB_API_KEY", "")
FIREBASE_PROJECT_ID = st.secrets.get("FIREBASE_PROJECT_ID", "")

def render_auth_handler_page():
    """Handle Firebase Authentication with Google Sign-In."""
    st.title("🔐 Sign In with Google")
    st.markdown("Connect your Google account to save progress across devices!")

    # Firebase Auth SDK integration
    firebase_config = {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": f"{FIREBASE_PROJECT_ID}.firebaseapp.com",
        "projectId": FIREBASE_PROJECT_ID,
        "storageBucket": f"{FIREBASE_PROJECT_ID}.firebasestorage.app",
        "messagingSenderId": "144901974646",
        "appId": "1:144901974646:web:5f677d6632d5b79f2c4d57"
    }

    # JavaScript for Firebase Auth
    firebase_auth_js = f"""
    <script type="module">
        console.log('Loading Firebase Auth module...');

        // Import Firebase modules
        import {{ initializeApp }} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
        import {{ getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged }} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

        console.log('Firebase modules imported successfully');

        // Firebase configuration
        const firebaseConfig = {json.dumps(firebase_config)};

        console.log('Initializing Firebase app...');
        // Initialize Firebase
        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();

        console.log('Firebase initialized, setting up auth...');

        // Configure Google provider
        provider.setCustomParameters({{
            prompt: 'select_account'
        }});

        // Auth state observer
        onAuthStateChanged(auth, (user) => {{
            console.log('Auth state changed:', user ? 'signed in' : 'signed out');
            if (user) {{
                // User is signed in
                console.log('User signed in:', user.email);
                const userData = {{
                    uid: user.uid,
                    email: user.email,
                    displayName: user.displayName,
                    photoURL: user.photoURL,
                    emailVerified: user.emailVerified,
                    isAnonymous: user.isAnonymous,
                    providerData: user.providerData
                }};

                // Redirect with user data as query parameters
                const userDataStr = encodeURIComponent(JSON.stringify(userData));
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('firebase_auth_type', 'success');
                currentUrl.searchParams.set('user_data', userDataStr);
                console.log('Redirecting to:', currentUrl.toString());
                window.location.href = currentUrl.toString();
            }} else {{
                // User is signed out - redirect to sign out
                console.log('User signed out');
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('firebase_auth_type', 'signout');
                window.location.href = currentUrl.toString();
            }}
        }});

        // Make functions available globally
        window.firebaseAuth = {{
            signIn: () => {{
                console.log('signIn function called');
                signInWithPopup(auth, provider)
                    .then((result) => {{
                        console.log('Sign in successful:', result.user.email);
                    }})
                    .catch((error) => {{
                        console.error('Sign in error:', error);
                        // Redirect with error
                        const currentUrl = new URL(window.location.href);
                        currentUrl.searchParams.set('firebase_auth_type', 'error');
                        currentUrl.searchParams.set('error', encodeURIComponent(error.message));
                        window.location.href = currentUrl.toString();
                    }});
            }},
            signOut: () => {{
                console.log('signOut function called');
                signOut(auth)
                    .then(() => {{
                        console.log('Sign out successful');
                    }})
                    .catch((error) => {{
                        console.error('Sign out error:', error);
                    }});
            }}
        }};

        console.log('Firebase Auth setup complete, window.firebaseAuth available:', !!window.firebaseAuth);

        // Listen for messages from Streamlit
        window.addEventListener('message', (event) => {{
            console.log('Received message:', event.data);
            if (event.data.type === 'trigger-sign-in') {{
                window.firebaseAuth.signIn();
            }} else if (event.data.type === 'trigger-sign-out') {{
                window.firebaseAuth.signOut();
            }}
        }});
    </script>
    """

    # Inject Firebase Auth JavaScript
    st.markdown(firebase_auth_js, unsafe_allow_html=True)

    # Handle authentication messages from JavaScript
    if 'auth_message' not in st.session_state:
        st.session_state.auth_message = None

    # JavaScript message handler (this will be called via rerun)
    auth_message_placeholder = st.empty()

    # Sign in button
    if not is_signed_in():
        # Add a container for status messages
        status_container = st.empty()

        if st.button("🔐 Sign In with Google", type="primary", use_container_width=True):
            # Trigger sign in via JavaScript with better error handling
            st.markdown("""
            <script>
                try {
                    if (window.firebaseAuth && window.firebaseAuth.signIn) {
                        console.log('Triggering Firebase sign in...');
                        window.firebaseAuth.signIn();
                    } else {
                        console.error('Firebase Auth not available');
                        // Show error message
                        const errorDiv = document.createElement('div');
                        errorDiv.style.cssText = 'color: red; padding: 10px; border: 1px solid red; border-radius: 4px; margin: 10px 0; background: #ffe6e6;';
                        errorDiv.textContent = 'Firebase Auth is not loaded yet. Please wait a moment and try again, or refresh the page.';
                        document.body.appendChild(errorDiv);
                        setTimeout(() => errorDiv.remove(), 5000);
                    }
                } catch (error) {
                    console.error('Error triggering sign in:', error);
                    alert('Error starting sign in process. Please refresh the page and try again.');
                }
            </script>
            """, unsafe_allow_html=True)

        # Show loading status
        st.markdown("""
        <div style="margin: 20px 0; padding: 10px; background: #e8f4fd; border-left: 4px solid #1e88e5; border-radius: 4px;">
            <strong>🔄 Ready to sign in!</strong><br>
            Click the button above to open Google sign-in popup.
        </div>
        """, unsafe_allow_html=True)

        # Add fallback link in case JavaScript fails
        st.markdown("---")
        st.markdown("**Having trouble?** Try the direct sign-in link:")
        auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={st.secrets.get('GOOGLE_CLIENT_ID', '')}&redirect_uri={st.secrets.get('REDIRECT_URI', '')}&scope=openid%20email%20profile&response_type=code&state=firebase_auth&prompt=select_account"
        st.markdown(f"[🔗 Direct Google Sign-In]({auth_url})", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Why sign in?**")
        st.markdown("✅ Save your progress across devices")
        st.markdown("✅ Backup your API keys securely")
        st.markdown("✅ Access advanced statistics")
        st.markdown("✅ Never lose your learning data")

    else:
        # User is signed in
        user = get_current_user()
        if user:
            st.success(f"✅ Signed in as {user.get('display_name', user.get('email', 'User'))}")

            # Show user info
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get('photo_url'):
                    st.image(user['photo_url'], width=60)
                else:
                    st.markdown("👤")
            with col2:
                st.markdown(f"**{user.get('display_name', 'User')}**")
                st.markdown(f"*{user.get('email', '')}*")

            st.markdown("---")

            if st.button("🚪 Sign Out", use_container_width=True):
                # Trigger sign out via JavaScript
                st.markdown("""
                <script>
                    if (window.firebaseAuth) {
                        window.firebaseAuth.signOut();
                    } else {
                        // Fallback: clear session state directly
                        window.location.href = window.location.href.split('?')[0] + '?firebase_auth_type=signout';
                    }
                </script>
                """, unsafe_allow_html=True)

            # Migration status
            if st.session_state.get('data_migrated', False):
                st.info("✅ Your data has been migrated to the cloud!")
            else:
                if st.button("☁️ Migrate My Data to Cloud", type="secondary", use_container_width=True):
                    with st.spinner("Migrating your data..."):
                        success = migrate_guest_data_to_user(user['uid'])
                        if success:
                            st.session_state.data_migrated = True
                            st.success("✅ Data migrated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to migrate data. Please try again.")

    # Instructions
    st.markdown("---")
    st.markdown("### 📋 Instructions")
    st.markdown("1. Click 'Sign In with Google' above")
    st.markdown("2. Choose your Google account in the popup")
    st.markdown("3. Grant permission to access your basic profile")
    st.markdown("4. Your data will be securely synced to the cloud!")

    # Privacy notice
    st.markdown("---")
    st.markdown("### 🔒 Privacy & Security")
    st.markdown("• We only access your basic Google profile (name, email, photo)")
    st.markdown("• Your data is encrypted and stored securely in Firebase")
    st.markdown("• You can delete your account and data anytime")
    st.markdown("• [Privacy Policy](https://agnel18.github.io/anki-fluent-forever-language-card-generator/privacy-policy.html)")

def render_user_profile():
    """Render user profile section in sidebar."""
    if is_signed_in():
        user = get_current_user()
        if user:
            # Display user info
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get('photoURL'):
                    st.image(user['photoURL'], width=40)
                else:
                    st.markdown("👤")
            with col2:
                st.markdown(f"**{user.get('displayName', 'User')}**")
                st.caption(user.get('email', ''))

            # Sign out button
            if st.button("🚪 Sign Out", key="sign_out_sidebar", use_container_width=True):
                sign_out()
                st.rerun()
        else:
            st.error("User data not available")
    else:
        # Show sign-in option
        st.markdown("### ☁️ Cloud Sync")
        st.markdown("Save progress across devices!")

        if st.button("🔐 Sign In", key="sign_in_sidebar", use_container_width=True):
            st.session_state.page = "auth_handler"
            st.rerun()

        st.caption("Optional - Guest mode available")