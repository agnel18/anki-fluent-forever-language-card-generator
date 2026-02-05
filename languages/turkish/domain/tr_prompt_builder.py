# languages/turkish/domain/tr_prompt_builder.py
"""
Turkish Prompt Builder - Domain Component

TURKISH PROMPT BUILDING:
This component demonstrates how to construct effective AI prompts for Turkish grammar analysis.
It uses Jinja2 templates for maintainable, parameterized prompts.

RESPONSIBILITIES:
1. Build single-sentence analysis prompts
2. Build batch analysis prompts for multiple sentences
3. Parameterize prompts with Turkish-specific context
4. Ensure prompts produce consistent JSON output
5. Handle template rendering errors gracefully

PROMPT ENGINEERING PRINCIPLES:
- Clear instructions: Explicit JSON structure requirements
- Contextual information: Include complexity level and target word
- Error prevention: Specify exact field names and formats
- Language specificity: Turkish-appropriate grammatical categories
- Consistency: Same structure for single and batch prompts

USAGE FOR TURKISH:
1. Copy template structure and modify content
2. Update grammatical role lists for Turkish features
3. Adjust examples and instructions for Turkish-specific features
4. Test prompts produce valid JSON with expected structure
5. Include Turkish-specific prompt context and examples

INTEGRATION:
- Called by main analyzer for prompt generation
- Receives configuration from TrConfig
- Templates support parameterization for different contexts
- Error handling prevents crashes from template issues
"""

import logging
import json
from typing import Dict, List, Any
from jinja2 import Template
from .tr_config import TrConfig

logger = logging.getLogger(__name__)

class TrPromptBuilder:
    """
    Builds prompts for Turkish grammar analysis using templates.

    TURKISH TEMPLATE SYSTEM:
    - Jinja2 templates: Maintainable and parameterized
    - Language-specific: Turkish-appropriate instructions and examples
    - Morphological focus: Emphasis on agglutination and vowel harmony
    - Case system: Clear case marker identification
    - Prevention-at-source: Explicit rules to prevent common errors
    """

    def __init__(self, config: TrConfig):
        """
        Initialize prompt builder with configuration.

        TURKISH CONFIGURATION INTEGRATION:
        - Access to grammatical roles and color schemes
        - Template access for different prompt types
        - Language-specific settings and patterns
        """
        self.config = config
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Template]:
        """Load Jinja2 templates for different prompt types."""
        import os
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        templates = {}

        # Single sentence template
        single_path = os.path.join(template_dir, 'tr_single_prompt.j2')
        if os.path.exists(single_path):
            with open(single_path, 'r', encoding='utf-8') as f:
                templates['single'] = Template(f.read())
        else:
            templates['single'] = Template(self._get_default_single_template())

        # Batch template
        batch_path = os.path.join(template_dir, 'tr_batch_prompt.j2')
        if os.path.exists(batch_path):
            with open(batch_path, 'r', encoding='utf-8') as f:
                templates['batch'] = Template(f.read())
        else:
            templates['batch'] = Template(self._get_default_batch_template())

        return templates

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """
        Build prompt for single Turkish sentence analysis.

        TURKISH SINGLE PROMPT FEATURES:
        - Morphological decomposition requirements
        - Vowel harmony validation instructions
        - Case system identification
        - Agglutination handling
        - Complexity-appropriate detail level
        """
        try:
            template = Template(self.config.prompt_templates["single"])
            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'language_name': self.config.language_name,
                'grammatical_roles_list': self._get_grammatical_roles_list(complexity),
            }

            prompt = template.render(**context)
            logger.debug(f"Built single prompt for sentence: {sentence[:50]}...")
            return prompt

        except Exception as e:
            logger.error(f"Failed to build single prompt: {e}")
            return self._create_fallback_single_prompt(sentence, target_word, complexity)

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """
        Build prompt for batch Turkish sentence analysis.

        TURKISH BATCH PROMPT FEATURES:
        - Consistent morphological analysis across sentences
        - Shared vowel harmony rules
        - Case system consistency
        - Efficient processing of multiple sentences
        """
        try:
            template = Template(self.config.prompt_templates["batch"])
            context = {
                'sentences': '\n'.join(f'{i+1}. {sentence}' for i, sentence in enumerate(sentences)),
                'target_word': target_word,
                'complexity': complexity,
                'language_name': self.config.language_name,
                'sentence_count': len(sentences),
            }

            prompt = template.render(**context)
            logger.debug(f"Built batch prompt for {len(sentences)} sentences")
            return prompt

        except Exception as e:
            logger.error(f"Failed to build batch prompt: {e}")
            return self._create_fallback_batch_prompt(sentences, target_word, complexity)

    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """Get formatted list of grammatical roles for the given complexity."""
        color_scheme = self.config.get_color_scheme(complexity)
        roles_list = []

        for role, color in color_scheme.items():
            if role != 'other':  # Skip the default 'other' category
                roles_list.append(f"- {role}: {color}")

        return '\n'.join(roles_list)

    def _get_default_single_template(self) -> str:
        """Default single sentence analysis template."""
        return """Analyze this Turkish sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

TURKISH GRAMMAR ANALYSIS REQUIREMENTS:

MORPHOLOGICAL ANALYSIS:
- Identify root words in agglutinated forms
- Break down suffixes and their functions
- Note vowel harmony patterns (back/front vowels)
- Identify case markers and their grammatical functions

GRAMMATICAL ROLES:
{{grammatical_roles_list}}

CASE SYSTEM (6 cases in Turkish):
- Nominative: subject case, no marker
- Accusative: direct object, -(y)i marker
- Dative: indirect object/direction, -(y)e marker
- Locative: location, -(d)e marker
- Ablative: source/origin, -(d)en marker
- Genitive: possession, -(n)in marker

OUTPUT FORMAT:
Return JSON with analysis array containing word, grammatical_role, individual_meaning, and color for each word."""

    def _get_default_batch_template(self) -> str:
        """Default batch analysis template."""
        return """Analyze these Turkish sentences:
{{sentences}}

Target word: {{target_word}}
Complexity level: {{complexity}}

TURKISH GRAMMAR ANALYSIS REQUIREMENTS:
- Identify morphological structure for each sentence
- Note vowel harmony patterns
- Identify case markers and their functions
- Use consistent grammatical roles: {{grammatical_roles_list}}

Return JSON with batch_results array containing analysis for each sentence."""
        """Create basic fallback prompt for single sentence."""
        return f"""Analyze this {self.config.language_name} sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

CRITICAL TURKISH RULES:
- Identify morphological structure (root + suffixes)
- Note vowel harmony patterns
- Identify case markers and their functions
- Explain agglutination where present

Return JSON with words array containing grammatical_role and individual_meaning for each word."""

    def _create_fallback_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Create basic fallback prompt for batch sentences."""
        sentences_text = '\n'.join(sentences)
        return f"""Analyze these {self.config.language_name} sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}

CRITICAL TURKISH RULES:
- Identify morphological structure for each sentence
- Note vowel harmony patterns
- Identify case markers and their functions
- Explain agglutination where present

Return JSON with batch_results array."""
        return """
You are a Turkish language analysis expert. Analyze the following Turkish text with {{ complexity }} complexity level.

CRITICAL TURKISH LINGUISTIC RULES (PREVENTION-AT-SOURCE):
========================================================

1. AGGLUTINATION HANDLING:
   - Turkish uses agglutination: words are formed by adding suffixes to roots
   - Each suffix carries specific grammatical meaning
   - NEVER analyze compound words as single units without morphological breakdown
   - Example: "evimdeki" = ev(im)(de)(ki) = house(my)(at)(that_is_in)

2. VOWEL HARMONY (MANDATORY):
   - Suffix vowels harmonize with the last vowel of the root
   - BACK VOWELS: a, ı, o, u → suffixes use: a, ı, u (for back harmony)
   - FRONT VOWELS: e, i, ö, ü → suffixes use: e, i, ü (for front harmony)
   - Example: "ev" (back) + "de" (back) = "evde" (at home)

3. CASE SYSTEM (REQUIRED ANALYSIS):
   - Nominative: subject (no marker) - "ev" (house)
   - Accusative: direct object - "ev-i" (house-ACC)
   - Dative: indirect object - "ev-e" (house-DAT)
   - Locative: location - "ev-de" (house-LOC)
   - Ablative: source - "ev-den" (house-ABL)
   - Genitive: possession - "ev-in" (house-GEN)

4. POSSESSIVE SUFFIXES:
   - 1SG: -im/ım/um/üm (benim evim = my house)
   - 2SG: -in/ın/un/ün (senin evin = your house)
   - 3SG: -i/ı/u/ü (onun evi = his/her house)
   - 1PL: -imiz/ımız/umuz/ümüz (bizim evimiz = our house)
   - 2PL: -iniz/ınız/unuz/ünüz (sizin eviniz = your house)
   - 3PL: -leri (onların evleri = their house)

5. WORD ORDER: Subject-Object-Verb (SOV)
   - "Ben kitap okuyorum." = I book read-PRES-1SG = "I am reading a book."
   - Case markers clarify roles, word order can vary for emphasis

6. QUESTION FORMATION:
   - Question particle "mı/mi/mu/mü" follows vowel harmony
   - Added to focused element: "Kitap mı okuyorsun?" (Are you reading a book?)

ANALYSIS REQUIREMENTS:
=====================

Text to analyze: "{{ text }}"

Complexity Level: {{ complexity }}

For each word in the text:
1. MORPHOLOGICAL BREAKDOWN: Show root + suffixes with meanings
2. GRAMMATICAL CATEGORY: Use only these categories:
   {% for category in categories %}
   - {{ category }}
   {% endfor %}
3. SYNTACTIC ROLE: Subject, object, modifier, etc.
4. VOWEL HARMONY: Explain harmony rules applied
5. COLOR CODE: Use provided color scheme

Output Format (JSON):
{
  "analysis": [
    {
      "word": "original_word",
      "morphology": {
        "root": "root_word",
        "suffixes": [
          {"form": "suffix", "meaning": "grammatical_meaning", "harmony": "harmony_rule"}
        ]
      },
      "category": "grammatical_category",
      "role": "syntactic_role",
      "color": "hex_color_code",
      "complexity": "{{ complexity }}"
    }
  ],
  "sentence_structure": "brief_description",
  "linguistic_features": ["feature1", "feature2"],
  "validation": {
    "vowel_harmony_correct": true/false,
    "morphology_complete": true/false,
    "case_system_applied": true/false
  }
}

PREVENTION RULES:
================
- NEVER skip morphological analysis for agglutinated words
- ALWAYS explain vowel harmony applications
- ALWAYS identify case markers and their functions
- NEVER confuse word order with grammatical roles (cases clarify)
- ALWAYS validate harmony rules are followed correctly
"""

    def _create_fallback_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Create basic fallback prompt for single sentence."""
        return f"""Analyze this {self.config.language_name} sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

CRITICAL TURKISH RULES:
- Identify morphological structure
- Note vowel harmony patterns
- Identify case markers and their functions
- Explain agglutination where present

Return JSON with word-by-word analysis."""

    def build_analysis_prompt(self, text: str, complexity: str = 'beginner') -> str:
        """Build the main analysis prompt with prevention-at-source rules."""

        # Get categories for complexity level
        categories = self.config.get_categories_for_complexity(complexity)

        # Template variables
        template_vars = {
            'text': text,
            'complexity': complexity,
            'categories': categories,
            'config': self.config,
            'vowel_harmony_rules': self._get_vowel_harmony_rules(),
            'case_system': self._get_case_system_description(),
            'examples': self._get_prevention_examples()
        }

        # Use template if available, otherwise use default
        if 'analysis' in self.templates:
            return self.templates['analysis'].render(**template_vars)
        else:
            # Fallback to method-based template
            return self._build_analysis_prompt_fallback(text, complexity, categories)

    def _build_analysis_prompt_fallback(self, text: str, complexity: str, categories: List[str]) -> str:
        """Fallback prompt building without templates."""
        return f"""
You are a Turkish language analysis expert. Analyze the following Turkish text with {complexity} complexity level.

CRITICAL TURKISH LINGUISTIC RULES (PREVENTION-AT-SOURCE):

1. AGGLUTINATION: Turkish words are formed by adding suffixes to roots. Each suffix has specific meaning.
   Example: "evimdeki" = ev(im)(de)(ki) = house(my)(at)(that_is_in)

2. VOWEL HARMONY: Suffix vowels must harmonize with root vowels:
   - BACK vowels (a, ı, o, u) → suffixes use back vowels (a, ı, u)
   - FRONT vowels (e, i, ö, ü) → suffixes use front vowels (e, i, ü)

3. CASE SYSTEM: Six cases clarify grammatical roles regardless of word order:
   - Nominative: subject (no marker)
   - Accusative: direct object (-i/ı/u/ü)
   - Dative: indirect object (-e/a)
   - Locative: location (-de/da)
   - Ablative: source (-den/dan)
   - Genitive: possession (-in/ın/un/ün)

4. WORD ORDER: Subject-Object-Verb (SOV), but flexible due to case markers.

Text to analyze: "{text}"

For each word, provide:
- Morphological breakdown (root + suffixes)
- Grammatical category (from: {', '.join(categories)})
- Syntactic role
- Vowel harmony explanation
- Color code

Output as JSON with analysis array.
"""

    def _get_vowel_harmony_rules(self) -> Dict[str, Any]:
        """Get detailed vowel harmony rules for prompt."""
        return {
            'back_vowels': self.config.morphological_features['vowel_harmony']['back_vowels'],
            'front_vowels': self.config.morphological_features['vowel_harmony']['front_vowels'],
            'rounded_vowels': self.config.morphological_features['vowel_harmony']['rounded_vowels'],
            'unrounded_vowels': self.config.morphological_features['vowel_harmony']['unrounded_vowels'],
            'examples': [
                {'root': 'ev', 'suffix': 'de', 'result': 'evde', 'rule': 'back harmony'},
                {'root': 'kitap', 'suffix': 'da', 'result': 'kitapta', 'rule': 'back harmony'},
                {'root': 'şehir', 'suffix': 'de', 'result': 'şehirde', 'rule': 'front harmony'}
            ]
        }

    def _get_case_system_description(self) -> Dict[str, Any]:
        """Get case system description for prompt."""
        cases = self.config.morphological_features['cases']
        return {
            'cases': cases,
            'examples': [
                {'case': 'nominative', 'word': 'ev', 'meaning': 'house (subject)'},
                {'case': 'accusative', 'word': 'evi', 'meaning': 'house (direct object)'},
                {'case': 'dative', 'word': 'eve', 'meaning': 'to house (indirect object)'},
                {'case': 'locative', 'word': 'evde', 'meaning': 'at home (location)'},
                {'case': 'ablative', 'word': 'evden', 'meaning': 'from home (source)'},
                {'case': 'genitive', 'word': 'evin', 'meaning': 'house\'s (possession)'}
            ]
        }

    def _get_prevention_examples(self) -> List[Dict[str, Any]]:
        """Get examples that prevent common analysis errors."""
        return [
            {
                'error_type': 'missing_morphology',
                'wrong': 'Analyze "evimdeki" as single adjective',
                'correct': 'Break down: ev(im)(de)(ki) = house(my)(at)(that_is_in)',
                'prevention': 'Always decompose agglutinated words'
            },
            {
                'error_type': 'wrong_harmony',
                'wrong': 'kitap + de = kitapde (wrong harmony)',
                'correct': 'kitap + da = kitapta (correct back harmony)',
                'prevention': 'Check vowel harmony for every suffix'
            },
            {
                'error_type': 'ignoring_cases',
                'wrong': 'Word order determines grammatical role',
                'correct': 'Case markers determine grammatical role',
                'prevention': 'Prioritize case markers over word position'
            }
        ]

    def build_validation_prompt(self, analysis_result: Dict[str, Any]) -> str:
        """Build prompt to validate analysis results."""
        return f"""
Validate this Turkish language analysis for accuracy:

Analysis Result:
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

Validation Checks:
1. Morphological decomposition complete for agglutinated words?
2. Vowel harmony rules correctly applied?
3. Case markers properly identified and explained?
4. Grammatical categories appropriate for complexity level?
5. Syntactic roles consistent with case markers?

Output validation results as JSON.
"""

    def get_supported_complexities(self) -> List[str]:
        """Get list of supported complexity levels."""
        return self.config.complexity_levels

    def validate_prompt_structure(self, prompt: str) -> List[str]:
        """Validate that prompt contains all required prevention rules."""
        required_elements = [
            'AGGLUTINATION',
            'VOWEL HARMONY',
            'CASE SYSTEM',
            'MORPHOLOGICAL BREAKDOWN',
            'PREVENTION'
        ]

        missing = []
        for element in required_elements:
            if element not in prompt:
                missing.append(element)

        return missing