# languages/{language}/{language}_config.py
"""
Language-specific configuration for {Language} analyzer.
Defines grammatical roles, color schemes, and language rules.
"""

class {Language}Config:
    """
    Configuration class for {Language} grammatical analysis.

    Defines:
    - Grammatical roles and categories
    - Color schemes for different complexity levels
    - Language-specific rules and constraints
    """

    def __init__(self):
        # Basic language information
        self.language_code = "{lang_code}"  # ISO language code
        self.language_name = "{Language}"   # Full language name

        # Core grammatical roles (CUSTOMIZE THIS)
        self.grammatical_roles = {{
            # Universal categories (present in most languages)
            'noun': '{noun_term}',
            'verb': '{verb_term}',
            'adjective': '{adjective_term}',
            'adverb': '{adverb_term}',
            'pronoun': '{pronoun_term}',
            'preposition': '{preposition_term}',  # or 'postposition'
            'conjunction': '{conjunction_term}',
            'determiner': '{determiner_term}',
            'interjection': '{interjection_term}',

            # Language-specific categories (ADD AS NEEDED)
            # Examples for different language families:

            # Romance languages
            'reflexive_verb': 'verbo_reflejo',
            'past_participle': 'participio_pasado',
            'gerund': 'gerundio',
            'imperative': 'imperativo',
            'subjunctive': 'subjuntivo',

            # Germanic languages
            'auxiliary_verb': 'Hilfsverb',
            'separable_prefix': 'trennbares_Präfix',
            'inseparable_prefix': 'untrennbares_Präfix',
            'strong_verb': 'starkes_Verb',

            # Slavic languages
            'aspect': 'вид',  # Perfective/imperfective
            'case': 'падеж',  # Nominative, genitive, etc.
            'reflexive_verb': 'возвратный_глагол',

            # Sino-Tibetan languages
            'classifier': '量词',
            'aspect_marker': '体标记',
            'structural_particle': '结构助词',
            'discourse_particle': '语篇助词',

            # Afroasiatic languages
            'root': 'جذر',  # Root morpheme
            'pattern': 'وزن',  # Morphological pattern
            'ablaut': 'إعلال',  # Vowel change
        }}

        # Language-specific attributes (CUSTOMIZE)
        self.genders = ['masculine', 'feminine']  # Add 'neuter' if applicable
        self.numbers = ['singular', 'plural']
        self.cases = []  # Add cases if applicable: ['nominative', 'accusative', 'dative', 'genitive']
        self.aspects = []  # Add aspects if applicable: ['perfective', 'imperfective']
        self.moods = []  # Add moods if applicable: ['indicative', 'subjunctive', 'imperative']
        self.tenses = []  # Add tenses if applicable

        # Word order pattern (CUSTOMIZE)
        self.word_order = "{SVO}"  # SVO, SOV, VSO, etc.

        # Special characters or scripts (CUSTOMIZE)
        self.has_diacritics = {False}  # True for languages with accents/diacritics
        self.script_type = "latin"  # latin, cyrillic, arabic, devanagari, han, etc.
        self.special_characters = []  # List of special characters used

        self._setup_color_schemes()

    def _setup_color_schemes(self):
        """Setup color schemes for different complexity levels"""

        # Beginner level - basic parts of speech (8-10 categories)
        self.beginner_colors = {{
            # Core categories - use distinct, accessible colors
            '{noun_term}': '#FF6B6B',        # Red - nouns
            '{verb_term}': '#4ECDC4',        # Teal - verbs
            '{adjective_term}': '#45B7D1',   # Blue - adjectives
            '{adverb_term}': '#FFA07A',      # Light Salmon - adverbs
            '{pronoun_term}': '#98D8C8',     # Mint - pronouns
            '{preposition_term}': '#F7DC6F', # Yellow - prepositions
            '{conjunction_term}': '#BB8FCE', # Light Purple - conjunctions
            '{determiner_term}': '#85C1E9'   # Light Blue - determiners
        }}

        # Intermediate level - adds grammatical complexity (12-15 categories)
        self.intermediate_colors = dict(self.beginner_colors)
        self.intermediate_colors.update({{
            # Add intermediate-level categories
            'reflexive_verb': '#F8C471',     # Orange
            'auxiliary_verb': '#82E0AA',     # Light Green
            'past_participle': '#F1948A',    # Light Coral
            'gerund': '#D7BDE2',            # Light Lavender
            'imperative': '#AED6F1',         # Light Sky Blue
            'subjunctive': '#FAD7A0',        # Light Orange
        }})

        # Advanced level - full grammatical analysis (15+ categories)
        self.advanced_colors = dict(self.intermediate_colors)
        self.advanced_colors.update({{
            # Add advanced categories
            'aspect': '#E8DAEF',             # Very Light Purple
            'case': '#D5DBDB',               # Light Gray
            'classifier': '#FCF3CF',         # Very Light Yellow
            'aspect_marker': '#D1F2EB',      # Very Light Teal
            'structural_particle': '#FDEDEC', # Very Light Red
            'discourse_particle': '#F2F3F4',  # Very Light Gray
            '{interjection_term}': '#D7BDE2' # Light Lavender
        }})

    def get_color_scheme(self, complexity):
        """Get color scheme for complexity level"""
        if complexity == 'beginner':
            return self.beginner_colors
        elif complexity == 'intermediate':
            return self.intermediate_colors
        else:  # advanced
            return self.advanced_colors

    def get_grammatical_roles(self, complexity):
        """Get grammatical roles for complexity level"""
        all_roles = self.grammatical_roles

        if complexity == 'beginner':
            # Return only basic roles for beginners
            basic_keys = ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                         'preposition', 'conjunction', 'determiner']
            return {{k: v for k, v in all_roles.items() if k in basic_keys}}

        elif complexity == 'intermediate':
            # Exclude most advanced roles
            exclude_keys = ['interjection', 'aspect', 'case', 'classifier',
                           'aspect_marker', 'structural_particle', 'discourse_particle']
            return {{k: v for k, v in all_roles.items() if k not in exclude_keys}}

        else:  # advanced
            return all_roles

    def get_language_specific_rules(self):
        """Get language-specific grammatical rules"""
        rules = {{
            'word_order': self.word_order,
            'gender_system': self.genders,
            'number_system': self.numbers,
            'script_type': self.script_type,
            'has_diacritics': self.has_diacritics,
        }}

        # Add optional systems
        if self.cases:
            rules['case_system'] = self.cases
        if self.aspects:
            rules['aspect_system'] = self.aspects
        if self.moods:
            rules['mood_system'] = self.moods
        if self.tenses:
            rules['tense_system'] = self.tenses
        if self.special_characters:
            rules['special_characters'] = self.special_characters

        return rules

    def validate_grammatical_role(self, role, complexity):
        """Validate if a grammatical role is valid for given complexity"""
        valid_roles = set(self.get_grammatical_roles(complexity).keys())
        return role in valid_roles

    def get_role_display_name(self, role_key, complexity='advanced'):
        """Get display name for grammatical role"""
        roles = self.get_grammatical_roles(complexity)
        return roles.get(role_key, role_key.replace('_', ' ').title())

    def get_color_for_role(self, role, complexity):
        """Get color for grammatical role"""
        colors = self.get_color_scheme(complexity)
        return colors.get(role, '#808080')  # Default gray

    def get_complexity_requirements(self):
        """Get requirements for each complexity level"""
        return {{
            'beginner': {{
                'max_sentence_length': 15,  # words
                'required_roles': ['noun', 'verb', 'adjective', 'adverb', 'pronoun'],
                'excluded_features': ['subjunctive', 'aspect', 'case', 'classifier']
            }},
            'intermediate': {{
                'max_sentence_length': 25,
                'required_roles': ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                                 'preposition', 'conjunction', 'determiner'],
                'excluded_features': ['complex_aspect', 'rare_cases']
            }},
            'advanced': {{
                'max_sentence_length': 50,
                'required_roles': list(self.grammatical_roles.keys()),
                'excluded_features': []  # All features included
            }}
        }}


# languages/{language}/{language}_prompt_builder.py
"""
AI prompt generation for {Language} grammar analysis.
Creates optimized prompts for Gemini AI models.
"""

import hashlib
from .{language}_config import {Language}Config


class {Language}PromptBuilder:
    """
    Builds AI prompts for {Language} grammatical analysis.

    Features:
    - Complexity-based prompt generation
    - Intelligent caching
    - Language-specific customization
    """

    def __init__(self):
        self.config = {Language}Config()
        self.prompt_cache = {{}}

    def build_single_prompt(self, sentence, target_word, complexity):
        """
        Build analysis prompt for single sentence.

        Args:
            sentence: The sentence to analyze
            target_word: Optional word to focus on
            complexity: Analysis complexity level

        Returns:
            Complete AI prompt string
        """

        cache_key = self._generate_cache_key(sentence, target_word, complexity)
        if cache_key in self.prompt_cache:
            return self.prompt_cache[cache_key]

        # Get language-specific configuration
        roles = self.config.get_grammatical_roles(complexity)
        language_rules = self.config.get_language_specific_rules()

        # Build target word instruction
        target_instruction = ""
        if target_word:
            target_instruction = f"\\nSPECIAL FOCUS: Pay particular attention to the word '{{target_word}}' and its grammatical function."

        # Build main prompt
        prompt = f"""
You are a linguistics expert specializing in {{self.config.language_name}} grammar analysis.

TASK: Analyze this {{self.config.language_name}} sentence with {{complexity}} complexity:
"{{sentence}}"{{target_instruction}}

GRAMMATICAL FRAMEWORK ({{complexity}} level):
{{self._format_roles_list(roles)}}

LANGUAGE-SPECIFIC RULES:
{{self._format_language_rules(language_rules)}}

REQUIREMENTS:
1. Identify EVERY word's grammatical role using ONLY the provided categories
2. Provide clear, accurate explanations in English
3. Maintain word order and sentence structure
4. Be linguistically precise and comprehensive

OUTPUT FORMAT:
{{
  "words": [
    {{
      "word": "exact_word_from_sentence",
      "grammatical_role": "exact_category_from_list",
      "meaning": "detailed_grammatical_explanation"
    }}
  ],
  "explanations": {{
    "overall_structure": "comprehensive_sentence_analysis",
    "key_features": "important_grammatical_concepts_demonstrated"
  }}
}}

Analyze now with expert precision:"""

        # Cache the prompt
        self.prompt_cache[cache_key] = prompt
        return prompt

    def _format_roles_list(self, roles):
        """Format grammatical roles for prompt"""
        return '\\n'.join(f"- {{role}}: {{self._get_role_description(role)}}"
                        for role in roles.keys())

    def _get_role_description(self, role):
        """Get description for grammatical role"""
        # Customize these descriptions for your language
        descriptions = {{
            'noun': 'person, place, thing, or idea',
            'verb': 'action or state of being',
            'adjective': 'describes or modifies a noun',
            'adverb': 'modifies verb, adjective, or another adverb',
            'pronoun': 'replaces a noun',
            'preposition': 'shows relationship between words',
            'conjunction': 'connects clauses or sentences',
            'determiner': 'introduces a noun',
            'interjection': 'expresses emotion or sudden feeling',
            # Add language-specific descriptions
        }}
        return descriptions.get(role, role.replace('_', ' '))

    def _format_language_rules(self, rules):
        """Format language-specific rules for prompt"""
        formatted = []
        for rule_name, rule_value in rules.items():
            if isinstance(rule_value, list):
                formatted.append(f"- {{rule_name.replace('_', ' ').title()}}: {{', '.join(rule_value)}}")
            else:
                formatted.append(f"- {{rule_name.replace('_', ' ').title()}}: {{rule_value}}")
        return '\\n'.join(formatted)

    def _generate_cache_key(self, sentence, target_word, complexity):
        """Generate cache key for prompt"""
        key_string = f"{{sentence}}|{{target_word or ''}}|{{complexity}}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def clear_cache(self):
        """Clear prompt cache"""
        self.prompt_cache.clear()


# languages/{language}/{language}_response_parser.py
"""
Response parsing and validation for {Language} AI responses.
Converts AI responses into standardized analysis format.
"""

import json
from .{language}_config import {Language}Config


class {Language}ResponseParser:
    """
    Parses and validates AI responses for {Language} analysis.

    Handles:
    - JSON response parsing
    - Data validation and sanitization
    - Confidence score calculation
    - Fallback parsing for malformed responses
    """

    def __init__(self):
        self.config = {Language}Config()

    def parse_response(self, response_text, sentence, complexity):
        """
        Parse AI response into standardized format.

        Args:
            response_text: Raw AI response text
            sentence: Original sentence being analyzed
            complexity: Analysis complexity level

        Returns:
            Standardized analysis result dictionary
        """

        try:
            # Extract JSON from response
            json_start = response_text.find('{{')
            json_end = response_text.rfind('}}') + 1
            json_str = response_text[json_start:json_end]

            parsed = json.loads(json_str)

            # Validate structure
            if 'words' not in parsed:
                raise ValueError("Missing 'words' array in response")

            # Process word explanations
            word_explanations = []
            colors = self.config.get_color_scheme(complexity)

            for word_info in parsed['words']:
                word = word_info.get('word', '')
                role = word_info.get('grammatical_role', '')
                meaning = word_info.get('meaning', '')

                # Get color for role
                color = colors.get(role, '#808080')  # Default gray

                word_explanations.append((word, role, color, meaning))

            # Process explanations
            explanations = parsed.get('explanations', {{}})
            overall_structure = explanations.get('overall_structure', '')
            key_features = explanations.get('key_features', '')

            # Calculate confidence
            confidence = self._calculate_confidence(word_explanations, sentence)

            return {{
                'word_explanations': word_explanations,
                'explanations': {{
                    'overall_structure': overall_structure,
                    'key_features': key_features
                }},
                'confidence_score': confidence,
                'sentence': sentence,
                'complexity': complexity
            }}

        except Exception as e:
            # Fallback parsing for malformed responses
            return self._fallback_parse(response_text, sentence, complexity)

    def _calculate_confidence(self, word_explanations, sentence):
        """
        Calculate confidence score for analysis.

        Factors:
        - Word coverage
        - Role validity
        - Explanation completeness
        """

        if not word_explanations:
            return 0.0

        # Check word coverage
        sentence_words = sentence.split()
        analyzed_words = len(word_explanations)
        coverage_ratio = min(analyzed_words / len(sentence_words), 1.0)

        # Check role validity
        valid_roles = set(self.config.get_grammatical_roles('advanced').keys())
        valid_count = sum(1 for _, role, _, _ in word_explanations if role in valid_roles)
        validity_ratio = valid_count / analyzed_words if analyzed_words > 0 else 0

        # Combine metrics (weighted average)
        confidence = (coverage_ratio * 0.5) + (validity_ratio * 0.5)

        return round(confidence, 2)

    def _fallback_parse(self, response_text, sentence, complexity):
        """
        Fallback parsing for non-JSON responses.
        Provides basic analysis when AI response is malformed.
        """

        # Simple word-by-word analysis
        words = sentence.split()
        colors = self.config.get_color_scheme(complexity)

        word_explanations = []
        for word in words:
            # Basic role assignment (customize for your language)
            role = self._guess_basic_role(word)
            color = colors.get(role, '#808080')
            meaning = f"Basic analysis: {{role.replace('_', ' ')}}"

            word_explanations.append((word, role, color, meaning))

        return {{
            'word_explanations': word_explanations,
            'explanations': {{
                'overall_structure': 'Fallback analysis due to parsing error',
                'key_features': 'Basic word-level analysis performed'
            }},
            'confidence_score': 0.3,
            'sentence': sentence,
            'complexity': complexity
        }}

    def _guess_basic_role(self, word):
        """Basic role guessing for fallback (customize for your language)"""
        word_lower = word.lower().strip('.,!?')

        # Language-specific basic heuristics (customize)
        basic_patterns = {{
            # Add your language's common patterns
            'noun': [],  # Default fallback
            'verb': [],  # Add common verb endings
            'adjective': [],  # Add common adjective patterns
            'pronoun': [],  # Add common pronouns
            'preposition': [],  # Add common prepositions
            'conjunction': [],  # Add common conjunctions
            'determiner': []  # Add common determiners
        }}

        # Check patterns (customize logic for your language)
        for role, patterns in basic_patterns.items():
            if any(pattern in word_lower for pattern in patterns):
                return role

        # Default to noun (most common)
        return 'noun'


# languages/{language}/{language}_validator.py
"""
Validation logic for {Language} grammar analysis results.
Ensures analysis quality and provides detailed feedback.
"""

from .{language}_config import {Language}Config


class {Language}Validator:
    """
    Validates {Language} grammar analysis results.

    Performs:
    - Structural validation
    - Linguistic accuracy checks
    - Quality metric calculation
    - Issue identification and reporting
    """

    def __init__(self):
        self.config = {Language}Config()

    def validate_analysis(self, result):
        """
        Validate analysis result for {Language}.

        Args:
            result: Analysis result dictionary

        Returns:
            Validation result with issues and quality metrics
        """

        validation_result = {{
            'is_valid': True,
            'issues': [],
            'confidence_score': result.get('confidence_score', 0),
            'quality_metrics': {{}}
        }}

        word_explanations = result.get('word_explanations', [])

        # Check word coverage
        sentence_words = result.get('sentence', '').split()
        if len(word_explanations) != len(sentence_words):
            validation_result['issues'].append({{
                'type': 'coverage',
                'severity': 'warning',
                'message': f'Word count mismatch: {{len(word_explanations)}} analyzed vs {{len(sentence_words)}} in sentence'
            }})

        # Check role validity
        valid_roles = set(self.config.get_grammatical_roles('advanced').keys())
        invalid_roles = []

        for word, role, color, meaning in word_explanations:
            if role not in valid_roles:
                invalid_roles.append(f"'{{word}}': '{{role}}'")

        if invalid_roles:
            validation_result['issues'].append({{
                'type': 'invalid_roles',
                'severity': 'error',
                'message': f'Invalid grammatical roles: {{", ".join(invalid_roles[:3])}}'
            }})
            validation_result['is_valid'] = False

        # Check for empty meanings
        empty_meanings = [word for word, role, color, meaning in word_explanations
                         if not meaning.strip()]
        if empty_meanings:
            validation_result['issues'].append({{
                'type': 'empty_meanings',
                'severity': 'warning',
                'message': f'Words without explanations: {{", ".join(empty_meanings[:3])}}'
            }})

        # Language-specific validations (customize)
        language_issues = self._validate_language_specific_rules(word_explanations, result)
        validation_result['issues'].extend(language_issues)

        if any(issue['severity'] == 'error' for issue in language_issues):
            validation_result['is_valid'] = False

        # Calculate quality metrics
        validation_result['quality_metrics'] = {{
            'word_coverage': len(word_explanations) / len(sentence_words) if sentence_words else 0,
            'role_validity': 1 - (len(invalid_roles) / len(word_explanations)) if word_explanations else 0,
            'explanation_completeness': 1 - (len(empty_meanings) / len(word_explanations)) if word_explanations else 0
        }}

        # Adjust confidence based on validation
        if not validation_result['is_valid']:
            validation_result['confidence_score'] *= 0.8

        return validation_result

    def _validate_language_specific_rules(self, word_explanations, result):
        """
        Validate language-specific grammatical rules.

        Customize this method for your language's specific requirements.
        """
        issues = []

        # Example validations (customize for your language):

        # Check for required grammatical elements
        # has_subject = any(role in ['noun', 'pronoun'] for _, role, _, _ in word_explanations)
        # if not has_subject:
        #     issues.append({{
        #         'type': 'missing_subject',
        #         'severity': 'warning',
        #         'message': 'Sentence appears to be missing a subject'
        #     }})

        # Check agreement rules
        # agreement_issues = self._check_agreement_rules(word_explanations)
        # issues.extend(agreement_issues)

        # Check word order
        # word_order_issues = self._check_word_order_rules(word_explanations, result.get('sentence', ''))
        # issues.extend(word_order_issues)

        return issues

    def _check_agreement_rules(self, word_explanations):
        """Check grammatical agreement rules (customize for your language)"""
        issues = []

        # Example: Check adjective-noun agreement
        # nouns = [(i, word, role) for i, (word, role, _, _) in enumerate(word_explanations) if role == 'noun']
        # adjectives = [(i, word, role) for i, (word, role, _, _) in enumerate(word_explanations) if role == 'adjective']

        # for adj_idx, adj_word, _ in adjectives:
        #     # Check if adjective agrees with nearby noun
        #     # (Implement language-specific agreement logic)
        #     pass

        return issues

    def _check_word_order_rules(self, word_explanations, sentence):
        """Check word order rules (customize for your language)"""
        issues = []

        # Example: Check for basic word order violations
        # words = [word for word, _, _, _ in word_explanations]
        # reconstructed = ' '.join(words)

        # if reconstructed != sentence.strip():
        #     issues.append({{
        #         'type': 'word_order',
        #         'severity': 'info',
        #         'message': 'Word order analysis completed'
        #     }})

        return issues


# languages/{language}/{language}_analyzer.py
"""
Main analyzer facade for {Language} grammar analysis.
Orchestrates all domain components following Clean Architecture.
"""

from .{language}_config import {Language}Config
from .{language}_prompt_builder import {Language}PromptBuilder
from .{language}_response_parser import {Language}ResponseParser
from .{language}_validator import {Language}Validator


class {Language}Analyzer:
    """
    Main analyzer for {Language} grammar analysis.

    Features:
    - Clean Architecture facade pattern
    - Component orchestration
    - Error handling and recovery
    - Performance monitoring
    """

    def __init__(self):
        # Initialize domain components
        self.config = {Language}Config()
        self.prompt_builder = {Language}PromptBuilder()
        self.response_parser = {Language}ResponseParser()
        self.validator = {Language}Validator()

        # Initialize infrastructure (will be injected)
        self.ai_service = None
        self.performance_monitor = None

    def analyze_grammar(self, sentence, target_word, complexity, api_key):
        """
        Analyze {Language} sentence grammar.

        Args:
            sentence: The sentence to analyze
            target_word: Optional word to focus on
            complexity: 'beginner', 'intermediate', or 'advanced'
            api_key: Gemini API key

        Returns:
            Analysis result dictionary
        """

        try:
            # Build analysis prompt
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

            # Get AI response
            if not self.ai_service:
                # Lazy initialization - customize import path
                from ..infrastructure.{language}_ai_service import {Language}AIService
                self.ai_service = {Language}AIService()

            response = self.ai_service.get_analysis(prompt, api_key)

            # Parse response
            result = self.response_parser.parse_response(response, sentence, complexity)

            # Validate result
            validation = self.validator.validate_analysis(result)

            # Update result with validation info
            result['validation'] = validation

            # Adjust confidence based on validation
            if not validation['is_valid']:
                result['confidence_score'] *= 0.8

            # Record performance metrics
            if self.performance_monitor:
                self.performance_monitor.record_analysis(complexity, result['confidence_score'])

            return result

        except Exception as e:
            # Return error result
            error_result = {{
                'word_explanations': [],
                'explanations': {{
                    'overall_structure': f'Analysis failed: {{str(e)}}',
                    'key_features': 'Error occurred during processing'
                }},
                'confidence_score': 0.0,
                'sentence': sentence,
                'complexity': complexity,
                'error': str(e)
            }}

            # Record error metrics
            if self.performance_monitor:
                self.performance_monitor.record_error(str(e))

            return error_result

    def get_supported_complexities(self):
        """Get list of supported complexity levels"""
        return ['beginner', 'intermediate', 'advanced']

    def get_language_info(self):
        """Get language information and capabilities"""
        return {{
            'language_code': self.config.language_code,
            'language_name': self.config.language_name,
            'supported_complexities': self.get_supported_complexities(),
            'grammatical_roles': self.config.get_grammatical_roles('advanced'),
            'language_specific_rules': self.config.get_language_specific_rules()
        }}

    def clear_caches(self):
        """Clear all internal caches"""
        self.prompt_builder.clear_cache()
        # Clear other component caches as needed


# infrastructure/{language}_ai_service.py
"""
AI service integration for {Language} analysis.
Handles Gemini API communication with error recovery.
"""

import time
import google.generativeai as genai
from .{language}_circuit_breaker import {Language}CircuitBreaker


class {Language}AIService:
    """
    AI service for {Language} grammar analysis.

    Features:
    - Gemini API integration
    - Circuit breaker pattern
    - Error recovery and retry logic
    - Performance monitoring
    """

    def __init__(self):
        self.circuit_breaker = {Language}CircuitBreaker()
        self.performance_monitor = None

    def get_analysis(self, prompt, api_key):
        """
        Get grammatical analysis from AI service.

        Args:
            prompt: Analysis prompt
            api_key: Gemini API key

        Returns:
            AI response text

        Raises:
            CircuitBreakerOpenException: When circuit breaker is open
            Exception: For other API errors
        """

        def api_call():
            return self._call_gemini_api(prompt, api_key)

        # Execute with circuit breaker protection
        return self.circuit_breaker.call(api_call)

    def _call_gemini_api(self, prompt, api_key):
        """
        Call Gemini API with error handling.

        Args:
            prompt: Analysis prompt
            api_key: API key

        Returns:
            API response text
        """

        try:
            # Configure API
            genai.configure(api_key=api_key)

            # Select model (customize based on language complexity)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')

            # Make API call
            start_time = time.time()
            response = model.generate_content(prompt)
            end_time = time.time()

            # Record performance
            if self.performance_monitor:
                latency = end_time - start_time
                self.performance_monitor.record_ai_latency(latency)

            return response.text

        except Exception as e:
            # Record error
            if self.performance_monitor:
                self.performance_monitor.record_ai_error(str(e))

            # Re-raise for circuit breaker handling
            raise e

    def set_performance_monitor(self, monitor):
        """Set performance monitoring instance"""
        self.performance_monitor = monitor


# infrastructure/{language}_circuit_breaker.py
"""
Circuit breaker implementation for {Language} AI service.
Prevents cascade failures and enables graceful degradation.
"""

import time
from enum import Enum


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class {Language}CircuitBreaker:
    """
    Circuit breaker for {Language} AI service protection.

    States:
    - CLOSED: Normal operation
    - OPEN: Failing, requests blocked
    - HALF_OPEN: Testing recovery
    """

    def __init__(self,
                 failure_threshold=5,
                 recovery_timeout=60,
                 expected_exception=(Exception,)):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception types to count as failures
        """

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: When circuit breaker is open
        """

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerOpenException("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            self._on_success()
            return result

        except self.expected_exception as e:
            # Failure - increment counter
            self._on_failure()
            raise e

    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True

        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def get_state(self):
        """Get current circuit breaker state"""
        return self.state.value

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None