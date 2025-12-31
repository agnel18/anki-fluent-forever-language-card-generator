# services/generation/session_validator.py
"""
Session Validator Service for Generation Operations
Handles session state validation, initialization, and error recovery for deck generation.
"""

import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional
import datetime


class SessionValidator:
    """
    Manages session state validation and initialization for generation operations.
    Ensures all required data is present before allowing generation to proceed.
    """

    def __init__(self):
        """Initialize the session validator."""
        self.required_vars = [
            'selected_lang', 'selected_words', 'sentences_per_word',
            'sentence_length_range', 'difficulty', 'audio_speed', 'selected_voice'
        ]

    def validate_session_state(self) -> bool:
        """
        Validate that all required session state variables exist.

        Returns:
            bool: True if validation passes, False otherwise

        Raises:
            SystemExit: If validation fails (handled internally with UI)
        """
        try:
            # Ensure st.session_state is a dict-like object
            if not hasattr(st.session_state, 'get'):
                st.error("❌ **Session state corrupted!** Please restart the application.")
                return False

            missing_vars = []
            for var in self.required_vars:
                try:
                    if var not in st.session_state:
                        missing_vars.append(var)
                except (TypeError, AttributeError) as e:
                    st.error(f"❌ **Session state access error for {var}:** {str(e)}")
                    return False

            if missing_vars:
                self._display_missing_vars_error(missing_vars)
                return False

            return True

        except Exception as e:
            st.error(f"❌ **Critical session state error:** {str(e)}")
            st.error("Please restart the application and complete the setup process.")
            return False

    def _display_missing_vars_error(self, missing_vars: List[str]) -> None:
        """Display error UI for missing session variables."""
        st.error("❌ **Missing required data!** Please complete the setup process first.")
        st.markdown(f"**Missing:** {', '.join(missing_vars)}")
        st.markdown("**Required:** Language selection, word selection, and sentence settings must be completed first.")
        if st.button("← Go Back to Setup", type="primary"):
            st.switch_page("pages/language_select.py")

    def initialize_generation_progress(self) -> None:
        """Initialize generation progress tracking in session state."""
        if 'generation_progress' not in st.session_state:
            st.session_state['generation_progress'] = {
                'step': 0,  # 0: not started, 1: generating, 2: complete
                'result': None,
                'success': False,
                'error': None,
                'errors': [],
                'error_summary': '',
                'tsv_path': None,
                'media_dir': None,
                'output_dir': None,
                'apkg_ready': False,
                'apkg_path': None,
                'partial_success': False
            }

    def initialize_logging(self) -> None:
        """Initialize logging infrastructure in session state."""
        if 'generation_log' not in st.session_state:
            st.session_state['generation_log'] = []
            st.session_state['generation_log_active'] = True

            # Create logs directory if it doesn't exist
            logs_dir = Path("./logs")
            logs_dir.mkdir(exist_ok=True)

            # Create persistent log file with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"generation_{timestamp}.log"
            log_filepath = logs_dir / log_filename

            st.session_state['log_file_path'] = str(log_filepath)
            st.session_state['log_filename'] = log_filename  # Store filename for display
            st.session_state['log_stream'] = open(log_filepath, "w+", encoding="utf-8")

    def get_generation_settings(self) -> Dict[str, Any]:
        """
        Extract generation settings from session state.

        Returns:
            Dict containing generation settings
        """
        return {
            'selected_lang': st.session_state.selected_lang,
            'selected_words': st.session_state.selected_words,
            'num_sentences': st.session_state.sentences_per_word,
            'min_length': st.session_state.sentence_length_range[0],
            'max_length': st.session_state.sentence_length_range[1],
            'difficulty': st.session_state.difficulty,
            'audio_speed': st.session_state.audio_speed,
            'voice': st.session_state.selected_voice,
            'enable_topics': st.session_state.get("enable_topics", False),
            'selected_topics': st.session_state.get("selected_topics", [])
        }

    def get_generation_step(self) -> int:
        """
        Get current generation step from session state.

        Returns:
            int: Current step (0: not started, 1: generating, 2: complete)
        """
        return st.session_state['generation_progress']['step']

    def update_generation_step(self, step: int) -> None:
        """
        Update the generation step in session state.

        Args:
            step: New step value
        """
        st.session_state['generation_progress']['step'] = step

    def get_generation_progress(self) -> Dict[str, Any]:
        """
        Get the complete generation progress data.

        Returns:
            Dict containing all progress information
        """
        return st.session_state['generation_progress']

    def update_generation_progress(self, updates: Dict[str, Any]) -> None:
        """
        Update generation progress with new data.

        Args:
            updates: Dict of fields to update
        """
        st.session_state['generation_progress'].update(updates)