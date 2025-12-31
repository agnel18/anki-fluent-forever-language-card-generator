"""
Auth Service - Core authentication logic and user management
"""

import firebase_admin
from firebase_admin import auth, firestore, exceptions
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import re
from .email_service import EmailService
from .session_manager import SessionManager


class AuthService:
    """
    Service for handling authentication operations and user management.
    """

    def __init__(self, email_service: EmailService, session_manager: SessionManager):
        """
        Initialize auth service with dependencies.

        Args:
            email_service: Email service for sending verification emails
            session_manager: Session manager for handling session state
        """
        self.email_service = email_service
        self.session_manager = session_manager
        self._db = None
        self._firebase_initialized = False

    def _ensure_firebase_initialized(self):
        """Ensure Firebase Admin is initialized. Called lazily."""
        if self._firebase_initialized:
            return

        try:
            firebase_admin.get_app()
            self._firebase_initialized = True
        except ValueError:
            # Initialize with your Firebase config
            cred = firebase_admin.credentials.Certificate({
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
            firebase_admin.initialize_app(cred)
            self._firebase_initialized = True

    @property
    def db(self):
        """Get Firestore client, initializing Firebase if needed."""
        if self._db is None:
            self._ensure_firebase_initialized()
            self._db = firestore.client()
        return self._db

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if email format is valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"

    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            Tuple of (success, message, user_data)
        """
        try:
            user = auth.get_user_by_email(email)

            # Check if user has verified their email
            if not user.email_verified:
                return False, "Please verify your email address before signing in. Check your inbox for the verification link.", None

            # Email is verified - proceed with login
            user_data = {
                'uid': user.uid,
                'email': user.email,
                'displayName': str(user.display_name or user.email.split('@')[0]),
                'emailVerified': user.email_verified
            }

            # Create user profile in Firestore if it doesn't exist
            user_profile = self.get_user_profile(user.uid)
            if not user_profile:
                self.create_user_profile(user.uid, user.email, str(user.display_name or user.email.split('@')[0]))

            self.session_manager.set_user(user_data)
            self.update_user_last_login(user.uid)

            return True, f"Welcome back, {user.email}!", user_data

        except exceptions.FirebaseError as e:
            error_message = str(e)
            if 'INVALID_PASSWORD' in error_message or 'USER_NOT_FOUND' in error_message:
                return False, "Invalid email or password. Please check your credentials.", None
            else:
                return False, f"Login failed: {error_message}", None
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}", None

    def register_user(self, email: str, password: str, display_name: str = None) -> Tuple[bool, str]:
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            display_name: Optional display name

        Returns:
            Tuple of (success, message)
        """
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
            email_sent = self.email_service.send_verification_email(email, verification_link)

            # Store user info in session for later use
            pending_user_data = {
                'uid': user.uid,
                'email': user.email,
                'display_name': str(user.display_name or email.split('@')[0])
            }
            self.session_manager.set_pending_verification_user(pending_user_data)

            success_message = "Account created successfully!"
            if email_sent:
                success_message += " Verification email sent! Please check your email and click the verification link."
            else:
                success_message += " Email not configured. Here's your verification link - copy and paste it into your browser:"
                success_message += f"\n{verification_link}"

            # Log successful registration
            print(f"User registered successfully: {email} (UID: {user.uid})")
            if email_sent:
                print(f"Verification email sent to: {email}")
            else:
                print(f"Email not sent - verification link: {verification_link}")

            return True, success_message

        except exceptions.FirebaseError as e:
            error_code = e.code if hasattr(e, 'code') else 'unknown'
            error_message = str(e)

            print(f"Registration failed for {email}: {error_code} - {error_message}")

            if 'EMAIL_EXISTS' in error_code:
                return False, "An account with this email already exists. Try signing in instead."
            elif 'INVALID_EMAIL' in error_code:
                return False, "Invalid email address format."
            elif 'WEAK_PASSWORD' in error_code:
                return False, "Password is too weak. Please choose a stronger password."
            else:
                return False, f"Registration failed: {error_message}"

        except Exception as e:
            print(f"Unexpected error during registration: {str(e)}")
            return False, f"An unexpected error occurred: {str(e)}"

    def send_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Send password reset email.

        Args:
            email: Email address for password reset

        Returns:
            Tuple of (success, message)
        """
        try:
            auth.generate_password_reset_link(email)
            return True, "Password reset email sent! Check your inbox."
        except exceptions.FirebaseError as e:
            return False, f"Failed to send reset email: {str(e)}"

    def resend_verification_email(self, email: str) -> Tuple[bool, str]:
        """
        Resend verification email.

        Args:
            email: Email address to resend verification to

        Returns:
            Tuple of (success, message)
        """
        try:
            # Generate verification link using Admin SDK
            link = auth.generate_email_verification_link(email)

            # Actually send the email
            if self.email_service.send_verification_email(email, link):
                return True, "Verification email sent! Please check your inbox (and spam folder)."
            else:
                return False, f"Email configuration not set up. Here's your verification link: {link}"

        except Exception as e:
            return False, f"Failed to generate verification link: {e}"

    def check_email_verification_status(self, email: str) -> Tuple[bool, str]:
        """
        Check if email is verified.

        Args:
            email: Email address to check

        Returns:
            Tuple of (is_verified, message)
        """
        try:
            # Reload user data
            user = auth.get_user_by_email(email)
            if user.email_verified:
                return True, "Email verified! You can now sign in."
            else:
                return False, "Email still not verified. Please check your email."
        except Exception as e:
            return False, f"Failed to check verification: {e}"

    # User Profile Management Methods

    def create_user_profile(self, uid: str, email: str, display_name: str = None):
        """
        Create user profile in Firestore.

        Args:
            uid: User ID
            email: User email
            display_name: Optional display name
        """
        user_ref = self.db.collection('users').document(uid)
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

        # Initialize achievements for new user
        try:
            from achievements_manager import initialize_achievements
            initialize_achievements(uid)
        except Exception as e:
            print(f"Warning: Could not initialize achievements for user {uid}: {e}")

    def update_user_last_login(self, uid: str):
        """
        Update user's last login timestamp.

        Args:
            uid: User ID
        """
        user_ref = self.db.collection('users').document(uid)
        user_ref.update({'lastLogin': firestore.SERVER_TIMESTAMP})

    def get_user_profile(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firestore.

        Args:
            uid: User ID

        Returns:
            User profile data or None
        """
        user_ref = self.db.collection('users').document(uid)
        doc = user_ref.get()
        return doc.to_dict() if doc.exists else None

    def save_user_api_keys(self, uid: str, api_keys: Dict[str, str]):
        """
        Save encrypted API keys to Firestore.

        Args:
            uid: User ID
            api_keys: API keys dictionary
        """
        api_keys_ref = self.db.collection('users').document(uid).collection('api_keys').document('keys')
        api_keys_ref.set({
            'groq': api_keys.get('groq', ''),
            'pixabay': api_keys.get('pixabay', ''),
            'lastUpdated': firestore.SERVER_TIMESTAMP
        })

    def get_user_api_keys(self, uid: str) -> Dict[str, str]:
        """
        Get user's API keys from Firestore.

        Args:
            uid: User ID

        Returns:
            API keys dictionary
        """
        api_keys_ref = self.db.collection('users').document(uid).collection('api_keys').document('keys')
        doc = api_keys_ref.get()
        return doc.to_dict() if doc.exists else {}

    def save_user_progress(self, uid: str, language: str, progress_data: Dict[str, Any]):
        """
        Save user progress to Firestore.

        Args:
            uid: User ID
            language: Language code
            progress_data: Progress data
        """
        progress_ref = self.db.collection('users').document(uid).collection('progress').document(language)
        progress_data['lastUpdated'] = firestore.SERVER_TIMESTAMP
        progress_ref.set(progress_data)

    def get_user_progress(self, uid: str, language: str) -> Optional[Dict[str, Any]]:
        """
        Get user progress from Firestore.

        Args:
            uid: User ID
            language: Language code

        Returns:
            Progress data or None
        """
        progress_ref = self.db.collection('users').document(uid).collection('progress').document(language)
        doc = progress_ref.get()
        return doc.to_dict() if doc.exists else None

    def save_user_preferences(self, uid: str, preferences: Dict[str, Any]):
        """
        Save user preferences to Firestore.

        Args:
            uid: User ID
            preferences: Preferences dictionary
        """
        user_ref = self.db.collection('users').document(uid)
        user_ref.update({
            'preferences': preferences,
            'lastUpdated': firestore.SERVER_TIMESTAMP
        })

    def get_user_preferences(self, uid: str) -> Dict[str, Any]:
        """
        Get user preferences from Firestore.

        Args:
            uid: User ID

        Returns:
            Preferences dictionary
        """
        user_doc = self.get_user_profile(uid)
        return user_doc.get('preferences', {}) if user_doc else {}