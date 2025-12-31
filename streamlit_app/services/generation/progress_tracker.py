# services/generation/progress_tracker.py
"""
Progress Tracker Service for Generation Operations
Handles progress bar updates, status display, and pass tracking for deck generation.
"""

import re
from typing import Optional, Any
import streamlit as st


class ProgressTracker:
    """
    Manages progress tracking and UI updates during generation operations.
    Handles progress bars, status updates, pass indicators, and real-time feedback.
    """

    def __init__(self, progress_bar: Any, status_text: Any, detail_text: Any,
                 pass_indicator: Any, log_manager: Any, log_display: Any = None):
        """
        Initialize the progress tracker.

        Args:
            progress_bar: Streamlit progress bar element
            status_text: Streamlit status text element
            detail_text: Streamlit detail text element
            pass_indicator: Streamlit pass indicator element
            log_manager: LogManager instance for logging
            log_display: Optional Streamlit element for displaying logs
        """
        self.progress_bar = progress_bar
        self.status_text = status_text
        self.detail_text = detail_text
        self.pass_indicator = pass_indicator
        self.log_manager = log_manager
        self.log_display = log_display

    def update_progress_pass_based(self, progress_pct: float, current_word: str, status: str) -> None:
        """
        Update progress using pass-based system (for legacy compatibility).

        Args:
            progress_pct: Progress percentage (0-1)
            current_word: Current word being processed
            status: Current status message
        """
        # Update progress bar based on pass
        pass_progress = {
            "PASS 1": 16.67,
            "PASS 2": 33.33,
            "PASS 3": 50.0,
            "PASS 4": 66.67,
            "PASS 5": 83.33,
            "PASS 6": 100.0
        }

        for pass_name, pct in pass_progress.items():
            if pass_name in status:
                self.progress_bar.progress(pct / 100)
                break
        else:
            self.progress_bar.progress(progress_pct)  # fallback to original

        # Update pass indicator
        pass_match = re.search(r'PASS (\d+)', status)
        if pass_match:
            pass_num = pass_match.group(1)
            self.pass_indicator.markdown(f"**Current Pass:** {pass_num}/6")

        # Update status displays
        self.detail_text.markdown(f"*{status}*")
        self.status_text.info(f"⚙️ {current_word}: {status}")

        # Log progress update
        self.log_manager.log_message(f"[DEBUG] Progress: {progress_pct:.1%} - Word: '{current_word}' - Status: {status}")

    def update_progress_percentage_based(self, progress: float, status: str, detail: Optional[str] = None) -> None:
        """
        Update progress using percentage-based system (for modern generation).

        Args:
            progress: Progress value (0-1)
            status: Current status message
            detail: Optional detail message
        """
        # Update progress bar
        progress_pct = int(progress * 100)
        self.progress_bar.progress(progress_pct / 100)

        # Update status text
        self.status_text.markdown(f"**{status}**")

        # Update detail text
        if detail:
            self.detail_text.markdown(f"*{detail}*")

        # Update pass indicator
        if 'PASS' in status:
            try:
                pass_num = int(re.search(r'PASS (\d+)', status).group(1))
                self.pass_indicator.markdown(f"**Pass {pass_num}/6**")
            except:
                pass

        # Log the progress update with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {status}"
        if detail:
            log_message += f"\n  └─ {detail}"
        self.log_manager.log_message(log_message)

        # Update log display in real-time if provided
        if self.log_display:
            self.log_display.code(self.log_manager.get_display_logs(), language=None)

    def reset_progress(self) -> None:
        """Reset all progress indicators to initial state."""
        self.progress_bar.progress(0)
        self.status_text.markdown("")
        self.detail_text.markdown("")
        self.pass_indicator.markdown("")

    def set_status(self, status: str, level: str = "info") -> None:
        """
        Set status message with specified level.

        Args:
            status: Status message
            level: Status level ('info', 'success', 'warning', 'error')
        """
        if level == "info":
            self.status_text.info(status)
        elif level == "success":
            self.status_text.success(status)
        elif level == "warning":
            self.status_text.warning(status)
        elif level == "error":
            self.status_text.error(status)
        else:
            self.status_text.markdown(status)

    def set_detail(self, detail: str) -> None:
        """
        Set detail message.

        Args:
            detail: Detail message
        """
        self.detail_text.markdown(f"*{detail}*")