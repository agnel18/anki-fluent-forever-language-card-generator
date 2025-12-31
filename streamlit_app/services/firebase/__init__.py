"""
Firebase Services Package

This package contains all Firebase-related services for the language learning application.
Services are organized by responsibility for better maintainability and testing.
"""

from .firebase_init import (
    init_firebase,
    is_firebase_initialized,
    is_firebase_available,
    get_firestore_client,
    get_auth_client
)

from .settings_service import (
    save_settings_to_firebase,
    load_settings_from_firebase,
    save_settings_to_session,
    load_settings_from_session
)

from .progress_service import (
    save_progress_to_firebase,
    load_progress_from_firebase,
    sync_progress_to_firebase,
    sync_progress_from_firebase,
    get_progress_languages
)

from .stats_service import (
    save_usage_stats_to_firebase,
    load_usage_stats_from_firebase,
    merge_guest_stats_to_firebase,
    get_usage_stats,
    increment_stat
)

from .session_service import (
    create_user_session,
    update_last_active,
    get_session_info,
    is_session_active,
    deactivate_session,
    get_active_sessions
)

from .firebase_auth_service import (
    sign_in_with_google,
    sign_out,
    is_signed_in,
    get_current_user,
    set_user_session,
    clear_user_session
)

from .migration_service import (
    migrate_guest_data_to_user,
    is_data_migrated
)

__all__ = [
    # Firebase Init
    'init_firebase',
    'is_firebase_initialized',
    'is_firebase_available',
    'get_firestore_client',
    'get_auth_client',

    # Settings Service
    'save_settings_to_firebase',
    'load_settings_from_firebase',
    'save_settings_to_session',
    'load_settings_from_session',

    # Progress Service
    'save_progress_to_firebase',
    'load_progress_from_firebase',
    'sync_progress_to_firebase',
    'sync_progress_from_firebase',
    'get_progress_languages',

    # Stats Service
    'save_usage_stats_to_firebase',
    'load_usage_stats_from_firebase',
    'merge_guest_stats_to_firebase',
    'get_usage_stats',
    'increment_stat',

    # Session Service
    'create_user_session',
    'update_last_active',
    'get_session_info',
    'is_session_active',
    'deactivate_session',
    'get_active_sessions',

    # Firebase Auth Service
    'sign_in_with_google',
    'sign_out',
    'is_signed_in',
    'get_current_user',
    'set_user_session',
    'clear_user_session',

    # Migration Service
    'migrate_guest_data_to_user',
    'is_data_migrated'
]