# languages/hindi/domain/hi_patterns.py
import re
from typing import Dict, Pattern
from .hi_config import HiConfig

class HiPatterns:
    """Regex patterns and markers for Hindi analysis."""
    
    def __init__(self, config: HiConfig):
        self.config = config
        self.postposition_pattern: Pattern[str] = re.compile(r'\b(?:' + '|'.join(re.escape(p) for p in config.common_postpositions) + r')\b')
        # Add more patterns as needed, e.g., gender, case, honorifics
        self.gender_patterns = {}  # Populate from config
        self.case_patterns = {}
        self.honorific_patterns = {}