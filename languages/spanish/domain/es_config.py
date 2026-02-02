# Spanish Configuration
# Language: Spanish (Español)
# Family: Indo-European (Romance)
# Script: Latin alphabet (LTR)
# Key Features: Gender agreement, verb conjugation, clitic pronouns

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class EsConfig:
    """
    Configuration for Spanish grammar analysis.
    Follows Clean Architecture pattern with external configuration.
    """

    def __init__(self):
        self.language_code = "es"
        self.language_name = "Spanish"
        self.language_name_native = "Español"

        # Spanish is LTR (Left to Right)
        self.is_rtl = False
        self.text_direction = "ltr"

        # Spanish script properties
        self.script_type = "alphabetic"
        self.unicode_range = (0x0000, 0x007F)  # Basic Latin

        # Load configuration from infrastructure/data directory
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "es_grammatical_roles.yaml") or self._load_grammatical_roles()
        self.verb_conjugations = self._load_yaml(config_dir / "es_verb_conjugations.yaml") or {}
        self.agreement_patterns = self._load_yaml(config_dir / "es_agreement_patterns.yaml") or {}
        self.clitic_patterns = self._load_yaml(config_dir / "es_clitic_patterns.yaml") or {}
        self.prep_distinctions = self._load_yaml(config_dir / "es_prep_distinctions.yaml") or {}

        # Load color schemes for different complexity levels
        self.color_schemes = self._load_color_schemes()

        # Create role hierarchy mapping for color inheritance
        self.role_hierarchy = self._create_role_hierarchy()

        # Create complexity-based role filtering
        self.complexity_role_filters = self._create_complexity_filters()

        # Load prompt templates
        self.prompt_templates = self._load_prompt_templates()

        # Spanish-specific linguistic features
        self.linguistic_features = {
            'gender_agreement': True,
            'number_agreement': True,
            'verb_conjugation': True,
            'clitic_pronouns': True,
            'ser_estar_distinction': True,
            'por_para_distinction': True,
            'subjunctive_mood': True,
            'differential_object_marking': True,
            'adjective_position_variation': True
        }

    def _load_grammatical_roles(self) -> Dict[str, Dict[str, str]]:
        """Load grammatical roles from external JSON file (fallback)"""
        config_path = Path(__file__).parent / "es_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('grammatical_roles', self._get_default_roles())
        return self._get_default_roles()

    def _get_default_roles(self) -> Dict[str, Dict[str, str]]:
        """Default grammatical roles for Spanish"""
        return {
            'beginner': {
                'noun': 'noun (sustantivo)',
                'verb': 'verb (verbo)',
                'adjective': 'adjective (adjetivo)',
                'pronoun': 'pronoun (pronombre)',
                'preposition': 'preposition (preposición)',
                'conjunction': 'conjunction (conjunción)',
                'determiner': 'determiner (determinante)',
                'adverb': 'adverb (adverbio)'
            },
            'intermediate': {
                'noun': 'noun (sustantivo)',
                'verb': 'verb (verbo)',
                'adjective': 'adjective (adjetivo)',
                'pronoun': 'pronoun (pronombre)',
                'preposition': 'preposition (preposición)',
                'conjunction': 'conjunction (conjunción)',
                'determiner': 'determiner (determinante)',
                'adverb': 'adverb (adverbio)',
                'auxiliary': 'auxiliary verb (verbo auxiliar)',
                'reflexive': 'reflexive pronoun (pronombre reflexivo)'
            },
            'advanced': {
                'noun': 'noun (sustantivo)',
                'verb': 'verb (verbo)',
                'adjective': 'adjective (adjetivo)',
                'pronoun': 'pronoun (pronombre)',
                'preposition': 'preposition (preposición)',
                'conjunction': 'conjunction (conjunción)',
                'determiner': 'determiner (determinante)',
                'adverb': 'adverb (adverbio)',
                'auxiliary': 'auxiliary verb (verbo auxiliar)',
                'reflexive': 'reflexive pronoun (pronombre reflexivo)',
                'clitic': 'clitic pronoun (pronombre clítico)',
                'subjunctive': 'subjunctive verb (verbo subjuntivo)'
            }
        }

    def _load_yaml(self, path: Path) -> Optional[Dict]:
        """Load YAML file if it exists"""
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return None

    def _load_json(self, path: Path) -> Optional[Dict]:
        """Load JSON file if it exists"""
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Load color schemes for grammatical roles"""
        return {
            'beginner': {
                'noun': '#FFAA00',
                'verb': '#4ECDC4',
                'adjective': '#FF44FF',
                'pronoun': '#9370DB',
                'preposition': '#4444FF',
                'conjunction': '#AAAAAA',
                'determiner': '#FFD700',
                'adverb': '#FF6347'
            },
            'intermediate': {
                'noun': '#FFAA00',
                'verb': '#4ECDC4',
                'adjective': '#FF44FF',
                'pronoun': '#9370DB',
                'preposition': '#4444FF',
                'conjunction': '#AAAAAA',
                'determiner': '#FFD700',
                'adverb': '#FF6347',
                'auxiliary': '#32CD32',
                'reflexive': '#FF69B4'
            },
            'advanced': {
                'noun': '#FFAA00',
                'verb': '#4ECDC4',
                'adjective': '#FF44FF',
                'pronoun': '#9370DB',
                'preposition': '#4444FF',
                'conjunction': '#AAAAAA',
                'determiner': '#FFD700',
                'adverb': '#FF6347',
                'auxiliary': '#32CD32',
                'reflexive': '#FF69B4',
                'clitic': '#8A2BE2',
                'subjunctive': '#DC143C'
            }
        }

    def _create_role_hierarchy(self) -> Dict[str, str]:
        """Create role hierarchy for color inheritance"""
        return {
            'clitic': 'pronoun',
            'reflexive': 'pronoun',
            'auxiliary': 'verb',
            'subjunctive': 'verb'
        }

    def _create_complexity_filters(self) -> Dict[str, List[str]]:
        """Create complexity-based role filtering"""
        return {
            'beginner': ['noun', 'verb', 'adjective', 'pronoun', 'preposition', 'conjunction', 'determiner', 'adverb'],
            'intermediate': ['noun', 'verb', 'adjective', 'pronoun', 'preposition', 'conjunction', 'determiner', 'adverb', 'auxiliary', 'reflexive'],
            'advanced': ['noun', 'verb', 'adjective', 'pronoun', 'preposition', 'conjunction', 'determiner', 'adverb', 'auxiliary', 'reflexive', 'clitic', 'subjunctive']
        }

    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for Spanish"""
        config_path = Path(__file__).parent.parent / "infrastructure" / "data" / "es_prompt_templates.yaml"
        if config_path.exists():
            return self._load_yaml(config_path) or self._get_default_prompt_templates()
        return self._get_default_prompt_templates()

    def _get_default_prompt_templates(self) -> Dict[str, str]:
        """Default prompt templates for Spanish - ENHANCED with gold standard patterns"""
        return {
            'single': """
You are an expert linguist specializing in Spanish grammar analysis.

Analyze this Spanish sentence: "{{sentence}}"
Target word: "{{target_word}}"

MANDATORY: Respond with VALID JSON only. No explanations, no markdown, no code blocks.

CRITICAL REQUIREMENTS:
1. Analyze EVERY SINGLE WORD in the sentence, not just the target word.
2. Provide UNIQUE, INDIVIDUAL meanings for EACH word. Do NOT repeat meanings across words.
3. Each word must have a DISTINCT contextual meaning specific to this sentence.
4. Use the EXACT grammatical roles listed below.

REQUIRED JSON FORMAT:
{% raw %}
{
  "words": [
    {
      "word": "exact_word",
      "grammatical_role": "noun|verb|adjective|pronoun|preposition|conjunction|determiner|adverb|auxiliary|reflexive|clitic|subjunctive",
      "individual_meaning": "UNIQUE contextual meaning specific to this word only"
    }
  ],
  "overall_analysis": {
    "sentence_structure": "brief description of Spanish sentence structure",
    "key_features": "important Spanish grammatical points"
  }
}
{% endraw %}

Grammatical roles: {{grammatical_roles}}
""",
            'batch': """
You are an expert linguist specializing in Spanish grammar analysis.

Sentences: {{sentences}}
Target word: "{{target_word}}"

MANDATORY: Respond with VALID JSON only. No explanations, no markdown, no code blocks.

CRITICAL REQUIREMENTS:
1. For EACH sentence, analyze EVERY SINGLE WORD in that sentence.
2. Provide UNIQUE, INDIVIDUAL meanings for EACH word in each sentence. Do NOT repeat meanings across words.
3. Each word must have a DISTINCT contextual meaning specific to its sentence.
4. Use the EXACT grammatical roles listed below.

REQUIRED JSON FORMAT:
{% raw %}
{
  "batch_results": [
    {
      "sentence": "exact sentence text",
      "analysis": [
        {
          "word": "exact_word",
          "grammatical_role": "noun|verb|adjective|pronoun|preposition|conjunction|determiner|adverb|auxiliary|reflexive|clitic|subjunctive",
          "individual_meaning": "UNIQUE contextual meaning specific to this word only"
        }
      ],
      "explanations": {
        "overall_structure": "brief description of Spanish sentence structure",
        "key_features": "important Spanish grammatical points"
      }
    }
  ]
}
{% endraw %}

Grammatical roles: {{grammatical_roles}}
"""
        }

    def get_grammatical_roles(self, complexity: str) -> Dict[str, str]:
        """Get grammatical roles for given complexity level"""
        return self.grammatical_roles.get(complexity, self.grammatical_roles.get('beginner', {}))

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme for given complexity level"""
        return self.color_schemes.get(complexity, self.color_schemes.get('beginner', {}))

    def is_spanish_text(self, text: str) -> bool:
        """Check if text contains Spanish characters"""
        spanish_chars = set('áéíóúüñ¿¡')
        return any(char in spanish_chars for char in text.lower())