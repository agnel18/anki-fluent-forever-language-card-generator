# Implementation Guide
## Step-by-Step Language Analyzer Development

**Prerequisites:** Complete research phase ([Research Guide](research_guide.md))  
**Gold Standards:** Study [Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py) analyzers  
**Time Estimate:** 2-4 weeks for full implementation  
**Critical:** Follow gold standard patterns - no artificial confidence boosting

## 🎯 Implementation Workflow

### Phase 1: Gold Standard Study (1-2 days)
#### 1.1 Study Working Analyzers Thoroughly
- [ ] **Hindi Analyzer** (`languages/hindi/hi_analyzer.py`):
  - Inherits from `IndoEuropeanAnalyzer`
  - Clean facade pattern with domain component orchestration
  - No artificial confidence boosting
  - Comprehensive error handling with fallbacks
  - Batch processing with 8-sentence limits

- [ ] **Chinese Simplified Analyzer** (`languages/zh/zh_analyzer.py`):
  - Inherits from `BaseGrammarAnalyzer` (analytic language)
  - Language-specific complexity-aware prompts
  - Character-based analysis for logographic script
  - Natural confidence scoring without manipulation

- [ ] **Chinese Traditional Analyzer** (`languages/chinese_traditional/zh_tw_analyzer.py`):
  - Inherits from `BaseGrammarAnalyzer` (Sino-Tibetan variant)
  - Rich explanation implementation with individual word meanings
  - Position-based HTML coloring for character-level analysis
  - Modular architecture with domain components (config, prompt_builder, response_parser, validator)

#### 1.2 Identify Key Patterns
- [ ] **Facade Pattern**: Single entry point orchestrating domain components
- [ ] **Domain Components**: config, prompt_builder, response_parser, validator
- [ ] **Clean Architecture**: Dependencies point inward
- [ ] **Natural Validation**: No artificial confidence boosting
- [ ] **Error Recovery**: Comprehensive fallback mechanisms
- [ ] **Rich Explanations**: Individual word meanings beyond grammatical roles (Chinese gold standard)

#### 1.3 Critical: Rich Explanations Pattern (Chinese Gold Standard)
**Key Learning from Chinese Traditional Fix:** Base analyzers provide only grammatical roles, but gold standard analyzers provide rich explanations with individual meanings.

**❌ Anti-Pattern (Base Analyzer):**
```python
# Basic grammatical roles only
"noun in zh-tw grammar"
"verb in zh-tw grammar"
```

**✅ Gold Standard Pattern (Chinese Analyzers):**
```python
# Rich explanations with individual meanings
"我 (I, me - first person singular pronoun)"
"喜歡 (to like, to be fond of - verb expressing preference)"
"吃 (to eat, to consume - verb of consumption)"
```

**Implementation Requirements:**
- [ ] **analyze_grammar method**: AI workflow → parsing → HTML generation
- [ ] **_generate_html_output method**: Position-based coloring with meanings
- [ ] **GrammarAnalysis return**: Structured word_explanations with [word, role, color, meaning]
- [ ] **Individual meaning extraction**: Parse `individual_meaning` from AI responses
- [ ] **Word Meanings Dictionary**: External JSON file with specific meanings (CRITICAL for Sino-Tibetan languages)

#### 1.4 Critical: Word Meanings Dictionary Pattern (Sino-Tibetan Requirement)

**Key Learning:** Sino-Tibetan languages require external word meanings dictionaries to provide rich explanations instead of generic grammatical roles.

**Why Required:**
- Sino-Tibetan languages use logographic scripts where characters have specific semantic meanings
- Generic fallback explanations like "numeral in zh-tw grammar" don't help learners
- Specific meanings like "three (numeral)" provide actual learning value

**Implementation Pattern:**
```python
# 1. Create word meanings JSON file
# File: infrastructure/data/{language}_word_meanings.json
{
  "一": "one (numeral)",
  "二": "two (numeral)", 
  "三": "three (numeral)",
  "如果": "if (conjunction)",
  "答案": "answer, solution (noun)"
}

# 2. Load in config
class LanguageConfig:
    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.word_meanings = self._load_json(config_dir / "{language}_word_meanings.json")
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load word meanings: {e}")
            return {}

# 3. Use in fallbacks
class LanguageFallbacks:
    def _analyze_word(self, word: str) -> Dict[str, Any]:
        # Check word meanings first
        if word in self.config.word_meanings:
            meaning = self.config.word_meanings[word]
            role = self._guess_grammatical_role(word)
            return {
                'word': word,
                'individual_meaning': meaning,  # Rich meaning
                'grammatical_role': role,
                'confidence': 'high'
            }
        
        # Generic fallback only if no dictionary entry
        role = self._guess_grammatical_role(word)
        meaning = self._generate_fallback_explanation(word, role)
        return {
            'word': word,
            'individual_meaning': meaning,  # Generic fallback
            'grammatical_role': role,
            'confidence': 'low'
        }
```

**Critical Checklist:**
- [ ] **Create word meanings JSON**: Essential vocabulary with specific meanings
- [ ] **Load in config**: Config class loads JSON file on initialization  
- [ ] **Prioritize dictionary**: Fallbacks check word_meanings before generic explanations
- [ ] **Test rich explanations**: Verify dictionary provides specific meanings over generic roles
- [ ] **Word Meanings Dictionary**: External JSON file with specific meanings (CRITICAL for Sino-Tibetan languages)

### Phase 2: Directory Structure Setup (2-4 hours)

#### 2.1 Create Gold Standard Directory Structure
```bash
languages/{language}/
├── {language}_analyzer.py              # Main facade class (COPY GOLD STANDARD STRUCTURE)
├── {language}_grammar_concepts.md      # Research documentation
├── domain/                             # Business logic components
│   ├── {language}_config.py           # Configuration (like hi_config.py/zh_config.py)
│   ├── {language}_prompt_builder.py   # AI prompt generation (like hi/zh prompt builders)
│   ├── {language}_response_parser.py  # AI response parsing (like hi/zh parsers)
│   └── {language}_validator.py        # Quality validation (NO CONFIDENCE BOOSTING)
├── infrastructure/                     # External concerns
│   └── {language}_fallbacks.py        # Error recovery (like gold standards)
└── tests/                              # Test suites (follow updated template)
    ├── __init__.py
    ├── test_{language}_analyzer.py    # Unit tests (no confidence boosting)
    └── test_{language}_integration.py # Integration tests
```

#### 2.2 Initialize Git Repository
```bash
cd languages/{language}
git init
echo "*.pyc" > .gitignore
echo "__pycache__/" >> .gitignore
```

### Phase 3: Domain Components Implementation (1-2 weeks)

#### 3.1 Configuration Component (4-6 hours)

**File:** `domain/{language}_config.py`

**Step 3.1.1: Define Language Metadata**
```python
from ..zh_config import ZhConfig  # Use as reference template

class {Language}Config(ZhConfig):
    """Configuration for {Language} analyzer"""

    def __init__(self):
        super().__init__()
        # Override with language-specific settings
        self.language_code = '{code}'
        self.language_name = '{Language}'
        self.native_name = '{Native Name}'
        self.language_family = '{Family}'
        self.script_type = 'alphabetic'  # alphabetic, logographic, abugida
        self.script_direction = 'ltr'    # ltr, rtl
```

**Step 3.1.2: Define Grammatical Roles Mapping**
```python
    @property
    def grammatical_roles(self) -> Dict[str, str]:
        """Map language-specific terms to universal roles"""
        return {
            # Nouns
            'noun_term': 'noun',
            'proper_noun_term': 'proper_noun',

            # Verbs
            'verb_term': 'verb',
            'auxiliary_term': 'auxiliary',

            # Adjectives
            'adjective_term': 'adjective',

            # Function words
            'preposition_term': 'preposition',
            'conjunction_term': 'conjunction',
            'pronoun_term': 'pronoun',

            # Language-specific roles
            'aspect_marker_term': 'aspect_marker',
            'classifier_term': 'classifier',
        }
```

**Step 3.1.3: Define Color Schemes**
```python
    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for grammatical roles"""
        schemes = {
            'beginner': {
                'noun': '#FFAA00',
                'verb': '#4ECDC4',
                'adjective': '#FF44FF',
                'adverb': '#9370DB',
                'pronoun': '#FFEAA7',
                'preposition': '#4444FF',
                'conjunction': '#AAAAAA',
            },
            'intermediate': {
                # Add more roles for intermediate
                **self.get_color_scheme('beginner'),
                'aspect_marker': '#9370DB',
                'classifier': '#FF8C00',
                'modal_particle': '#DA70D6',
            },
            'advanced': {
                # Add all roles for advanced
                **self.get_color_scheme('intermediate'),
                'structural_particle': '#98FB98',
                'discourse_particle': '#F0E68C',
            }
        }
        return schemes.get(complexity, schemes['beginner'])
```

**Step 3.1.4: Define Prompt Templates**
```python
        self.prompt_templates = {
            "single": """
Analyze this {language_name} sentence: {{sentence}}

Target word: {{target_word}}
Complexity level: {{complexity}}

Identify the grammatical role of each word:
{grammatical_roles_list}

Return JSON:
{{
  "words": [
    {{
      "word": "word1",
      "grammatical_role": "noun",
      "meaning": "brief explanation"
    }}
  ],
  "explanations": {{
    "overall_structure": "sentence structure explanation",
    "key_features": "important grammatical features"
  }}
}}

Be accurate and provide clear explanations.""",

            "batch": """
Analyze these {language_name} sentences:

{{sentences}}

Target word: {{target_word}}
Complexity level: {{complexity}}

For each sentence, provide grammatical analysis in this format:
{{
  "batch_results": [
    {{
      "sentence": "sentence text",
      "words": [...],
      "explanations": {{...}}
    }}
  ]
}}

Provide comprehensive analysis for each sentence."""
        }
```

#### 3.2 Prompt Builder Component (6-8 hours)

**File:** `domain/{language}_prompt_builder.py`

**Step 3.2.1: Basic Implementation**
```python
import logging
from typing import List
from jinja2 import Template
from .zh_prompt_builder import ZhPromptBuilder  # Reference implementation

logger = logging.getLogger(__name__)

class {Language}PromptBuilder(ZhPromptBuilder):
    """Builds AI prompts for {Language} grammar analysis"""

    def __init__(self, config: {Language}Config):
        self.config = config
        # Initialize templates
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

        # Pre-load complexity-specific templates if needed
        self._init_complexity_templates()

    def _init_complexity_templates(self):
        """Initialize complexity-specific prompt templates"""
        # Override for language-specific complexity handling
        pass
```

**Step 3.2.2: Single Prompt Generation**
```python
    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single sentence analysis"""
        try:
            context = {
                'sentence': sentence,
                'target_word': target_word or '',
                'complexity': complexity,
                'language_name': self.config.language_name,
                'grammatical_roles_list': self._format_roles_list(complexity),
                'native_language': 'English',  # Target language for explanations
            }

            prompt = self.single_template.render(**context)
            logger.debug(f"Built single prompt for {complexity} complexity")
            return prompt

        except Exception as e:
            logger.error(f"Failed to build single prompt: {e}")
            return self._create_fallback_prompt(sentence, target_word, complexity)

    def _format_roles_list(self, complexity: str) -> str:
        """Format grammatical roles list for prompt"""
        roles = self.config.grammatical_roles

        if complexity == 'beginner':
            # Basic roles only
            basic_roles = ['noun', 'verb', 'adjective', 'adverb', 'pronoun']
            role_list = [k for k, v in roles.items() if v in basic_roles]
        elif complexity == 'intermediate':
            # Add function words
            intermediate_roles = ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                                'preposition', 'conjunction', 'aspect_marker', 'classifier']
            role_list = [k for k, v in roles.items() if v in intermediate_roles]
        else:  # advanced
            # All roles
            role_list = list(roles.keys())

        return '- ' + '\n- '.join(role_list)
```

**Step 3.2.3: Batch Prompt Generation**
```python
    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch analysis"""
        try:
            context = {
                'sentences': '\n'.join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences)),
                'target_word': target_word or '',
                'complexity': complexity,
                'language_name': self.config.language_name,
                'sentence_count': len(sentences),
            }

            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch prompt for {len(sentences)} sentences")
            return prompt

        except Exception as e:
            logger.error(f"Failed to build batch prompt: {e}")
            return self._create_fallback_batch_prompt(sentences, target_word, complexity)

    def _create_fallback_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Create basic fallback prompt"""
        return f"""Analyze this {self.config.language_name} sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}
Provide grammatical analysis in JSON format."""

    def _create_fallback_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Create basic fallback batch prompt"""
        sentences_text = '\n'.join(sentences)
        return f"""Analyze these {self.config.language_name} sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}
Provide batch grammatical analysis in JSON format."""
```

#### 3.3 Response Parser Component (8-12 hours)

**File:** `domain/{language}_response_parser.py`

**Step 3.3.1: Basic Implementation**
```python
import json
import logging
import re
from typing import Dict, Any, List
from .zh_response_parser import ZhResponseParser

logger = logging.getLogger(__name__)

class {Language}ResponseParser(ZhResponseParser):
    """Parses AI responses for {Language} analysis"""

    def __init__(self, config: {Language}Config):
        super().__init__(config)
        self.config = config

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str) -> Dict[str, Any]:
        """Parse AI response into standardized format"""
        try:
            # Extract JSON from response
            json_data = self._extract_json(ai_response)
            if not json_data:
                logger.warning("No JSON found in AI response")
                return self.fallbacks.create_fallback(sentence, complexity)

            # Validate basic structure
            if not self._validate_response_structure(json_data):
                logger.warning("Invalid response structure")
                return self.fallbacks.create_fallback(sentence, complexity)

            # Apply language-specific transformations
            normalized = self._normalize_response(json_data, sentence, complexity)

            # Create standardized output format
            return self._create_standard_format(normalized, sentence, complexity)

        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return self.fallbacks.create_fallback(sentence, complexity)
```

**Step 3.3.2: JSON Extraction**
```python
    def _extract_json(self, ai_response: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        try:
            # Look for JSON block in response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Try parsing entire response
                return json.loads(ai_response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return None

    def _validate_response_structure(self, json_data: Dict) -> bool:
        """Validate basic response structure"""
        # Check for required fields
        if 'words' not in json_data and 'batch_results' not in json_data:
            return False

        # For single response
        if 'words' in json_data:
            words = json_data.get('words', [])
            if not isinstance(words, list) or len(words) == 0:
                return False

            # Check each word has required fields
            for word in words:
                if not isinstance(word, dict):
                    return False
                if 'word' not in word or 'grammatical_role' not in word:
                    return False

        # For batch response
        if 'batch_results' in json_data:
            results = json_data.get('batch_results', [])
            if not isinstance(results, list) or len(results) == 0:
                return False

        return True
```

**Step 3.3.3: Response Normalization**
```python
    def _normalize_response(self, json_data: Dict, sentence: str, complexity: str) -> Dict:
        """Apply language-specific normalizations"""
        normalized = json_data.copy()

        # Handle single vs batch responses
        if 'batch_results' in json_data:
            # Batch response - take first result if single sentence
            results = json_data['batch_results']
            if len(results) == 1:
                normalized = results[0]
            else:
                # Multiple results - keep batch format
                normalized['batch_results'] = [
                    self._normalize_single_result(result, complexity)
                    for result in results
                ]
                return normalized

        # Normalize single result
        return self._normalize_single_result(normalized, complexity)

    def _normalize_single_result(self, result: Dict, complexity: str) -> Dict:
        """Normalize a single result"""
        normalized = result.copy()

        # Normalize grammatical roles
        if 'words' in normalized:
            normalized['words'] = [
                self._normalize_word(word, complexity)
                for word in normalized['words']
            ]

        # Ensure explanations exist
        if 'explanations' not in normalized:
            normalized['explanations'] = {
                'overall_structure': 'Analysis completed',
                'key_features': 'Grammatical roles identified'
            }

        return normalized

    def _normalize_word(self, word: Dict, complexity: str) -> Dict:
        """Normalize individual word analysis"""
        normalized = word.copy()

        # Normalize grammatical role
        if 'grammatical_role' in normalized:
            original_role = normalized['grammatical_role']
            normalized['grammatical_role'] = self._normalize_role(original_role)

        # Ensure meaning exists
        if 'meaning' not in normalized:
            normalized['meaning'] = f"{normalized.get('word', 'word')} in sentence context"

        return normalized

    def _normalize_role(self, role: str) -> str:
        """Normalize role to standard format"""
        # Map language-specific terms to universal roles
        role_mapping = self.config.grammatical_roles
        return role_mapping.get(role.lower(), role.lower())
```

**Step 3.3.4: Standard Format Creation**
```python
    def _create_standard_format(self, normalized: Dict, sentence: str, complexity: str) -> Dict:
        """Create standardized output format"""
        # Convert to word_explanations format expected by analyzer
        word_explanations = []

        if 'words' in normalized:
            color_scheme = self.config.get_color_scheme(complexity)

            for word_data in normalized['words']:
                word = word_data.get('word', '')
                role = word_data.get('grammatical_role', 'unknown')
                meaning = word_data.get('meaning', '')

                # Get color for role
                category = self._map_role_to_category(role)
                color = color_scheme.get(category, '#888888')

                word_explanations.append([word, role, color, meaning])

        return {
            'word_explanations': word_explanations,
            'elements': {},  # Can be populated with additional analysis
            'explanations': normalized.get('explanations', {}),
            'sentence': sentence,
            'complexity': complexity,
            'language_code': self.config.language_code
        }

    def _map_role_to_category(self, role: str) -> str:
        """Map grammatical role to color category"""
        # Simple mapping - can be made more sophisticated
        role_to_category = {
            'noun': 'noun',
            'verb': 'verb',
            'adjective': 'adjective',
            'adverb': 'adverb',
            'pronoun': 'pronoun',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'aspect_marker': 'aspect_marker',
            'classifier': 'classifier',
        }
        return role_to_category.get(role, 'other')
```

#### 3.4 Validator Component (6-8 hours)

**File:** `domain/{language}_validator.py`

**Step 3.4.1: Basic Implementation**
```python
import logging
from typing import Dict, Any, List
from .zh_validator import ZhValidator

logger = logging.getLogger(__name__)

class {Language}Validator(ZhValidator):
    """Validates {Language} analysis results"""

    def __init__(self, config: {Language}Config):
        super().__init__(config)
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores"""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence:.2f}) for sentence: {sentence}")

        # Add validation metadata
        result['validation_metadata'] = {
            'word_count': len(result.get('word_explanations', [])),
            'sentence_length': len(sentence),
            'complexity_level': result.get('complexity', 'unknown'),
            'validation_timestamp': self._get_timestamp()
        }

        return result

    def _get_timestamp(self) -> str:
        """Get current timestamp for validation metadata"""
        from datetime import datetime
        return datetime.now().isoformat()
```

**Step 3.4.2: Confidence Calculation**
```python
    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on multiple heuristics"""
        score = 1.0
        issues = []

        # Check 1: Word count matches sentence structure
        word_explanations = result.get('word_explanations', [])
        sentence_words = self._tokenize_sentence(sentence)

        if len(word_explanations) == 0:
            return 0.0

        # Allow some flexibility for compound words or different tokenization
        word_ratio = len(word_explanations) / len(sentence_words)
        if word_ratio < 0.5 or word_ratio > 2.0:
            score *= 0.7
            issues.append(f"Word count mismatch: {len(word_explanations)} analyzed vs {len(sentence_words)} in sentence")

        # Check 2: Role distribution makes sense
        roles = [exp[1] if len(exp) > 1 else 'unknown' for exp in word_explanations]
        role_score = self._evaluate_role_distribution(roles)
        score *= role_score

        # Check 3: Explanations quality
        explanation_score = self._evaluate_explanations(result)
        score *= explanation_score

        # Check 4: Language-specific patterns
        pattern_score = self._check_language_patterns(result, sentence)
        score *= pattern_score

        # Log issues for debugging
        if issues:
            logger.info(f"Validation issues for '{sentence}': {issues}")

        return min(max(score, 0.0), 1.0)

    def _tokenize_sentence(self, sentence: str) -> List[str]:
        """Basic sentence tokenization"""
        # Simple whitespace tokenization - override for complex scripts
        return sentence.split()

    def _evaluate_role_distribution(self, roles: List[str]) -> float:
        """Evaluate if role distribution makes sense"""
        if not roles:
            return 0.0

        # Basic checks
        unique_roles = set(roles)

        # Should have some content words
        content_words = {'noun', 'verb', 'adjective', 'adverb'}
        has_content = any(role in content_words for role in unique_roles)

        # Shouldn't have too many unknown roles
        unknown_ratio = roles.count('unknown') / len(roles)

        score = 1.0
        if not has_content:
            score *= 0.6
        if unknown_ratio > 0.3:
            score *= 0.8

        return score

    def _evaluate_explanations(self, result: Dict[str, Any]) -> float:
        """Evaluate quality of explanations"""
        explanations = result.get('explanations', {})

        if not explanations:
            return 0.7

        score = 1.0

        # Check overall structure explanation
        overall = explanations.get('overall_structure', '')
        if len(overall.strip()) < 10:
            score *= 0.9

        # Check key features explanation
        features = explanations.get('key_features', '')
        if len(features.strip()) < 10:
            score *= 0.9

        return score

    def _check_language_patterns(self, result: Dict[str, Any], sentence: str) -> float:
        """Check for language-specific patterns"""
        # Basic implementation - override for specific languages
        return 1.0
```

### Phase 4: Main Analyzer Implementation (4-6 hours)

#### 4.1 Create Main Analyzer Class

**File:** `{language}_analyzer.py`

```python
import logging
from typing import Dict, List, Any
from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig
from .domain.{language}_config import {Language}Config
from .domain.{language}_prompt_builder import {Language}PromptBuilder
from .domain.{language}_response_parser import {Language}ResponseParser
from .domain.{language}_validator import {Language}Validator

logger = logging.getLogger(__name__)

class {Language}Analyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for {Language} ({native_name}).

    {Brief description of language-specific features}
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "{code}"
    LANGUAGE_NAME = "{Language}"

    def __init__(self):
        """Initialize {Language} analyzer with domain components"""
        logger.info(f"Initializing {Language} analyzer v{self.VERSION}")

        # Initialize domain components
        self.config = {Language}Config()
        self.prompt_builder = {Language}PromptBuilder(self.config)
        self.response_parser = {Language}ResponseParser(self.config)
        self.validator = {Language}Validator(self.config)

        # Create language configuration
        language_config = LanguageConfig(
            code=self.config.language_code,
            name=self.config.language_name,
            native_name=self.config.native_name,
            family=self.config.language_family,
            script_type=self.config.script_type,
            complexity_rating="medium",  # low, medium, high
            key_features=['feature1', 'feature2', 'feature3'],  # From research
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )

        super().__init__(language_config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str):
        """Main analysis method - orchestrates domain components"""
        try:
            logger.info(f"Analyzing sentence: {sentence[:50]}...")

            # Build AI prompt
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)

            # Call AI API
            ai_response = self._call_ai(prompt, gemini_api_key)

            # Parse response
            parsed_result = self.parse_grammar_response(ai_response, complexity, sentence)

            # Validate result
            validated_result = self.validate_analysis(parsed_result, sentence)

            # Generate HTML output
            html_output = self._generate_html_output(validated_result, sentence, complexity)

            # Create final GrammarAnalysis object
            from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis

            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated_result.get('elements', {}),
                explanations=validated_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=validated_result.get('confidence', 0.5),
                word_explanations=validated_result.get('word_explanations', [])
            )

        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            # Return fallback analysis
            return self._create_fallback_analysis(sentence, target_word, complexity, str(e))

    # Abstract method implementations
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate AI prompt for grammar analysis"""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized format"""
        return self.response_parser.parse_response(ai_response, complexity, sentence, target_word)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis and return confidence score"""
        validated = self.validator.validate_result(parsed_data, original_sentence)
        return validated.get('confidence', 0.5)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for grammatical roles"""
        return self.config.get_color_scheme(complexity)

    def _create_fallback_analysis(self, sentence: str, target_word: str, complexity: str, error: str):
        """Create fallback analysis when main analysis fails"""
        logger.warning(f"Using fallback analysis for: {sentence}")

        # Create basic word-by-word breakdown
        words = sentence.split()
        word_explanations = []

        for word in words:
            # Basic role assignment - very simplistic
            if word.lower() in ['the', 'a', 'an']:
                role = 'determiner'
            elif word.lower() in ['is', 'am', 'are', 'was', 'were', 'be', 'been', 'being']:
                role = 'verb'
            else:
                role = 'noun'  # Default assumption

            color = self.get_color_scheme(complexity).get(role, '#888888')
            word_explanations.append([word, role, color, f"Basic analysis: {role}"])

        from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis

        return GrammarAnalysis(
            sentence=sentence,
            target_word=target_word or "",
            language_code=self.language_code,
            complexity_level=complexity,
            grammatical_elements={},
            explanations={
                'overall_structure': 'Fallback analysis due to processing error',
                'key_features': f'Error: {error}'
            },
            color_scheme=self.get_color_scheme(complexity),
            html_output=self._generate_html_output({'word_explanations': word_explanations}, sentence, complexity),
            confidence_score=0.2,  # Low confidence for fallback
            word_explanations=word_explanations
        )
```

### Phase 5: Testing Implementation (1-2 weeks)

#### 5.1 Unit Tests (4-6 hours)

**File:** `tests/test_{language}_analyzer.py`

```python
import pytest
from ..{language}_analyzer import {Language}Analyzer
from ..domain.{language}_config import {Language}Config

class Test{Language}Analyzer:
    """Unit tests for {Language} analyzer components"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    @pytest.fixture
    def config(self):
        return {Language}Config()

    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.language_code == "{code}"
        assert analyzer.language_name == "{Language}"
        assert hasattr(analyzer, 'config')
        assert hasattr(analyzer, 'prompt_builder')
        assert hasattr(analyzer, 'response_parser')
        assert hasattr(analyzer, 'validator')

    def test_config_properties(self, config):
        """Test configuration has required properties"""
        assert hasattr(config, 'language_code')
        assert hasattr(config, 'grammatical_roles')
        assert hasattr(config, 'get_color_scheme')

    def test_color_scheme(self, config):
        """Test color scheme generation"""
        colors = config.get_color_scheme('beginner')
        assert isinstance(colors, dict)
        assert len(colors) > 0

        # Check some basic roles exist
        assert 'noun' in colors
        assert 'verb' in colors

    def test_prompt_generation(self, analyzer):
        """Test prompt generation"""
        prompt = analyzer.get_grammar_prompt('beginner', 'Test sentence', 'test')
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'Test sentence' in prompt

    def test_response_parsing(self, analyzer):
        """Test response parsing with mock data"""
        mock_response = '''{
            "words": [
                {"word": "test", "grammatical_role": "noun", "meaning": "a test word"}
            ],
            "explanations": {
                "overall_structure": "Simple sentence",
                "key_features": "Basic grammar"
            }
        }'''

        result = analyzer.parse_grammar_response(mock_response, 'beginner', 'test sentence')
        assert 'word_explanations' in result
        assert len(result['word_explanations']) > 0

    def test_validation(self, analyzer):
        """Test result validation"""
        mock_result = {
            'word_explanations': [['test', 'noun', '#FFAA00', 'a test']],
            'explanations': {'overall_structure': 'test', 'key_features': 'test'}
        }

        confidence = analyzer.validate_analysis(mock_result, 'test sentence')
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_fallback_analysis(self, analyzer):
        """Test fallback analysis creation"""
        result = analyzer._create_fallback_analysis('test sentence', 'test', 'beginner', 'mock error')
        assert result.sentence == 'test sentence'
        assert result.confidence_score < 0.5  # Low confidence for fallback
```

#### 5.2 Integration Tests (6-8 hours)

**File:** `tests/test_{language}_integration.py`

```python
import pytest
from ..{language}_analyzer import {Language}Analyzer

class Test{Language}Integration:
    """Integration tests for complete analysis workflow"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    def test_full_analysis_workflow_mock(self, analyzer, monkeypatch):
        """Test complete analysis with mocked AI call"""
        # Mock the AI call to return predictable response
        def mock_call_ai(prompt, api_key):
            return '''{
                "words": [
                    {"word": "The", "grammatical_role": "determiner", "meaning": "definite article"},
                    {"word": "cat", "grammatical_role": "noun", "meaning": "subject of sentence"},
                    {"word": "eats", "grammatical_role": "verb", "meaning": "main action"},
                    {"word": "fish", "grammatical_role": "noun", "meaning": "object of action"}
                ],
                "explanations": {
                    "overall_structure": "Subject-Verb-Object sentence structure",
                    "key_features": "Basic English word order"
                }
            }'''

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar('The cat eats fish', 'cat', 'beginner', 'mock_key')

        assert result.sentence == 'The cat eats fish'
        assert result.target_word == 'cat'
        assert len(result.word_explanations) == 4
        assert result.confidence_score > 0.5

    def test_error_handling(self, analyzer, monkeypatch):
        """Test error handling and fallback mechanisms"""
        # Mock AI call to raise exception
        def mock_call_ai(prompt, api_key):
            raise Exception("API Error")

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        result = analyzer.analyze_grammar('Test sentence', 'test', 'beginner', 'mock_key')

        # Should return fallback analysis
        assert result.sentence == 'Test sentence'
        assert result.confidence_score < 0.5

    def test_complexity_levels(self, analyzer, monkeypatch):
        """Test different complexity levels"""
        def mock_call_ai(prompt, api_key):
            return '''{"words": [{"word": "test", "grammatical_role": "noun", "meaning": "test"}], "explanations": {"overall_structure": "test", "key_features": "test"}}'''

        monkeypatch.setattr(analyzer, '_call_ai', mock_call_ai)

        for complexity in ['beginner', 'intermediate', 'advanced']:
            result = analyzer.analyze_grammar('Test sentence', 'test', complexity, 'mock_key')
            assert result.complexity_level == complexity

    def test_color_schemes(self, analyzer):
        """Test color scheme variations"""
        beginner_colors = analyzer.get_color_scheme('beginner')
        intermediate_colors = analyzer.get_color_scheme('intermediate')
        advanced_colors = analyzer.get_color_scheme('advanced')

        # Intermediate should have at least as many colors as beginner
        assert len(intermediate_colors) >= len(beginner_colors)
        # Advanced should have at least as many colors as intermediate
        assert len(advanced_colors) >= len(intermediate_colors)
```

### Phase 6: Integration and Deployment (2-4 hours)

#### 6.1 Register Analyzer

**File:** `streamlit_app/language_analyzers/__init__.py` (or equivalent)

```python
# Add import for new analyzer
from languages.{language}.{language}_analyzer import {Language}Analyzer

# Add to analyzer registry
ANALYZER_REGISTRY = {
    # ... existing analyzers
    '{code}': {Language}Analyzer(),
}
```

#### 6.2 Test Integration

```python
# Test that analyzer integrates properly
from streamlit_app.language_analyzers import ANALYZER_REGISTRY

def test_analyzer_registration():
    """Test that new analyzer is properly registered"""
    assert '{code}' in ANALYZER_REGISTRY
    analyzer = ANALYZER_REGISTRY['{code}']
    assert isinstance(analyzer, {Language}Analyzer)
    assert analyzer.language_code == '{code}'
```

## ✅ Success Criteria

### Code Quality
- [ ] All domain components implemented and tested
- [ ] Clean separation of concerns maintained
- [ ] Proper error handling and logging
- [ ] Comprehensive docstrings and comments

### Functionality
- [ ] Single sentence analysis works correctly
- [ ] Batch processing supported
- [ ] HTML output generation functional
- [ ] Color-coded grammatical roles accurate

### Testing
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Error scenarios handled gracefully
- [ ] Performance within acceptable limits

### Quality Assurance
- [ ] Linguistic accuracy validated against research
- [ ] Confidence scoring works appropriately
- [ ] Fallback mechanisms functional
- [ ] Documentation complete and accurate

## 🚨 Common Implementation Pitfalls

### 1. Skipping Research Phase
**Problem:** Starting coding without comprehensive research
**Prevention:** Always complete `{language}_grammar_concepts.md` first

### 2. Tight Coupling
**Problem:** Components depend on each other too heavily
**Prevention:** Follow dependency injection and interface segregation

### 3. Poor Error Handling
**Problem:** Analysis fails silently or crashes
**Prevention:** Implement comprehensive error handling and fallbacks

### 4. Inadequate Testing
**Problem:** Bugs discovered late in development
**Prevention:** Write tests as you implement, not after

### 5. Ignoring Complexity Levels
**Problem:** Same analysis for all complexity levels
**Prevention:** Implement different logic for beginner/intermediate/advanced

## 📊 Implementation Timeline

- **Phase 1:** Research Validation - 1-2 days
- **Phase 2:** Directory Setup - 2-4 hours
- **Phase 3:** Domain Components - 1-2 weeks
- **Phase 4:** Main Analyzer - 4-6 hours
- **Phase 5:** Testing - 1-2 weeks
- **Phase 6:** Integration - 2-4 hours

**Total Time:** 3-5 weeks for complete implementation

## 🎯 Next Steps

### After Implementation
1. **Run Comprehensive Tests** - Ensure all functionality works
2. **Validate Against Research** - Compare results with research document
3. **Performance Testing** - Check speed and resource usage
4. **Integration Testing** - Test with full application

### For Production Deployment
1. **Code Review** - Get feedback from experienced developers
2. **Load Testing** - Test with realistic usage patterns
3. **Monitoring Setup** - Add production monitoring and alerting
4. **Documentation Update** - Update all relevant documentation

---

**🚀 Ready to start implementing?** Begin with Phase 1: Research Validation, then follow each phase sequentially. Remember: quality over speed - take time to do it right!

**Need help?** Refer to the [Architecture Guide](architecture_guide.md) for design patterns, [Testing Guide](testing_guide.md) for testing strategies, or [Troubleshooting Guide](troubleshooting_guide.md) for common issues.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\implementation_guide.md