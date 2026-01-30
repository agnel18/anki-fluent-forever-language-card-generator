# Arabic Language Configuration
# Language: Arabic (العربية)
# Family: Afro-Asiatic (Semitic)
# Script: Arabic abjad (RTL - Right to Left)
# Key Features: Root-based morphology, case marking (i'rab), verb forms (abwab)

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class ArConfig:
    """
    Configuration for Arabic grammar analysis.
    Follows Clean Architecture pattern with external configuration.
    """

    def __init__(self):
        self.language_code = "ar"
        self.language_name = "Arabic"
        self.language_name_native = "العربية"

        # Arabic is RTL (Right to Left)
        self.is_rtl = True
        self.text_direction = "rtl"

        # Arabic script properties
        self.script_type = "abjad"
        self.unicode_range = (0x0600, 0x06FF)  # Arabic Unicode block

        # Load configuration from infrastructure/data directory (like gold standards)
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "ar_grammatical_roles.yaml") or self._load_grammatical_roles()
        self.case_markers = self._load_yaml(config_dir / "ar_case_markers.yaml") or {}
        self.verb_patterns = self._load_yaml(config_dir / "ar_verb_patterns.yaml") or {}
        self.definite_article_patterns = self._load_yaml(config_dir / "ar_definite_article_patterns.yaml") or {}
        self.plural_patterns = self._load_yaml(config_dir / "ar_plural_patterns.yaml") or {}
        self.root_patterns = self._load_yaml(config_dir / "ar_root_patterns.yaml") or {}
        self.patterns = self._load_yaml(config_dir / "ar_patterns.yaml") or {}
        self.word_meanings = self._load_json(config_dir / "ar_word_meanings.json") or {}

        # Load color schemes for different complexity levels
        self.color_schemes = self._load_color_schemes()

        # Create role hierarchy mapping for color inheritance
        self.role_hierarchy = self._create_role_hierarchy()

        # Create complexity-based role filtering
        self.complexity_role_filters = self._create_complexity_filters()

        # Load prompt templates
        self.prompt_templates = self._load_prompt_templates()

        # Arabic-specific linguistic features
        self.linguistic_features = {
            'root_based_morphology': True,
            'case_marking_i3rab': True,
            'verb_forms_abwab': True,
            'definite_article_al': True,
            'article_assimilation': True,
            'dual_number': True,
            'sound_plural': True,
            'broken_plural': True,
            'hamza_variations': True,
            'tanween': True,
            'shadda': True
        }

        # Common Arabic roots for analysis
        self.common_roots = {
            'ك-ت-ب': ['writing', 'book', 'author'],
            'ق-ر-أ': ['reading', 'reciting', 'lecture'],
            'ش-ر-ب': ['drinking', 'beverage', 'intoxication'],
            'أ-ك-ل': ['eating', 'food', 'consumer'],
            'ذ-ه-ب': ['going', 'gold', 'departure'],
            'ج-ل-س': ['sitting', 'session', 'gathering'],
            'ق-و-ل': ['saying', 'word', 'speech'],
            'ع-م-ل': ['working', 'action', 'deed'],
            'ر-أ-ي': ['seeing', 'vision', 'opinion'],
            'س-م-ع': ['hearing', 'listening', 'obedience']
        }

    def _load_grammatical_roles(self) -> Dict[str, Dict[str, str]]:
        """Load grammatical roles from external JSON file (fallback)"""
        config_path = Path(__file__).parent / "ar_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('grammatical_roles', self._get_default_roles())
        return self._get_default_roles()

    def _get_default_roles(self) -> Dict[str, Dict[str, str]]:
        """Default grammatical roles for Arabic"""
        return {
            'beginner': {
                'noun': 'noun (اسم)',
                'verb': 'verb (فعل)',
                'particle': 'particle (حرف)',
                'other': 'other'
            },
            'intermediate': {
                'noun': 'noun (اسم)',
                'verb': 'verb (فعل)',
                'adjective': 'adjective (صفة)',
                'preposition': 'preposition (حرف جر)',
                'conjunction': 'conjunction (حرف عطف)',
                'interrogative': 'interrogative (حرف استفهام)',
                'negation': 'negation (نفي)',
                'definite_article': 'definite article (ال)',
                'pronoun': 'pronoun (ضمير)',
                'other': 'other'
            },
            'advanced': {
                'noun': 'noun (اسم)',
                'verb': 'verb (فعل)',
                'adjective': 'adjective (صفة)',
                'preposition': 'preposition (حرف جر)',
                'conjunction': 'conjunction (حرف عطف)',
                'interrogative': 'interrogative (حرف استفهام)',
                'negation': 'negation (نفي)',
                'definite_article': 'definite article (ال)',
                'pronoun': 'pronoun (ضمير)',
                'nominative': 'nominative case (رفع)',
                'accusative': 'accusative case (نصب)',
                'genitive': 'genitive case (جر)',
                'perfect_verb': 'perfect verb (فعل ماض)',
                'imperfect_verb': 'imperfect verb (فعل مضارع)',
                'imperative_verb': 'imperative verb (فعل أمر)',
                'active_participle': 'active participle (اسم فاعل)',
                'passive_participle': 'passive participle (اسم مفعول)',
                'verbal_noun': 'verbal noun (مصدر)',
                'instrument_noun': 'instrument noun (اسم آلة)',
                'place_noun': 'place noun (اسم مكان)',
                'dual': 'dual number (مثنى)',
                'sound_plural': 'sound plural (جمع سالم)',
                'broken_plural': 'broken plural (جمع مكسر)',
                'root_based': 'root-based morphology (جذر)',
                'verb_form_i': 'verb form I (فعل ثلاثي مجرد)',
                'verb_form_ii': 'verb form II (فعل ثلاثي مزيد)',
                'verb_form_iii': 'verb form III (فعل ثلاثي لازم)',
                'verb_form_iv': 'verb form IV (فعل رباعي)',
                'verb_form_v': 'verb form V (فعل خماسي)',
                'verb_form_vi': 'verb form VI (فعل سداسي)',
                'verb_form_vii': 'verb form VII (فعل سباعي)',
                'verb_form_viii': 'verb form VIII (فعل ثماني)',
                'verb_form_ix': 'verb form IX (فعل تسعي)',
                'verb_form_x': 'verb form X (فعل عشري)',
                'emphatic_consonant': 'emphatic consonant (حرف مُظْمَى)',
                'sun_letter': 'sun letter (حرف شمسي)',
                'moon_letter': 'moon letter (حرف قمري)',
                'hamza': 'hamza (همزة)',
                'shadda': 'shadda (شدة)',
                'tanween': 'tanween (تنوين)',
                'other': 'other'
            }
        }

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Load color schemes from external configuration"""
        config_path = Path(__file__).parent / "ar_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('color_schemes', self._get_default_color_schemes())
        return self._get_default_color_schemes()

    def _get_default_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Default color schemes for Arabic"""
        return {
            'beginner': {
                'noun': '#4ECDC4',      # Teal
                'verb': '#FF44FF',      # Magenta
                'particle': '#FFAA00',  # Orange
                'other': '#9370DB'      # Medium Purple
            },
            'intermediate': {
                'noun': '#4ECDC4',      # Teal
                'verb': '#FF44FF',      # Magenta
                'adjective': '#FFD700', # Gold
                'preposition': '#FFAA00', # Orange
                'conjunction': '#FF6347', # Tomato
                'interrogative': '#32CD32', # Lime Green
                'negation': '#DC143C',   # Crimson
                'definite_article': '#FF4500', # Orange Red
                'pronoun': '#9370DB',   # Medium Purple
                'other': '#708090'      # Slate Gray
            },
            'advanced': {
                'noun': '#4ECDC4',      # Teal
                'verb': '#FF44FF',      # Magenta
                'adjective': '#FFD700', # Gold
                'preposition': '#FFAA00', # Orange
                'conjunction': '#FF6347', # Tomato
                'interrogative': '#32CD32', # Lime Green
                'negation': '#DC143C',   # Crimson
                'definite_article': '#FF4500', # Orange Red
                'pronoun': '#9370DB',   # Medium Purple
                'nominative': '#00CED1',   # Dark Turquoise
                'accusative': '#FF69B4',   # Hot Pink
                'genitive': '#DDA0DD',     # Plum
                'perfect_verb': '#FF44FF', # Magenta
                'imperfect_verb': '#DA70D6', # Orchid
                'imperative_verb': '#BA55D3', # Medium Orchid
                'active_participle': '#9932CC', # Dark Orchid
                'passive_participle': '#8A2BE2', # Blue Violet
                'dual': '#4169E1',       # Royal Blue
                'sound_plural': '#0000FF', # Blue
                'broken_plural': '#1E90FF', # Dodger Blue
                'verbal_noun': '#FF6347',   # Tomato
                'instrument_noun': '#32CD32', # Lime Green
                'place_noun': '#DC143C',   # Crimson
                'root_based': '#FF4500',   # Orange Red
                'verb_form_i': '#9370DB',  # Medium Purple
                'verb_form_ii': '#00CED1', # Dark Turquoise
                'verb_form_iii': '#FF69B4', # Hot Pink
                'verb_form_iv': '#DDA0DD', # Plum
                'verb_form_v': '#DA70D6',  # Orchid
                'verb_form_vi': '#BA55D3', # Medium Orchid
                'verb_form_vii': '#9932CC', # Dark Orchid
                'verb_form_viii': '#8A2BE2', # Blue Violet
                'verb_form_ix': '#4169E1', # Royal Blue
                'verb_form_x': '#0000FF',  # Blue
                'emphatic_consonant': '#1E90FF', # Dodger Blue
                'sun_letter': '#FFD700',   # Gold
                'moon_letter': '#FFAA00',  # Orange
                'hamza': '#FF6347',        # Tomato
                'shadda': '#32CD32',       # Lime Green
                'tanween': '#DC143C',      # Crimson
                'other': '#708090'      # Slate Gray
            }
        }

    def _create_role_hierarchy(self) -> Dict[str, str]:
        """Create role hierarchy mapping for color inheritance"""
        return {
            # Verb subtypes inherit verb color
            'perfect_verb': 'verb',
            'imperfect_verb': 'verb',
            'imperative_verb': 'verb',
            'active_participle': 'verb',
            'passive_participle': 'verb',
            'verbal_noun': 'noun',  # Verbal nouns are nouns
            
            # Noun subtypes inherit noun color
            'instrument_noun': 'noun',
            'place_noun': 'noun',
            'sound_plural': 'noun',
            'broken_plural': 'noun',
            'dual': 'noun',
            
            # Case markers inherit from their base roles
            'nominative': 'noun',  # Case applies to nouns
            'accusative': 'noun',
            'genitive': 'noun',
            
            # Verb forms inherit verb color
            'verb_form_i': 'verb',
            'verb_form_ii': 'verb',
            'verb_form_iii': 'verb',
            'verb_form_iv': 'verb',
            'verb_form_v': 'verb',
            'verb_form_vi': 'verb',
            'verb_form_vii': 'verb',
            'verb_form_viii': 'verb',
            'verb_form_ix': 'verb',
            'verb_form_x': 'verb',
            
            # Other linguistic features
            'root_based': 'other',
            'emphatic_consonant': 'other',
            'sun_letter': 'other',
            'moon_letter': 'other',
            'hamza': 'other',
            'shadda': 'other',
            'tanween': 'other'
        }

    def _create_complexity_filters(self) -> Dict[str, set]:
        """Create complexity-based role filtering"""
        return {
            'beginner': {
                'noun', 'verb', 'pronoun', 'particle', 'other'
            },
            'intermediate': {
                'noun', 'verb', 'pronoun', 'adjective', 'preposition', 'conjunction', 
                'interrogative', 'negation', 'definite_article', 'imperfect_verb', 
                'perfect_verb', 'active_participle', 'passive_participle', 'other'
            },
            'advanced': set()  # Allow all roles for advanced
        }

    def should_show_role(self, role: str, complexity: str) -> bool:
        """Check if a role should be shown at given complexity level"""
        if complexity == 'advanced':
            return True
        allowed_roles = self.complexity_role_filters.get(complexity, set())
        return role in allowed_roles or self.get_parent_role(role) in allowed_roles

    def get_parent_role(self, role: str) -> str:
        """Get the parent role for color inheritance"""
        return self.role_hierarchy.get(role, role)

    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates from external configuration"""
        config_path = Path(__file__).parent / "ar_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('prompt_templates', self._get_default_prompt_templates())
        return self._get_default_prompt_templates()

    def _get_default_prompt_templates(self) -> Dict[str, str]:
        """Default prompt templates for Arabic"""
        return {
            'single': """
Analyze this Arabic sentence for language learning: "{sentence}"
Target word: "{target_word}"

For each word, provide a detailed explanation that combines grammatical role, meaning, and function in this EXACT format:

"grammatical_role (specific_type) - meaning 'semantic_meaning' - functions as syntactic_function - morphological_notes"

EXAMPLE for Arabic word "يكتب":
"verb (imperfect) - meaning 'he writes' - functions as main verb of sentence - Form I, third person masculine singular, nominative case"

Return ONLY valid JSON in this exact format:
{{
  "words": [
    {{
      "word": "exact_word",
      "grammatical_role": "brief_role",
      "meaning": "grammatical_role (specific_type) - meaning 'semantic_meaning' - functions as syntactic_function - morphological_notes"
    }}
  ],
  "overall_analysis": {{
    "sentence_structure": "brief description",
    "key_features": "important grammatical points"
  }}
}}
""",
            'batch': """
You are an expert linguist specializing in Arabic grammar analysis. Your task is to analyze Arabic sentences and provide contextual word meanings.

Sentences: {sentences}
Target word: "{target_word}"
Complexity level: {complexity}

MANDATORY: Respond with VALID JSON only. No explanations, no markdown, no code blocks.

REQUIRED JSON FORMAT:
{{
  "batch_results": [
    {{
      "sentence": "exact sentence text",
      "analysis": [
        {{
          "word": "exact_word",
          "grammatical_role": "noun|verb|pronoun|adjective|conjunction|preposition|other",
          "meaning": "WORD (GRAMMATICAL_ROLE): contextual meaning — grammatical function"
        }}
      ],
      "explanations": {{
        "overall_structure": "brief description",
        "key_features": "important grammatical points"
      }}
    }}
  ]
}}

CRITICAL RULES:
1. EXACTLY 3 fields per word: "word", "grammatical_role", "meaning"
2. "meaning" MUST follow this format: "WORD (GRAMMATICAL_ROLE): contextual meaning — grammatical function"
3. Use contextual meanings, not generic definitions
4. Explain each word's specific role in THIS sentence

EXAMPLES:
- "هي (pronoun): she — subject of the sentence"
- "تأكل (verb): eats/is eating — main verb of the sentence"  
- "الموز (noun): the banana — direct object of the verb"
- "و (conjunction): and — connects two objects"
- "البطيخ (noun): the watermelon — second direct object"

DO NOT add fields like "case", "person", "type", "other". ONLY use "word", "grammatical_role", "meaning".

Grammatical roles: {grammatical_roles}
""",
            'sentence_generation': """
You are an expert in Modern Standard Arabic.

Generate content for the Arabic word "{word}".

{enriched_meaning_instruction}

Provide grammatical restrictions for "{word}":
If no restrictions, say "No specific restrictions."

Generate exactly {num_sentences} natural Arabic sentences using "{word}".
Each sentence max {max_length} words.
Difficulty: {difficulty}
{context_instruction}

For each sentence, provide:
- English translation
- IPA pronunciation
- 3 image keywords

Format:

MEANING: [meaning]

RESTRICTIONS: [restrictions]

SENTENCES:
1. [Arabic sentence 1]
2. [Arabic sentence 2]

TRANSLATIONS:
1. [English 1]
2. [English 2]

IPA:
1. [IPA 1]
2. [IPA 2]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]

Return only the formatted text.
"""
        }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme for given complexity level"""
        return self.color_schemes.get(complexity, self.color_schemes['beginner'])

    def get_grammatical_roles(self, complexity: str) -> Dict[str, str]:
        """Get grammatical roles for given complexity level"""
        return self.grammatical_roles.get(complexity, self.grammatical_roles.get('beginner', {}))

    def is_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if text is None:
            return False
        for char in text:
            if self.unicode_range[0] <= ord(char) <= self.unicode_range[1]:
                return True
        return False

    def normalize_arabic_text(self, text: str) -> str:
        """Normalize Arabic text (remove tatweel, normalize hamza, etc.)"""
        # Basic normalization - can be expanded
        import unicodedata
        return unicodedata.normalize('NFC', text)

    def extract_arabic_root(self, word: str) -> Optional[str]:
        """
        Basic Arabic root extraction (simplified implementation).
        In a full system, this would use morphological analysis algorithms.
        """
        # Remove common prefixes and suffixes
        cleaned = word.strip()
        cleaned = cleaned.replace('ال', '')  # Remove definite article
        cleaned = cleaned.replace('و', '')   # Remove conjunction
        cleaned = cleaned.replace('ف', '')   # Remove conjunction
        cleaned = cleaned.replace('ب', '')   # Remove preposition
        cleaned = cleaned.replace('ك', '')   # Remove preposition
        cleaned = cleaned.replace('ل', '')   # Remove preposition

        # Basic pattern matching for common roots
        if len(cleaned) >= 3:
            # Look for triliteral root patterns
            consonants = ''.join(c for c in cleaned if c not in 'َُِّْ')
            if len(consonants) >= 3:
                root_candidate = f"{consonants[0]}-{consonants[1]}-{consonants[2]}"
                if root_candidate in self.common_roots:
                    return root_candidate

        return None

    def get_root_meaning(self, root: str) -> Optional[str]:
        """Get basic meaning of an Arabic root"""
        meanings = self.common_roots.get(root, [])
        return ', '.join(meanings) if meanings else None

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file with error handling"""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f"Warning: YAML file not found: {path}")
                return {}
        except Exception as e:
            print(f"Error loading YAML file {path}: {e}")
            return {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: JSON file not found: {path}")
                return {}
        except Exception as e:
            print(f"Error loading JSON file {path}: {e}")
            return {}

    def is_sun_letter(self, letter: str) -> bool:
        """Check if a letter is a sun letter (causes assimilation)"""
        sun_letters = ['ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن']
        return letter in sun_letters

    def is_emphatic_consonant(self, letter: str) -> bool:
        """Check if a consonant is emphatic (velarized)"""
        emphatic = ['ص', 'ض', 'ط', 'ظ']
        return letter in emphatic