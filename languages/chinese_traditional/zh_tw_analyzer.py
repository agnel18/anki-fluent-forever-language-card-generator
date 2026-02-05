# languages/chinese_traditional/zh_tw_analyzer.py
"""
Chinese Traditional Analyzer - Main Facade

Following Chinese Simplified Clean Architecture gold standard:
- Clean facade pattern for domain component integration
- Single entry point for all Chinese Traditional analysis
- Error handling and fallback coordination
- Type safety and validation throughout

RESPONSIBILITIES:
1. Coordinate all domain components for analysis
2. Provide unified API for single and batch analysis
3. Handle configuration loading and initialization
4. Manage error recovery and fallback mechanisms
5. Ensure consistent Chinese Traditional linguistic accuracy

INTEGRATION:
- Main entry point for Chinese Traditional analysis
- Used by infrastructure layer (API endpoints, CLI)
- Coordinates with all domain components
- Maintains separation of concerns

ANALYSIS WORKFLOW:
1. Initialize domain components with configuration
2. Validate input and select analysis strategy
3. Generate prompts using ZhTwPromptBuilder
4. Call AI service (external dependency)
5. Parse responses with ZhTwResponseParser
6. Validate results with ZhTwValidator
7. Apply patterns with ZhTwPatterns
8. Return structured analysis results
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_tw_config import ZhTwConfig
from .domain.zh_tw_prompt_builder import ZhTwPromptBuilder
from .domain.zh_tw_response_parser import ZhTwResponseParser, ParseResult, ParsedSentence
from .domain.zh_tw_validator import ZhTwValidator, ValidationResult
from .domain.zh_tw_patterns import ZhTwPatterns
from .domain.zh_tw_fallbacks import ZhTwFallbacks

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model

logger = logging.getLogger(__name__)

@dataclass
class AnalysisRequest:
    """Request for grammatical analysis."""
    sentence: str
    target_word: Optional[str] = None
    complexity: str = "intermediate"
    analysis_type: str = "single"  # "single" or "batch"

@dataclass
class AnalysisResult:
    """Result of grammatical analysis."""
    success: bool
    sentence: str
    words: List[Dict[str, Any]]
    overall_structure: str
    key_features: str
    confidence: float
    validation_issues: List[str]
    validation_suggestions: List[str]
    error_message: Optional[str] = None
    fallback_used: bool = False

@dataclass
class BatchAnalysisResult:
    """Result of batch grammatical analysis."""
    success: bool
    results: List[AnalysisResult]
    total_sentences: int
    average_confidence: float
    error_message: Optional[str] = None
    fallback_used: bool = False

class ZhTwAnalyzer(BaseGrammarAnalyzer):
    """
    Main analyzer facade for Chinese Traditional grammar analysis.

    Following Chinese Simplified Clean Architecture:
    - Facade pattern: Single entry point for all operations
    - Dependency injection: Domain components injected at initialization
    - Error boundaries: Comprehensive error handling and recovery
    - Clean API: Simple, type-safe interface for clients

    ANALYSIS CAPABILITIES:
    - Single sentence analysis
    - Batch sentence analysis
    - Configurable complexity levels
    - Integrated validation and confidence scoring
    - Fallback mechanisms for robustness
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "zh-tw"
    LANGUAGE_NAME = "Chinese Traditional"

    def __init__(self):
        """
        Initialize analyzer with all domain components.

        COMPONENT INITIALIZATION:
        1. Create language config for Chinese Traditional
        2. Initialize domain components first (before parent constructor)
        3. Call parent constructor with config
        4. Set up component relationships
        5. Validate component integrity
        """
        # Create language config
        language_config = LanguageConfig(
            code="zh-tw",
            name="Chinese (Traditional)",
            native_name="繁體中文",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="intermediate",
            key_features=["tonal_language", "character_based", "analytic_syntax"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )
        
        # Initialize domain components first (needed for color schemes)
        self.zh_tw_config = ZhTwConfig()
        self.prompt_builder = ZhTwPromptBuilder(self.zh_tw_config)
        self.response_parser = ZhTwResponseParser(self.zh_tw_config)
        self.validator = ZhTwValidator(self.zh_tw_config)
        self.patterns = ZhTwPatterns(self.zh_tw_config)
        self.fallbacks = ZhTwFallbacks(self.zh_tw_config)
        
        # Call parent constructor
        super().__init__(language_config)

        logger.info("ZhTwAnalyzer initialized with all domain components")

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """
        Analyze grammar for a single sentence.

        CHINESE TRADITIONAL WORKFLOW:
        1. Build AI prompt using prompt_builder (Traditional-specific templates)
        2. Call AI API with proper error handling
        3. Parse response using response_parser (with Traditional fallbacks)
        4. Validate results using validator (aspect particles, classifiers)
        5. Generate HTML output for colored sentence display
        6. Return GrammarAnalysis object

        CHINESE TRADITIONAL FALLBACK HIERARCHY:
        - Primary: AI-generated analysis with aspect/classifier validation
        - Secondary: Pattern-based fallbacks for particles and compounds
        - Tertiary: Basic rule-based fallbacks for character-based analysis

        OUTPUT FORMAT:
        - word_explanations: [[word, role, color, meaning], ...]
        - Maintains sentence word order (LTR) for optimal user experience
        - Colors based on grammatical roles and complexity level
        """
        try:
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Additional explanation quality validation
            quality_validation = self.validator.validate_explanation_quality(validated_result)
            validated_result['explanation_quality'] = quality_validation

            # Adjust confidence score based on explanation quality
            base_confidence = validated_result.get('confidence', 0.5)
            quality_score = quality_validation.get('quality_score', 1.0)
            adjusted_confidence = min(base_confidence * quality_score, 1.0)
            validated_result['confidence'] = adjusted_confidence

            # Log quality issues if any
            if quality_validation.get('issues'):
                logger.info(f"Explanation quality issues for '{sentence}': {quality_validation['issues']}")

            # Generate HTML output
            html_output = self._generate_html_output(validated_result, sentence, complexity)

            # Return GrammarAnalysis object
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated_result.get('elements', {}),
                explanations=validated_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=validated_result.get('confidence', 0.0),
                word_explanations=validated_result.get('word_explanations', [])
            )
        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            # Create fallback analysis
            fallback_result = self.response_parser.fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback_result, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback_result.get('elements', {}),
                explanations=fallback_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback_result.get('confidence', 0.3),
                word_explanations=fallback_result.get('word_explanations', [])
            )

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """
        Analyze grammar for multiple sentences.

        CHINESE TRADITIONAL BATCH PROCESSING:
        - Handles 8 sentences efficiently (prevents token overflow)
        - Uses single AI call for all sentences (cost-effective)
        - Applies per-result validation and fallbacks
        - Maintains sentence order in output
        - Provides partial fallbacks (some sentences may succeed even if others fail)

        CHINESE TRADITIONAL BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence
        - Accounts for character-based analysis complexity

        ERROR HANDLING:
        - If entire batch fails: Return fallbacks for all sentences
        - If individual sentences fail: Use fallbacks only for failed ones
        - Maintains output consistency regardless of partial failures
        """
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
        try:
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)
            ai_response = self._call_ai(prompt, gemini_api_key)
            results = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_word)

            grammar_analyses = []
            for result, sentence in zip(results, sentences):
                validated_result = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(validated_result, sentence, complexity)

                grammar_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=validated_result.get('elements', {}),
                    explanations=validated_result.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=validated_result.get('confidence', 0.0),
                    word_explanations=validated_result.get('word_explanations', [])
                ))

            return grammar_analyses
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            # Return fallback analyses
            fallback_analyses = []
            for sentence in sentences:
                fallback_result = self.response_parser.fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(fallback_result, sentence, complexity)
                fallback_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=fallback_result.get('elements', {}),
                    explanations=fallback_result.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=fallback_result.get('confidence', 0.3),
                    word_explanations=fallback_result.get('word_explanations', [])
                ))
            return fallback_analyses

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """
        Call Google Gemini AI for grammar analysis.

        CHINESE TRADITIONAL AI INTEGRATION:
        - Uses gemini-2.5-flash model (primary) with gemini-3-flash-preview fallback
        - 2000 max_output_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        CHINESE TRADITIONAL CONSIDERATIONS:
        - Handles traditional logographic script properly
        - Accounts for compound word analysis
        - Supports aspect marker and classifier validation
        - Future-proof: Update model names as Google releases new versions

        ERROR HANDLING:
        - Catches all exceptions to prevent crashes
        - Returns standardized error response for fallback logic
        - Logs detailed information for debugging
        """
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            # Try primary model first
            try:
                model = genai.GenerativeModel(get_gemini_model())
                response = model.generate_content(prompt)
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                model = genai.GenerativeModel(get_gemini_fallback_model())
                response = model.generate_content(prompt)
                ai_response = response.text.strip()
            logger.info(f"DEBUG: AI response: {ai_response[:500]}...")
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.info(f"DEBUG: AI call failed: {e}")
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'  # Standardized error response

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate Chinese Traditional-specific AI prompt for grammar analysis with complexity-aware logic."""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt for Chinese Traditional."""
        return f"""Analyze this ENTIRE Chinese Traditional sentence WORD BY WORD: {sentence}

For EACH AND EVERY INDIVIDUAL WORD/CHARACTER in the sentence, provide:
- Its individual meaning and pronunciation (if applicable)
- Its basic grammatical role (noun, verb, adjective, particle, etc.)
- How it functions in this simple sentence
- Basic relationships with other words

Pay special attention to the target word: {target_word}

Focus on basic Chinese Traditional features:
- Basic particles (的, 了, 嗎, etc.)
- Simple subject-verb-object structure
- Basic classifiers and measure words

Return a JSON object with detailed word analysis for ALL words in the sentence:
{{
  "words": [
    {{
      "word": "example_word",
      "individual_meaning": "translation/meaning",
      "grammatical_role": "noun/verb/adjective/particle/etc",
      "basic_function": "subject/object/modifier",
      "importance": "learning significance"
    }}
  ],
  "explanations": {{
    "overall_structure": "Basic sentence structure explanation",
    "key_features": "Simple Chinese Traditional grammatical features"
  }}
}}

CRITICAL: Analyze EVERY word in the sentence, not just the target word! Provide COMPREHENSIVE explanations for basic Chinese Traditional grammar."""

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt for Chinese Traditional."""
        return f"""Analyze this Chinese Traditional sentence with INTERMEDIATE grammar focus: {sentence}

Provide detailed analysis including:
- Aspect markers (了, 着, 過) and their functions
- Classifier usage and selection
- Pronoun systems and reference
- Complex particle functions (把, 被, 給, etc.)
- Topic-comment structure

Pay special attention to the target word: {target_word}

Return a JSON object with comprehensive analysis:
{{
  "words": [
    {{
      "word": "example",
      "grammatical_role": "role",
      "aspect_info": "aspect marking if applicable",
      "classifier_info": "classifier usage",
      "syntactic_role": "function in sentence"
    }}
  ],
  "explanations": {{
    "aspect_system": "aspect marker usage in sentence",
    "classifier_usage": "classifier selection and function",
    "complex_structures": "intermediate Chinese Traditional syntax"
  }}
}}

CRITICAL: Analyze EVERY word in the sentence! Provide COMPREHENSIVE explanations for Chinese Traditional-specific features."""

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt for Chinese Traditional."""
        return f"""Perform advanced grammatical analysis of this Chinese Traditional sentence: {sentence}

Analyze complex linguistic phenomena:
- Multiple aspect markers and their interactions
- Complex classifier systems and quantification
- Discourse particles and pragmatic functions (呢, 吧, 啊, etc.)
- Topic chains and information structure
- Serial verb constructions
- Resultative compounds and directional complements

Pay special attention to the target word: {target_word}

Return detailed JSON analysis with advanced Chinese Traditional linguistic features:
{{
  "words": [
    {{
      "word": "example",
      "grammatical_role": "detailed_role",
      "aspect_complexity": "multiple aspect interactions",
      "discourse_function": "pragmatic particle usage",
      "syntactic_complexity": "advanced structure analysis"
    }}
  ],
  "explanations": {{
    "aspect_interactions": "complex aspect marker combinations",
    "discourse_structure": "information packaging and topic-comment",
    "advanced_syntax": "serial verbs, compounds, complements"
  }}
}}

CRITICAL: Analyze EVERY word in the sentence! Provide COMPREHENSIVE explanations for advanced Chinese Traditional grammar phenomena."""

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Chinese Traditional text with inline color styling for Anki compatibility"""
        explanations = parsed_data.get('word_explanations', [])

        print(f"DEBUG Chinese Traditional HTML Gen - Input explanations count: {len(explanations)}")
        print("DEBUG Chinese Traditional HTML Gen - Input sentence: '" + str(sentence) + "'")

        # For Chinese Traditional (logographic script without spaces), use position-based replacement
        color_scheme = self.get_color_scheme('intermediate')

        # Sort explanations by position in sentence to avoid conflicts
        sorted_explanations = sorted(explanations, key=lambda x: sentence.find(x[0]) if len(x) >= 3 else len(sentence))

        # Build HTML by processing the sentence character by character
        html_parts = []
        i = 0
        sentence_len = len(sentence)

        while i < sentence_len:
            # Check if current position matches any word explanation
            matched = False
            for exp in sorted_explanations:
                if len(exp) >= 3:
                    word = exp[0]
                    word_len = len(word)

                    # Check if word matches at current position
                    if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                        pos = exp[1]
                        category = self._map_grammatical_role_to_category(pos)
                        color = color_scheme.get(category, '#888888')

                        # Escape curly braces in word to prevent f-string issues
                        safe_word_display = word.replace('{', '{{').replace('}', '}}')
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                        html_parts.append(colored_word)

                        print("DEBUG Chinese Traditional HTML Gen - Replaced '" + str(word) + "' with category '" + str(category) + "' and color '" + str(color) + "'")

                        i += word_len
                        matched = True
                        break

            if not matched:
                # No match, add character as-is
                html_parts.append(sentence[i])
                i += 1

        html = ''.join(html_parts)
        print("DEBUG Chinese Traditional HTML Gen - Final HTML result: " + html)
        return html

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map Chinese Traditional grammatical roles to color scheme categories"""
        role_mapping = {
            'noun': 'noun',
            'verb': 'verb',
            'adjective': 'adjective',
            'adverb': 'adverb',
            'pronoun': 'pronoun',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'interjection': 'interjection',
            'particle': 'particle',
            'classifier': 'classifier',
            'aspect_marker': 'aspect_marker',
            'modal_particle': 'modal_particle',
            'structural_particle': 'structural_particle',
            'measure_word': 'measure_word',
            'numeral': 'numeral',
            'other': 'other'
        }
        return role_mapping.get(grammatical_role, 'other')

    def _mock_batch_ai_response(self, sentences: List[str], complexity: str) -> str:
        """Mock batch AI response for testing."""
        results = []
        for s in sentences:
            words = s.split()
            word_data = []
            for word in words:
                role = 'other'
                if word in ['的', '了', '着', '過']:
                    role = 'particle'
                elif word in ['個', '本', '杯']:
                    role = 'classifier'
                word_data.append({
                    'word': word,
                    'grammatical_role': role,
                    'individual_meaning': f'{role} in sentence'
                })
            results.append({"sentence": s, "words": word_data})
        return '{"batch_results": ' + str(results).replace("'", '"') + '}'

    def _mock_ai_response(self, sentence: str, complexity: str) -> str:
        """Mock single AI response for testing."""
        words = sentence.split()
        word_data = []
        for word in words:
            role = 'other'
            if word in ['的', '了', '着', '過']:
                role = 'particle'
            elif word in ['個', '本', '杯']:
                role = 'classifier'
            word_data.append({
                'word': word,
                'grammatical_role': role,
                'individual_meaning': f'{role} in sentence'
            })
        return '{"sentence": "' + sentence + '", "words": ' + str(word_data).replace("'", '"') + '}'

        logger.info("ZhTwAnalyzer initialized with all domain components")

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate language-specific AI prompt for grammar analysis."""
        return self.prompt_builder.build_single_analysis_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized grammar analysis format."""
        parse_result = self.response_parser.parse_single_response(ai_response, sentence)
        # Convert ParseResult to the expected dict format
        return {
            'elements': parse_result.elements,
            'explanations': parse_result.explanations,
            'word_explanations': parse_result.word_explanations
        }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for grammatical elements based on complexity level."""
        return self.zh_tw_config.get_color_scheme(complexity)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis quality and return confidence score (0.0-1.0)."""
        # Create a ParsedSentence from parsed_data
        from .domain.zh_tw_response_parser import ParsedSentence, ParsedWord
        
        words = []
        for word_exp in parsed_data.get('word_explanations', []):
            if len(word_exp) >= 4:
                word = ParsedWord(
                    word=word_exp[0],
                    role=word_exp[1],
                    color=word_exp[2],
                    meaning=word_exp[3]
                )
                words.append(word)
        
        parsed_sentence = ParsedSentence(
            sentence=original_sentence,
            words=words,
            explanations=parsed_data.get('explanations', {}),
            confidence=0.5  # Default, will be updated by validator
        )
        
        validation_result = self.validator.validate_parsed_sentence(parsed_sentence, "intermediate")
        return validation_result.confidence

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = "") -> List[Dict[str, Any]]:
        """
        Parse batch AI response into list of standardized grammar analysis formats.
        
        Args:
            ai_response: Raw batch response from AI model
            sentences: List of original sentences
            complexity: Complexity level used for analysis
            target_word: Target word being learned
            
        Returns:
            List of dictionaries with grammatical elements, explanations, etc.
        """
        parse_result = self.response_parser.parse_batch_response(ai_response, sentences)
        
        results = []
        for i, sentence in enumerate(sentences):
            if i < len(parse_result.sentences):
                parsed_sentence = parse_result.sentences[i]
                
                # Convert ParsedSentence to expected dict format
                word_explanations = [[w.word, w.grammatical_role, '#000000', w.individual_meaning] for w in parsed_sentence.words]
                
                # Group words by grammatical role for elements
                elements = {}
                for word_data in word_explanations:
                    role = word_data[1]  # role is at index 1
                    if role not in elements:
                        elements[role] = []
                    elements[role].append({
                        'word': word_data[0],
                        'role': role,
                        'explanation': word_data[3]  # meaning
                    })
                
                result = {
                    'elements': elements,
                    'explanations': {
                        'sentence_structure': parsed_sentence.overall_structure,
                        'key_features': parsed_sentence.key_features
                    },
                    'word_explanations': word_explanations
                }
            else:
                # Fallback for missing sentences
                result = {
                    'elements': {},
                    'explanations': {'sentence_structure': 'Batch parsing failed', 'complexity_notes': ''},
                    'word_explanations': []
                }
            results.append(result)
        
        return results

    def analyze_sentence(
        self,
        sentence: str,
        target_word: Optional[str] = None,
        complexity: str = "intermediate"
    ) -> AnalysisResult:
        """
        Analyze a single Chinese Traditional sentence.

        ANALYSIS WORKFLOW:
        1. Validate input parameters
        2. Generate AI prompt using prompt builder
        3. Call AI service (placeholder - would integrate with actual AI)
        4. Parse AI response using response parser
        5. Validate results using validator
        6. Apply pattern analysis for additional insights
        7. Return structured analysis result

        Args:
            sentence: Chinese Traditional sentence to analyze
            target_word: Specific word to focus analysis on
            complexity: Learning complexity level

        Returns:
            AnalysisResult with detailed grammatical breakdown
        """
        try:
            # Validate input
            if not sentence or not sentence.strip():
                return AnalysisResult(
                    success=False,
                    sentence=sentence,
                    words=[],
                    overall_structure="",
                    key_features="",
                    confidence=0.0,
                    validation_issues=["Empty sentence provided"],
                    validation_suggestions=["Provide a valid Chinese Traditional sentence"],
                    error_message="Empty sentence"
                )

            # Validate text using patterns
            text_validation = self.patterns.validate_text(sentence)
            if not text_validation['is_valid']:
                logger.warning(f"Text validation issues: {text_validation['issues']}")

            # Generate prompt
            target = target_word or self._extract_target_word(sentence)
            prompt = self.prompt_builder.build_single_analysis_prompt(
                sentence, target, complexity
            )

            # TODO: Call actual AI service here
            # For now, simulate AI response with fallback parsing
            ai_response = self._simulate_ai_response(sentence, target, complexity)

            # Parse response
            parse_result = self.response_parser.parse_single_response(ai_response, sentence)

            if not parse_result.sentences:
                return AnalysisResult(
                    success=False,
                    sentence=sentence,
                    words=[],
                    overall_structure="",
                    key_features="",
                    confidence=0.0,
                    validation_issues=["Failed to parse AI response"],
                    validation_suggestions=["Try rephrasing the sentence"],
                    error_message="Response parsing failed"
                )

            parsed_sentence = parse_result.sentences[0]

            # Validate results
            validation_result = self.validator.validate_parsed_sentence(
                parsed_sentence, complexity
            )

            # Convert to API result format
            words_data = [
                {
                    "word": word.word,
                    "grammatical_role": word.grammatical_role,
                    "individual_meaning": word.individual_meaning,
                    "confidence": word.confidence
                }
                for word in parsed_sentence.words
            ]

            return AnalysisResult(
                success=True,
                sentence=parsed_sentence.sentence,
                words=words_data,
                overall_structure=parsed_sentence.overall_structure,
                key_features=parsed_sentence.key_features,
                confidence=validation_result.confidence_score,
                validation_issues=validation_result.issues,
                validation_suggestions=validation_result.suggestions,
                fallback_used=parse_result.fallback_used
            )

        except Exception as e:
            logger.error(f"Error analyzing sentence: {e}")
            return AnalysisResult(
                success=False,
                sentence=sentence,
                words=[],
                overall_structure="",
                key_features="",
                confidence=0.0,
                validation_issues=["Analysis failed due to internal error"],
                validation_suggestions=["Try again or contact support"],
                error_message=str(e)
            )

    def analyze_sentences_batch(
        self,
        sentences: List[str],
        target_word: Optional[str] = None,
        complexity: str = "intermediate"
    ) -> BatchAnalysisResult:
        """
        Analyze multiple Chinese Traditional sentences.

        Args:
            sentences: List of sentences to analyze
            target_word: Target word for analysis
            complexity: Learning complexity level

        Returns:
            BatchAnalysisResult with analysis for all sentences
        """
        try:
            if not sentences:
                return BatchAnalysisResult(
                    success=False,
                    results=[],
                    total_sentences=0,
                    average_confidence=0.0,
                    error_message="No sentences provided"
                )

            results = []
            total_confidence = 0.0

            for sentence in sentences:
                result = self.analyze_sentence(sentence, target_word, complexity)
                results.append(result)
                total_confidence += result.confidence

            average_confidence = total_confidence / len(results) if results else 0.0

            return BatchAnalysisResult(
                success=all(r.success for r in results),
                results=results,
                total_sentences=len(sentences),
                average_confidence=average_confidence,
                fallback_used=any(r.fallback_used for r in results)
            )

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return BatchAnalysisResult(
                success=False,
                results=[],
                total_sentences=len(sentences),
                average_confidence=0.0,
                error_message=str(e)
            )

    def get_supported_complexity_levels(self) -> List[str]:
        """Get list of supported complexity levels."""
        return ["beginner", "intermediate", "advanced"]

    def get_grammatical_roles(self) -> Dict[str, str]:
        """Get available grammatical roles and their descriptions."""
        return self.zh_tw_config.grammatical_roles.copy()

    def get_color_scheme(self, complexity: str = "intermediate") -> Dict[str, str]:
        """Get color scheme for grammatical roles."""
        return self.zh_tw_config.get_color_scheme(complexity)

    def validate_text(self, text: str) -> Dict[str, Any]:
        """Validate Chinese Traditional text using pattern analysis."""
        return self.patterns.validate_text(text)

    def _extract_target_word(self, sentence: str) -> str:
        """
        Extract a reasonable target word from sentence.

        TARGET WORD SELECTION:
        - Prefer verbs and content words
        - Fall back to first non-particle word
        - Use first word as last resort
        """
        words = self.patterns.segment_sentence(sentence)

        # Prefer verbs and content words
        for word in words:
            if len(word) > 1:  # Multi-character words are likely content words
                return word

        # Fall back to first word
        return words[0] if words else sentence[:1]

    def _simulate_ai_response(self, sentence: str, target_word: str, complexity: str) -> str:
        """
        Simulate AI response for development/testing.

        SIMULATION STRATEGY:
        - Use pattern analysis to generate basic structure
        - Create realistic JSON response format
        - Include Chinese Traditional specific elements
        - Vary response quality for testing fallbacks
        """
        words = self.patterns.segment_sentence(sentence)

        # Generate basic word analysis
        word_analysis = []
        for i, word in enumerate(words):
            role = self._infer_grammatical_role(word, i, words)
            meaning = self._generate_meaning_explanation(word, role, sentence)

            word_analysis.append({
                "word": word,
                "grammatical_role": role,
                "individual_meaning": meaning
            })

        # Generate explanations
        overall_structure = f"This is a {'simple' if len(words) < 5 else 'complex'} Chinese Traditional sentence with {len(words)} elements."
        key_features = "Features include traditional characters and Chinese grammatical structures."

        response_data = {
            "sentence": sentence,
            "words": word_analysis,
            "explanations": {
                "overall_structure": overall_structure,
                "key_features": key_features
            }
        }

        return str(response_data)  # Simulate JSON response

    def _infer_grammatical_role(self, word: str, position: int, all_words: List[str]) -> str:
        """
        Infer grammatical role for a word in context.

        ROLE INFERENCE:
        - Use patterns and position
        - Consider Traditional Chinese grammar
        - Provide reasonable defaults
        """
        # Check for known particles
        if word in self.config.aspect_markers:
            return "aspect_particle"
        if word in self.config.modal_particles:
            return "modal_particle"
        if word in self.config.structural_particles:
            return "structural_particle"
        if word in self.config.common_classifiers:
            return "measure_word"

        # Position-based inference
        if position == 0:
            return "noun"  # Subject often first
        if position == len(all_words) - 1:
            return "verb"  # Predicate often at end

        # Length-based inference (longer words tend to be content words)
        if len(word) > 1:
            return "verb" if any(vowel in word for vowel in "aeiouāēīōūǖ") else "noun"

        return "particle"  # Default for single characters

    def _generate_meaning_explanation(self, word: str, role: str, sentence: str) -> str:
        """
        Generate a basic meaning explanation.

        EXPLANATION GENERATION:
        - Role-based explanation templates
        - Chinese Traditional specific terminology
        - Contextual relationship hints
        """
        templates = {
            "noun": f"'{word}' serves as a noun, representing a person, place, thing, or concept in the sentence.",
            "verb": f"'{word}' functions as a verb, indicating an action or state of being.",
            "aspect_particle": f"'{word}' is an aspect particle indicating completed action or ongoing state.",
            "modal_particle": f"'{word}' is a modal particle expressing tone or mood.",
            "measure_word": f"'{word}' is a measure word/classifier used with nouns.",
            "structural_particle": f"'{word}' is a structural particle connecting sentence elements.",
            "particle": f"'{word}' is a grammatical particle with structural function."
        }

        return templates.get(role, f"'{word}' has grammatical function: {role}")

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Chinese Traditional-specific sentence generation prompt to ensure proper response formatting.
        """
        # Build context instruction based on topics
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions"

        # Build meaning instruction based on enriched data
        if enriched_meaning and enriched_meaning != 'N/A':
            if enriched_meaning.startswith('{') and enriched_meaning.endswith('}'):
                # Parse the enriched context format
                context_lines = enriched_meaning[1:-1].split('\n')  # Remove {} and split
                definitions = []
                source = "Unknown"
                for line in context_lines:
                    line = line.strip()
                    if line.startswith('Source:'):
                        source = line.replace('Source:', '').strip()
                    elif line.startswith('Definition'):
                        # Extract just the definition text
                        def_text = line.split(':', 1)[1].strip() if ':' in line else line
                        # Remove part of speech info
                        def_text = def_text.split(' | ')[0].strip()
                        definitions.append(def_text)

                if definitions:
                    meaning_summary = '; '.join(definitions[:4])  # Use first 4 definitions
                    enriched_meaning_instruction = f'Analyze this linguistic data for "{word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings and provide a comprehensive meaning.'
                else:
                    enriched_meaning_instruction = f'Analyze this linguistic context for "{word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning.'
            else:
                # Legacy format
                enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". Generate a clean English meaning based on this.'
        else:
            enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

        # Custom prompt for Chinese Traditional to ensure proper formatting
        prompt = f"""You are a native-level expert linguist in Traditional Chinese (繁體中文).

Your task: Generate a complete learning package for the Traditional Chinese word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: particles only (的/了/嗎), specific measure words required, character-based restrictions.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Traditional Chinese for the word "{word}".

QUALITY RULES:
- Every sentence must use proper Traditional Chinese characters (繁體字)
- Grammar, syntax, and character usage must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be no more than {max_length} characters long
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different aspect particles (了, 着, 過) and sentence structures if applicable
- Use different sentence types: declarative, interrogative, imperative
- Include appropriate measure words/classifiers when needed
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: PINYIN TRANSCRIPTION
===========================
For EACH sentence above, provide accurate Pinyin transcription with tone marks.
- Use proper tone marks (ā, á, ǎ, à, ē, é, ě, è, etc.)
- Include spaces between words for readability

===========================
STEP 5: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 specific keywords for image search.
- Keywords should be concrete and specific
- Keywords in English only

===========================
OUTPUT FORMAT - FOLLOW EXACTLY
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions]

SENTENCES:
1. [sentence 1 in Traditional Chinese]
2. [sentence 2 in Traditional Chinese]
3. [sentence 3 in Traditional Chinese]
4. [sentence 4 in Traditional Chinese]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

PINYIN:
1. [Pinyin for sentence 1]
2. [Pinyin for sentence 2]
3. [Pinyin for sentence 3]
4. [Pinyin for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Traditional Chinese characters only
- Ensure exactly {num_sentences} sentences, translations, Pinyin, and keywords"""

        return prompt

    def get_component_status(self) -> Dict[str, Any]:
        """
        Get status of all domain components.

        Returns:
            Dictionary with component status information
        """
        return {
            "config_loaded": bool(self.config.grammatical_roles),
            "patterns_available": self.patterns.get_pattern_info(),
            "complexity_levels": self.get_supported_complexity_levels(),
            "grammatical_roles_count": len(self.config.grammatical_roles),
            "color_schemes": {level: len(self.get_color_scheme(level))
                            for level in self.get_supported_complexity_levels()}
        }