# languages/english/tests/test_en_analyzer.py
"""
Integration-level tests for EnAnalyzer.
AI calls are mocked — no real API key required.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.english.en_analyzer import EnAnalyzer


class TestEnAnalyzer:
    def test_placeholder(self):
        pytest.skip("Phase 6 — tests come later")
