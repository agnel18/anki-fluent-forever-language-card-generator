# languages/hindi/domain/hi_prompt_builder.py
import logging
from typing import List
from jinja2 import Template
from .hi_config import HiConfig

logger = logging.getLogger(__name__)

class HiPromptBuilder:
    """Builds prompts for Hindi grammar analysis using templates."""
    
    def __init__(self, config: HiConfig):
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
            return f"Analyze this Hindi sentence: {sentence}\nTarget word: {target_word}\nComplexity: {complexity}\nProvide JSON response with grammatical analysis."
    
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
            return f"Analyze these Hindi sentences:\n{sentences_text}\nTarget word: {target_word}\nComplexity: {complexity}\nProvide batch JSON response."