# languages/hindi/domain/hi_config.py
import json
import logging
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class GrammaticalRole(Enum):
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    POSTPOSITION = "postposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    PARTICLE = "particle"
    # Add more as needed

@dataclass
class HiConfig:
    """Configuration for Hindi analyzer, loaded from external files."""
    grammatical_roles: Dict[str, str]
    common_postpositions: List[str]
    gender_markers: Dict[str, str]
    case_markers: Dict[str, str]
    honorific_markers: Dict[str, str]
    word_meanings: Dict[str, str]
    prompt_templates: Dict[str, str]
    patterns: Dict[str, Any]  # For regex patterns, etc.

    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "hi_grammatical_roles.yaml")
        self.common_postpositions = self._load_yaml(config_dir / "hi_common_postpositions.yaml")
        self.gender_markers = self._load_yaml(config_dir / "hi_gender_markers.yaml")
        self.case_markers = self._load_yaml(config_dir / "hi_case_markers.yaml")
        self.honorific_markers = self._load_yaml(config_dir / "hi_honorific_markers.yaml")
        self.word_meanings = self._load_json(config_dir / "hi_word_meanings.json")
        # For simplicity, define templates inline or load from file
        self.prompt_templates = {
            "single": """
Analyze this Hindi sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "first_word",
      "grammatical_role": "noun|verb|pronoun|adjective|adverb|postposition|conjunction|interjection|particle|other",
      "individual_meaning": "brief explanation of this word's role in the sentence"
    },
    {
      "word": "second_word", 
      "grammatical_role": "noun|verb|pronoun|adjective|adverb|postposition|conjunction|interjection|particle|other",
      "individual_meaning": "brief explanation of this word's role in the sentence"
    }
  ],
  "explanations": {
    "overall_structure": "brief explanation of sentence structure",
    "key_features": "any notable grammatical features"
  }
}

Important: 
- Break down the sentence into individual words
- Assign appropriate grammatical roles from the list above
- Provide meaningful explanations for each word
- Use only valid JSON format
""",
            "batch": """
Analyze these Hindi sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "first_word",
          "grammatical_role": "noun|verb|pronoun|adjective|adverb|postposition|conjunction|interjection|particle|other",
          "individual_meaning": "brief explanation of this word's role"
        }
      ],
      "explanations": {
        "overall_structure": "brief explanation",
        "key_features": "notable features"
      }
    },
    {
      "sentence": "second sentence",
      "words": [...],
      "explanations": {...}
    }
  ]
}

Important:
- Analyze each sentence separately
- Break down each sentence into individual words
- Assign appropriate grammatical roles
- Provide meaningful explanations
- Use only valid JSON format
"""
        }
        self.patterns = self._load_yaml(config_dir / "hi_patterns.yaml")
        self.postpositions = self.common_postpositions  # Alias for compatibility

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML file {path}: {e}")
            return {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON file {path}: {e}")
            return {}

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Hindi grammatical elements based on complexity."""
        schemes = {
            "beginner": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF", 
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "postposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "particle": "#AA44FF",
                "other": "#AAAAAA"
            },
            "intermediate": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#4ECDC4", 
                "adverb": "#44FFFF",
                "pronoun": "#FFEAA7",
                "personal_pronoun": "#FFEAA7",
                "demonstrative_pronoun": "#FFEAA7",
                "postposition": "#4444FF",
                "auxiliary_verb": "#4ECDC4",
                "conjunction": "#888888",
                "particle": "#AA44FF",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF", 
                "pronoun": "#FF4444",
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "interrogative_pronoun": "#FF4444",
                "relative_pronoun": "#FF4444",
                "postposition": "#4444FF",
                "auxiliary_verb": "#44FF44",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "particle": "#AA44FF",
                "onomatopoeia": "#FFD700",
                "ideophone": "#FFD700",
                "echo_word": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])