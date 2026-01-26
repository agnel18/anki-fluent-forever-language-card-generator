# sync_manager.py - Data synchronization between local and cloud storage

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# DATA SYNCHRONIZATION
# ============================================================================

def sync_user_data() -> bool:
    """Sync data between local and cloud.
    
    Returns:
        True if sync successful, False otherwise
    """
    from firebase_manager import is_signed_in, save_settings_to_firebase
    
    if not is_signed_in():
        logger.debug("User not signed in, skipping sync")
        return False
    
    try:
        # Get user's sync preferences
        sync_prefs = st.session_state.get('sync_preferences', ["API Keys", "Theme Settings", "Audio Preferences"])
        
        # Collect data to sync based on preferences
        sync_data = {
            'last_sync': datetime.now().isoformat()
        }
        
        if "API Keys" in sync_prefs:
            sync_data.update({
                'google_api_key': st.session_state.get('google_api_key', ''),
            })
            
        if "Theme Settings" in sync_prefs:
            sync_data['theme'] = st.session_state.get('theme', 'dark')
            
        if "Audio Preferences" in sync_prefs:
            sync_data['audio_speed'] = st.session_state.get('audio_speed', 0.8)
            
        if "Usage Statistics" in sync_prefs:
            sync_data['usage_stats'] = st.session_state.get('persistent_usage_stats', {})
        
        # Save to Firebase
        success = save_settings_to_firebase(st.session_state.session_id, sync_data)
        
        if success:
            st.session_state.last_sync_time = datetime.now()
            logger.info("✅ Data synced to cloud successfully")
            return True
        else:
            logger.error("❌ Failed to sync data to cloud")
            return False
            
    except Exception as e:
        logger.error(f"❌ Sync error: {e}")
        handle_sync_error(e)
        return False


def load_cloud_data() -> bool:
    """Load data from cloud on sign in.
    
    Returns:
        True if data loaded successfully, False otherwise
    """
    from firebase_manager import is_signed_in, load_settings_from_firebase
    
    if not is_signed_in():
        logger.debug("User not signed in, skipping cloud load")
        return False
    
    try:
        cloud_data = load_settings_from_firebase(st.session_state.session_id)
        
        if cloud_data:
            # Merge with local data (cloud takes precedence for conflicts)
            resolved_data = resolve_data_conflicts(
                local_data={
                    'google_api_key': st.session_state.get('google_api_key', ''),
                    'theme': st.session_state.get('theme', 'dark'),
                    'audio_speed': st.session_state.get('audio_speed', 0.8),
                },
                cloud_data=cloud_data
            )
            
            # Apply resolved data
            for key, value in resolved_data.items():
                if value:  # Only update if there's a value
                    st.session_state[key] = value
                    
            logger.info("✅ Cloud data loaded and merged successfully")
            return True
        else:
            logger.info("ℹ️ No cloud data found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error loading cloud data: {e}")
        st.session_state.sync_errors.append(str(e))
        return False


def resolve_data_conflicts(local_data: Dict, cloud_data: Dict) -> Dict:
    """Resolve conflicts between local and cloud data.
    
    Args:
        local_data: Current local session data
        cloud_data: Data from Firebase
        
    Returns:
        Resolved data dictionary
    """
    resolved = {}
    
    # Define conflict resolution rules
    conflict_rules = {
        'google_api_key': 'cloud',  # Cloud wins for API keys
        'theme': 'local',  # Local preference for UI settings
        'audio_speed': 'local',  # Local preference for UI settings
    }
    
    for key in set(local_data.keys()) | set(cloud_data.keys()):
        local_val = local_data.get(key)
        cloud_val = cloud_data.get(key)
        
        if local_val and cloud_val and local_val != cloud_val:
            # Conflict exists, apply rule
            rule = conflict_rules.get(key, 'local')  # Default to local
            if rule == 'cloud':
                resolved[key] = cloud_val
                logger.debug(f"Resolved {key} conflict: chose cloud value")
            else:
                resolved[key] = local_val
                logger.debug(f"Resolved {key} conflict: chose local value")
        else:
            # No conflict, use whichever value exists
            resolved[key] = local_val or cloud_val
            
    return resolved


def export_user_data() -> Optional[Dict]:
    """Export all user data for download.
    
    Returns:
        Dictionary of user data, or None if error
    """
    try:
        return {
            'google_api_key': st.session_state.get('google_api_key', ''),
            'theme': st.session_state.get('theme', 'dark'),
            'audio_speed': st.session_state.get('audio_speed', 0.8),
            'exported_at': datetime.now().isoformat(),
            'session_id': st.session_state.get('session_id', ''),
        }
    except Exception as e:
        logger.error(f"❌ Error exporting data: {e}")
        return None


def delete_user_data() -> bool:
    """Delete all user data from cloud.
    
    Returns:
        True if successful, False otherwise
    """
    # This will be implemented when we add delete functionality to firebase_manager
    logger.warning("⚠️ Cloud data deletion not yet implemented")
    return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_online() -> bool:
    """Check if user is online."""
    try:
        import urllib.request
        urllib.request.urlopen('http://www.google.com', timeout=1)
        return True
    except:
        return False


def handle_sync_error(error: Exception) -> None:
    """Handle sync errors gracefully."""
    error_msg = str(error)
    st.session_state.sync_errors.append(error_msg)
    
    # Show user-friendly message based on error type
    if "network" in error_msg.lower() or "connection" in error_msg.lower():
        st.warning("⚠️ Sync failed due to network issues. Will retry automatically.")
    elif "auth" in error_msg.lower() or "permission" in error_msg.lower():
        st.error("🔐 Authentication expired. Please sign in again.")
        from firebase_manager import sign_out
        sign_out()
    elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
        st.warning("⚠️ Cloud storage quota exceeded. Some data may not be synced.")
    else:
        st.error(f"☁️ Sync error: {error_msg}")
        
    logger.error(f"Sync error handled: {error_msg}")


def safe_sync() -> bool:
    """Only sync if online and signed in."""
    if is_online() and st.session_state.get('user'):
        return sync_user_data()
    return False