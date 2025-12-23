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
        // Import Firebase modules
        import {{ initializeApp }} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
        import {{ getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged }} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

        // Firebase configuration
        const firebaseConfig = {json.dumps(firebase_config)};

        // Initialize Firebase
        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();

        // Configure Google provider
        provider.setCustomParameters({{
            prompt: 'select_account'
        }});

        // Auth state observer
        onAuthStateChanged(auth, (user) => {{
            if (user) {{
                // User is signed in
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
                window.location.href = currentUrl.toString();
            }} else {{
                // User is signed out - redirect to sign out
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('firebase_auth_type', 'signout');
                window.location.href = currentUrl.toString();
            }}
        }});

        // Make functions available globally
        window.firebaseAuth = {{
            signIn: () => {{
                signInWithPopup(auth, provider)
                    .then((result) => {{
                        console.log('Sign in successful');
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
                signOut(auth)
                    .then(() => {{
                        console.log('Sign out successful');
                    }})
                    .catch((error) => {{
                        console.error('Sign out error:', error);
                    }});
            }}
        }};

        // Listen for messages from Streamlit
        window.addEventListener('message', (event) => {{
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
        if st.button("🔐 Sign In with Google", type="primary", use_container_width=True):
            # Trigger sign in via JavaScript
            st.markdown("""
            <script>
                if (window.firebaseAuth) {
                    window.firebaseAuth.signIn();
                } else {
                    alert('Firebase Auth not loaded yet. Please refresh the page.');
                }
            </script>
            """, unsafe_allow_html=True)

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