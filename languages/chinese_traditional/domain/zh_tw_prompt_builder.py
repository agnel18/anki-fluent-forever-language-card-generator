# languages/chinese_traditional/domain/zh_tw_prompt_builder.py
"""
Chinese Traditional Prompt Builder - Domain Component

Following Chinese Simplified Clean Architecture gold standard:
- Jinja2 template-based prompt generation
- Integration with external configuration
- Type safety and validation
- Separation of concerns (templates vs. logic)

RESPONSIBILITIES:
1. Generate AI prompts using Jinja2 templates
2. Integrate with ZhTwConfig for template selection
3. Handle template rendering with proper context
4. Support different complexity levels and analysis types
5. Provide consistent prompt structure across all analyses

INTEGRATION:
- Depends on ZhTwConfig for templates and settings
- Used by ZhTwAnalyzer facade for prompt generation
- Supports single sentence and batch analysis modes
- Maintains Chinese Traditional linguistic accuracy

TEMPLATE PHILOSOPHY:
- External templates: Keep prompts separate from code
- Contextual rendering: Use Jinja2 for dynamic content
- Linguistic precision: Chinese Traditional specific terminology
- Educational focus: Support different learning levels
"""

import logging
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment, BaseLoader

from .zh_tw_config import ZhTwConfig, ComplexityLevel

logger = logging.getLogger(__name__)

class ZhTwPromptBuilder:
    """
    Builds AI prompts for Chinese Traditional grammar analysis.

    Following Chinese Simplified Clean Architecture:
    - Template-based: Use Jinja2 for prompt generation
    - Config-driven: Templates loaded from ZhTwConfig
    - Type-safe: Validate inputs and outputs
    - Modular: Separate template logic from analysis logic

    PROMPT GENERATION STRATEGY:
    1. Select appropriate template based on analysis type
    2. Render template with context variables
    3. Validate rendered prompt structure
    4. Return formatted prompt for AI consumption

    SUPPORTED ANALYSIS TYPES:
    - single: Individual sentence analysis
    - batch: Multiple sentences analysis
    - targeted: Focus on specific grammatical elements
    """

    def __init__(self, config: ZhTwConfig):
        """
        Initialize prompt builder with configuration.

        Args:
            config: ZhTwConfig instance with templates and settings
        """
        self.config = config
        self.jinja_env = Environment(loader=BaseLoader())

    def build_single_analysis_prompt(
        self,
        sentence: str,
        target_word: str,
        complexity: str = "intermediate"
    ) -> str:
        """
        Build prompt for single sentence analysis.

        Following Chinese Simplified pattern:
        - Template-based rendering
        - Context variable injection
        - Complexity level support
        - Chinese Traditional linguistic focus

        Args:
            sentence: The Chinese Traditional sentence to analyze
            target_word: Word to focus analysis on
            complexity: Learning level (beginner/intermediate/advanced)

        Returns:
            Formatted prompt string for AI analysis
        """
        template_str = self.config.prompt_templates.get("single", "")
        if not template_str:
            logger.error("Single analysis template not found in config")
            return self._build_fallback_single_prompt(sentence, target_word, complexity)

        template = self.jinja_env.from_string(template_str)

        context = {
            "sentence": sentence,
            "target_word": target_word,
            "complexity": complexity,
            "language": "Chinese Traditional",
            "grammatical_roles": self.config.grammatical_roles,
            "aspect_markers": self.config.aspect_markers,
            "modal_particles": self.config.modal_particles,
            "structural_particles": self.config.structural_particles
        }

        try:
            prompt = template.render(**context)
            logger.debug(f"Generated single analysis prompt for sentence: {sentence[:50]}...")
            return prompt
        except Exception as e:
            logger.error(f"Failed to render single analysis template: {e}")
            return self._build_fallback_single_prompt(sentence, target_word, complexity)

    def build_batch_analysis_prompt(
        self,
        sentences: list,
        target_word: str,
        complexity: str = "intermediate"
    ) -> str:
        """
        Build prompt for batch sentence analysis.

        Args:
            sentences: List of Chinese Traditional sentences to analyze
            target_word: Word to focus analysis on
            complexity: Learning level

        Returns:
            Formatted prompt string for batch AI analysis
        """
        template_str = self.config.prompt_templates.get("batch", "")
        if not template_str:
            logger.error("Batch analysis template not found in config")
            return self._build_fallback_batch_prompt(sentences, target_word, complexity)

        template = self.jinja_env.from_string(template_str)

        # Format sentences for template
        sentences_text = "\n".join(f"{i+1}. {sent}" for i, sent in enumerate(sentences))

        context = {
            "sentences": sentences_text,
            "target_word": target_word,
            "complexity": complexity,
            "language": "Chinese Traditional",
            "sentence_count": len(sentences),
            "grammatical_roles": self.config.grammatical_roles,
            "aspect_markers": self.config.aspect_markers,
            "modal_particles": self.config.modal_particles,
            "structural_particles": self.config.structural_particles
        }

        try:
            prompt = template.render(**context)
            logger.debug(f"Generated batch analysis prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to render batch analysis template: {e}")
            return self._build_fallback_batch_prompt(sentences, target_word, complexity)

    def _build_fallback_single_prompt(
        self,
        sentence: str,
        target_word: str,
        complexity: str
    ) -> str:
        """
        Fallback prompt builder when template loading fails.

        MAINTAINS FUNCTIONALITY:
        - Basic analysis structure
        - Chinese Traditional focus
        - Essential grammatical elements
        """
        return f"""
Analyze this Chinese Traditional sentence and provide detailed grammatical breakdown.

Sentence: {sentence}
Target word: {target_word}
Complexity level: {complexity}

For EACH word/character in the sentence, provide:
- Its specific grammatical function and role
- How it contributes to the sentence meaning
- Relationships with adjacent words
- Chinese-specific features (aspect, classifiers, particles)

Return a JSON object with exactly this structure:
{{
  "sentence": "{sentence}",
  "words": [
    {{
      "word": "character/word",
      "grammatical_role": "noun|verb|aspect_particle|measure_word|particle|...",
      "individual_meaning": "Detailed explanation of this element's function, relationships, and contribution to sentence meaning"
    }}
  ],
  "explanations": {{
    "overall_structure": "Detailed explanation of sentence structure and word relationships",
    "key_features": "Notable Chinese grammatical features like aspect usage, classifier selection, particle functions"
  }}
}}

CRITICAL: Provide COMPREHENSIVE explanations for EVERY element, explaining relationships and functions in detail.
"""

    def _build_fallback_batch_prompt(
        self,
        sentences: list,
        target_word: str,
        complexity: str
    ) -> str:
        """
        Fallback batch prompt builder when template loading fails.
        """
        sentences_text = "\n".join(f"{i+1}. {sent}" for i, sent in enumerate(sentences))

        return f"""
Analyze these Chinese Traditional sentences and provide detailed grammatical breakdowns for each.

Sentences:
{sentences_text}

Target word: {target_word}
Complexity level: {complexity}

For EACH sentence, provide comprehensive analysis including:
- Word-by-word grammatical breakdown
- Chinese-specific features (aspect particles, measure words, modal particles)
- Relationships between sentence elements
- Overall sentence structure and function

Return a JSON object with exactly this structure:
{{
  "batch_results": [
    {{
      "sentence": "first sentence",
      "words": [
        {{
          "word": "character/word",
          "grammatical_role": "noun|verb|aspect_particle|measure_word|particle|...",
          "individual_meaning": "Detailed explanation of function and relationships"
        }}
      ],
      "explanations": {{
        "overall_structure": "Detailed structural analysis",
        "key_features": "Chinese grammatical features and their functions"
      }}
    }}
  ]
}}

CRITICAL: Provide COMPREHENSIVE explanations for ALL elements in EACH sentence.
"""

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch analysis of multiple Chinese Traditional sentences."""
        try:
            # Use template if available
            template_str = self.config.prompt_templates.get("batch", "")
            if template_str:
                template = self.jinja_env.from_string(template_str)
                context = {
                    'sentences': sentences,
                    'target_word': target_word,
                    'complexity': complexity,
                    'native_language': 'English'
                }
                return template.render(**context)
            else:
                # Fallback to hardcoded prompt
                return self._build_fallback_batch_prompt(sentences, target_word, complexity)
        except Exception as e:
            logger.error(f"Failed to build batch prompt: {e}")
            return self._build_fallback_batch_prompt(sentences, target_word, complexity)

    def build_batch_prompt(self, sentences: list, target_word: str, complexity: str) -> str:
        """Build batch prompt - compatibility method that delegates to build_batch_analysis_prompt."""
        return self.build_batch_analysis_prompt(sentences, target_word, complexity)