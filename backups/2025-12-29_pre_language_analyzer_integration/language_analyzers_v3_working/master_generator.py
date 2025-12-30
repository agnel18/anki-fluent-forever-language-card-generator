# Master Language Analyzer Generator
# Generates complete language-specific analyzer classes for all 77 languages

import json
import os
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class MasterAnalyzerGenerator:
    """
    Master generator for creating language-specific grammar analyzers.

    This system generates complete analyzer classes for all 77 languages
    using linguistic data and standardized templates.
    """

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Default to the directory containing this file
            base_dir = Path(__file__).parent

        self.base_dir = Path(base_dir)
        self.templates_dir = self.base_dir / "templates"
        self.configs_dir = self.base_dir / "language_configs"
        self.analyzers_dir = self.base_dir / "analyzers"

        # Create directories if they don't exist
        self.templates_dir.mkdir(exist_ok=True)
        self.configs_dir.mkdir(exist_ok=True)
        self.analyzers_dir.mkdir(exist_ok=True)

    def generate_analyzer(self, language_code: str) -> str:
        """
        Generate a complete analyzer class for the specified language.

        Args:
            language_code: ISO language code (e.g., 'zh', 'ja', 'es')

        Returns:
            Path to the generated analyzer file
        """
        # Load language configuration
        config = self._load_language_config(language_code)

        # Generate analyzer code
        analyzer_code = self._generate_analyzer_code(config)

        # Write to file
        output_file = self.analyzers_dir / f"{language_code}_analyzer.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(analyzer_code)

        logger.info(f"Generated analyzer for {config['name']} at {output_file}")
        return str(output_file)

    def _load_language_config(self, language_code: str) -> Dict[str, Any]:
        """Load language configuration from JSON file"""
        config_file = self.configs_dir / f"{language_code}.json"

        if not config_file.exists():
            raise FileNotFoundError(f"Language config not found: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config

    def _generate_analyzer_code(self, config: Dict[str, Any]) -> str:
        """Generate complete analyzer class code"""

        # Extract configuration
        language_code = config['code']
        language_name = config['name']
        native_name = config.get('native_name', language_name)
        language_family = config['family']
        script_type = config['script_type']
        complexity_rating = config['complexity_rating']
        key_features = config['key_features']
        supported_levels = config['supported_complexity_levels']

        # Generate color schemes
        color_schemes = self._generate_color_schemes(config)

        # Generate grammar prompts code (separate methods)
        grammar_prompts_code = self._generate_grammar_prompts_code(config)

        # Generate parsing logic
        parsing_logic = self._generate_parsing_logic(config)

        # Generate validation logic
        validation_logic = self._generate_validation_logic(config)

        # Assemble the complete class
        class_template = '''# {language_name} Grammar Analyzer
# Auto-generated analyzer for {language_name} ({native_name})
# Language Family: {language_family}
# Script Type: {script_type}
# Complexity Rating: {complexity_rating}

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class {language_code}Analyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for {language_name} ({native_name}).

    Key Features: {key_features}
    Complexity Levels: {supported_levels}
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "{language_code_lower}"
    LANGUAGE_NAME = "{language_name}"

    def __init__(self):
        config = LanguageConfig(
            code="{language_code_lower}",
            name="{language_name}",
            native_name="{native_name}",
            family="{language_family}",
            script_type="{script_type}",
            complexity_rating="{complexity_rating}",
            key_features={key_features!r},
            supported_complexity_levels={supported_levels!r}
        )
        super().__init__(config)

        # Language-specific patterns and rules
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize language-specific patterns and rules"""
        # Override in language-specific implementations
        pass

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate AI prompt for {language_name} grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

{grammar_prompts_code}

    def parse_grammar_response(self, ai_response: str, complexity: str) -> Dict[str, Any]:
        """Parse AI response into structured {language_name} grammar analysis"""
        try:
{parsing_logic}

        except Exception as e:
            logger.error(f"Failed to parse {{self.language_name}} grammar response: {{e}}")
            return self._create_fallback_parse(ai_response)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for {language_name} grammatical elements"""
        schemes = {color_schemes}

        if complexity not in schemes:
            complexity = "{supported_levels[0]}"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate {language_name} grammar analysis quality (85% threshold required)"""
{validation_logic}

    def _create_fallback_parse(self, ai_response: str) -> Dict[str, Any]:
        """Create fallback parsing when main parsing fails"""
        return {{
            'sentence': ai_response.split('.')[0] if '.' in ai_response else ai_response[:100],
            'elements': {{}},
            'explanations': {{
                'parsing_error': 'Unable to parse AI response, using fallback analysis'
            }}
        }}

# Register analyzer
def create_analyzer():
    """Factory function to create {language_name} analyzer"""
    return {language_code}Analyzer()
'''

        class_code = class_template.format(
            language_name=language_name,
            native_name=native_name,
            language_family=language_family,
            script_type=script_type,
            complexity_rating=complexity_rating,
            language_code=language_code.title(),
            language_code_lower=language_code,
            key_features=key_features,
            supported_levels=supported_levels,
            grammar_prompts_code=grammar_prompts_code,
            parsing_logic=parsing_logic,
            color_schemes=color_schemes,
            validation_logic=validation_logic
        )

        return class_code

    def _generate_color_schemes(self, config: Dict[str, Any]) -> str:
        """Generate color scheme code for the language"""
        # Use default color schemes based on language family and features
        color_schemes = {}

        for level in config['supported_complexity_levels']:
            if level == 'beginner':
                color_schemes[level] = self._get_beginner_colors(config)
            elif level == 'intermediate':
                color_schemes[level] = self._get_intermediate_colors(config)
            elif level == 'advanced':
                color_schemes[level] = self._get_advanced_colors(config)

        return str(color_schemes).replace("'", '"')

    def _get_beginner_colors(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate beginner-level color scheme"""
        base_colors = {
            'nouns': '#3498db',      # Blue
            'verbs': '#e74c3c',      # Red
            'adjectives': '#2ecc71', # Green
            'particles': '#f39c12',  # Orange
            'questions': '#9b59b6'   # Purple
        }

        # Customize based on language features
        if 'particles' in config['key_features']:
            base_colors['particles'] = '#e67e22'  # More prominent for particle languages

        return base_colors

    def _get_intermediate_colors(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate intermediate-level color scheme"""
        base_colors = self._get_beginner_colors(config)

        # Add intermediate features
        intermediate_additions = {
            'aspect_markers': '#8e44ad',  # Purple for aspect
            'case_markers': '#16a085',    # Teal for cases
            'tense_markers': '#d35400',   # Dark orange for tense
            'negation': '#c0392b'         # Dark red for negation
        }

        base_colors.update(intermediate_additions)
        return base_colors

    def _get_advanced_colors(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate advanced-level color scheme"""
        base_colors = self._get_intermediate_colors(config)

        # Add advanced features
        advanced_additions = {
            'modal_particles': '#2c3e50',    # Dark blue for modals
            'discourse_markers': '#f1c40f',  # Yellow for discourse
            'focus_particles': '#e84393',    # Pink for focus
            'structural_particles': '#00b894' # Mint for structure
        }

        base_colors.update(advanced_additions)
        return base_colors

    def _generate_grammar_prompts_code(self, config: Dict[str, Any]) -> str:
        """Generate grammar prompt methods for different complexity levels"""
        methods = []

        for level in config['supported_complexity_levels']:
            if level == 'beginner':
                method = self._generate_beginner_prompt_method(config)
            elif level == 'intermediate':
                method = self._generate_intermediate_prompt_method(config)
            elif level == 'advanced':
                method = self._generate_advanced_prompt_method(config)
            methods.append(method)

        return '\n\n'.join(methods)

    def _generate_beginner_prompt_method(self, config: Dict[str, Any]) -> str:
        """Generate beginner-level prompt method"""
        features = config['key_features']
        language_name = config['name']

        focus_items = []
        if 'particles' in features:
            focus_items.append('        - Essential particles and their functions')
        if 'nouns' in features or 'verbs' in features:
            focus_items.append('        - Basic parts of speech (nouns, verbs, adjectives)')
        if 'questions' in features:
            focus_items.append('        - Question formation elements')

        focus_text = '\n'.join(focus_items) if focus_items else '        - Basic grammatical elements'

        method = f'''    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt"""
        base_prompt = """Analyze this {language_name} sentence for basic grammatical elements: SENTENCE_PLACEHOLDER

Focus on identifying:
{focus_text}

Return a JSON object with:
{{
  "elements": {{
    "particles": [{{"word": "的", "function": "possessive particle"}}],
    "nouns": [{{"word": "猫", "function": "subject"}}],
    "verbs": [{{"word": "睡觉", "function": "main verb"}}]
  }},
  "explanations": {{
    "particles": "Particles connect words and show grammatical relationships",
    "sentence_structure": "Basic explanation of sentence structure"
  }}
}}

Be precise and focus on the target word: TARGET_PLACEHOLDER"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)'''.replace('{language_name}', language_name).replace('{focus_text}', focus_text)

        return method

        return '\n'.join(prompt_parts)

        return '\n'.join(prompt_parts)

    def _generate_intermediate_prompt_method(self, config: Dict[str, Any]) -> str:
        """Generate intermediate-level prompt method"""
        features = config['key_features']
        language_name = config['name']

        focus_items = []
        if 'aspect' in features:
            focus_items.append('        - Aspect markers and their functions')
        if 'case' in features:
            focus_items.append('        - Case system and noun modifications')
        if 'tense' in features:
            focus_items.append('        - Tense and time expressions')

        focus_text = '\n'.join(focus_items) if focus_items else '        - Grammatical structures and relationships'

        method = f'''    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt"""
        base_prompt = """Analyze this {language_name} sentence for intermediate grammatical concepts: SENTENCE_PLACEHOLDER

Focus on:
{focus_text}

Return a JSON object with:
{{
  "elements": {{
    "aspect_markers": [{{"word": "正在", "function": "progressive aspect"}}],
    "particles": [{{"word": "的", "function": "possessive particle"}}],
    "nouns": [{{"word": "猫", "function": "subject"}}],
    "verbs": [{{"word": "睡觉", "function": "main verb"}}]
  }},
  "explanations": {{
    "aspect": "Aspect markers indicate the temporal flow of actions",
    "particles": "Particles connect words and show grammatical relationships",
    "sentence_structure": "Intermediate sentence structure with aspect markers"
  }}
}}

Be precise and focus on the target word: TARGET_PLACEHOLDER"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)'''.replace('{language_name}', language_name).replace('{focus_text}', focus_text)

        return method

        return '\n'.join(prompt_parts)

    def _generate_advanced_prompt_method(self, config: Dict[str, Any]) -> str:
        """Generate advanced-level prompt method"""
        features = config['key_features']
        language_name = config['name']

        focus_items = []
        if 'modal_particles' in features:
            focus_items.append('        - Modal and discourse particles')
        if 'focus' in features:
            focus_items.append('        - Focus and emphasis constructions')
        if 'syntax' in features:
            focus_items.append('        - Complex syntactic structures')

        focus_text = '\n'.join(focus_items) if focus_items else '        - Advanced grammatical phenomena'

        method = f'''    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt"""
        base_prompt = """Perform advanced grammatical analysis of this {language_name} sentence: SENTENCE_PLACEHOLDER

Analyze:
{focus_text}

Return a JSON object with:
{{
  "elements": {{
    "modal_particles": [{{"word": "吧", "function": "suggestion particle"}}],
    "aspect_markers": [{{"word": "正在", "function": "progressive aspect"}}],
    "structural_particles": [{{"word": "的", "function": "attributive particle"}}],
    "discourse_markers": [{{"word": "但是", "function": "contrast marker"}}]
  }},
  "explanations": {{
    "modal_particles": "Modal particles express speaker attitude and discourse functions",
    "aspect_system": "Complex aspectual distinctions and temporal relationships",
    "discourse_structure": "Advanced discourse organization and pragmatic functions"
  }}
}}

Be precise and focus on the target word: TARGET_PLACEHOLDER"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)'''.replace('{language_name}', language_name).replace('{focus_text}', focus_text)

        return method

    def _generate_grammar_prompts(self, config: Dict[str, Any]) -> str:
        """Generate grammar analysis prompts for different complexity levels"""
        prompts = {}

        for level in config['supported_complexity_levels']:
            if level == 'beginner':
                prompts[level] = self._get_beginner_prompt(config)
            elif level == 'intermediate':
                prompts[level] = self._get_intermediate_prompt(config)
            elif level == 'advanced':
                prompts[level] = self._get_advanced_prompt(config)

        return str(prompts)

    def _get_beginner_prompt(self, config: Dict[str, Any]) -> str:
        """Generate beginner-level grammar analysis prompt"""
        features = config['key_features']
        language_name = config['name']

        prompt = f'''Analyze this {language_name} sentence for basic grammatical elements: {{{{sentence}}}}

Focus on identifying:
'''

        if 'particles' in features:
            prompt += '- Essential particles and their functions\n'
        if 'nouns' in features or 'verbs' in features:
            prompt += '- Basic parts of speech (nouns, verbs, adjectives)\n'
        if 'questions' in features:
            prompt += '- Question formation elements\n'

        prompt += '''
Return a JSON object with:
{
  "elements": {
    "particles": [{{"word": "的", "function": "possessive particle"}}],
    "nouns": [{{"word": "猫", "function": "subject"}}],
    "verbs": [{{"word": "睡觉", "function": "main verb"}}]
  },
  "explanations": {
    "particles": "Particles connect words and show grammatical relationships",
    "sentence_structure": "Basic explanation of sentence structure"
  }
}

Be precise and focus on the target word: {{{{target_word}}}}'''

        return prompt

    def _get_intermediate_prompt(self, config: Dict[str, Any]) -> str:
        """Generate intermediate-level grammar analysis prompt"""
        features = config['key_features']
        language_name = config['name']

        prompt = f'''Analyze this {language_name} sentence for intermediate grammatical concepts: "{{sentence}}"

Focus on:
'''

        if 'aspect' in features:
            prompt += '- Aspect markers and their functions\n'
        if 'case' in features:
            prompt += '- Case system and noun modifications\n'
        if 'tense' in features:
            prompt += '- Tense and time expressions\n'

        prompt += '''
Return detailed JSON analysis with grammatical breakdown and explanations.
Include aspectual information, case markings, and structural elements.

Target word: "{target_word}"
'''

        return prompt

    def _get_advanced_prompt(self, config: Dict[str, Any]) -> str:
        """Generate advanced-level grammar analysis prompt"""
        features = config['key_features']
        language_name = config['name']

        prompt = f'''Perform advanced grammatical analysis of this {language_name} sentence: "{{sentence}}"

Analyze:
'''

        if 'modal_particles' in features:
            prompt += '- Modal and discourse particles\n'
        if 'focus' in features:
            prompt += '- Focus and emphasis constructions\n'
        if 'syntax' in features:
            prompt += '- Complex syntactic structures\n'

        prompt += '''
Provide comprehensive analysis including pragmatic functions, discourse structure,
and advanced grammatical phenomena.

Target word: "{target_word}"
'''

        return prompt

    def _generate_parsing_logic(self, config: Dict[str, Any]) -> str:
        """Generate response parsing logic"""
        parsing_code = '''
            # Try to extract JSON from response
            json_match = re.search(r'```json\\s*(.*?)\\s*```', ai_response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Try direct JSON parsing
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                pass

            # Fallback: extract structured information from text
            return self._parse_text_response(ai_response)
'''

        return parsing_code

    def _generate_validation_logic(self, config: Dict[str, Any]) -> str:
        """Generate validation logic for 85% accuracy threshold"""
        validation_code = '''
        try:
            # Check if essential elements are present
            elements = parsed_data.get('elements', {})
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_elements = len(elements) > 0
            has_explanations = len(explanations) > 0

            # Check if target word appears in analysis
            sentence_words = set(original_sentence.lower().split())
            analyzed_words = set()

            for element_list in elements.values():
                for item in element_list:
                    if isinstance(item, dict) and 'word' in item:
                        analyzed_words.add(item['word'].lower())

            word_coverage = len(sentence_words.intersection(analyzed_words)) / len(sentence_words)

            # Calculate confidence score
            base_score = 0.8 if (has_elements and has_explanations) else 0.5
            coverage_bonus = word_coverage * 0.2

            confidence = min(base_score + coverage_bonus, 1.0)

            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5  # Conservative fallback
'''

        return validation_code

    def create_language_config(self, language_code: str, config_data: Dict[str, Any]) -> str:
        """Create language configuration file"""
        config_file = self.configs_dir / f"{language_code}.json"

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        return str(config_file)

    def generate_all_analyzers(self, language_codes: List[str]) -> List[str]:
        """Generate analyzers for multiple languages"""
        generated_files = []

        for code in language_codes:
            try:
                file_path = self.generate_analyzer(code)
                generated_files.append(file_path)
                logger.info(f"Generated analyzer for {code}")
            except Exception as e:
                logger.error(f"Failed to generate analyzer for {code}: {e}")

        return generated_files

# Convenience functions
def generate_chinese_analyzer():
    """Generate Chinese analyzer"""
    generator = MasterAnalyzerGenerator()
    return generator.generate_analyzer('zh')

def generate_japanese_analyzer():
    """Generate Japanese analyzer"""
    generator = MasterAnalyzerGenerator()
    return generator.generate_analyzer('ja')

def generate_spanish_analyzer():
    """Generate Spanish analyzer"""
    generator = MasterAnalyzerGenerator()
    return generator.generate_analyzer('es')