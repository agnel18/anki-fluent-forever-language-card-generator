# services/generation/file_manager.py
"""
File Manager Service for Generation Operations
Handles file and directory operations for deck generation, including clearing, reading, and managing output files.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st


class FileManager:
    """
    Manages file and directory operations for generation operations.
    Handles output directory clearing, file reading, and path management.
    """

    def __init__(self, log_manager: Any):
        """
        Initialize the file manager.

        Args:
            log_manager: LogManager instance for logging operations
        """
        self.log_manager = log_manager
        self.output_dir = str(Path("./output"))

    def clear_output_directories(self) -> None:
        """
        Clear output directories (media and images) at the start of generation.
        Only clears if not already cleared in this session.
        """
        if 'output_dirs_cleared' in st.session_state:
            return

        # Clear media directory
        media_dir = str(Path(self.output_dir) / "media")
        if os.path.exists(media_dir):
            try:
                shutil.rmtree(media_dir)
                self.log_manager.log_message(f"<b>🧹 Cleared existing media directory:</b> {media_dir}")
                if st.session_state.get('log_stream'):
                    st.session_state['log_stream'].write(f"[DEBUG] Cleared media directory: {media_dir}\n")
                    st.session_state['log_stream'].flush()
            except Exception as e:
                self.log_manager.log_message(f"<b>⚠️ Could not clear media directory:</b> {e}")
                if st.session_state.get('log_stream'):
                    st.session_state['log_stream'].write(f"[WARNING] Could not clear media directory {media_dir}: {e}\n")
                    st.session_state['log_stream'].flush()

        # Clear images directory
        images_dir = str(Path(self.output_dir) / "images")
        if os.path.exists(images_dir):
            try:
                shutil.rmtree(images_dir)
                self.log_manager.log_message(f"<b>🧹 Cleared existing images directory:</b> {images_dir}")
                if st.session_state.get('log_stream'):
                    st.session_state['log_stream'].write(f"[DEBUG] Cleared images directory: {images_dir}\n")
                    st.session_state['log_stream'].flush()
            except Exception as e:
                self.log_manager.log_message(f"<b>⚠️ Could not clear images directory:</b> {e}")
                if st.session_state.get('log_stream'):
                    st.session_state['log_stream'].write(f"[WARNING] Could not clear images directory {images_dir}: {e}\n")
                    st.session_state['log_stream'].flush()

        st.session_state['output_dirs_cleared'] = True
        if st.session_state.get('log_stream'):
            st.session_state['log_stream'].write(f"[DEBUG] Output directories cleared. Media: {media_dir}, Images: {images_dir}\n")
            st.session_state['log_stream'].flush()

    def load_apkg_file(self, apkg_path: Optional[str]) -> bool:
        """
        Load APKG file into session state for download.

        Args:
            apkg_path: Path to the APKG file

        Returns:
            bool: True if file was loaded successfully, False otherwise
        """
        if not apkg_path or not os.path.exists(apkg_path):
            self.log_manager.log_message(f"<b>⚠️ APKG file not found at path:</b> {apkg_path}")
            if st.session_state.get('log_stream'):
                st.session_state['log_stream'].write(f"[ERROR] APKG file not found at path: {apkg_path}\n")
                st.session_state['log_stream'].flush()
            return False

        try:
            # Read APKG file and store in session state
            with open(apkg_path, 'rb') as f:
                st.session_state.apkg_file = f.read()

            # Generate timestamp for unique filename
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            selected_lang = st.session_state.get('selected_lang', 'Unknown')
            st.session_state.apkg_filename = f"{selected_lang.replace(' ', '_')}_{timestamp}_deck.apkg"

            self.log_manager.log_message(f"<b>📦 APKG file found:</b> {apkg_path}")
            self.log_manager.log_message(f"<b>� APKG file loaded for download:</b> {len(st.session_state.apkg_file)} bytes")
            if st.session_state.get('log_stream'):
                st.session_state['log_stream'].write(f"[DEBUG] APKG file loaded: {len(st.session_state.apkg_file)} bytes, filename: {st.session_state.apkg_filename}\n")
                st.session_state['log_stream'].flush()

            return True

        except Exception as e:
            self.log_manager.log_message(f"<b>⚠️ Failed to load APKG file:</b> {e}")
            if st.session_state.get('log_stream'):
                st.session_state['log_stream'].write(f"[ERROR] Failed to load APKG file: {e}\n")
                st.session_state['log_stream'].flush()
            return False

    def get_log_file_data(self) -> Optional[Dict[str, Any]]:
        """
        Get log file data for download.

        Returns:
            Dict with file data and metadata, or None if file not found
        """
        log_file_path = st.session_state.get('log_file_path')
        if not log_file_path or not os.path.exists(log_file_path):
            return None

        try:
            with open(log_file_path, "rb") as f:
                return {
                    "data": f.read(),
                    "filename": os.path.basename(log_file_path),
                    "mime_type": "text/plain"
                }
        except Exception as e:
            self.log_manager.log_message(f"<b>⚠️ Could not read log file:</b> {e}")
            return None

    def get_output_directory_paths(self) -> Dict[str, str]:
        """
        Get the standard output directory paths.

        Returns:
            Dict containing output_dir, media_dir, and images_dir paths
        """
        media_dir = str(Path(self.output_dir) / "media")
        images_dir = str(Path(self.output_dir) / "images")

        return {
            'output_dir': self.output_dir,
            'media_dir': media_dir,
            'images_dir': images_dir
        }

    def ensure_output_directories_exist(self) -> None:
        """
        Ensure output directories exist (create if they don't).
        """
        paths = self.get_output_directory_paths()

        for dir_path in [paths['output_dir'], paths['media_dir'], paths['images_dir']]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def reset_session_file_state(self) -> None:
        """
        Reset file-related session state variables.
        """
        # Clear file state
        if 'apkg_file' in st.session_state:
            del st.session_state.apkg_file
        if 'apkg_filename' in st.session_state:
            del st.session_state.apkg_filename
        if 'output_dirs_cleared' in st.session_state:
            del st.session_state.output_dirs_cleared

        # Reset generation progress file paths
        progress = st.session_state.get('generation_progress', {})
        progress.update({
            'tsv_path': None,
            'media_dir': None,
            'output_dir': None,
            'apkg_ready': False,
            'apkg_path': None
        })
        st.session_state['generation_progress'] = progress