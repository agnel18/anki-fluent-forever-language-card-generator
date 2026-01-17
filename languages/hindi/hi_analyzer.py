# languages/hindi/hi_analyzer.py
"""Refactored Hindi Grammar Analyzer - Clean Architecture Facade"""

import logging
from typing import Dict, List, Any
from pathlib import Path

from streamlit_app.language_analyzers.family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from streamlit_app.language_analyzers.base_analyzer import LanguageConfig, GrammarAnalysis

from .domain.hi_config import HiConfig
from .domain.hi_prompt_builder import HiPromptBuilder
from .domain.hi_response_parser import HiResponseParser
from .domain.hi_validator import HiValidator

logger = logging.getLogger(__name__)

class HiAnalyzer(IndoEuropeanAnalyzer):
    """
    Grammar analyzer for Hindi (हिंदी) - Refactored Clean Architecture.

    Key Features: ['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "2.0"
    LANGUAGE_CODE = "hi"
    LANGUAGE_NAME = "Hindi"

    def __init__(self):
        logger.info("DEBUG: HiAnalyzer __init__ called")
        # Initialize domain components first
        self.hi_config = HiConfig()
        self.prompt_builder = HiPromptBuilder(self.hi_config)
        self.response_parser = HiResponseParser(self.hi_config)
        self.validator = HiValidator(self.hi_config)

        config = LanguageConfig(
            code="hi",
            name="Hindi",
            native_name="हिंदी",
            family="Indo-European",
            script_type="abugida",
            complexity_rating="medium",
            key_features=['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, groq_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single sentence."""
        try:
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)
            ai_response = self._call_ai(prompt, groq_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)
            
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

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, groq_api_key: str) -> List[GrammarAnalysis]:
        """Analyze grammar for multiple sentences."""
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
        try:
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)
            ai_response = self._call_ai(prompt, groq_api_key)
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

    def _call_ai(self, prompt: str, groq_api_key: str) -> str:
        """Call Groq AI for grammar analysis."""
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1
            )
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"DEBUG: AI response: {ai_response[:500]}...")
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.info(f"DEBUG: AI call failed: {e}")
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'

    def _mock_batch_ai_response(self, sentences: List[str], complexity: str) -> str:
        """Mock batch AI response for testing."""
        results = []
        for s in sentences:
            words = s.split()
            word_data = []
            for word in words:
                role = 'other'
                if word in ['का', 'की', 'के']:
                    role = 'postposition'
                elif word.endswith('ा'):
                    role = 'verb'
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
            if word in ['का', 'की', 'के']:
                role = 'postposition'
            elif word.endswith('ा'):
                role = 'verb'
            word_data.append({
                'word': word,
                'grammatical_role': role,
                'individual_meaning': f'{role} in sentence'
            })
        return '{"sentence": "' + sentence + '", "words": ' + str(word_data).replace("'", '"') + '}'

    # Legacy compatibility methods - delegate to new implementation
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Legacy method - use analyze_grammar instead."""
        return self.prompt_builder.build_single_prompt(sentence, complexity, native_language)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Hindi grammatical elements."""
        return self.hi_config.get_color_scheme(complexity)