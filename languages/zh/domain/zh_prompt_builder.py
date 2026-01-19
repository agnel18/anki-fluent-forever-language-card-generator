# languages/zh/domain/zh_prompt_builder.py
"""
Chinese Simplified Prompt Builder - Domain Component

CHINESE PROMPT BUILDING:
This component demonstrates how to construct effective AI prompts for Chinese grammar analysis.
It uses Jinja2 templates for maintainable, parameterized prompts.

RESPONSIBILITIES:
1. Build single-sentence analysis prompts
2. Build batch analysis prompts for multiple sentences
3. Parameterize prompts with Chinese-specific context
4. Ensure prompts produce consistent JSON output
5. Handle template rendering errors gracefully

PROMPT ENGINEERING PRINCIPLES:
- Clear instructions: Explicit JSON structure requirements
- Contextual information: Include complexity level and target word
- Error prevention: Specify exact field names and formats
- Language specificity: Chinese-appropriate grammatical categories
- Consistency: Same structure for single and batch prompts

USAGE FOR CHINESE:
1. Copy template structure and modify content
2. Update grammatical role lists for Chinese features
3. Adjust examples and instructions for Chinese-specific features
4. Test prompts produce valid JSON with expected structure
5. Include Chinese-specific prompt context and examples

INTEGRATION:
- Called by main analyzer for prompt generation
- Receives configuration from ZhConfig
- Templates support parameterization for different contexts
- Error handling prevents crashes from template issues
"""

import logging
from typing import List
from jinja2 import Template
from .zh_config import ZhConfig

logger = logging.getLogger(__name__)

class ZhPromptBuilder:
    """
    Builds prompts for Chinese Simplified grammar analysis using templates.

    CHINESE TEMPLATE SYSTEM:
    - Jinja2 templates: Maintainable and parameterized
    - Language-specific: Chinese-appropriate instructions and examples
    - Structured output: Explicit JSON format requirements
    - Error handling: Graceful fallbacks for template failures

    TEMPLATE FEATURES:
    - Complexity-aware: Different instructions for different levels
    - Target word highlighting: Special handling for focus words
    - Batch support: Efficient multi-sentence processing
    - JSON validation: Clear structure requirements
    - Chinese-specific: Aspect markers, classifiers, particles
    """

    def __init__(self, config: ZhConfig):
        """
        Initialize with configuration.

        TEMPLATE INITIALIZATION:
        1. Store config reference for access to templates and settings
        2. Pre-compile templates for performance
        3. Validate template availability
        4. Set up error handling for template rendering
        """
        self.config = config
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single sentence analysis."""
        try:
            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'native_language': 'English',
                'patterns': self.config.patterns,
            }
            prompt = self.single_template.render(**context)
            logger.debug(f"Built single prompt for complexity {complexity}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build single prompt for '{sentence}': {e}")
            return f"Analyze this Chinese sentence: {sentence}\nTarget word: {target_word}\nComplexity: {complexity}\nProvide JSON response with grammatical analysis."

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch analysis."""
        try:
            context = {
                'sentences': sentences,
                'target_word': target_word,
                'complexity': complexity,
                'native_language': 'English',
                'patterns': self.config.patterns,
            }
            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build batch prompt: {e}")
            sentences_text = '\n'.join(sentences)
            return f"Analyze these Chinese sentences:\n{sentences_text}\nTarget word: {target_word}\nComplexity: {complexity}\nProvide batch JSON response."