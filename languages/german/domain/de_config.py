# German Configuration
# Language: German (Deutsch)
# Family: Germanic (Indo-European)
# Script: Latin alphabet with extensions (ä, ö, ü, ß)
# Key Features: Case system, gender agreement, V2 word order, complex morphology

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class DeConfig:
    """
    Configuration for German grammar analysis.
    Follows Clean Architecture pattern with external configuration.
    Based on Duden German grammar standards.
    """

    def __init__(self):
        self.language_code = "de"
        self.language_name = "German"
        self.language_name_native = "Deutsch"

        # German is LTR (Left to Right)
        self.is_rtl = False
        self.text_direction = "ltr"

        # German script properties
        self.script_type = "alphabetic"
        self.unicode_range = (0x0000, 0x007F)  # Basic Latin + extensions

        # Load configuration from infrastructure/data directory
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "de_grammatical_roles.yaml") or self._load_grammatical_roles()
        self.verb_conjugations = self._load_yaml(config_dir / "de_verb_conjugations.yaml") or {}
        self.case_patterns = self._load_yaml(config_dir / "de_case_patterns.yaml") or {}
        self.gender_patterns = self._load_yaml(config_dir / "de_gender_patterns.yaml") or {}

        # Load color schemes for different complexity levels
        self.color_schemes = self._load_color_schemes()

        # Create role hierarchy mapping for color inheritance
        self.role_hierarchy = self._create_role_hierarchy()

        # Create complexity-based role filtering
        self.complexity_role_filters = self._create_complexity_filters()

        # Load prompt templates
        self.prompt_templates = self._load_prompt_templates()

    def _load_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML configuration file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
        return None

    def _load_grammatical_roles(self) -> Dict[str, Any]:
        """Load default grammatical roles for German"""
        return {
            "article": {
                "description": "Definite/indefinite articles (der/die/das, ein/eine/ein)",
                "complexity": ["beginner", "intermediate", "advanced"],
                "german_name": "Artikel",
                "examples": ["der", "die", "das", "ein", "eine"]
            },
            "noun": {
                "description": "Nouns with case and gender marking",
                "complexity": ["beginner", "intermediate", "advanced"],
                "german_name": "Substantiv/Nomen",
                "examples": ["Mann", "Frau", "Haus"]
            },
            "verb": {
                "description": "Verbs with conjugation and position rules",
                "complexity": ["beginner", "intermediate", "advanced"],
                "german_name": "Verb",
                "examples": ["sein", "haben", "gehen"]
            },
            "adjective": {
                "description": "Adjectives with declension (stark/schwach/gemischt)",
                "complexity": ["intermediate", "advanced"],
                "german_name": "Adjektiv",
                "examples": ["groß", "klein", "schön"]
            },
            "pronoun": {
                "description": "Personal pronouns with case changes",
                "complexity": ["beginner", "intermediate", "advanced"],
                "german_name": "Pronomen",
                "examples": ["ich", "du", "er/sie/es"]
            },
            "preposition": {
                "description": "Prepositions requiring specific cases",
                "complexity": ["intermediate", "advanced"],
                "german_name": "Präposition",
                "examples": ["in", "auf", "mit", "für"]
            },
            "conjunction": {
                "description": "Coordinating and subordinating conjunctions",
                "complexity": ["intermediate", "advanced"],
                "german_name": "Konjunktion",
                "examples": ["und", "oder", "aber", "weil"]
            },
            "auxiliary": {
                "description": "Auxiliary verbs (haben/sein/werden)",
                "complexity": ["intermediate", "advanced"],
                "german_name": "Hilfsverb",
                "examples": ["haben", "sein", "werden"]
            },
            "modal": {
                "description": "Modal verbs (können/müssen/wollen/dürfen)",
                "complexity": ["intermediate", "advanced"],
                "german_name": "Modalverb",
                "examples": ["können", "müssen", "wollen"]
            },
            "particle": {
                "description": "Separable verb prefixes and particles",
                "complexity": ["advanced"],
                "german_name": "Partikel",
                "examples": ["auf", "aus", "ein", "mit"]
            }
        }

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Load color schemes for different complexity levels - BRIGHTER AND MORE VIBRANT"""
        return {
            "beginner": {
                "article": "#FF4444",      # Bright Red
                "noun": "#00FFCC",        # Bright Teal/Cyan
                "verb": "#0088FF",        # Bright Blue
                "pronoun": "#FF8800",     # Bright Orange
                "default": "#666666"      # Gray
            },
            "intermediate": {
                "article": "#FF4444",      # Bright Red
                "noun": "#00FFCC",        # Bright Teal/Cyan
                "verb": "#0088FF",        # Bright Blue
                "adjective": "#FFFF00",   # Bright Yellow
                "pronoun": "#FF8800",     # Bright Orange
                "preposition": "#AA00FF", # Bright Purple
                "conjunction": "#00AAFF", # Bright Sky Blue
                "default": "#666666"      # Gray
            },
            "advanced": {
                "article": "#FF4444",      # Bright Red
                "noun": "#00FFCC",        # Bright Teal/Cyan
                "verb": "#0088FF",        # Bright Blue
                "adjective": "#FFFF00",   # Bright Yellow
                "pronoun": "#FF8800",     # Bright Orange
                "preposition": "#AA00FF", # Bright Purple
                "conjunction": "#00AAFF", # Bright Sky Blue
                "auxiliary": "#00FF44",   # Bright Green
                "modal": "#FFAA00",       # Bright Gold
                "particle": "#FF00AA",    # Bright Magenta
                "default": "#666666"      # Gray
            }
        }

    def _create_role_hierarchy(self) -> Dict[str, str]:
        """Create role hierarchy for color inheritance"""
        return {
            "auxiliary": "verb",      # Auxiliary verbs inherit verb colors
            "modal": "verb",          # Modal verbs inherit verb colors
            "particle": "verb"        # Particles inherit verb colors
        }

    def _create_complexity_filters(self) -> Dict[str, List[str]]:
        """Create complexity-based role filtering"""
        return {
            "beginner": ["article", "noun", "verb", "pronoun"],
            "intermediate": ["article", "noun", "verb", "adjective", "pronoun", "preposition", "conjunction"],
            "advanced": ["article", "noun", "verb", "adjective", "pronoun", "preposition",
                        "conjunction", "auxiliary", "modal", "particle"]
        }

    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for German - ENHANCED with Spanish gold standard patterns"""
        return {
            'single': """
You are an expert linguist specializing in German grammar analysis.

Analyze this German sentence: "{{sentence}}"
Target word: "{{target_word}}"
Complexity level: "{{complexity}}"

For EACH word in the sentence, provide:
- Its specific grammatical function and role in German grammar
- How it contributes to the sentence meaning and structure
- Relationships with adjacent words and grammatical agreement
- German-specific features (case, gender, verb conjugations, word order)

MANDATORY: Respond with VALID JSON only. No explanations, no markdown, no code blocks.

REQUIRED JSON FORMAT:
{% raw %}
{
  "words": [
    {
      "word": "exact_word",
      "grammatical_role": "detailed role description (e.g., definite article, transitive verb, reflexive pronoun)",
      "grammatical_case": "nominative|accusative|dative|genitive|null",
      "gender": "masculine|feminine|neuter|null",
      "individual_meaning": "Detailed explanation of this word's function, relationships, and contribution to the sentence meaning"
    }
  ],
  "overall_analysis": {
    "sentence_structure": "brief description of German sentence structure",
    "key_features": "important German grammatical points"
  }
}
{% endraw %}

CRITICAL: Provide COMPREHENSIVE explanations for EVERY word, explaining their specific functions and relationships in detail. Do NOT repeat word prefixes in the explanations.

Grammatical roles: {{grammatical_roles}}
""",
            'batch': """
You are an expert linguist specializing in German grammar analysis.

Sentences: {{sentences}}
Target word: "{{target_word}}"
Complexity level: "{{complexity}}"

For EACH sentence, analyze EVERY word and provide:
- Specific grammatical function and role in German grammar
- How each word contributes to the sentence meaning and structure
- Relationships with adjacent words and grammatical agreement
- German-specific features (case, gender, verb conjugations, word order)

MANDATORY: Respond with VALID JSON only. No explanations, no markdown, no code blocks.

REQUIRED JSON FORMAT:
{% raw %}
{
  "batch_results": [
    {
      "sentence": "exact sentence text",
      "analysis": [
        {
          "word": "exact_word",
          "grammatical_role": "detailed role description (e.g., definite article, transitive verb, reflexive pronoun)",
          "grammatical_case": "nominative|accusative|dative|genitive|null",
          "gender": "masculine|feminine|neuter|null",
          "individual_meaning": "Detailed explanation of this word's function, relationships, and contribution to the sentence meaning"
        }
      ],
      "explanations": {
        "sentence_structure": "brief description of German sentence structure",
        "key_features": "important German grammatical points"
      }
    }
  ]
}
{% endraw %}

CRITICAL: Provide COMPREHENSIVE explanations for EVERY word in each sentence, explaining their specific functions and relationships in detail. Do NOT repeat word prefixes in the explanations.

Grammatical roles: {{grammatical_roles}}
""",

        }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme for given complexity level"""
        return self.color_schemes.get(complexity, self.color_schemes.get("beginner", {}))
    def get_grammatical_roles(self, complexity: str) -> Dict[str, str]:
        """Get grammatical roles for given complexity level"""
        return self.grammatical_roles.get(complexity, self.grammatical_roles.get('beginner', {}))
    def get_case_name(self, case_code: str) -> str:
        """Convert case code to full German name"""
        case_names = {
            'nom': 'Nominativ',
            'akk': 'Akkusativ',
            'dat': 'Dativ',
            'gen': 'Genitiv',
            'nominativ': 'Nominativ',
            'akkusativ': 'Akkusativ',
            'dativ': 'Dativ',
            'genitiv': 'Genitiv'
        }
        return case_names.get(case_code.lower(), case_code)

    def get_gender_name(self, gender_code: str) -> str:
        """Convert gender code to full German name"""
        gender_names = {
            'm': 'Maskulinum',
            'f': 'Femininum',
            'n': 'Neutrum',
            'maskulin': 'Maskulinum',
            'feminin': 'Femininum',
            'neutrum': 'Neutrum'
        }
        return gender_names.get(gender_code.lower(), gender_code)

    def get_roles_for_complexity(self, complexity: str) -> List[str]:
        """Get grammatical roles to analyze for given complexity"""
        return self.complexity_role_filters.get(complexity, self.complexity_role_filters.get("beginner", []))

    def get_role_description(self, role: str) -> str:
        """Get description for grammatical role"""
        role_info = self.grammatical_roles.get(role, {})
        return role_info.get("description", f"Unknown role: {role}")

    def get_grammatical_roles(self, complexity: str) -> Dict[str, str]:
        """Get grammatical roles for given complexity level"""
        return self.grammatical_roles.get(complexity, self.grammatical_roles.get('beginner', {}))
        """Get German name for grammatical role"""
        role_info = self.grammatical_roles.get(role, {})
        return role_info.get("german_name", role)

    def is_role_supported(self, role: str, complexity: str) -> bool:
        """Check if role is supported for given complexity"""
        supported_roles = self.get_roles_for_complexity(complexity)
        return role in supported_roles

    def get_prompt_template(self, complexity: str) -> str:
        """Get prompt template for given complexity"""
        return self.prompt_templates.get(complexity, self.prompt_templates.get("beginner", ""))

    def get_case_requirements(self, preposition: str) -> List[str]:
        """Get case requirements for preposition"""
        # Common German prepositions and their case requirements
        case_requirements = {
            # Akkusativ only
            'durch': ['akkusativ'],
            'für': ['akkusativ'],
            'gegen': ['akkusativ'],
            'ohne': ['akkusativ'],
            'um': ['akkusativ'],

            # Dativ only
            'aus': ['dativ'],
            'bei': ['dativ'],
            'mit': ['dativ'],
            'nach': ['dativ'],
            'von': ['dativ'],
            'zu': ['dativ'],

            # Akkusativ or Dativ (Wechselpräpositionen)
            'an': ['akkusativ', 'dativ'],
            'auf': ['akkusativ', 'dativ'],
            'hinter': ['akkusativ', 'dativ'],
            'in': ['akkusativ', 'dativ'],
            'neben': ['akkusativ', 'dativ'],
            'über': ['akkusativ', 'dativ'],
            'unter': ['akkusativ', 'dativ'],
            'vor': ['akkusativ', 'dativ'],
            'zwischen': ['akkusativ', 'dativ'],

            # Genitiv (less common)
            'wegen': ['genitiv'],
            'trotz': ['genitiv'],
            'während': ['genitiv']
        }

        return case_requirements.get(preposition.lower(), [])

    def get_verb_type(self, verb: str) -> str:
        """Determine verb type (stark/schwach/gemischt)"""
        # This is a simplified version - in practice would need a comprehensive verb database
        stark_verbs = ['sein', 'haben', 'werden', 'gehen', 'kommen', 'essen', 'trinken']
        gemischt_verbs = ['bringen', 'denken', 'kennen', 'nennen', 'rennen', 'senden', 'wenden']

        verb_stem = verb.lower().replace('ge', '').replace('te', '').replace('t', '')

        if verb_stem in stark_verbs:
            return 'stark'
        elif verb_stem in gemischt_verbs:
            return 'gemischt'
        else:
            return 'schwach'

    def validate_case_agreement(self, article: str, noun: str, case: str, gender: str) -> bool:
        """Validate case and gender agreement between article and noun"""
        # Simplified validation - in practice would need declension tables
        article_lower = article.lower()
        case_lower = case.lower()
        gender_lower = gender.lower()

        # Definite articles
        definite_articles = {
            'nominativ': {'maskulin': 'der', 'feminin': 'die', 'neutrum': 'das'},
            'akkusativ': {'maskulin': 'den', 'feminin': 'die', 'neutrum': 'das'},
            'dativ': {'maskulin': 'dem', 'feminin': 'der', 'neutrum': 'dem'},
            'genitiv': {'maskulin': 'des', 'feminin': 'der', 'neutrum': 'des'}
        }

        # Indefinite articles
        indefinite_articles = {
            'nominativ': {'maskulin': 'ein', 'feminin': 'eine', 'neutrum': 'ein'},
            'akkusativ': {'maskulin': 'einen', 'feminin': 'eine', 'neutrum': 'ein'},
            'dativ': {'maskulin': 'einem', 'feminin': 'einer', 'neutrum': 'einem'},
            'genitiv': {'maskulin': 'eines', 'feminin': 'einer', 'neutrum': 'eines'}
        }

        # Check definite articles
        if case_lower in definite_articles and gender_lower in definite_articles[case_lower]:
            if article_lower == definite_articles[case_lower][gender_lower]:
                return True

        # Check indefinite articles
        if case_lower in indefinite_articles and gender_lower in indefinite_articles[case_lower]:
            if article_lower == indefinite_articles[case_lower][gender_lower]:
                return True

        return False

    def get_adjective_declension_type(self, adjective: str, context: str) -> str:
        """Determine adjective declension type (stark/schwach/gemischt)"""
        # Simplified logic - in practice would need more context
        if context in ['nach bestimmtem artikel', 'nach demonstrativpronomen']:
            return 'schwach'
        elif context in ['nach unbestimmtem artikel', 'nach possessivpronomen']:
            return 'gemischt'
        else:
            return 'stark'

    def get_grammatical_roles(self, complexity: str) -> Dict[str, str]:
        """Get grammatical roles for given complexity level"""
        # Convert the German grammatical_roles structure to the expected format
        roles_for_complexity = {}
        for role_key, role_info in self.grammatical_roles.items():
            if complexity in role_info.get('complexity', []):
                german_name = role_info.get('german_name', role_key)
                description = role_info.get('description', '')
                roles_for_complexity[role_key] = f"{role_key} ({german_name}): {description}"

        return roles_for_complexity