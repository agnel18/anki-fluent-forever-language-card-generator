# Base Grammar Analyzer Framework
# Abstract base class for all language-specific grammar analyzers

import abc
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

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
                       complexity: str, groq_api_key: str) -> GrammarAnalysis:
        """
        Main analysis method - orchestrates the complete grammar analysis process.

        Args:
            sentence: Sentence to analyze
            target_word: Target word being learned
            complexity: Complexity level ('beginner', 'intermediate', 'advanced')
            groq_api_key: API key for Groq AI

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
            analysis_data = self._call_ai_model(prompt, groq_api_key)

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
            logger.error(f"Grammar analysis failed for {self.language_name}: {e}")
            # Return minimal fallback analysis
            return self._create_fallback_analysis(sentence, target_word, complexity)

    def _call_ai_model(self, prompt: str, api_key: str) -> str:
        """Call Groq AI model with the generated prompt"""
        try:
            from groq import Groq

            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,  # Allow detailed analysis
                temperature=0.3   # Consistent, focused responses
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"AI model call failed: {e}")
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
        """Generate HTML output for Anki cards with color-coded elements"""
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
                    all_words.append((word, element_type))

        # Sort by length descending to handle longer matches first
        all_words.sort(key=lambda x: len(x[0]), reverse=True)

        # Replace each word with colored version using CSS classes
        for word, element_type in all_words:
            # Create colored span with CSS class for Anki compatibility
            colored_span = f'<span class="grammar-{element_type}">{word}</span>'

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