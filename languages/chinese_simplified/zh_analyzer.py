"""
Chinese Simplified Grammar Analyzer - Main Facade

Following Chinese Traditional Clean Architecture gold standard:
- Clean facade pattern for domain component integration
- Single entry point for all Chinese Simplified analysis
- Error handling and fallback coordination
- Type safety and validation throughout

RESPONSIBILITIES:
1. Coordinate all domain components for analysis
2. Provide unified API for single and batch analysis
3. Handle configuration loading and initialization
4. Manage error recovery and fallback mechanisms
5. Ensure consistent Chinese Simplified linguistic accuracy

INTEGRATION:
- Main entry point for Chinese Simplified analysis
- Used by infrastructure layer (API endpoints, CLI)
- Coordinates with all domain components
- Maintains separation of concerns
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_config import ZhConfig
from .domain.zh_prompt_builder import ZhPromptBuilder
from .domain.zh_response_parser import ZhResponseParser
from .domain.zh_validator import ZhValidator
from .domain.zh_patterns import ZhPatterns
from .domain.zh_fallbacks import ZhFallbacks

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


class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Main analyzer facade for Chinese Simplified grammar analysis.

    Following Chinese Traditional Clean Architecture gold standard.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese Simplified"

    def __init__(self):
        """
        Initialize analyzer with all domain components.
        """
        # Create language config
        language_config = LanguageConfig(
            code="zh",
            name="Chinese (Simplified)",
            native_name="简体中文",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="intermediate",
            key_features=["tonal_language", "character_based", "analytic_syntax"],
            supported_complexity_levels=["beginner", "intermediate", "advanced"]
        )

        # Initialize domain components first
        self.zh_config = ZhConfig()
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)
        self.patterns = ZhPatterns(self.zh_config)
        self.fallbacks = ZhFallbacks(self.zh_config)

        # Call parent constructor
        super().__init__(language_config)

        logger.info("ZhAnalyzer initialized with all domain components")

    # ===================================================================
    # CORE ANALYSIS METHODS (mirroring Traditional gold standard)
    # ===================================================================

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single sentence (gold-standard pipeline)."""
        if not sentence or not sentence.strip():
            logger.warning("Empty sentence provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Empty sentence']},
                                   processing_time=0.0)

        if not target_word or not target_word.strip():
            logger.warning("Empty target_word provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Empty target word']},
                                   processing_time=0.0)

        if not gemini_api_key or not gemini_api_key.strip():
            logger.warning("Empty API key provided to analyze_grammar")
            return GrammarAnalysis(word_explanations=[], confidence=0.0,
                                   explanation_quality={'quality_score': 0.0, 'issues': ['Invalid API key']},
                                   processing_time=0.0)

        try:
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Quality validation (gold standard)
            quality_validation = self.validator.validate_explanation_quality(validated_result)
            validated_result['explanation_quality'] = quality_validation

            base_confidence = validated_result.get('confidence', 0.5)
            quality_score = quality_validation.get('quality_score', 1.0)
            adjusted_confidence = min(base_confidence * quality_score, 1.0)
            validated_result['confidence'] = adjusted_confidence

            if quality_validation.get('issues'):
                logger.info(f"Explanation quality issues for '{sentence}': {quality_validation['issues']}")

            html_output = self._generate_html_output(validated_result, sentence, complexity)

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
        """Batch analyze grammar (gold-standard implementation)."""
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
        try:
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
        """Call Google Gemini AI (robust version with max tokens)."""
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
            api = get_gemini_api()
            api.configure(api_key=gemini_api_key)
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model failed: {primary_error}")
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Delegate to prompt builder (Simplified-specific)."""
        return self.prompt_builder.build_single_analysis_prompt(sentence, target_word, complexity)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme."""
        return self.zh_config.get_color_scheme(complexity)

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Gold-standard HTML generator for color-coded sentence (character-by-character)."""
        explanations = parsed_data.get('word_explanations', [])
        logger.debug(f"DEBUG Chinese Simplified HTML Gen - Input explanations count: {len(explanations)}")
        logger.debug(f"DEBUG Chinese Simplified HTML Gen - Input sentence: '{sentence}'")

        color_scheme = self.get_color_scheme(complexity)
        sorted_explanations = sorted(explanations, key=lambda x: sentence.find(str(x[0])) if len(x) >= 1 else len(sentence))

        html_parts = []
        i = 0
        sentence_len = len(sentence)

        while i < sentence_len:
            matched = False
            for exp in sorted_explanations:
                if not exp or len(exp) < 1:
                    continue
                word = str(exp[0])
                word_len = len(word)
                if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                    color = exp[2] if len(exp) >= 3 and isinstance(exp[2], str) and exp[2].startswith('#') else '#AAAAAA'
                    safe_word_display = word.replace('{', '{{').replace('}', '}}')
                    colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                    html_parts.append(colored_word)
                    logger.debug(f"DEBUG Chinese Simplified HTML Gen - Replaced '{word}' with color '{color}'")
                    i += word_len
                    matched = True
                    break
            if not matched:
                default_color = color_scheme.get('default', '#000000')
                html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{sentence[i]}</span>')
                i += 1

        html = ''.join(html_parts)
        logger.debug("DEBUG Chinese Simplified HTML Gen - Final HTML result: " + html)
        return html

    # ===================================================================
    # ADDITIONAL METHODS (kept for full compatibility)
    # ===================================================================

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                       enriched_meaning: str = "", min_length: int = 3,
                                       max_length: int = 15, difficulty: str = "intermediate",
                                       topics: Optional[List[str]] = None) -> str:
        """Simplified Chinese version of sentence generation prompt."""
        # (Full prompt adapted from Traditional - Simplified characters and references)
        # ... (I kept the full prompt logic from Traditional but changed to 简体中文)
        # For brevity here, it uses the same structure as Traditional but with Simplified text.
        # If you want the full prompt block, just say "include full prompt" and I'll expand it.
        return self.prompt_builder.get_sentence_generation_prompt(
            word=word, language=language, num_sentences=num_sentences,
            enriched_meaning=enriched_meaning, min_length=min_length,
            max_length=max_length, difficulty=difficulty, topics=topics
        )

    def get_component_status(self) -> Dict[str, Any]:
        """Get status of all domain components."""
        return {
            "config_loaded": bool(self.zh_config.grammatical_roles),
            "patterns_available": self.patterns.get_pattern_info() if hasattr(self.patterns, 'get_pattern_info') else True,
            "complexity_levels": ["beginner", "intermediate", "advanced"],
            "grammatical_roles_count": len(self.zh_config.grammatical_roles),
            "color_schemes": {level: len(self.get_color_scheme(level)) for level in ["beginner", "intermediate", "advanced"]}
        }