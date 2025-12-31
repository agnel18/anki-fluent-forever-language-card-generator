"""
Preferences Manager Service
Handles language preferences, favorite languages, and per-language settings.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple


class PreferencesManager:
    """Manages user preferences including language settings and favorites."""

    def __init__(self):
        """Initialize the preferences manager."""
        pass

    def get_favorite_languages(self) -> List[Dict[str, Any]]:
        """
        Get the current favorite languages from session state.

        Returns:
            List of favorite language dictionaries
        """
        return st.session_state.get("learned_languages", [])

    def update_favorite_languages(self, selected_languages: List[str]) -> None:
        """
        Update favorite languages in session state.

        Args:
            selected_languages: List of selected language names
        """
        current_favorites = self.get_favorite_languages()
        current_names = [lang["name"] for lang in current_favorites]

        if selected_languages != current_names:
            # Convert selected names back to language objects with usage data
            updated_favorites = []
            for lang_name in selected_languages:
                # Find existing language data or create new entry
                existing = next((lang for lang in current_favorites if lang["name"] == lang_name), None)
                if existing:
                    updated_favorites.append(existing)
                else:
                    updated_favorites.append({"name": lang_name, "usage": 0})

            st.session_state.learned_languages = updated_favorites

    def get_per_language_settings(self, language: str) -> Dict[str, Any]:
        """
        Get settings for a specific language.

        Args:
            language: Language name

        Returns:
            Dictionary of language-specific settings
        """
        per_language_settings = st.session_state.get("per_language_settings", {})
        return per_language_settings.get(language, self._get_default_language_settings())

    def save_per_language_settings(self, language: str, settings: Dict[str, Any]) -> None:
        """
        Save settings for a specific language.

        Args:
            language: Language name
            settings: Settings dictionary to save
        """
        if "per_language_settings" not in st.session_state:
            st.session_state.per_language_settings = {}

        st.session_state.per_language_settings[language] = settings.copy()

    def get_theme(self) -> str:
        """
        Get the current theme setting.

        Returns:
            Theme name ('light' or 'dark')
        """
        return st.session_state.get("theme", "dark")

    def set_theme(self, theme: str) -> None:
        """
        Set the theme in session state.

        Args:
            theme: Theme name ('light' or 'dark')
        """
        st.session_state.theme = theme.lower()

    def get_sync_preferences(self) -> List[str]:
        """
        Get the current sync preferences.

        Returns:
            List of data types to sync
        """
        return st.session_state.get("sync_preferences",
                                   ["API Keys", "Theme Settings", "Audio Preferences"])

    def set_sync_preferences(self, preferences: List[str]) -> None:
        """
        Set sync preferences in session state.

        Args:
            preferences: List of data types to sync
        """
        st.session_state.sync_preferences = preferences

    def get_all_languages(self) -> List[Dict[str, str]]:
        """
        Get all available languages.

        Returns:
            List of language dictionaries with 'name' key
        """
        return st.session_state.get("all_languages", [])

    def get_language_names(self) -> List[str]:
        """
        Get list of all language names.

        Returns:
            List of language names
        """
        all_languages = self.get_all_languages()
        return [lang["name"] for lang in all_languages]

    def _get_default_language_settings(self) -> Dict[str, Any]:
        """
        Get default settings for a language.

        Returns:
            Default language settings dictionary
        """
        return {
            "difficulty": "intermediate",
            "sentence_length_range": (6, 16),
            "sentences_per_word": 10,
            "audio_speed": 0.8,
            "enable_topics": False,
            "selected_topics": [],
            "custom_topics": []
        }

    def validate_topic_selection(self, selected_topics: List[str], custom_topics: List[str]) -> Tuple[bool, str]:
        """
        Validate topic selection against limits.

        Args:
            selected_topics: Currently selected topics
            custom_topics: Custom topics list

        Returns:
            Tuple of (is_valid, error_message)
        """
        TOPIC_LIMIT = 5
        if len(selected_topics) > TOPIC_LIMIT:
            return False, f"Maximum of {TOPIC_LIMIT} topics allowed."

        return True, ""

    def add_custom_topic(self, topic: str, language: str) -> Tuple[bool, str]:
        """
        Add a custom topic for a language.

        Args:
            topic: Topic name to add
            language: Language name

        Returns:
            Tuple of (success, message)
        """
        from constants import CURATED_TOPICS

        clean_topic = topic.strip()

        if len(clean_topic) < 2:
            return False, "Topic must be at least 2 characters long."

        settings = self.get_per_language_settings(language)

        if clean_topic in settings["selected_topics"]:
            return False, "This topic is already selected."

        if clean_topic in CURATED_TOPICS:
            return False, "This topic already exists in the curated list."

        if "custom_topics" not in settings:
            settings["custom_topics"] = []

        settings["custom_topics"].append(clean_topic)
        settings["selected_topics"].append(clean_topic)

        self.save_per_language_settings(language, settings)
        return True, f"Added topic: {clean_topic}"

    def remove_custom_topic(self, topic: str, language: str) -> None:
        """
        Remove a custom topic from a language.

        Args:
            topic: Topic name to remove
            language: Language name
        """
        settings = self.get_per_language_settings(language)

        if topic in settings["selected_topics"]:
            settings["selected_topics"].remove(topic)

        if topic in settings["custom_topics"]:
            settings["custom_topics"].remove(topic)

        self.save_per_language_settings(language, settings)

    def get_curated_topics(self) -> List[str]:
        """
        Get the list of curated topics.

        Returns:
            List of curated topic names
        """
        from constants import CURATED_TOPICS
        return CURATED_TOPICS

    def get_difficulty_options(self) -> Dict[str, str]:
        """
        Get difficulty level options with descriptions.

        Returns:
            Dictionary mapping difficulty levels to descriptions
        """
        return {
            "beginner": "Beginner - Simple vocabulary and basic sentence structures",
            "intermediate": "Intermediate - Moderate vocabulary with varied sentence patterns",
            "advanced": "Advanced - Complex vocabulary and sophisticated sentence structures"
        }