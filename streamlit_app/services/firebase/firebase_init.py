"""
Firebase Initialization Service

Handles Firebase Admin SDK initialization and configuration.
Provides centralized Firebase setup for the application.
"""

import logging
from typing import Optional
import streamlit as st

logger = logging.getLogger(__name__)

# Global Firebase state
firebase_initialized = False
firebase_available = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    firebase_available = True
except ImportError:
    logger.warning("Firebase SDK not installed. Install with: pip install firebase-admin")


def init_firebase() -> bool:
    """
    Initialize Firebase Admin SDK with service account credentials.

    Returns:
        True if initialization successful, False otherwise
    """
    global firebase_initialized

    if firebase_initialized:
        return True

    if not firebase_available:
        logger.warning("Firebase SDK not available")
        return False

    try:
        # Check if already initialized
        if firebase_admin._apps:
            firebase_initialized = True
            logger.info("Firebase already initialized")
            return True

        # Try to get credentials from Streamlit secrets
        try:
            firebase_config = st.secrets.get("firebase", {})
            service_account_key = firebase_config.get("service_account_key")

            if service_account_key:
                # Parse the service account key JSON
                import json
                creds_dict = json.loads(service_account_key)

                # Initialize with credentials
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                firebase_initialized = True
                logger.info("✅ Firebase initialized successfully with service account")
                return True
            else:
                logger.warning("No service account key found in secrets")

        except Exception as e:
            logger.debug(f"Could not initialize from secrets: {e}")

        # Try to initialize from local config file
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "firebase_config.json")

            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    creds_dict = json.load(f)

                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                firebase_initialized = True
                logger.info("✅ Firebase initialized successfully from config file")
                return True
            else:
                logger.warning("Firebase config file not found")

        except Exception as e:
            logger.debug(f"Could not initialize from config file: {e}")

        # If we get here, initialization failed
        logger.error("❌ Firebase initialization failed - no valid credentials found")
        return False

    except Exception as e:
        logger.error(f"❌ Firebase initialization error: {e}")
        return False


def is_firebase_initialized() -> bool:
    """Check if Firebase is initialized and available."""
    return firebase_initialized


def is_firebase_available() -> bool:
    """Check if Firebase SDK is available."""
    return firebase_available


def get_firestore_client():
    """
    Get Firestore client instance.

    Returns:
        Firestore client if initialized, None otherwise
    """
    if not firebase_initialized:
        logger.warning("Firebase not initialized, cannot get Firestore client")
        return None

    try:
        return firestore.client()
    except Exception as e:
        logger.error(f"Error getting Firestore client: {e}")
        return None


def get_auth_client():
    """
    Get Firebase Auth client instance.

    Returns:
        Auth client if initialized, None otherwise
    """
    if not firebase_initialized:
        logger.warning("Firebase not initialized, cannot get Auth client")
        return None

    try:
        return auth
    except Exception as e:
        logger.error(f"Error getting Auth client: {e}")
        return None