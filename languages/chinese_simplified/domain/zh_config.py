# languages/chinese_simplified/domain/zh_config.py
"""
Chinese Simplified Configuration - Domain Component

Single source of truth for all Chinese-specific settings.
Loads YAML/JSON data files from infrastructure/data/.
"""


import json
import logging
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .zh_types import AnalysisRequest, AnalysisResult, BatchAnalysisResult, ParsedWord, ParsedSentence, ParseResult, ValidationResult

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Prompt templates (kept as module constants — Jinja-renderable)
# ----------------------------------------------------------------------

_SINGLE_PROMPT = """\
You are an expert linguist teaching Simplified Chinese to learners.

Analyze this Chinese sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

**TOKENIZATION RULES (CRITICAL):**
- Split into NATURAL WORD UNITS, not raw characters.
- Compounds and disyllabic/multi-syllabic words MUST stay together.
  Examples: 电话, 苹果, 朋友, 学校, 喜欢, 但是, 因为, 已经, 一起, 好吃, 漂亮, 知道.
- Single-character function words / pronouns / common verbs stay alone:
  我, 你, 他, 是, 的, 了, 很, 在, 给, 打, 到, 有.
- Punctuation is its own token.
- Examples of correct segmentation:
  "这个苹果很好吃。" -> ["这个", "苹果", "很", "好吃", "。"]
  "我打电话给你。"   -> ["我", "打", "电话", "给", "你", "。"]
  "我一到家就给你打电话。" -> ["我", "一", "到", "家", "就", "给", "你", "打", "电话", "。"]

**STRICT OUTPUT RULES:**
- For EVERY word you MUST return BOTH:
  - "grammatical_role": exactly one of these lowercase values:
    noun, verb, adjective, adverb, pronoun, particle, classifier, numeral,
    aspect_marker, structural_particle, modal_particle, preposition,
    conjunction, interjection, determiner, other
  - "individual_meaning": rich, CONTEXT-SPECIFIC 1-2 sentence learner explanation
    of what the word does in THIS sentence. NOT a generic dictionary definition.
    Bad: "a word that describes a noun"
    Good: "Used here as a degree adverb modifying 好吃, intensifying it to 'very tasty'."
- The target word gets the richest, most teaching-oriented explanation.
- Do NOT capitalize roles. No "Structural particle", "Personal pronoun", etc.
- "explanations.overall_structure": describe the sentence pattern in plain English
  (e.g. "Topic-comment structure with adjectival predicate", "一...就... immediate-succession structure").
- "explanations.key_features": call out notable Chinese grammar features used.

Return ONLY valid JSON in this EXACT shape (no prose, no markdown fences):
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "natural word unit",
      "grammatical_role": "<one of the lowercase roles above>",
      "individual_meaning": "<rich context-specific explanation>"
    }
  ],
  "explanations": {
    "overall_structure": "Detailed explanation of sentence pattern.",
    "key_features": "Notable Chinese grammatical features in this sentence."
  }
}
"""

_BATCH_PROMPT = """\
You are an expert linguist teaching Simplified Chinese to learners.

Analyze the following Chinese sentences. Apply the SAME rules to every sentence.

Sentences (numbered):
{{sentences}}

Target word: {{target_word}}
Complexity level: {{complexity}}

**TOKENIZATION RULES (CRITICAL):**
- Split into NATURAL WORD UNITS, not raw characters.
- Compounds MUST stay together: 电话, 苹果, 朋友, 学校, 喜欢, 但是, 因为, 已经, 好吃.
- Single-character function words / pronouns stay alone: 我, 你, 他, 是, 的, 了, 很.
- Punctuation is its own token.

**STRICT OUTPUT RULES:**
- For EVERY word in EVERY sentence return BOTH:
  - "grammatical_role" (lowercase, one of):
    noun, verb, adjective, adverb, pronoun, particle, classifier, numeral,
    aspect_marker, structural_particle, modal_particle, preposition,
    conjunction, interjection, determiner, other
  - "individual_meaning": rich, CONTEXT-SPECIFIC 1-2 sentence learner explanation
    of the word's role in THAT sentence. Never a generic dictionary entry.
- Target word "{{target_word}}" gets the richest explanation in each sentence.
- "overall_structure" / "key_features" must describe the sentence's specific pattern.

Return ONLY valid JSON (no prose, no markdown fences):
{
  "batch_results": [
    {
      "sentence": "<sentence 1 verbatim>",
      "words": [
        {
          "word": "<natural word unit>",
          "grammatical_role": "<lowercase role>",
          "individual_meaning": "<rich context-specific explanation>"
        }
      ],
      "explanations": {
        "overall_structure": "Detailed explanation of THIS sentence's pattern.",
        "key_features": "Notable Chinese grammatical features in THIS sentence."
      }
    }
  ]
}

CRITICAL: Return one batch_results entry per input sentence, in the same order.
"""


@dataclass
class ZhConfig:
    """
    Configuration for Chinese Simplified analyzer.
    """
    grammatical_roles: Dict[str, str] = field(default_factory=dict)
    common_classifiers: List[str] = field(default_factory=list)
    aspect_markers: Dict[str, str] = field(default_factory=dict)
    structural_particles: Dict[str, str] = field(default_factory=dict)
    modal_particles: Dict[str, str] = field(default_factory=dict)
    word_meanings: Dict[str, str] = field(default_factory=dict)
    prompt_templates: Dict[str, str] = field(default_factory=dict)
    patterns: Dict[str, Any] = field(default_factory=dict)
    classifiers: List[str] = field(default_factory=list)

    def __post_init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "zh_grammatical_roles.yaml")
        self.common_classifiers = self._load_yaml(config_dir / "zh_common_classifiers.yaml")
        self.aspect_markers = self._load_yaml(config_dir / "zh_aspect_markers.yaml")
        self.structural_particles = self._load_yaml(config_dir / "zh_structural_particles.yaml")
        self.modal_particles = self._load_yaml(config_dir / "zh_modal_particles.yaml")
        self.word_meanings = self._load_json(config_dir / "zh_word_meanings.json")
        self.prompt_templates = {
            "single": _SINGLE_PROMPT,
            "batch": _BATCH_PROMPT,
        }
        self.patterns = self._load_yaml(config_dir / "zh_patterns.yaml")
        self.classifiers = self.common_classifiers  # Alias for compatibility

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
        """Return color scheme for Chinese Simplified grammatical elements based on complexity."""
        schemes = {
            "beginner": {
                "target_word": "#E63939",
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "particle": "#AA44FF",
                "aspect_marker": "#8A2BE2",
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            },
            "intermediate": {
                "target_word": "#E63939",
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "particle": "#AA44FF",
                "aspect_marker": "#8A2BE2",
                "modal_particle": "#DA70D6",
                "structural_particle": "#9013FE",
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "other": "#AAAAAA"
            },
            "advanced": {
                "target_word": "#E63939",
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "interrogative_pronoun": "#FF4444",
                "particle": "#AA44FF",
                "aspect_marker": "#8A2BE2",
                "modal_particle": "#DA70D6",
                "structural_particle": "#9013FE",
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])

    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """Return formatted bullet list of allowed roles."""
        if complexity == "beginner":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "particle", "classifier", "numeral"
            ]
        elif complexity == "intermediate":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "particle", "classifier", "numeral", "aspect_marker",
                "structural_particle", "modal_particle"
            ]
        else:  # advanced
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "particle", "classifier", "numeral", "aspect_marker",
                "structural_particle", "modal_particle", "determiner",
                "preposition", "conjunction", "interjection"
            ]

        return '\n'.join([f'- {role}' for role in role_list])