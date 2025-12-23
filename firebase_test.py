import streamlit as st
import json

st.title("🔥 Firebase Auth Test")

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDUMMY_API_KEY_FOR_TESTING",
    "authDomain": "dummy-project-id.firebaseapp.com",
    "projectId": "dummy-project-id",
    "storageBucket": "dummy-project-id.firebasestorage.app",
    "messagingSenderId": "144901974646",
    "appId": "1:144901974646:web:5f677d6632d5b79f2c4d57"
}

# JavaScript for Firebase Auth - Simplified version for better compatibility
firebase_auth_js = f"""
<script>
    console.log('🔄 Starting Firebase Auth setup...');

    // Show loading indicator
    var loadingDiv = document.createElement('div');
    loadingDiv.id = 'firebase-loading';
    loadingDiv.style.cssText = 'position: fixed; top: 10px; right: 10px; background: #2196F3; color: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; z-index: 1000;';
    loadingDiv.textContent = '🔄 Loading Firebase...';
    document.body.appendChild(loadingDiv);

    // Load Firebase scripts dynamically
    function loadScript(src, callback) {{
        var script = document.createElement('script');
        script.src = src;
        script.onload = callback;
        document.head.appendChild(script);
    }}

    // Firebase configuration
    var firebaseConfig = {json.dumps(firebase_config)};

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
                loadingDiv.textContent = '✅ Firebase Ready';
                loadingDiv.style.background = '#4CAF50';
                setTimeout(function() {{ loadingDiv.remove(); }}, 3000);

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

                        // Show success message
                        alert('✅ Sign in successful!\\nEmail: ' + user.email + '\\nName: ' + user.displayName);
                        console.log('🔀 User data:', userData);
                    }} else {{
                        console.log('🚪 User signed out');
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
                            }});
                    }},
                    signOut: function() {{
                        console.log('🚪 signOut called');
                        firebase.auth().signOut()
                            .then(function() {{
                                console.log('✅ Sign out successful');
                                alert('✅ Signed out successfully');
                            }})
                            .catch(function(error) {{
                                console.error('❌ Sign out error:', error);
                            }});
                    }}
                }};

                console.log('✅ Firebase Auth setup complete');

            }} catch (error) {{
                console.error('❌ Firebase initialization error:', error);
                loadingDiv.textContent = '❌ Firebase Error';
                loadingDiv.style.background = '#f44336';
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
</script>
"""

# Inject Firebase Auth JavaScript
st.markdown(firebase_auth_js, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🧪 Firebase Auth Test")
st.markdown("Check the browser console (F12) for Firebase messages.")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Test Sign In", use_container_width=True, type="primary"):
        st.markdown("""
        <script>
            if (window.firebaseAuth && window.firebaseAuth.signIn) {
                window.firebaseAuth.signIn();
            } else {
                alert('Firebase Auth not ready yet. Please wait for the loading indicator to disappear.');
            }
        </script>
        """, unsafe_allow_html=True)

with col2:
    if st.button("🚪 Test Sign Out", use_container_width=True):
        st.markdown("""
        <script>
            if (window.firebaseAuth && window.firebaseAuth.signOut) {
                window.firebaseAuth.signOut();
            } else {
                alert('Firebase Auth not ready yet.');
            }
        </script>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📋 Instructions")
st.markdown("1. Open browser console (F12)")
st.markdown("2. Click 'Test Sign In' button")
st.markdown("3. Check console for Firebase messages")
st.markdown("4. If popup appears, authentication is working!")
st.markdown("5. If no messages appear, JavaScript isn't loading")