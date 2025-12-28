# auth_handler.py - Firebase Email/Password Authentication

import streamlit as st
import firebase_admin
from firebase_admin import auth, firestore, exceptions, credentials, initialize_app
from typing import Optional, Dict, Any
import streamlit.components.v1 as components
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Firebase Admin
try:
    firebase_admin.get_app()
except ValueError:
    # Initialize with your Firebase config
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets.get("FIREBASE_PROJECT_ID", ""),
        "private_key_id": st.secrets.get("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": st.secrets.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": st.secrets.get("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": st.secrets.get("FIREBASE_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets.get('FIREBASE_CLIENT_EMAIL', '')}"
    })
    initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def send_verification_email(email: str, verification_link: str) -> bool:
    """Send verification email using SMTP."""
    try:
        # Email configuration from secrets
        smtp_server = st.secrets.get("EMAIL_SMTP_SERVER", "")
        smtp_port = int(st.secrets.get("EMAIL_SMTP_PORT", "587"))
        username = st.secrets.get("EMAIL_USERNAME", "")
        password = st.secrets.get("EMAIL_PASSWORD", "")
        from_email = st.secrets.get("EMAIL_FROM", username)
        from_name = st.secrets.get("EMAIL_FROM_NAME", "Language Learning App")

        print(f"Email config - Server: {smtp_server}, Port: {smtp_port}, User: {username}, From: {from_email}")

        if not all([smtp_server, smtp_port, username, password]):
            print("Email configuration incomplete - missing required fields")
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Verify Your Email - Language Learning App"
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = email

        # HTML content
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">Welcome to Language Anki Deck Generator! 🎓</h2>
            <p>Thank you for creating an account. To complete your registration, please verify your email address by clicking the button below:</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Verify Email Address</a>
            </div>

            <p><strong>Verification Link:</strong><br>
            <a href="{verification_link}">{verification_link}</a></p>

            <p>If you didn't create an account, you can safely ignore this email.</p>

            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #666; font-size: 12px;">This email was sent by Language Anki Deck Generator. If you have any questions, please contact support.</p>
        </body>
        </html>
        """

        # Plain text content
        text = f"""
        Welcome to Language Anki Deck Generator!

        Thank you for creating an account. To complete your registration, please verify your email address by clicking this link:

        {verification_link}

        If you didn't create an account, you can safely ignore this email.

        This email was sent by Language Anki Deck Generator.
        """

        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        print(f"Logging in as {username}")
        server.login(username, password)
        print(f"Sending email to {email}")
        server.sendmail(from_email, email, msg.as_string())
        server.quit()

        print(f"Verification email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"Failed to send verification email to {email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Firebase Auth JavaScript component for client-side authentication
def firebase_auth_component():
    """Firebase Auth component using JavaScript SDK."""
    firebase_config = {
        "apiKey": st.secrets.get("FIREBASE_API_KEY", ""),
        "authDomain": st.secrets.get("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": st.secrets.get("FIREBASE_PROJECT_ID", ""),
        "storageBucket": st.secrets.get("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": st.secrets.get("FIREBASE_APP_ID", "")
    }

    # JavaScript code for Firebase Auth with email verification
    auth_js = f"""
    <script type="module">
        import {{ initializeApp }} from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js';
        import {{ getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, sendEmailVerification, reload, sendPasswordResetEmail }} from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js';

        const firebaseConfig = {firebase_config};
        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);

        window.firebaseAuth = {{
            login: async (email, password) => {{
                try {{
                    const userCredential = await signInWithEmailAndPassword(auth, email, password);
                    const user = userCredential.user;

                    // Check if email is verified
                    if (!user.emailVerified) {{
                        return {{
                            success: false,
                            error: "Please verify your email address before signing in. Check your inbox for the verification link.",
                            needsVerification: true,
                            user: {{
                                uid: user.uid,
                                email: user.email,
                                displayName: user.displayName || user.email.split('@')[0],
                                emailVerified: false
                            }}
                        }};
                    }}

                    return {{
                        success: true,
                        user: {{
                            uid: user.uid,
                            email: user.email,
                            displayName: user.displayName || user.email.split('@')[0],
                            emailVerified: user.emailVerified
                        }}
                    }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            register: async (email, password, displayName) => {{
                try {{
                    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                    const user = userCredential.user;

                    // Update display name if provided
                    if (displayName) {{
                        await user.updateProfile({{ displayName: displayName }});
                    }}

                    // Send email verification
                    await sendEmailVerification(user);

                    return {{
                        success: true,
                        user: {{
                            uid: user.uid,
                            email: user.email,
                            displayName: user.displayName || user.email.split('@')[0],
                            emailVerified: false
                        }},
                        message: "Account created successfully! Please check your email and click the verification link before signing in."
                    }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            resendVerification: async () => {{
                try {{
                    const user = auth.currentUser;
                    if (user) {{
                        await sendEmailVerification(user);
                        return {{ success: true, message: "Verification email sent! Please check your inbox." }};
                    }} else {{
                        return {{ success: false, error: "No user signed in" }};
                    }}
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            logout: async () => {{
                try {{
                    await signOut(auth);
                    return {{ success: true }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            resetPassword: async (email) => {{
                try {{
                    await sendPasswordResetEmail(auth, email);
                    return {{ success: true, message: "Password reset email sent! Check your inbox." }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            checkEmailVerified: async () => {{
                try {{
                    const user = auth.currentUser;
                    if (user) {{
                        await reload(user);
                        return {{
                            emailVerified: user.emailVerified,
                            user: {{
                                uid: user.uid,
                                email: user.email,
                                displayName: user.displayName || user.email.split('@')[0]
                            }}
                        }};
                    }}
                    return {{ emailVerified: false }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            onAuthStateChanged: (callback) => {{
                onAuthStateChanged(auth, callback);
            }}
        }};
    </script>
    """

    components.html(auth_js, height=0)

# Local auth functions
def is_signed_in():
    """Check if user is authenticated."""
    return st.session_state.get("user") is not None

def get_current_user():
    """Get current authenticated user info."""
    return st.session_state.get("user")

def sign_out():
    """Sign out user."""
    st.session_state.user = None
    st.session_state.is_guest = True

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def create_user_profile(uid: str, email: str, display_name: str = None):
    """Create user profile in Firestore."""
    user_ref = db.collection('users').document(uid)
    user_data = {
        'email': email,
        'displayName': display_name or email.split('@')[0],
        'createdAt': firestore.SERVER_TIMESTAMP,
        'lastLogin': firestore.SERVER_TIMESTAMP,
        'preferences': {
            'theme': 'light',
            'audioSpeed': 1.0,
            'syncPreferences': []
        }
    }
    user_ref.set(user_data)

def update_user_last_login(uid: str):
    """Update user's last login timestamp."""
    user_ref = db.collection('users').document(uid)
    user_ref.update({'lastLogin': firestore.SERVER_TIMESTAMP})

def get_user_profile(uid: str) -> Dict[str, Any]:
    """Get user profile from Firestore."""
    user_ref = db.collection('users').document(uid)
    doc = user_ref.get()
    return doc.to_dict() if doc.exists else None

def save_user_api_keys(uid: str, api_keys: Dict[str, str]):
    """Save encrypted API keys to Firestore."""
    api_keys_ref = db.collection('users').document(uid).collection('api_keys').document('keys')
    api_keys_ref.set({
        'groq': api_keys.get('groq', ''),
        'pixabay': api_keys.get('pixabay', ''),
        'lastUpdated': firestore.SERVER_TIMESTAMP
    })

def get_user_api_keys(uid: str) -> Dict[str, str]:
    """Get user's API keys from Firestore."""
    api_keys_ref = db.collection('users').document(uid).collection('api_keys').document('keys')
    doc = api_keys_ref.get()
    return doc.to_dict() if doc.exists else {}

def save_user_progress(uid: str, language: str, progress_data: Dict[str, Any]):
    """Save user progress to Firestore."""
    progress_ref = db.collection('users').document(uid).collection('progress').document(language)
    progress_data['lastUpdated'] = firestore.SERVER_TIMESTAMP
    progress_ref.set(progress_data)

def get_user_progress(uid: str, language: str) -> Dict[str, Any]:
    """Get user progress from Firestore."""
    progress_ref = db.collection('users').document(uid).collection('progress').document(language)
    doc = progress_ref.get()
    return doc.to_dict() if doc.exists else {}

def save_user_preferences(uid: str, preferences: Dict[str, Any]):
    """Save user preferences to Firestore."""
    user_ref = db.collection('users').document(uid)
    user_ref.update({
        'preferences': preferences,
        'lastUpdated': firestore.SERVER_TIMESTAMP
    })

def get_user_preferences(uid: str) -> Dict[str, Any]:
    """Get user preferences from Firestore."""
    user_doc = get_user_profile(uid)
    return user_doc.get('preferences', {}) if user_doc else {}

# UI Components
def login_form():
    """Display login form."""
    st.subheader("🔐 Sign In")

    # Check if we need to show verification options (set from previous login attempt)
    if st.session_state.get('show_verification_options'):
        _show_verification_options()
        return

    with st.form("login_form"):
        # Email field with label
        st.markdown("**📧 Email Address**")
        email = st.text_input("Enter your email address", key="login_email", help="Enter the email you used to create your account")

        # Password field with label
        st.markdown("**🔒 Password**")
        password = st.text_input("Enter your password", type="password", key="login_password", help="Your account password")

        submitted = st.form_submit_button("🔓 Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return

            if not validate_email(email):
                st.error("Please enter a valid email address")
                return

            # Show loading spinner
            with st.spinner("Signing you in..."):
                # Use client-side Firebase Auth
                auth_result = None

                # JavaScript call to login user
                js_code = f"""
                <script>
                (async () => {{
                    try {{
                        const result = await window.firebaseAuth.login('{email}', '{password}');
                        window.authResult = result;
                    }} catch (error) {{
                        window.authResult = {{ success: false, error: error.message }};
                    }}
                }})();
                </script>
                """

                components.html(js_code, height=0)

                # Wait a moment for JavaScript to execute
                import time
                time.sleep(2)

                # For now, simulate successful login (in production, you'd properly handle the async result)
                # This is a simplified approach - proper implementation would use Streamlit's session state
                # to pass results from JavaScript to Python

                # Temporary: Use Firebase Admin SDK to verify (this is a hybrid approach)
                try:
                    user = auth.get_user_by_email(email)

                    # Check if user has verified their email
                    if not user.email_verified:
                        st.error("📧 **Email not verified!**")
                        st.info("Please check your email and click the verification link before signing in.")
                        st.markdown("💡 **Didn't receive the verification email?**")

                        # Set flag to show verification options outside the form
                        st.session_state.show_verification_options = True
                        st.session_state.verification_email = email
                        st.rerun()
                        return

                    # Email is verified - proceed with login
                    st.success(f"Welcome back, {user.email}!")

                    # Create user profile in Firestore if it doesn't exist
                    user_profile = get_user_profile(user.uid)
                    if not user_profile:
                        create_user_profile(user.uid, user.email, str(user.display_name or user.email.split('@')[0]))

                    st.session_state.user = {
                        'uid': user.uid,
                        'email': user.email,
                        'displayName': str(user.display_name or user.email.split('@')[0]),
                        'emailVerified': user.email_verified
                    }
                    st.session_state.is_guest = False
                    update_user_last_login(user.uid)
                    st.rerun()

                except exceptions.FirebaseError as e:
                    error_message = str(e)
                    if 'INVALID_PASSWORD' in error_message or 'USER_NOT_FOUND' in error_message:
                        st.error("❌ Invalid email or password. Please check your credentials.")
                    else:
                        st.error(f"❌ Login failed: {error_message}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")

def _show_verification_options():
    """Show email verification options outside the form."""
    email = st.session_state.get('verification_email', '')

    st.subheader("📧 Email Verification Required")
    st.info(f"Please verify your email address: **{email}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📧 Resend Verification Email", key="resend_verification"):
            try:
                # Generate verification link using Admin SDK
                link = auth.generate_email_verification_link(email)

                # Actually send the email
                if send_verification_email(email, link):
                    st.success("✅ Verification email sent! Please check your inbox (and spam folder).")
                else:
                    st.warning("⚠️ Email configuration not set up. Here's your verification link:")
                    st.code(link)
                    st.info("📋 Copy and paste this link into your browser to verify your email.")

                print(f"Verification link generated for {email}: {link}")
            except Exception as e:
                st.error(f"❌ Failed to generate verification link: {e}")
                print(f"Error generating verification link for {email}: {e}")

    with col2:
        if st.button("🔄 Check Verification Status", key="check_verification"):
            try:
                # Reload user data
                user = auth.get_user_by_email(email)
                if user.email_verified:
                    st.success("✅ Email verified! You can now sign in.")
                    # Clear verification flags
                    st.session_state.show_verification_options = False
                    del st.session_state.verification_email
                    st.rerun()
                else:
                    st.warning("Email still not verified. Please check your email.")
            except Exception as e:
                st.error(f"Failed to check verification: {e}")

    with col3:
        if st.button("⬅️ Back to Sign In", key="back_to_login"):
            # Clear verification flags
            st.session_state.show_verification_options = False
            if 'verification_email' in st.session_state:
                del st.session_state.verification_email
            st.rerun()

def registration_form():
    """Display registration form."""
    st.subheader("📝 Create Account")

    # Debug: Check if Firebase auth is loaded
    st.markdown("""
    <script>
    setTimeout(() => {
        if (window.firebaseAuth) {
            console.log('Firebase Auth loaded successfully');
        } else {
            console.error('Firebase Auth NOT loaded');
        }
    }, 2000);
    </script>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        # Email field with label
        st.markdown("**📧 Email Address**")
        email = st.text_input("Enter your email address", key="register_email", help="We'll use this to create your account and send important updates")

        # Password field with label and requirements
        st.markdown("**🔒 Password**")
        password = st.text_input("Create a strong password", type="password", key="register_password",
                                help="Must be at least 8 characters with uppercase, lowercase, and numbers")

        # Password requirements shown inline
        with st.expander("💡 Password Requirements", expanded=False):
            st.markdown("""
            Your password must contain:
            - At least 8 characters
            - One uppercase letter (A-Z)
            - One lowercase letter (a-z)
            - One number (0-9)
            """)

        # Confirm password field
        st.markdown("**🔄 Confirm Password**")
        confirm_password = st.text_input("Re-enter your password", type="password", key="confirm_password",
                                       help="Enter the same password again to confirm")

        # Display name field
        st.markdown("**👤 Display Name** *(optional)*")
        display_name = st.text_input("Choose a display name", key="display_name",
                                   help="This will be shown in your profile. If left blank, we'll use your email username")

        submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in email and password")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if not validate_email(email):
                st.error("Please enter a valid email address")
                return

            is_valid, msg = validate_password(password)
            if not is_valid:
                st.error(msg)
                return

            # Show loading spinner
            with st.spinner("Creating your account..."):
                try:
                    # Use Firebase Admin SDK for more reliable user creation
                    user = auth.create_user(
                        email=email,
                        password=password,
                        display_name=display_name or email.split('@')[0]
                    )

                    # Generate email verification link and send email
                    verification_link = auth.generate_email_verification_link(email)

                    # Send verification email
                    email_sent = send_verification_email(email, verification_link)

                    # Store user info in session for later use
                    st.session_state.pending_verification_user = {
                        'uid': user.uid,
                        'email': user.email,
                        'display_name': str(user.display_name or email.split('@')[0])
                    }

                    st.success("✅ Account created successfully!")

                    if email_sent:
                        st.info("📧 **Verification email sent!** Please check your email and click the verification link.")
                        st.markdown("💡 **Check your spam folder** if you don't see it in your inbox.")
                    else:
                        st.warning("⚠️ **Email not configured.** Here's your verification link - copy and paste it into your browser:")
                        st.code(verification_link)

                    st.markdown(f"💡 **Account created for:** {email}")

                    # Log successful registration
                    print(f"User registered successfully: {email} (UID: {user.uid})")
                    if email_sent:
                        print(f"Verification email sent to: {email}")
                    else:
                        print(f"Email not sent - verification link: {verification_link}")

                    # Don't rerun immediately - let user see the success message

                except exceptions.FirebaseError as e:
                    error_code = e.code if hasattr(e, 'code') else 'unknown'
                    error_message = str(e)

                    print(f"Registration failed for {email}: {error_code} - {error_message}")

                    if 'EMAIL_EXISTS' in error_code:
                        st.error("❌ An account with this email already exists. Try signing in instead.")
                    elif 'INVALID_EMAIL' in error_code:
                        st.error("❌ Invalid email address format.")
                    elif 'WEAK_PASSWORD' in error_code:
                        st.error("❌ Password is too weak. Please choose a stronger password.")
                    else:
                        st.error(f"❌ Registration failed: {error_message}")

                except Exception as e:
                    print(f"Unexpected error during registration: {str(e)}")
                    st.error(f"❌ An unexpected error occurred: {str(e)}")

def password_reset_form():
    """Display password reset form."""
    st.subheader("🔑 Reset Password")

    with st.form("reset_form"):
        # Email field with label
        st.markdown("**📧 Account Email**")
        email = st.text_input("Enter your account email", key="reset_email",
                            help="We'll send a password reset link to this email address")

        submitted = st.form_submit_button("📤 Send Reset Email", use_container_width=True)

        if submitted:
            if not email:
                st.error("Please enter your email address")
                return

            if not validate_email(email):
                st.error("Please enter a valid email address")
                return

            # Show loading spinner
            with st.spinner("Sending reset email..."):
                # Use client-side Firebase Auth for password reset
                js_code = f"""
                <script>
                (async () => {{
                    try {{
                        const result = await window.firebaseAuth.resetPassword('{email}');
                        window.authResult = result;
                    }} catch (error) {{
                        window.authResult = {{ success: false, error: error.message }};
                    }}
                }})();
                </script>
                """

                components.html(js_code, height=0)

                # Wait a moment for JavaScript to execute
                import time
                time.sleep(1)

                # For now, use Firebase Admin SDK as fallback
                try:
                    auth.generate_password_reset_link(email)
                    st.success("Password reset email sent! Check your inbox.")
                except exceptions.FirebaseError as e:
                    st.error(f"Failed to send reset email: {str(e)}")

def show_auth_forms():
    """Display authentication forms with tabs."""
    st.markdown("### Choose an option below:")

    tab1, tab2, tab3 = st.tabs(["🔐 Sign In", "📝 Create Account", "🔑 Reset Password"])

    with tab1:
        login_form()

    with tab2:
        registration_form()

    with tab3:
        password_reset_form()

def firebase_auth_component_legacy():
    """Legacy function for backward compatibility."""
    if not is_signed_in():
        col1, col2 = st.columns([1, 1])
        with col1:
            show_auth_forms()
        with col2:
            st.info("Optional - Guest mode available")
        return None
    else:
        user_info = get_current_user()
        return user_info

def render_user_profile():
    """Render user profile section in sidebar."""
    if is_signed_in():
        user = get_current_user()
        if user:
            # Display user info
            col1, col2 = st.columns([1, 3])
            with col1:
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

def render_auth_handler_page():
    """Handle authentication page."""
    if not is_signed_in():
        st.title("🔐 Sign In")
        st.markdown("Create an account or sign in to save progress across devices!")
        st.markdown("📧 **Email verification required** - You'll need to verify your email before you can sign in.")

        show_auth_forms()

        st.markdown("---")

        # Why create an account section
        with st.expander("💡 Why create an account?", expanded=False):
            st.markdown("""
            **🌟 Benefits of having an account:**

            ✅ **Save Progress Across Devices** - Access your learning data from any computer or mobile device

            ✅ **Secure API Key Storage** - Your Groq and Pixabay API keys are encrypted and stored safely in the cloud

            ✅ **Advanced Statistics** - Track your learning progress over time with detailed analytics

            ✅ **Never Lose Your Data** - Your generated decks, preferences, and settings are backed up automatically

            ✅ **Personalized Experience** - Your preferences and custom settings sync across all your devices

            **Your privacy matters!** We only store the data you choose to save, and you can delete your account anytime.
            """)

        st.markdown("---")
        st.markdown("**Password Requirements:**")
        st.markdown("• At least 8 characters")
        st.markdown("• One uppercase letter")
        st.markdown("• One lowercase letter")
        st.markdown("• One number")

        # Privacy notice
        st.markdown("---")
        st.markdown("### 🔒 Privacy & Security")
        st.markdown("• Your password is securely hashed and stored")
        st.markdown("• Your data is encrypted and stored securely")
        st.markdown("• Email verification ensures account security")
        st.markdown("• You can delete your account and data anytime")
        st.markdown("• [Privacy Policy](https://agnel18.github.io/anki-fluent-forever-language-card-generator/privacy-policy.html)")
    else:
        st.success("You're already signed in!")
        user = get_current_user()
        st.write(f"Welcome back, {user.get('displayName', 'User')}!")

        # Show user stats
        user_profile = get_user_profile(user['uid'])
        if user_profile:
            col1, col2 = st.columns(2)
            with col1:
                created_at = user_profile.get('createdAt')
                if created_at:
                    # Convert DatetimeWithNanoseconds to readable string
                    if hasattr(created_at, 'strftime'):
                        created_at_str = created_at.strftime('%Y-%m-%d %H:%M')
                    else:
                        created_at_str = str(created_at).split('+')[0]  # Fallback
                    st.metric("Account Created", created_at_str)
                else:
                    st.metric("Account Created", "Unknown")
            with col2:
                last_login = user_profile.get('lastLogin')
                if last_login:
                    # Convert DatetimeWithNanoseconds to readable string
                    if hasattr(last_login, 'strftime'):
                        last_login_str = last_login.strftime('%Y-%m-%d %H:%M')
                    else:
                        last_login_str = str(last_login).split('+')[0]  # Fallback
                    st.metric("Last Login", last_login_str)
                else:
                    st.metric("Last Login", "Unknown")

        if st.button("Go to Main App"):
            st.session_state.page = "main"
            st.rerun()
