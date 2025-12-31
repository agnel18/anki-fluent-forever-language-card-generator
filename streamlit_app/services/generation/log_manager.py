# services/generation/log_manager.py
"""
Log Manager Service for Generation Operations
Handles log accumulation, file writing, and provides log content for UI display.
"""

import datetime
import re
from typing import Optional, TextIO


class LogManager:
    """
    Manages logging for generation operations.
    Handles log accumulation, file writing, and provides clean log content for display.
    """

    def __init__(self, log_stream: Optional[TextIO] = None):
        """
        Initialize the log manager.

        Args:
            log_stream: Optional file stream for persistent logging
        """
        self.log_stream = log_stream
        self.logs_list = []  # For structured log storage
        self.logs_string = ""  # For UI display (clean, timestamped)

    def log_message(self, message: str) -> None:
        """
        Log a message with timestamp and clean formatting.

        Args:
            message: The message to log
        """
        # Store in structured list
        self.logs_list.append(message)

        # Write to file if stream available
        if self.log_stream:
            self.log_stream.write(message + '\n')
            self.log_stream.flush()

        # Update clean display string
        clean_msg = self._clean_html_tags(message)
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.logs_string += f"[{timestamp}] {clean_msg}\n"

    def get_display_logs(self) -> str:
        """
        Get logs formatted for UI display.

        Returns:
            Clean, timestamped log string for UI
        """
        return self.logs_string

    def get_raw_logs(self) -> list:
        """
        Get raw log messages.

        Returns:
            List of raw log messages
        """
        return self.logs_list.copy()

    def clear_logs(self) -> None:
        """Clear all logs."""
        self.logs_list.clear()
        self.logs_string = ""

    def _clean_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text for clean display.

        Args:
            text: Text potentially containing HTML tags

        Returns:
            Text with HTML tags removed
        """
        return re.sub(r'<[^>]+>', '', text)

    def get_log_count(self) -> int:
        """
        Get the number of log entries.

        Returns:
            Number of log messages
        """
        return len(self.logs_list)