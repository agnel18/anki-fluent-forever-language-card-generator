# auth_handler.py - Firebase Auth SDK integration for Streamlit

import streamlit as st
import streamlit.components.v1 as components
import json
from firebase_manager import is_signed_in, get_current_user, migrate_guest_data_to_user, sign_out

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
    # Debug: Show current configuration
    st.write("### 🔧 Firebase Configuration Check")
    col1, col2 = st.columns(2)
    with col1:
        api_key_display = f"`{FIREBASE_API_KEY[:20]}...`" if FIREBASE_API_KEY else "❌ Missing"
        st.write("**API Key:**", api_key_display)
        st.write("**Project ID:**", f"`{FIREBASE_PROJECT_ID}`" if FIREBASE_PROJECT_ID else "❌ Missing")
        st.write("**Auth Domain:**", f"`{firebase_config['authDomain']}`")
    with col2:
        st.write("**Storage Bucket:**", f"`{firebase_config['storageBucket']}`")
        st.write("**App ID:**", f"`{firebase_config['appId']}`")
        st.write("**Current URL:**", f"`{st.query_params}`")

    # Check if we're on Streamlit Cloud
    is_streamlit_cloud = "streamlit.app" in str(st.query_params).lower()
    st.write(f"**Environment:** {'🌐 Streamlit Cloud' if is_streamlit_cloud else '💻 Local Development'}")

    if not FIREBASE_API_KEY or not FIREBASE_PROJECT_ID:
        st.error("❌ Firebase configuration is incomplete. Please check your Streamlit Cloud secrets.")
        st.info("**Required secrets in Streamlit Cloud:**")
        st.code("""
FIREBASE_WEB_API_KEY = "your-api-key-here"
FIREBASE_PROJECT_ID = "your-project-id-here"
        """)
        return
    # JavaScript for Firebase Auth - Working version with traditional script loading
    firebase_auth_js = """
    <script>
        (function() {{
            console.log('🔄 Firebase Auth JavaScript loaded and executing!');
            console.log('Current URL:', window.location.href);

            // Show loading indicator (only if document.body is available)
            if (document.body) {{
                var loadingDiv = document.createElement('div');
                loadingDiv.id = 'firebase-loading';
                loadingDiv.style.cssText = 'position: fixed; top: 10px; right: 10px; background: #2196F3; color: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; z-index: 1000;';
                loadingDiv.textContent = '🔄 Loading Firebase...';
                document.body.appendChild(loadingDiv);
            }} else {{
                console.log('Document body not available, skipping loading indicator');
            }}

            // Load Firebase scripts dynamically
            function loadScript(src, callback) {{
                var script = document.createElement('script');
                script.src = src;
                script.onload = callback;
                document.head.appendChild(script);
            }}

            // Firebase configuration
            var firebaseConfig = {firebase_config_json};

            // Load Firebase App first
            loadScript('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js', function() {{
                console.log('📦 Firebase App loaded');

                // Load Firebase Auth
                loadScript('https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js', function() {{
                    console.log('🔐 Firebase Auth loaded');

                    try {{
                        // Initialize Firebase
                        firebase.initializeApp(firebaseConfig);
                        var auth = firebase.auth();

                        // Configure Google provider
                        var provider = new firebase.auth.GoogleAuthProvider();
                        provider.setCustomParameters({{
                            prompt: 'select_account'
                        }});

                        // Update loading indicator
                        if (loadingDiv) {{
                            loadingDiv.textContent = '✅ Firebase Ready';
                            loadingDiv.style.background = '#4CAF50';
                            setTimeout(function() {{ if (loadingDiv) loadingDiv.remove(); }}, 3000);
                        }}

                        // Auth state observer
                        firebase.auth().onAuthStateChanged(function(user) {{
                            console.log('🔄 Auth state changed:', user ? 'signed in' : 'signed out');
                            if (user) {{
                                console.log('✅ User signed in:', user.email);
                                var userData = {{
                                    uid: user.uid,
                                    email: user.email,
                                    displayName: user.displayName,
                                    photoURL: user.photoURL,
                                    emailVerified: user.emailVerified,
                                    isAnonymous: user.isAnonymous,
                                    providerData: user.providerData
                                }};

                                // Redirect with user data
                                var userDataStr = encodeURIComponent(JSON.stringify(userData));
                                var currentUrl = new URL(window.location.href);
                                currentUrl.searchParams.set('firebase_auth_type', 'success');
                                currentUrl.searchParams.set('user_data', userDataStr);
                                console.log('🔀 Redirecting to:', currentUrl.toString());
                                window.location.href = currentUrl.toString();
                            }} else {{
                                console.log('🚪 User signed out');
                                var currentUrl = new URL(window.location.href);
                                currentUrl.searchParams.set('firebase_auth_type', 'signout');
                                window.location.href = currentUrl.toString();
                            }}
                        }});

                        // Make functions globally available
                        window.firebaseAuth = {{
                            signIn: function() {{
                                console.log('🚀 signIn called');
                                firebase.auth().signInWithPopup(provider)
                                    .then(function(result) {{
                                        console.log('✅ Sign in successful:', result.user.email);
                                    }})
                                    .catch(function(error) {{
                                        console.error('❌ Sign in error:', error);
                                        alert('Sign in failed: ' + error.message);
                                        var currentUrl = new URL(window.location.href);
                                        currentUrl.searchParams.set('firebase_auth_type', 'error');
                                        currentUrl.searchParams.set('error', encodeURIComponent(error.message));
                                        window.location.href = currentUrl.toString();
                                    }});
                            }},
                            signOut: function() {{
                                console.log('🚪 signOut called');
                                firebase.auth().signOut()
                                    .then(function() {{
                                        console.log('✅ Sign out successful');
                                    }})
                                    .catch(function(error) {{
                                        console.error('❌ Sign out error:', error);
                                    }});
                            }}
                        }};

                        console.log('✅ Firebase Auth setup complete');

                    }} catch (error) {{
                        console.error('❌ Firebase initialization error:', error);
                        if (loadingDiv) {{
                            loadingDiv.textContent = '❌ Firebase Error';
                            loadingDiv.style.background = '#f44336';
                        }}
                        alert('Firebase setup failed: ' + error.message);
                    }}
                }});
            }});

            // Listen for messages from Streamlit
            window.addEventListener('message', function(event) {{
                console.log('📨 Received message:', event.data);
                if (event.data && event.data.type === 'trigger-sign-in') {{
                    if (window.firebaseAuth && window.firebaseAuth.signIn) {{
                        window.firebaseAuth.signIn();
                    }}
                }} else if (event.data && event.data.type === 'trigger-sign-out') {{
                    if (window.firebaseAuth && window.firebaseAuth.signOut) {{
                        window.firebaseAuth.signOut();
                    }}
                }}
            }});

        }})();
    </script>
    """.format(firebase_config_json=json.dumps(firebase_config))

    # Inject Firebase Auth JavaScript using components for better Streamlit Cloud compatibility
    components.html(firebase_auth_js, height=0, width=0)
    
    # Status indicator
    st.success("✅ Firebase JavaScript has been injected into the page!")
    st.info("🔄 If you don't see Firebase loading messages in your browser console, try refreshing the page.")

    # Add a manual trigger button as backup
    st.markdown("---")
    st.markdown("**Alternative: Manual Sign-In**")
    if st.button("🚀 Manual Firebase Sign-In", key="manual_signin"):
        # This will trigger the JavaScript via a different method
        manual_trigger_js = """
        <script>
            // Wait a bit for Firebase to load, then try to sign in
            setTimeout(() => {
                try {
                    if (window.firebaseAuth && window.firebaseAuth.signIn) {
                        console.log('Manual trigger: Calling Firebase sign in...');
                        window.firebaseAuth.signIn();
                    } else {
                        console.error('Manual trigger: Firebase Auth not available');
                        alert('Firebase is still loading. Please wait a moment and try again.');
                    }
                } catch (error) {
                    console.error('Manual trigger error:', error);
                    alert('Error: ' + error.message);
                }
            }, 2000); // Wait 2 seconds for Firebase to load
        </script>
        """
        components.html(manual_trigger_js, height=0, width=0)
        st.info("⏳ Attempting to sign in... Check the popup that should open.")

    # Sign in button
    if not is_signed_in():
        # Add a container for status messages
        status_container = st.empty()

        if st.button("🔐 Sign In with Google", type="primary", use_container_width=True):
            # Trigger sign in via JavaScript with better error handling
            signin_trigger_js = """
            <script>
                try {
                    if (window.firebaseAuth && window.firebaseAuth.signIn) {
                        console.log('Triggering Firebase sign in...');
                        window.firebaseAuth.signIn();
                    } else {
                        console.error('Firebase Auth not available');
                        alert('Firebase Auth is not loaded yet. Please wait a moment and try again, or refresh the page.');
                    }
                } catch (error) {
                    console.error('Error triggering sign in:', error);
                    alert('Error starting sign in process. Please refresh the page and try again.');
                }
            </script>
            """
            components.html(signin_trigger_js, height=0, width=0)

        # Show loading status
        st.markdown("""
        <div style="margin: 20px 0; padding: 10px; background: #e8f4fd; border-left: 4px solid #1e88e5; border-radius: 4px;">
            <strong>🔄 Ready to sign in!</strong><br>
            Click the button above to open Google sign-in popup.
        </div>
        """, unsafe_allow_html=True)

        # Add debug information
        with st.expander("🔧 Debug Information (for troubleshooting)"):
            st.code(f"""
Firebase Config:
- API Key: {FIREBASE_API_KEY[:20]}...
- Project ID: {FIREBASE_PROJECT_ID}
- Auth Domain: {FIREBASE_PROJECT_ID}.firebaseapp.com

Current URL: {st.query_params}
            """)

            if st.button("🔄 Reload Firebase Auth", key="reload_firebase"):
                st.rerun()

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
                signout_js = """
                <script>
                    if (window.firebaseAuth) {
                        window.firebaseAuth.signOut();
                    } else {
                        // Fallback: clear session state directly
                        window.location.href = window.location.href.split('?')[0] + '?firebase_auth_type=signout';
                    }
                </script>
                """
                components.html(signout_js, height=0, width=0)

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