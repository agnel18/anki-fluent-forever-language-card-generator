# languages/chinese_traditional/domain/zh_tw_config.py
"""
Configuration for Chinese Traditional (繁體中文) grammar analyzer.
Defines grammatical roles, color schemes, and language-specific rules.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ZhTwConfig:
    """
    Configuration class for Chinese Traditional grammatical analysis.

    Defines grammatical categories specific to Chinese linguistics:
    - 實詞 (Shící) - Content words with independent meaning
    - 虛詞 (Xūcí) - Function words for structure/grammar
    """

    def __init__(self):
        # Basic language information
        self.language_code = "zh-tw"
        self.language_name = "Chinese Traditional"
        self.native_name = "繁體中文"
        self.family = "Sino-Tibetan"
        self.script_type = "logographic"
        self.complexity_rating = "high"

        # Key linguistic features
        self.key_features = [
            'word_segmentation',
            'compounds_first',
            'chinese_categories',
            'aspect_system',
            'topic_comment'
        ]

        # Supported complexity levels
        self.supported_complexity_levels = ['beginner', 'intermediate', 'advanced']

        # Load word meanings from external file
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.word_meanings = self._load_json(config_dir / "zh_tw_word_meanings.json")

        # Grammatical Role Mapping (16 categories based on Chinese linguistics)
        self.grammatical_roles: Dict[str, str] = {
            # Content Words (實詞 / Shící) - Independent Meaning
            "noun": "#FFAA00",                    # Orange - People/places/things/concepts
            "verb": "#44FF44",                    # Green - Actions/states/changes
            "adjective": "#FF44FF",               # Magenta - Qualities/descriptions
            "numeral": "#FFFF44",                 # Yellow - Numbers/quantities
            "measure_word": "#FFD700",            # Gold - Classifiers (個, 本, 杯)
            "pronoun": "#FF4444",                 # Red - Replacements for nouns
            "time_word": "#FFA500",               # Orange-red - Time expressions
            "locative_word": "#FF8C00",           # Dark orange - Location/direction

            # Function Words (虛詞 / Xūcí) - Structural/Grammatical
            "aspect_particle": "#8A2BE2",         # Purple - Aspect markers (了, 著, 過)
            "modal_particle": "#DA70D6",          # Plum - Tone/mood particles (嗎, 呢, 吧)
            "structural_particle": "#9013FE",     # Violet - Structural particles (的, 地, 得)
            "preposition": "#4444FF",             # Blue - Prepositions/coverbs
            "conjunction": "#888888",             # Gray - Connectors
            "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
            "interjection": "#FFD700",            # Gold - Emotions/exclamations
            "onomatopoeia": "#FFD700"             # Gold - Sound imitation
        }

        # Language-specific patterns and rules
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize Chinese Traditional-specific patterns and rules"""

        # Word segmentation patterns (Traditional characters)
        self.word_patterns = {
            'measure_words': [
                '個', '本', '杯', '張', '件', '位', '隻', '頭', '條', '棵',
                '顆', '粒', '滴', '片', '塊', '座', '棟', '艘', '輛', '架'
            ],
            'aspect_particles': ['了', '著', '過', '起來', '下去'],
            'modal_particles': ['嗎', '呢', '吧', '呀', '啦', '喲', '麼'],
            'structural_particles': ['的', '地', '得', '所', '之'],
            'prepositions': ['在', '對', '給', '從', '向', '往', '到', '自', '由', '於'],
            'conjunctions': ['和', '與', '及', '以及', '或', '或者', '但是', '可是', '而', '而且'],
            'adverbs': ['很', '太', '最', '更', '也', '都', '還', '就', '只', '才']
        }

        # Sentence structure patterns
        self.sentence_patterns = {
            'question_patterns': [
                r'.*嗎？?$',  # Ma particle questions
                r'.*呢？?$',  # Ne particle questions
                r'.*吧？?$',  # Ba particle questions
                r'.*什麼.*',  # Shenme questions
                r'.*誰.*',    # Shei questions
                r'.*哪裡.*',  # Nali questions
                r'.*多少.*',  # Duoshao questions
                r'.*怎麼.*'   # Zenme questions
            ],
            'negation_patterns': [
                r'不.*',      # Bu negation
                r'沒.*',      # Mei negation
                r'沒有.*'     # Meiyou negation
            ]
        }

    def get_color_scheme(self, complexity: str = "intermediate") -> Dict[str, str]:
        """
        Get color scheme based on complexity level.
        For Chinese Traditional, we use the same colors across complexity levels
        but may adjust opacity or add additional categories for advanced learners.
        """
        base_scheme = self.grammatical_roles.copy()
        
        # Add special categories
        base_scheme.update({
            "target_word": "#FFFF00",  # Yellow - Target word being learned
            "other": "#888888"         # Gray - Fallback for unrecognized roles
        })

        if complexity == "advanced":
            # Add advanced categories for expert learners
            base_scheme.update({
                "resultative_compound": "#FF1493",  # Deep pink - Verb-resultative (吃完)
                "directional_compound": "#00BFFF",   # Deep sky blue - Verb-directional (進來)
                "pivot_construction": "#32CD32",    # Lime green - Topic-comment (我書看完了)
            })

        return base_scheme

    def get_validation_rules(self) -> Dict[str, Any]:
        """
        Get validation rules for Chinese Traditional analysis.
        """
        return {
            'min_words_per_sentence': 2,
            'max_words_per_sentence': 25,
            'required_categories': ['noun', 'verb'],
            'word_segmentation_required': True,
            'traditional_characters_only': True,
            'aspect_system_check': True,
            'measure_word_validation': True
        }

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """
        Load JSON file with error handling.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON file {path}: {e}")
            return {}