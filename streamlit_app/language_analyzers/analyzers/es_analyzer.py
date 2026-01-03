# Spanish Grammar Analyzer
# Auto-generated analyzer for Spanish (español)
# Language Family: Romance
# Script Type: alphabetic
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class EsAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Spanish (español).

    Key Features: ['verb_conjugation', 'noun_adjective_agreement', 'pronoun_usage', 'sentence_structure', 'idiomatic_expressions']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "es"
    LANGUAGE_NAME = "Spanish"

    def __init__(self):
        config = LanguageConfig(
            code="es",
            name="Spanish",
            native_name="español",
            family="Romance",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=['verb_conjugation', 'noun_adjective_agreement', 'pronoun_usage', 'sentence_structure', 'idiomatic_expressions'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

        # Language-specific patterns and rules
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize language-specific patterns and rules"""
        # Override in language-specific implementations
        pass

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate AI prompt for Spanish grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt with word-by-word explanations"""
        base_prompt = """Analyze this ENTIRE Spanish sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Its individual meaning and pronunciation (in IPA)
- Its grammatical role and function in this context (USE ONLY: pronoun, noun, verb, adjective, adverb, postposition, conjunction, interjection, other)
- How it shows gender agreement (masculine/feminine/neuter)
- How it shows number agreement (singular/plural)
- Why it's important for learners

IMPORTANT: In Spanish, articles (el, la, los, las, un, una, unos, unas) should be classified as "other", NOT as "adjective" or "determiner".
Prepositions (a, de, en, con, por, para, etc.) should be classified as "other", NOT as "postposition".
Common Spanish grammatical roles: pronouns (yo, tú, él/ella, nosotros), nouns (casa, perro), verbs (ser, estar, hablar), adjectives (grande, bonito), adverbs (muy, aquí), conjunctions (y, o, pero), interjections (¡ay!, ¡hola!).

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "la",
      "individual_meaning": "the (feminine singular definite article)",
      "pronunciation": "la",
      "grammatical_role": "other",
      "color": "#888888",
      "gender_agreement": "feminine",
      "number_agreement": "singular",
      "importance": "Definite article indicating specificity"
    },
    {
      "word": "casa",
      "individual_meaning": "house/home",
      "pronunciation": "ˈkasa",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "gender_agreement": "feminine",
      "number_agreement": "singular",
      "importance": "Common noun for buildings and homes"
    },
    {
      "word": "es",
      "individual_meaning": "is (third person singular of ser)",
      "pronunciation": "es",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "n/a",
      "number_agreement": "singular",
      "importance": "Essential copula verb for identity and characteristics"
    }
  ],
  "word_combinations": [
    {
      "word": "la casa",
      "words": ["la", "casa"],
      "combined_meaning": "the house",
      "grammatical_structure": "article + noun",
      "usage_notes": "Basic noun phrase construction"
    }
  ],
  "explanations": {
    "gender_agreement": "Spanish nouns have grammatical gender (masculine/feminine) that affects articles and adjectives",
    "number_agreement": "Words agree in number (singular/plural) throughout noun phrases",
    "verb_conjugation": "Verbs change endings to match subject person, number, tense, and mood",
    "word_order": "Subject-Verb-Object word order, but flexible due to case markings",
    "pronunciation": "Spanish uses consistent phonetic spelling with stress on penultimate syllable"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!
CRITICAL: grammatical_role MUST be EXACTLY one of these 9 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "other"
CRITICAL: For EACH word, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- other: #888888 (gray)
CRITICAL: Do NOT use descriptions like "definite article" or "action verb" - use ONLY the exact words above!
CRITICAL: If unsure, use "other" rather than making up a new category!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with aspect and agreement patterns"""
        base_prompt = """Analyze this Spanish sentence with INTERMEDIATE grammar focus: SENTENCE_PLACEHOLDER

Provide detailed analysis including:
- Verb conjugation patterns and tense/aspect/mood
- Gender and number agreement throughout noun phrases
- Pronoun usage and reference relationships
- Prepositional phrases and their functions
- Word combinations and compound structures

IMPORTANT: Articles (el, la, los, las, un, una, unos, unas) should be classified as "other".
Prepositions (a, de, en, con, por, para, desde, hasta) should be classified as "other".

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{
  "words": [
    {
      "word": "habla",
      "individual_meaning": "speaks/is speaking (third person singular present)",
      "pronunciation": "ˈaβla",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "n/a",
      "number_agreement": "singular",
      "verb_conjugation": "hablar (regular -ar verb, present indicative)",
      "importance": "Shows ongoing action or habitual activity"
    },
    {
      "word": "español",
      "individual_meaning": "Spanish (language)",
      "pronunciation": "espaˈɲol",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "gender_agreement": "masculine",
      "number_agreement": "singular",
      "case_marking": "direct object (implied)",
      "importance": "Language names function as nouns"
    }
  ],
  "word_combinations": [
    {
      "word": "habla español",
      "words": ["habla", "español"],
      "combined_meaning": "speaks Spanish",
      "grammatical_structure": "verb + direct object",
      "usage_notes": "Common construction for language proficiency"
    }
  ],
  "explanations": {
    "verb_conjugation": "Regular verbs follow patterns (-ar, -er, -ir) with stem changes in some cases",
    "gender_agreement": "All adjectives, articles, and some pronouns agree with noun gender",
    "number_agreement": "Plural forms affect entire noun phrases (nouns, adjectives, articles)",
    "pronoun_system": "Complex system with subject, object, and reflexive pronouns",
    "prepositional_usage": "Prepositions determine case relationships and idiomatic expressions"
  }
}

CRITICAL: grammatical_role MUST be EXACTLY one of these 9 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "other"
CRITICAL: For EACH word, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- other: #888888 (gray)
CRITICAL: Do NOT use descriptions like "definite article" or "action verb" - use ONLY the exact words above!

Focus on grammatical relationships and morphological patterns."""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with complex morphological features"""
        base_prompt = """Perform ADVANCED morphological and syntactic analysis of this Spanish sentence: SENTENCE_PLACEHOLDER

Analyze complex features including:
- Subjunctive mood and conditional structures
- Passive voice and impersonal constructions
- Complex relative clauses and embedded structures
- Idiomatic expressions and figurative language
- Advanced verb forms (perfect, progressive, compound tenses)

IMPORTANT: Articles and prepositions should be classified as "other".

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{
  "words": [
    {
      "word": "hubiera",
      "individual_meaning": "had (pluperfect subjunctive)",
      "pronunciation": "uˈβjera",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "n/a",
      "number_agreement": "singular",
      "verb_conjugation": "haber (auxiliary) + past participle, pluperfect subjunctive",
      "importance": "Shows hypothetical past actions in conditional sentences"
    },
    {
      "word": "tomado",
      "individual_meaning": "taken (past participle)",
      "pronunciation": "toˈmaðo",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "masculine",
      "number_agreement": "singular",
      "verb_conjugation": "tomar (regular -ar verb, past participle)",
      "importance": "Forms perfect tenses and passive voice"
    }
  ],
  "word_combinations": [
    {
      "word": "hubiera tomado",
      "words": ["hubiera", "tomado"],
      "combined_meaning": "had taken (hypothetical)",
      "grammatical_structure": "auxiliary verb + past participle",
      "usage_notes": "Pluperfect subjunctive in conditional sentences"
    }
  ],
  "explanations": {
    "subjunctive_mood": "Subjunctive expresses doubt, emotion, necessity, and hypothetical situations",
    "compound_tenses": "Perfect tenses use haber + past participle",
    "passive_voice": "Ser + past participle forms passive constructions",
    "relative_clauses": "Complex sentences with relative pronouns (que, quien, donde)",
    "impersonal_constructions": "Se + verb for impersonal actions or passive voice",
    "morphological_complexity": "Words can have multiple layers of agreement and conjugation",
    "sentence_structure": "Advanced sentence structure with multiple clauses and complex verb forms"
  }
}

CRITICAL: grammatical_role MUST be EXACTLY one of these 9 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "other"
CRITICAL: For EACH word, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- other: #888888 (gray)
CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Spanish word-level grammar analysis"""
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    parsed['sentence'] = sentence
                    logger.info(f"Spanish analyzer parsed JSON from markdown successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Spanish analyzer (markdown): {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try to extract JSON from response - look for JSON object after text
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    parsed['sentence'] = sentence
                    logger.info(f"Spanish analyzer parsed JSON successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Spanish analyzer: {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                logger.info(f"Spanish analyzer direct JSON parse successful: {len(parsed.get('words', []))} words")
                return self._transform_to_standard_format(parsed, complexity)
            except json.JSONDecodeError as e:
                logger.error(f"Direct JSON parse error in Spanish analyzer: {e}")
                logger.error(f"Raw AI response: {ai_response[:500]}...")

            # Fallback: extract structured information from text
            logger.warning("Spanish analyzer falling back to text parsing")
            return self._parse_text_response(ai_response, sentence)

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            return self._create_fallback_parse(ai_response, sentence)

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any], complexity: str = 'beginner') -> Dict[str, Any]:
        """Transform Spanish analyzer output to standard BaseGrammarAnalyzer format"""
        try:
            # Extract original data
            words = parsed_data.get('words', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            logger.info(f"Spanish analyzer transforming {len(words)} words")
            if words:
                sample_roles = [w.get('grammatical_role', 'MISSING') for w in words[:3]]
                logger.info(f"Sample grammatical roles: {sample_roles}")

            # Transform words into elements grouped by grammatical role
            elements = {}

            # Group words by their grammatical role
            for word_data in words:
                grammatical_role = word_data.get('grammatical_role', 'other')
                logger.debug(f"Processing word '{word_data.get('word', 'UNKNOWN')}' with role '{grammatical_role}'")
                if grammatical_role not in elements:
                    elements[grammatical_role] = []
                elements[grammatical_role].append(word_data)

            # Add word combinations as a special category
            if word_combinations:
                elements['word_combinations'] = word_combinations

            # Create word_explanations for HTML coloring: [word, pos, color, explanation]
            word_explanations = []
            colors = self.get_color_scheme(complexity)  # Use the actual complexity level

            logger.info(f"DEBUG Spanish Transform - Color scheme for complexity '{complexity}': {colors}")

            for word_data in words:
                word = word_data.get('word', '')
                grammatical_role = word_data.get('grammatical_role', 'other')
                individual_meaning = word_data.get('individual_meaning', '')
                pronunciation = word_data.get('pronunciation', '')
                
                # Ensure grammatical_role is a string
                if not isinstance(grammatical_role, str):
                    logger.warning(f"grammatical_role is not a string: {grammatical_role} (type: {type(grammatical_role)}), defaulting to 'other'")
                    grammatical_role = 'other'
                category = self._map_grammatical_role_to_category(grammatical_role)
                color = colors.get(category, '#888888')
                
                # Override with AI-provided color if available and standardize it
                ai_color = word_data.get('color')
                if ai_color:
                    color = self._standardize_color(ai_color, category)
                
                logger.info(f"DEBUG Spanish Transform - Word: '{word}', Role: '{grammatical_role}', Category: '{category}', Color: '{color}'")
                
                # Create explanation text from available data
                explanation_parts = []
                if individual_meaning:
                    explanation_parts.append(individual_meaning)
                if pronunciation:
                    explanation_parts.append(f"({pronunciation})")
                
                explanation = ", ".join(explanation_parts) if explanation_parts else f"{grammatical_role}"
                
                word_explanations.append([word, grammatical_role, color, explanation])
                logger.info(f"DEBUG Spanish Transform - Added word_explanation: {word_explanations[-1]}")

            logger.info(f"DEBUG Spanish Transform - Final word_explanations count: {len(word_explanations)}")

            # Return in standard format expected by BaseGrammarAnalyzer
            return {
                'elements': elements,
                'explanations': explanations,
                'word_explanations': word_explanations,
                'sentence': parsed_data.get('sentence', '')
            }

        except Exception as e:
            logger.error(f"Failed to transform Spanish analysis data: {e}")
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'word_explanations': [],
                'sentence': parsed_data.get('sentence', '')
            }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return vibrant, educational color scheme for Spanish grammatical elements"""
        schemes = {
            "beginner": {
                "pronouns": "#FF4444",         # Bright Red - People/references
                "verbs": "#44FF44",            # Bright Green - Actions/states
                "nouns": "#FFAA00",            # Orange - Things/objects
                "adjectives": "#FF44FF",       # Magenta - Descriptions
                "adverbs": "#44FFFF",          # Cyan - How/when/where
                "other": "#888888"             # Gray - Other/unknown
            },
            "intermediate": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green - Time expressions
                "idiomatic_expressions": "#FF8844",    # Coral - Expressions
                "other": "#888888"             # Gray
            },
            "advanced": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green
                "idiomatic_expressions": "#FF8844",    # Coral
                "sentence_structure": "#AA44FF",  # Purple - Tone/emotion
                "discourse_markers": "#88FFAA",    # Mint
                "other": "#888888"             # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Spanish word-level grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            words = parsed_data.get('words', [])
            phrase_combinations = parsed_data.get('phrase_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_words = len(words) > 0
            has_combinations = len(phrase_combinations) > 0
            has_explanations = len(explanations) > 0

            # Check word coverage in sentence
            sentence_words = original_sentence.split()
            analyzed_words = [word_data.get('word', '') for word_data in words]

            word_coverage = len(set(sentence_words).intersection(set(analyzed_words))) / len(sentence_words) if sentence_words else 0

            # Calculate confidence score
            base_score = 0.9 if (has_words and has_explanations) else 0.6
            coverage_bonus = word_coverage * 0.1
            combination_bonus = 0.05 if has_combinations else 0

            confidence = min(base_score + coverage_bonus + combination_bonus, 1.0)

            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5  # Conservative fallback


    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Parse text response when JSON extraction fails - extract Spanish word-level elements"""
        try:
            # Initialize empty structure
            words = []
            phrase_combinations = []
            explanations = {}

            # Extract sentence (first line or first 100 chars)
            sentence = ai_response.split('\n')[0].strip()
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."

            # Look for word analysis patterns in text
            text_lower = ai_response.lower()

            # Extract individual Spanish words from the sentence
            spanish_words = re.findall(r'\b\w+\b', sentence)

            # Create basic word entries for ALL words in the sentence
            for word in spanish_words:  # Analyze ALL words, not just first 10
                words.append({
                    "word": word,
                    "individual_meaning": f"Word '{word}' (meaning needs analysis)",
                    "pronunciation": "unknown",
                    "grammatical_role": "unknown",
                    "combinations": [],
                    "importance": "Part of the sentence structure"
                })

            # Look for phrase combination patterns
            # Find sequences of 2-4 words that appear in the text
            for i in range(len(spanish_words) - 1):
                for j in range(i + 2, min(i + 5, len(spanish_words) + 1)):
                    phrase = ' '.join(spanish_words[i:j])
                    if phrase in ai_response:
                        phrase_combinations.append({
                            "phrase": phrase,
                            "words": spanish_words[i:j],
                            "combined_meaning": f"Phrase '{phrase}' (compound meaning)",
                            "grammatical_structure": "word combination",
                            "usage_notes": "Forms a meaningful unit in Spanish"
                        })

            # Generate explanations based on found elements
            if words:
                explanations["word_analysis"] = "Each Spanish word has its own meaning and can combine to form phrases"
            if phrase_combinations:
                explanations["phrase_combinations"] = "Words combine to create phrases with specific meanings"
            explanations["sentence_structure"] = "Spanish sentence structure relies on word combinations and grammatical particles"

            return {
                'sentence': sentence,
                'words': words,
                'phrase_combinations': phrase_combinations,
                'explanations': explanations
            }

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            return self._create_fallback_parse(ai_response, sentence)


    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Spanish text with word-level coloring using colors from word_explanations (single source of truth)"""
        explanations = parsed_data.get('word_explanations', [])

        logger.info(f"DEBUG Spanish HTML Gen - Input explanations count: {len(explanations)}")
        logger.info(f"DEBUG Spanish HTML Gen - Input sentence: '{sentence}'")

        # Generate HTML by coloring each word individually using colors from grammar explanations
        import re

        # Create mapping of cleaned words to colors directly from word_explanations (authoritative source)
        word_to_color = {}
        for exp in explanations:
            if len(exp) >= 3:
                word, pos, color = exp[0], exp[1], exp[2]
                clean_key = re.sub(r'[^\w\s]', '', word)  # Clean the key for consistent matching
                word_to_color[clean_key] = color
                logger.info(f"DEBUG Spanish HTML Gen - Word '{word}' (clean: '{clean_key}') -> Color '{color}' (POS: '{pos}')")

        logger.info(f"DEBUG Spanish HTML Gen - Word-to-color mapping: {word_to_color}")

        words_in_sentence = re.findall(r'\S+', sentence)

        logger.info(f"DEBUG Spanish HTML Gen - Words found in sentence: {words_in_sentence}")

        html_parts = []
        for word in words_in_sentence:
            # Remove punctuation for matching but keep original word
            clean_word = re.sub(r'[^\w\s]', '', word)

            logger.info(f"DEBUG Spanish HTML Gen - Processing word '{word}' -> clean '{clean_word}'")

            if clean_word in word_to_color:
                color = word_to_color[clean_word]
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                logger.info(f"DEBUG Spanish HTML Gen - ✓ Colored word '{word}' with color '{color}'")
            else:
                # For words without analysis, use default color (should be rare with new architecture)
                html_parts.append(f'<span style="color: #888888;">{word}</span>')
                logger.warning(f"DEBUG Spanish HTML Gen - ✗ No color found for word '{word}' (clean: '{clean_word}'). Available words: {list(word_to_color.keys())}")

        result = ' '.join(html_parts)
        logger.info(f"DEBUG Spanish HTML Gen - Final HTML output length: {len(result)}")
        logger.info(f"DEBUG Spanish HTML Gen - Final HTML preview: {result[:300]}...")
        return result

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names"""
        role_lower = grammatical_role.lower()

        # Map various grammatical roles to color categories
        # Order matters: more specific checks first
        if any(keyword in role_lower for keyword in ['pronoun', 'personal', 'demonstrative']):
            return 'pronouns'
        elif any(keyword in role_lower for keyword in ['verb', 'action', 'state']):
            return 'verbs'
        elif any(keyword in role_lower for keyword in ['noun', 'object', 'subject']):
            return 'nouns'
        elif any(keyword in role_lower for keyword in ['adjective', 'description', 'quality']):
            return 'adjectives'
        elif any(keyword in role_lower for keyword in ['adverb', 'manner', 'time', 'place']):
            return 'adverbs'
        elif any(keyword in role_lower for keyword in ['idiomatic', 'expression']):
            return 'idiomatic_expressions'
        else:
            return 'other'

    def _get_default_category_for_word(self, word: str) -> str:
        """Get a default grammatical category for words that don't have detailed analysis"""
        # This is a simple heuristic based on common Spanish word patterns
        # In a real implementation, this could use more sophisticated analysis

        # Common pronouns
        if word.lower() in ['yo', 'tú', 'él', 'ella', 'nosotros', 'nosotras', 'vosotros', 'vosotras', 'ellos', 'ellas', 'usted', 'ustedes']:
            return 'pronouns'

        # Common verbs (basic forms)
        if word.lower() in ['ser', 'estar', 'tener', 'hacer', 'ir', 'ver', 'dar', 'saber', 'querer', 'llegar', 'pasar', 'deber', 'poner', 'parecer', 'quedar', 'creer', 'hablar', 'llevar', 'dejar', 'seguir']:
            return 'verbs'

        # Common articles
        if word.lower() in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']:
            return 'nouns'  # Articles are often categorized with nouns

        # Common prepositions
        if word.lower() in ['de', 'en', 'a', 'por', 'para', 'con', 'sin', 'sobre', 'desde', 'hasta', 'entre', 'durante', 'contra', 'hacia']:
            return 'other'  # Prepositions might not have specific color

        # Default to 'other' for unknown words
        return 'other'

    def _standardize_color(self, ai_color: str, category: str) -> str:
        """Standardize AI-provided color to ensure consistency with the defined color scheme"""
        # Define the exact color mapping that should be used
        standard_colors = {
            "pronouns": "#FF4444",         # Red
            "nouns": "#FFAA00",            # Orange
            "verbs": "#44FF44",            # Green
            "adjectives": "#FF44FF",       # Magenta
            "adverbs": "#44FFFF",          # Cyan
            "postpositions": "#4444FF",    # Blue
            "other": "#888888"             # Gray
        }

        # If AI provided a color, check if it matches the standard for this category
        if ai_color and ai_color.startswith('#'):
            expected_color = standard_colors.get(category, "#888888")
            # If AI color doesn't match expected, use the standard color
            if ai_color.upper() != expected_color.upper():
                logger.debug(f"AI provided color {ai_color} for category '{category}', standardizing to {expected_color}")
                return expected_color
            else:
                return ai_color  # AI got it right

        # If no AI color or invalid format, use standard color
        return standard_colors.get(category, "#888888")

    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create fallback parsing when main parsing fails"""
        return {
            'sentence': sentence,
            'elements': {},
            'explanations': {
                'parsing_error': 'Unable to parse AI response, using fallback analysis'
            }
        }

# Register analyzer
def create_analyzer():
    """Factory function to create Spanish analyzer"""
    return EsAnalyzer()