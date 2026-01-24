# Base Grammar Analyzer Framework
# Abstract base class for all language-specific grammar analyzers

import abc
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# Import centralized configuration
from config import get_gemini_model, get_gemini_fallback_model

logger = logging.getLogger(__name__)

@dataclass
class GrammarAnalysis:
    """Standardized grammar analysis result"""
    sentence: str
    target_word: str
    language_code: str
    complexity_level: str
    grammatical_elements: Dict[str, List[Dict[str, Any]]]
    explanations: Dict[str, str]
    color_scheme: Dict[str, str]
    html_output: str
    confidence_score: float
    word_explanations: List[List[Any]] = field(default_factory=list)

@dataclass
class LanguageConfig:
    """Language-specific configuration"""
    code: str
    name: str
    native_name: str
    family: str
    script_type: str
    complexity_rating: str
    key_features: List[str]
    supported_complexity_levels: List[str]

class BaseGrammarAnalyzer(abc.ABC):
    """
    Abstract base class for language-specific grammar analyzers.

    Each language analyzer must implement:
    - get_grammar_prompt(): Generate AI prompt for grammar analysis
    - parse_grammar_response(): Parse AI response into structured data
    - get_color_scheme(): Return color scheme for grammatical elements
    - validate_analysis(): Validate analysis quality meets 85% threshold
    """

    def __init__(self, language_config: LanguageConfig):
        self.config = language_config
        self.language_code = language_config.code
        self.language_name = language_config.name
        self.supported_levels = language_config.supported_complexity_levels

        # Initialize color schemes for each complexity level
        self.color_schemes = self._initialize_color_schemes()

    @abc.abstractmethod
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """
        Generate language-specific AI prompt for grammar analysis.

        Args:
            complexity: 'beginner', 'intermediate', or 'advanced'
            sentence: The sentence to analyze
            target_word: The target word being learned

        Returns:
            Formatted prompt string for the AI model
        """
        pass

    @abc.abstractmethod
    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """
        Parse AI response into standardized grammar analysis format.

        Args:
            ai_response: Raw response from AI model
            complexity: Complexity level used for analysis
            sentence: Original sentence being analyzed

        Returns:
            Dictionary with grammatical elements, explanations, etc.
        """
        pass

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """
        Generate language-specific AI prompt for batch grammar analysis.
        Default implementation creates individual prompts and combines them.
        Subclasses can override for more efficient batch processing.

        Args:
            complexity: 'beginner', 'intermediate', or 'advanced'
            sentences: List of sentences to analyze
            target_word: The target word being learned
            native_language: User's native language for explanations

        Returns:
            Formatted batch prompt string for the AI model
        """
        # Default implementation - create batch format
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze the grammar of these {self.language_name} sentences and provide detailed analysis for each one.

Target word: "{target_word}"
Language: {self.language_name}
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

Return your analysis in this exact JSON format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "example",
          "grammatical_role": "noun",
          "category": "nouns",
          "explanation": "Explanation in {{native_language}}"
        }}
      ],
      "word_combinations": [],
      "explanations": {{
        "sentence_structure": "Brief grammatical summary in {{native_language}}",
        "complexity_notes": "Notes about {{complexity}} level structures used"
      }}
    }}
  ]
}}

IMPORTANT:
- Analyze ALL {len(sentences)} sentences in this single response
- Each sentence must have complete word-by-word grammatical analysis
- Use {self.language_name}-specific grammatical categories
- Provide explanations in {native_language}
- Return ONLY the JSON object, no additional text or markdown formatting
"""

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, native_language: str = "English") -> List[Dict[str, Any]]:
        """
        Parse batch AI response into list of standardized grammar analysis formats.
        Default implementation parses batch JSON and calls individual parse method for each.
        Subclasses can override for more efficient batch parsing.

        Args:
            ai_response: Raw batch response from AI model
            sentences: List of original sentences
            complexity: Complexity level used for analysis
            native_language: User's native language

        Returns:
            List of dictionaries with grammatical elements, explanations, etc.
        """
        try:
            # Extract JSON from response
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()

            batch_data = json.loads(ai_response)
            if "batch_results" not in batch_data:
                raise ValueError("Missing batch_results in response")

            results = []
            for item in batch_data["batch_results"]:
                sentence_index = item.get("sentence_index", 0) - 1  # Convert to 0-based
                if 0 <= sentence_index < len(sentences):
                    sentence = sentences[sentence_index]
                    # Convert batch item to individual format and parse
                    individual_response = json.dumps(item)
                    parsed = self.parse_grammar_response(individual_response, complexity, sentence)
                    results.append(parsed)
                else:
                    results.append({
                        "sentence": sentences[len(results)] if len(results) < len(sentences) else "",
                        "elements": {},
                        "explanations": {"sentence_structure": "Batch parsing failed", "complexity_notes": ""},
                        "word_explanations": []
                    })

            return results

        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            # Fallback to individual parsing (less efficient but works)
            return [self.parse_grammar_response(ai_response, complexity, sentence) for sentence in sentences]

    @abc.abstractmethod
    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """
        Return color scheme for grammatical elements based on complexity level.

        Args:
            complexity: 'beginner', 'intermediate', or 'advanced'

        Returns:
            Dictionary mapping grammatical element types to hex colors
        """
        pass

    def analyze_grammar(self, sentence: str, target_word: str,
                       complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """
        Main analysis method - orchestrates the complete grammar analysis process.

        Args:
            sentence: Sentence to analyze
            target_word: Target word being learned
            complexity: Complexity level ('beginner', 'intermediate', 'advanced')
            gemini_api_key: Google Gemini API key

        Returns:
            Complete GrammarAnalysis object
        """
        try:
            # Validate inputs
            if complexity not in self.supported_levels:
                raise ValueError(f"Unsupported complexity level: {complexity}")

            # Generate AI prompt
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)

            # Call AI model
            analysis_data = self._call_ai_model(prompt, gemini_api_key)

            # Parse response
            parsed_data = self.parse_grammar_response(analysis_data, complexity, sentence)

            # Validate quality
            confidence = self.validate_analysis(parsed_data, sentence)
            if confidence < 0.85:
                logger.warning(f"Analysis confidence below 85% threshold: {confidence}")

            # Generate HTML output (colors guaranteed to match by design with new architecture)
            html_output = self._generate_html_output(parsed_data, sentence, complexity)

            # Create result object
            result = GrammarAnalysis(
                sentence=sentence,
                target_word=target_word,
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=parsed_data.get('elements', {}),
                explanations=parsed_data.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=confidence
            )

            return result

        except Exception as e:
            logger.error("Grammar analysis failed for " + self.language_name + ": " + str(e))
            # Return minimal fallback analysis
            return self._create_fallback_analysis(sentence, target_word, complexity)

    def batch_analyze_grammar(self, sentences: List[str], target_word: str,
                             complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """
        Batch analyze multiple sentences in a single API call for efficiency.

        Args:
            sentences: List of sentences to analyze
            target_word: Target word being learned (same for all sentences)
            complexity: Complexity level ('beginner', 'intermediate', 'advanced')
            gemini_api_key: Google Gemini API key

        Returns:
            List of GrammarAnalysis objects, one per sentence
        """
        try:
            # Validate inputs
            if complexity not in self.supported_levels:
                raise ValueError(f"Unsupported complexity level: {complexity}")

            if not sentences:
                return []

            # Generate batch AI prompt
            prompt = self.get_batch_grammar_prompt(complexity, sentences, target_word)

            # Call AI model once for all sentences
            analysis_data = self._call_ai_model(prompt, gemini_api_key)

            # Parse batch response
            batch_results = self.parse_batch_grammar_response(analysis_data, sentences, complexity)

            # Convert to GrammarAnalysis objects
            results = []
            for i, (sentence, parsed_data) in enumerate(zip(sentences, batch_results)):
                try:
                    # Validate quality
                    confidence = self.validate_analysis(parsed_data, sentence)
                    if confidence < 0.85:
                        logger.warning(f"Batch analysis confidence below 85% for sentence {i+1}: {confidence}")

                    # Generate HTML output
                    html_output = self._generate_html_output(parsed_data, sentence, complexity)

                    # Create result object
                    result = GrammarAnalysis(
                        sentence=sentence,
                        target_word=target_word,
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=parsed_data.get('elements', {}),
                        explanations=parsed_data.get('explanations', {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=confidence
                    )
                    results.append(result)

                except Exception as e:
                    logger.error(f"Failed to create GrammarAnalysis for sentence {i+1}: {e}")
                    # Return fallback for this sentence
                    results.append(self._create_fallback_analysis(sentence, target_word, complexity))

            return results

        except Exception as e:
            logger.error(f"Batch grammar analysis failed for {self.language_name}: {e}")
            # Return fallbacks for all sentences
            return [self._create_fallback_analysis(sentence, target_word, complexity)
                   for sentence in sentences]

    def _call_ai_model(self, prompt: str, api_key: str) -> str:
        """Call Google Gemini AI model with the generated prompt"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            # Try primary model first
            try:
                model = genai.GenerativeModel(get_gemini_model())
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                model = genai.GenerativeModel(get_gemini_fallback_model())
                response = model.generate_content(prompt)
                return response.text.strip()

        except Exception as e:
            logger.error("AI model call failed: " + str(e))
            raise

    @abc.abstractmethod
    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """
        Validate analysis quality and return confidence score (0.0-1.0).

        Must achieve 85% (0.85) confidence threshold.

        Args:
            parsed_data: Parsed analysis data
            original_sentence: Original sentence for validation

        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Anki cards with color-coded elements using inline styles"""
        colors = self.get_color_scheme(complexity)
        elements = parsed_data.get('elements', {})

        # Start with the original sentence
        result = sentence

        # Process each element type and color the words
        # Sort by word length (longest first) to avoid partial matches
        all_words = []
        for element_type, word_list in elements.items():
            if element_type == 'word_combinations':
                continue  # Skip combinations for individual word coloring

            color = colors.get(element_type, '#000000')
            for word_data in word_list:
                word = word_data.get('word', '').strip()
                if word:
                    all_words.append((word, color))

        # Sort by length descending to handle longer matches first
        all_words.sort(key=lambda x: len(x[0]), reverse=True)

        # Replace each word with colored version using inline styles
        for word, color in all_words:
            # Use inline style for Anki compatibility
            colored_span = f'<span style="color: {color};">{word}</span>'

            # Use simple string replacement with word boundaries
            # Split the sentence into words, replace exact matches, then rejoin
            import re

            # For complex scripts, use a more careful approach
            # Replace only when the word appears as a whole word with boundaries
            words_in_sentence = re.findall(r'\S+', result)  # Split on whitespace
            
            # Replace exact word matches
            for i, w in enumerate(words_in_sentence):
                if w == word:
                    words_in_sentence[i] = colored_span
            
            # Rejoin the sentence
            result = ' '.join(words_in_sentence)

        return result

    def _initialize_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Initialize color schemes for all complexity levels"""
        schemes = {}
        for level in self.supported_levels:
            schemes[level] = self.get_color_scheme(level)
        return schemes

    def _create_fallback_analysis(self, sentence: str, target_word: str,
                                complexity: str) -> GrammarAnalysis:
        """Create minimal fallback analysis when main analysis fails"""
        return GrammarAnalysis(
            sentence=sentence,
            target_word=target_word,
            language_code=self.language_code,
            complexity_level=complexity,
            grammatical_elements={},
            explanations={'error': 'Analysis temporarily unavailable'},
            color_scheme=self.get_color_scheme(complexity),
            html_output=sentence,  # Plain text fallback
            confidence_score=0.0
        )

    @property
    def version(self) -> str:
        """Return analyzer version for tracking updates"""
        return getattr(self, 'VERSION', '1.0')

    def get_supported_features(self) -> List[str]:
        """Return list of supported grammatical features"""
        return self.config.key_features

    def is_complexity_supported(self, complexity: str) -> bool:
        """Check if complexity level is supported"""
        return complexity in self.supported_levels

    def validate_color_consistency(self, html_output: str, word_explanations: List[List[Any]]) -> Tuple[bool, str]:
        """
        DEPRECATED: With the new color consistency architecture (Phase 5.5),
        colors are guaranteed to match by design. This method is kept for backwards compatibility
        but always returns True with the original HTML.

        The new architecture ensures Grammar Explanation colors flow programmatically to
        Colored Sentences, eliminating the need for validation.
        """
        # Colors are now guaranteed to match by design - no validation needed
        return True, html_output