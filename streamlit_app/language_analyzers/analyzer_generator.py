# Analyzer Generation System
# Uses AI to generate language analyzers based on Chinese gold standard

import json
import logging
import re
import warnings
from typing import Dict, Any, Optional

# Suppress the google.generativeai deprecation warning
warnings.filterwarnings("ignore", message=".*google.generativeai.*deprecated.*", category=FutureWarning)

import google.generativeai as genai

# Import centralized configuration
from ..shared_utils import get_gemini_model

logger = logging.getLogger(__name__)

class AnalyzerGenerator:
    """Generates language analyzers using AI based on Chinese template."""

    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(get_gemini_model())

    def generate_analyzer(self, language_name: str, language_code: str, family: str, script_type: str, complexity: str) -> str:
        """
        Generate analyzer code for a language using AI.

        Args:
            language_name: Full language name (e.g., "Spanish")
            language_code: ISO code (e.g., "es")
            family: Language family (e.g., "Romance")
            script_type: Script type (e.g., "alphabetic")
            complexity: "low", "medium", "high"

        Returns:
            Generated analyzer Python code as string
        """

        # Read Chinese analyzer as template
        template_path = "streamlit_app/language_analyzers/analyzers/zh_analyzer.py"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_code = f.read()
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            return ""

        prompt = f"""You are an expert linguist and Python developer. Generate a grammar analyzer for {language_name} based on the Chinese analyzer template.

TARGET LANGUAGE: {language_name} ({language_code})
LANGUAGE FAMILY: {family}
SCRIPT TYPE: {script_type}
COMPLEXITY: {complexity}

Use this Chinese analyzer template as the gold standard:

```python
{template_code}
```

Generate a complete analyzer class for {language_name} following the exact same structure and patterns. Key requirements:

1. **Class Structure**: Inherit from BaseGrammarAnalyzer, implement all required methods
2. **Language Config**: Set correct code, name, family, script_type, complexity_rating
3. **Key Features**: Identify 3-5 key grammatical features for {language_name}
4. **Complexity Levels**: Support beginner/intermediate/advanced
5. **Grammar Prompts**: Create detailed prompts for grammar analysis in {language_name}
6. **Color Schemes**: Define pedagogical color schemes for highlighting
7. **Patterns**: Implement language-specific regex patterns and rules
8. **Error Handling**: Include comprehensive error handling

IMPORTANT:
- Maintain exact method signatures and return types
- Use appropriate linguistic knowledge for {language_name}
- Ensure 85%+ accuracy target for grammar analysis
- Include detailed comments explaining linguistic concepts
- Follow the Chinese template's code style and structure

Return ONLY the complete Python code for the analyzer, no explanations."""

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,  # Consistency for code generation
                max_output_tokens=4000,
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            generated_code = response.text.strip()

            # Clean up markdown code blocks if present
            if generated_code.startswith("```python"):
                generated_code = generated_code[9:]
            if generated_code.endswith("```"):
                generated_code = generated_code[:-3]

            return generated_code.strip()

        except Exception as e:
            logger.error(f"Failed to generate analyzer for {language_name}: {e}")
            return ""

    def validate_analyzer_code(self, code: str) -> bool:
        """Basic validation of generated analyzer code."""
        required_elements = [
            "class.*Analyzer(BaseGrammarAnalyzer)",
            "def __init__",
            "def get_grammar_prompt",
            "def analyze_grammar",
            "LanguageConfig",
            "VERSION",
            "LANGUAGE_CODE",
            "LANGUAGE_NAME"
        ]

        for element in required_elements:
            if not re.search(element, code, re.IGNORECASE):
                logger.warning(f"Missing required element: {element}")
                return False

        return True

    def save_analyzer(self, language_code: str, code: str) -> bool:
        """Save generated analyzer to file."""
        filename = f"streamlit_app/language_analyzers/analyzers/{language_code}_analyzer.py"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            logger.info(f"Saved analyzer for {language_code} to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save analyzer for {language_code}: {e}")
            return False