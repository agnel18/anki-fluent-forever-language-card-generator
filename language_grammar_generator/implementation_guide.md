# Implementation Guide
## Step-by-Step Language Analyzer Development

**Prerequisites:** Complete research phase ([Research Guide](research_guide.md))
**Primary Gold Standard:** Study [French Analyzer v2.0](languages/french/fr_analyzer.py) - Production Excellence
**Secondary References:** [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py), [Hindi](languages/hindi/hi_analyzer.py)
**Time Estimate:** 2-4 weeks for full implementation
**Critical:** Follow French v2.0 patterns - enterprise reliability, advanced AI integration, comprehensive quality assurance

## 🎯 Implementation Workflow

### Phase 1: Gold Standard Study (1-2 days)
#### 1.1 Study Working Analyzers Thoroughly
- [ ] **French Analyzer v2.0** (`languages/french/fr_analyzer.py`) - **PRIMARY GOLD STANDARD**:
  - Enterprise-grade reliability with circuit breaker patterns
  - Advanced AI integration with 5-level fallback parsing
  - Comprehensive error handling and monitoring
  - Confidence scoring with quality validation
  - APKG-ready output with HTML color coding
  - Production monitoring and observability
  - 99.9% uptime with graceful degradation

- [ ] **Chinese Simplified Analyzer** (`languages/chinese_simplified/zh_analyzer.py`) - **SECONDARY REFERENCE**:
  - Clean Architecture with domain-driven design
  - External configuration files for maintainability
  - Integrated fallback systems within domain layer
  - Template-based prompt engineering

- [ ] **Hindi Analyzer** (`languages/hindi/hi_analyzer.py`):
  - Indo-European family reference implementation
  - Complex language handling patterns
  - Comprehensive error handling with fallbacks

#### 1.2 Identify Key Patterns from French v2.0
- [ ] **Enterprise Reliability**: Circuit breaker pattern, comprehensive monitoring, graceful degradation
- [ ] **Advanced AI Integration**: 5-level fallback parsing, retry logic, confidence scoring
- [ ] **Quality Assurance**: Gold standard validation, performance benchmarking, automated testing
- [ ] **APKG Optimization**: HTML color coding, detailed word explanations, interactive flashcards
- [ ] **Production Monitoring**: Structured logging, performance metrics, alerting integration
- [ ] **Robust Error Handling**: Multi-level fallbacks, error classification, recovery mechanisms

#### 1.3 Critical: Production Excellence Pattern (French v2.0 Gold Standard)
**Key Learning from French v2.0:** Enterprise-grade implementations require comprehensive error handling, monitoring, and quality assurance beyond basic functionality.

**✅ Production Excellence Pattern (French v2.0):**
```python
# Enterprise-grade components
fr_analyzer.py              # Main facade with enterprise error handling
domain/
├── fr_config.py           # Advanced configuration with validation
├── fr_prompt_builder.py   # AI prompt generation with Jinja2
├── fr_response_parser.py  # 5-level fallback parsing strategy
├── fr_validator.py        # Confidence scoring & quality validation
└── fr_fallbacks.py        # Rule-based analysis with performance monitoring
infrastructure/
├── fr_circuit_breaker.py  # Circuit breaker pattern implementation
├── fr_ai_service.py       # Advanced Gemini integration with retry logic
└── data/                  # External configuration with validation rules
tests/
├── test_fr_gold_standard.py    # Gold standard validation
└── test_fr_performance.py      # Performance benchmarking
```
zh_word_meanings.json
zh_patterns.yaml

# Domain components with integrated fallbacks
class ZhResponseParser:
    def __init__(self, config: ZhConfig, fallbacks: ZhFallbacks):
        # Integrated fallback system
        
class ZhPromptBuilder:
    def __init__(self, config: ZhConfig):
        # Jinja2 template system
```

**âŒ Anti-Pattern (Complex Modular Architecture):**
```python
# Separate infrastructure layer
infrastructure/
â”œâ”€â”€ zh_tw_fallbacks.py  # Separate component
â””â”€â”€ data/

# Hardcoded configurations
class ZhTwConfig:
    def __init__(self):
        self.grammatical_roles = {...}  # Hardcoded
```
```python
# Rich explanations with individual meanings
"æˆ‘ (I, me - first person singular pronoun)"
"å–œæ­¡ (to like, to be fond of - verb expressing preference)"
"åƒ (to eat, to consume - verb of consumption)"
```

**Implementation Requirements:**
- [ ] **analyze_grammar method**: AI workflow â†’ parsing â†’ HTML generation
- [ ] **_generate_html_output method**: Position-based coloring with meanings
- [ ] **GrammarAnalysis return**: Structured word_explanations with [word, role, color, meaning]
- [ ] **Individual meaning extraction**: Parse `individual_meaning` from AI responses
- [ ] **Word Meanings Dictionary**: External JSON file with specific meanings (CRITICAL for Sino-Tibetan languages)
- [ ] **Sentence Generation Character Limits**: Word explanations < 75 chars, grammar summaries < 60 chars (CRITICAL for UX)

#### 1.4 Critical: Role Hierarchy & Complexity Filtering (Arabic Analyzer Innovation)

**Key Learning from Arabic Analyzer:** Implement role hierarchy mapping and complexity-based filtering to provide educational depth without visual clutter.

**Why Required:**
- **Educational Depth vs Visual Clarity**: Specific roles (imperfect_verb) provide detailed explanations while general roles (verb) maintain consistent coloring
- **Progressive Disclosure**: Beginner learners see basic roles, advanced learners see morphological details
- **Color Inheritance**: Specific roles inherit colors from parent categories for visual consistency
- **Role Consistency**: Meaning text matches display role to eliminate grammatical role repetition

**Implementation Pattern:**
```python
# 1. Role Hierarchy Mapping
class LanguageConfig:
    def _create_role_hierarchy(self) -> Dict[str, str]:
        """Map specific roles to parent roles for color inheritance"""
        return {
            # Verb subtypes inherit verb color
            'perfect_verb': 'verb',
            'imperfect_verb': 'verb', 
            'imperative_verb': 'verb',
            'active_participle': 'verb',
            'passive_participle': 'verb',
            
            # Noun subtypes inherit noun color
            'dual': 'noun',
            'sound_plural': 'noun',
            'broken_plural': 'noun',
            
            # Case markers inherit from base roles
            'nominative': 'noun',
            'accusative': 'noun',
            'genitive': 'noun',
        }

# 2. Complexity-Based Role Filtering
class LanguageConfig:
    def _create_complexity_filters(self) -> Dict[str, set]:
        """Filter roles based on complexity level"""
        return {
            'beginner': {'noun', 'verb', 'pronoun', 'particle'},
            'intermediate': {
                'noun', 'verb', 'pronoun', 'adjective', 'preposition', 
                'conjunction', 'interrogative', 'negation', 'definite_article',
                'imperfect_verb', 'perfect_verb', 'active_participle', 'passive_participle'
            },
            'advanced': set()  # Allow all roles
        }
    
    def should_show_role(self, role: str, complexity: str) -> bool:
        """Check if role should be displayed at complexity level"""
        if complexity == 'advanced':
            return True
        allowed_roles = self.complexity_role_filters.get(complexity, set())
        return role in allowed_roles or self.get_parent_role(role) in allowed_roles

# 3. Prevention-at-Source Word Explanations (German & Spanish Innovation)

**Key Learning from German & Spanish Analyzers:** Prevention-at-source eliminates complex post-processing and produces superior educational explanations.

**OLD Approach (Post-Processing - REMOVED):**
```python
# Complex role consistency processing
if meaning and '(' in meaning and ')' in meaning:
    # Regex parsing and role replacement
    updated_meaning = f"{word_part} ({display_role}): {rest_meaning}"
```

**NEW Approach (Prevention-at-Source - RECOMMENDED):**
```python
# Direct preservation of AI's detailed explanations
word_data['meaning'] = meaning  # No post-processing needed
```

### Response Parser - Prevention-at-Source Pattern

**File:** `domain/{language}_response_parser.py`
```python
class LanguageResponseParser:
    def _process_word_explanations(self, words_data: List[Dict], complexity: str) -> List[List]:
        explanations = []

        for word_data in words_data:
            word = word_data.get('word', '')
            grammatical_role = word_data.get('grammatical_role', '')
            meaning = word_data.get('individual_meaning', word_data.get('meaning', ''))

            # Apply complexity-based role filtering
            normalized_role = self._normalize_grammatical_role(grammatical_role)
            if not self.config.should_show_role(normalized_role, complexity):
                display_role = self.config.get_parent_role(normalized_role)
            else:
                display_role = normalized_role

            # Color inheritance from parent role
            parent_role = self.config.get_parent_role(normalized_role)
            color = color_scheme.get(parent_role, color_scheme.get('other', '#708090'))

            # PREVENTION-AT-SOURCE: Keep AI's detailed explanation as-is
            # No post-processing format addition or role consistency fixes needed

            explanations.append([word, display_role, color, meaning])

        return explanations
```

### Quality Results - Prevention-at-Source Examples

**German Example:**
```json
"individual_meaning": "Serves as the subject of the sentence, representing the individual who performs the action. It is a common noun, inherently masculine in gender. Its nominative case indicates its function as the grammatical subject, the actor in the sentence. The singular form of the noun dictates that the verb 'geht' must be conjugated in the 3rd person singular. It forms the complete subject noun phrase 'Der Mann' in conjunction with its preceding definite article."
```

**Spanish Example:**
```json
"individual_meaning": "Serves as the subject of the sentence, identifying the entity performing the action of 'ir' (to go). It is a masculine singular noun, agreeing in gender and number with its preceding determiner 'El'. As the core of the subject noun phrase, it dictates the singular, third-person conjugation of the verb 'va', establishing the agent of the sentence."
```

**Benefits:**
- **No Repetition:** Each explanation is unique and contextual
- **Educational Depth:** Shows grammatical relationships and language-specific features
- **Maintainability:** Eliminates complex post-processing logic
- **Superior Quality:** AI generates detailed explanations directly
```

**Critical Checklist:**
- [ ] **Prevention-at-Source Prompts:** Use descriptive prompts that generate detailed explanations directly (like German/Spanish analyzers)
- [ ] **No Post-Processing:** Eliminate repetitive format addition in response parsers
- [ ] **Unique Explanations:** Each word gets a distinct, contextual explanation
- [ ] **Language-Specific Features:** Highlight grammar unique to each language
- [ ] **Educational Depth:** Show grammatical relationships and contributions to sentence meaning

#### 1.5 Critical: Sentence Generation Character Limits (UX Requirement)

**Key Learning:** Sentence generation prompts must enforce strict character limits to prevent overwhelming users with verbose explanations.

**Why Required:**
- **UX Overload Prevention**: Long explanations reduce user engagement and completion rates
- **Mobile-Friendly**: Shorter explanations work better on mobile devices
- **Cognitive Load**: Users can process concise information more effectively
- **Consistent Experience**: Same limits across all languages prevent jarring differences

**Character Limits:**
- **Word Explanations**: < 75 characters total (e.g., "house (building where people live)" = 32 chars)
- **Grammar Summaries**: < 60 characters total (e.g., "Irregular verb: go/went/gone" = 26 chars)

**Implementation Pattern:**
```python
# In sentence generation prompts (content_generator.py or custom analyzers)
prompt = f"""
MEANING: [brief English meaning]
IMPORTANT: Keep the entire meaning under 75 characters total.

RESTRICTIONS: [grammatical restrictions]
IMPORTANT: Keep the entire restrictions summary under 60 characters total.
"""
```

**Critical Checklist:**
- [ ] **Update default prompts**: Modify `content_generator.py` with character limits
- [ ] **Update custom prompts**: If analyzer has `get_sentence_generation_prompt()`, add limits
- [ ] **Test limits**: Verify AI responses stay within character bounds
- [ ] **Fallback handling**: Ensure fallbacks also respect character limits
- [ ] **Sentence Generation Character Limits**: < 75 chars for meanings, < 60 chars for grammar (CRITICAL for UX)

#### 1.6 Critical: Sentence Length Range Enforcement (Quality Requirement)

**Key Learning:** Word-count ranges from UI must be enforced in both prompts and post-parse validation. If not, models can return very short sentences that trigger fallback.

**Why Required:**
- **User Expectation:** Settings like 6-15 words per sentence must be honored
- **Consistency:** Avoids silent fallback to short or generic templates
- **Quality Control:** Ensures sentence length matches learner level

**Implementation Pattern:**
```python
# In sentence generation prompts (content_generator.py or custom analyzers)
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally

# In post-parse validation
word_count = len(sentence.split())
if not (min_length <= word_count <= max_length):
    # Reject and replace with fallback
```

**Chinese Exception:** If no spaces are present, treat characters as words for length checks.

**Critical Checklist:**
- [ ] **Prompt enforcement:** Min/max range included in custom prompts
- [ ] **Post-parse enforcement:** Reject sentences outside range
- [ ] **Chinese handling:** Count characters when no spaces

### Phase 2: Directory Structure Setup (2-4 hours)

#### 2.1 Create Gold Standard Directory Structure
```bash
languages/{language}/
â”œâ”€â”€ {language}_analyzer.py              # Main facade class (COPY GOLD STANDARD STRUCTURE)
â”œâ”€â”€ {language}_grammar_concepts.md      # Research documentation
â”œâ”€â”€ domain/                             # Business logic components
â”‚   â”œâ”€â”€ {language}_config.py           # Configuration (like hi_config.py/zh_config.py)
â”‚   â”œâ”€â”€ {language}_prompt_builder.py   # AI prompt generation (like hi/zh prompt builders)
â”‚   â”œâ”€â”€ {language}_response_parser.py  # AI response parsing (like hi/zh parsers)
â”‚   â””â”€â”€ {language}_validator.py        # Quality validation (NO CONFIDENCE BOOSTING)
â”œâ”€â”€ infrastructure/                     # External concerns
â”‚   â””â”€â”€ {language}_fallbacks.py        # Error recovery (like gold standards)
â””â”€â”€ tests/                              # Test suites (follow updated template)
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ test_{language}_analyzer.py    # Unit tests (no confidence boosting)
    â””â”€â”€ test_{language}_integration.py # Integration tests
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

> **CRITICAL:** Implement robust JSON parsing to handle AI responses that may be wrapped in markdown code blocks, explanatory text, or other formats. AI models often return JSON embedded in explanatory text rather than pure JSON. Use the robust extraction methods shown below to prevent fallback analysis due to parsing failures.

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

**Step 3.3.2: Robust JSON Extraction**
```python
    def _extract_json(self, ai_response: str) -> Dict[str, Any]:
        """Extract JSON from AI response with robust parsing for various formats"""
        try:
            # Clean the response
            cleaned_response = ai_response.strip()

            # If response starts with JSON, try direct parsing first
            if cleaned_response.startswith(('{', '[')):
                try:
                    return json.loads(cleaned_response)
                except json.JSONDecodeError:
                    pass  # Continue with extraction methods

            # Method 1: Extract from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL | re.IGNORECASE)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Method 2: Extract JSON between curly braces (most common case)
            brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if brace_match:
                try:
                    return json.loads(brace_match.group(0))
                except json.JSONDecodeError:
                    pass

            # Method 3: Look for JSON after explanatory text
            # Pattern: some text, then JSON starting a new line
            lines = cleaned_response.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith(('{', '[')):
                    try:
                        # Try to parse from this line onwards
                        potential_json = '\n'.join(lines[i:])
                        return json.loads(potential_json)
                    except json.JSONDecodeError:
                        continue

            # Method 4: Try parsing entire response as last resort
            return json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for all extraction methods: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during JSON extraction: {e}")
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

### Phase 4.5: Sentence Generation Prompt Implementation (2-4 hours)

**CRITICAL:** All language analyzers must implement custom sentence generation prompts for optimal AI quality. Generic prompts produce lower-quality results for linguistically complex languages.

#### 4.5.1 Add get_sentence_generation_prompt Method

**File:** `{language}_analyzer.py`

Add this method to the main analyzer class (after the existing methods):

```python
def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                 enriched_meaning: str = "", min_length: int = 3,
                                 max_length: int = 15, difficulty: str = "intermediate",
                                 topics: Optional[List[str]] = None) -> Optional[str]:
    """
    Get {Language}-specific sentence generation prompt to ensure proper response formatting.
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

    # Custom prompt for {Language} to ensure proper formatting
    prompt = f"""You are a native-level expert linguist in {self.config.language_name}.

Your task: Generate a complete learning package for the {self.config.language_name} word "{word}" in ONE response.

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
Examples: [Add language-specific examples here - e.g., case requirements, gender agreement, particles, etc.]
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in {self.config.language_name} for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native {self.config.language_name}
- Grammar, syntax, spelling, and [language-specific features] must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different [language-specific grammar features] if applicable
- Use different tenses and forms if applicable
- Use different sentence types: declarative, interrogative, imperative
[Add language-specific variety requirements here]
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: [LANGUAGE-SPECIFIC TRANSCRIPTION]
===========================
For EACH sentence above, provide [appropriate transcription method for the language].
- [Add specific transcription instructions - IPA, Pinyin, Romanization, etc.]
- [Add formatting requirements]

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
1. [sentence 1 in {language}]
2. [sentence 2 in {language}]
3. [sentence 3 in {language}]
4. [sentence 4 in {language}]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

[TRANSCRIPTION_SECTION]:
1. [transcription for sentence 1]
2. [transcription for sentence 2]
3. [transcription for sentence 3]
4. [transcription for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in {language} only
- Ensure exactly {num_sentences} sentences, translations, [transcription], and keywords"""

    return prompt
```

#### 4.5.2 Language-Specific Customizations

**For Each Language, Customize These Sections:**

**Arabic (`ar_analyzer.py`):**
- STEP 4: IPA TRANSCRIPTION (already implemented)
- Language-specific features: root-based morphology, case marking (i'rab), verb forms (abwab)
- Variety requirements: different verb forms, case usage, definite article assimilation

**Chinese Traditional/Simplified (`zh_tw_analyzer.py`, `zh_analyzer.py`):**
- STEP 4: PINYIN TRANSCRIPTION (already implemented)
- Language-specific features: aspect particles (äº†, ç€, è¿‡), measure words, character-based restrictions
- Variety requirements: different aspect markers, sentence structures

**German (`de_analyzer.py`):**
- STEP 4: IPA TRANSCRIPTION (already implemented)
- Language-specific features: case system (nominative/accusative/dative/genitive), separable verbs, gender agreement
- Variety requirements: different cases, verb forms, separable verbs

**Hindi (`hi_analyzer.py`):**
- STEP 4: ROMANIZATION (already implemented)
- Language-specific features: postpositions (à¤•à¤¾, à¤•à¥‹, à¤®à¥‡à¤‚, à¤¸à¥‡), gender agreement, Devanagari script
- Variety requirements: different postpositions, verb forms, gender agreement

**Spanish (`es_analyzer.py`):**
- STEP 4: IPA TRANSCRIPTION (already implemented)
- Language-specific features: gender agreement, verb conjugations, regional variations
- Variety requirements: different tenses, verb forms, regional variations

#### 4.5.3 Import Requirements

Add this import to the analyzer file if not already present:

```python
from typing import Optional
```

#### 4.5.4 Testing the Implementation

```python
# Test the method works
analyzer = {Language}Analyzer()
prompt = analyzer.get_sentence_generation_prompt('test_word', '{language_code}', 4)
assert isinstance(prompt, str)
assert len(prompt) > 1000  # Should be a substantial prompt
print(f"Prompt length: {len(prompt)}")
```

#### 4.5.5 Quality Validation

- [ ] Method returns valid string prompt
- [ ] Prompt includes language-specific instructions
- [ ] Output format matches expected structure
- [ ] Transcription method appropriate for language
- [ ] Language-specific grammatical features included

### Phase 4.6: Voice Implementation Validation (1-2 hours)

**CRITICAL:** All language analyzers must implement proper voice configurations that match Google Cloud Text-to-Speech voice availability and quality standards.

#### 4.6.1 Voice Configuration Requirements

**Reference Documentation:** [Google Cloud Text-to-Speech Voices](https://docs.cloud.google.com/text-to-speech/docs/list-voices-and-types)

**File:** `domain/{language}_config.py`

Add voice configuration to the language config:

```python
class {Language}Config:
    """Configuration for {Language} analyzer"""

    def __init__(self):
        # ... existing config ...

        # Voice configuration for Google Cloud Text-to-Speech
        self.voice_config = {
            'language_code': '{language_code}',  # e.g., 'ar', 'zh-CN', 'de', 'hi', 'es', 'zh-TW'
            'primary_voice': {
                'name': '{voice_name}',  # e.g., 'ar-XA-Wavenet-A', 'cmn-CN-Wavenet-A'
                'ssml_gender': '{gender}',  # MALE, FEMALE, NEUTRAL
                'natural_sample_rate_hertz': 24000
            },
            'fallback_voices': [
                {'name': '{fallback_voice_1}', 'ssml_gender': '{gender_1}'},
                {'name': '{fallback_voice_2}', 'ssml_gender': '{gender_2}'}
            ],
            'voice_quality': 'Wavenet',  # Standard, WaveNet, Neural2
            'speaking_rate': 1.0,  # 0.25-4.0
            'pitch': 0.0  # -20.0 to 20.0
        }

    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice configuration for text-to-speech"""
        return self.voice_config.copy()

    def get_primary_voice(self) -> Dict[str, Any]:
        """Get primary voice for high-quality synthesis"""
        return self.voice_config['primary_voice'].copy()

    def get_fallback_voices(self) -> List[Dict[str, Any]]:
        """Get fallback voices for error recovery"""
        return self.voice_config['fallback_voices'].copy()
```

#### 4.6.2 Language-Specific Voice Configurations

**Arabic (`ar_config.py`):**
```python
self.voice_config = {
    'language_code': 'ar-XA',  # Arabic (Modern Standard)
    'primary_voice': {
        'name': 'ar-XA-Wavenet-A',
        'ssml_gender': 'FEMALE',
        'natural_sample_rate_hertz': 24000
    },
    'fallback_voices': [
        {'name': 'ar-XA-Wavenet-B', 'ssml_gender': 'MALE'},
        {'name': 'ar-XA-Standard-A', 'ssml_gender': 'FEMALE'}
    ],
    'voice_quality': 'Wavenet',
    'speaking_rate': 0.9,  # Slightly slower for clarity
    'pitch': 0.0
}
```

**Chinese Traditional (`zh_tw_config.py`):**
```python
self.voice_config = {
    'language_code': 'zh-TW',  # Chinese (Traditional)
    'primary_voice': {
        'name': 'zh-TW-Wavenet-A',
        'ssml_gender': 'FEMALE',
        'natural_sample_rate_hertz': 24000
    },
    'fallback_voices': [
        {'name': 'zh-TW-Wavenet-B', 'ssml_gender': 'MALE'},
        {'name': 'zh-TW-Standard-A', 'ssml_gender': 'FEMALE'}
    ],
    'voice_quality': 'Wavenet',
    'speaking_rate': 1.0,
    'pitch': 0.0
}
```

**German (`de_config.py`):**
```python
self.voice_config = {
    'language_code': 'de',  # German
    'primary_voice': {
        'name': 'de-DE-Wavenet-A',
        'ssml_gender': 'FEMALE',
        'natural_sample_rate_hertz': 24000
    },
    'fallback_voices': [
        {'name': 'de-DE-Wavenet-B', 'ssml_gender': 'MALE'},
        {'name': 'de-DE-Standard-A', 'ssml_gender': 'FEMALE'}
    ],
    'voice_quality': 'Wavenet',
    'speaking_rate': 1.0,
    'pitch': 0.0
}
```

**Hindi (`hi_config.py`):**
```python
self.voice_config = {
    'language_code': 'hi',  # Hindi
    'primary_voice': {
        'name': 'hi-IN-Wavenet-A',
        'ssml_gender': 'FEMALE',
        'natural_sample_rate_hertz': 24000
    },
    'fallback_voices': [
        {'name': 'hi-IN-Wavenet-B', 'ssml_gender': 'MALE'},
        {'name': 'hi-IN-Standard-A', 'ssml_gender': 'FEMALE'}
    ],
    'voice_quality': 'Wavenet',
    'speaking_rate': 0.95,  # Slightly slower for Devanagari clarity
    'pitch': 0.0
}
```

**Spanish (`es_config.py`):**
```python
self.voice_config = {
    'language_code': 'es',  # Spanish (Spain)
    'primary_voice': {
        'name': 'es-ES-Wavenet-A',
        'ssml_gender': 'FEMALE',
        'natural_sample_rate_hertz': 24000
    },
    'fallback_voices': [
        {'name': 'es-ES-Wavenet-B', 'ssml_gender': 'MALE'},
        {'name': 'es-ES-Standard-A', 'ssml_gender': 'FEMALE'}
    ],
    'voice_quality': 'Wavenet',
    'speaking_rate': 1.0,
    'pitch': 0.0
}
```

**Chinese Simplified (`zh_config.py`):**
```python
self.voice_config = {
    'language_code': 'zh-CN',  # Chinese (Simplified)
    'primary_voice': {
        'name': 'zh-CN-Wavenet-A',
        'ssml_gender': 'FEMALE',
        'natural_sample_rate_hertz': 24000
    },
    'fallback_voices': [
        {'name': 'zh-CN-Wavenet-B', 'ssml_gender': 'MALE'},
        {'name': 'zh-CN-Standard-A', 'ssml_gender': 'FEMALE'}
    ],
    'voice_quality': 'Wavenet',
    'speaking_rate': 1.0,
    'pitch': 0.0
}
```

#### 4.6.3 Voice Validation Tests

**File:** `tests/test_{language}_voice_config.py`

```python
import pytest
from languages.{language}.domain.{language}_config import {Language}Config

class Test{Language}VoiceConfig:
    """Test voice configuration for Google Cloud Text-to-Speech"""

    @pytest.fixture
    def config(self):
        return {Language}Config()

    def test_voice_config_structure(self, config):
        """Test voice configuration has required structure"""
        voice_config = config.get_voice_config()

        required_keys = ['language_code', 'primary_voice', 'fallback_voices', 'voice_quality', 'speaking_rate', 'pitch']
        for key in required_keys:
            assert key in voice_config, f"Missing voice config key: {key}"

    def test_primary_voice_structure(self, config):
        """Test primary voice has required attributes"""
        primary_voice = config.get_primary_voice()

        required_keys = ['name', 'ssml_gender', 'natural_sample_rate_hertz']
        for key in required_keys:
            assert key in primary_voice, f"Missing primary voice key: {key}"

        # Validate voice name format
        assert primary_voice['name'].startswith(config.voice_config['language_code']), \
            f"Voice name {primary_voice['name']} doesn't match language code {config.voice_config['language_code']}"

    def test_fallback_voices_available(self, config):
        """Test fallback voices are configured"""
        fallback_voices = config.get_fallback_voices()
        assert len(fallback_voices) >= 1, "At least one fallback voice required"

        for voice in fallback_voices:
            assert 'name' in voice, "Fallback voice missing name"
            assert 'ssml_gender' in voice, "Fallback voice missing gender"

    def test_voice_quality_settings(self, config):
        """Test voice quality parameters are valid"""
        voice_config = config.get_voice_config()

        # Speaking rate validation
        speaking_rate = voice_config['speaking_rate']
        assert 0.25 <= speaking_rate <= 4.0, f"Speaking rate {speaking_rate} out of range (0.25-4.0)"

        # Pitch validation
        pitch = voice_config['pitch']
        assert -20.0 <= pitch <= 20.0, f"Pitch {pitch} out of range (-20.0 to 20.0)"

        # Voice quality validation
        quality = voice_config['voice_quality']
        valid_qualities = ['Standard', 'WaveNet', 'Neural2']
        assert quality in valid_qualities, f"Invalid voice quality: {quality}"

    def test_voice_availability_check(self, config):
        """Test that configured voices exist in Google TTS"""
        # This would require API call to verify voice availability
        # For now, check basic format validation
        voice_config = config.get_voice_config()

        # Basic voice name format check
        import re
        voice_pattern = r'^[a-z]{2,3}(-[A-Z]{2})?-Wavenet-[A-Z]$|^[a-z]{2,3}(-[A-Z]{2})?-Standard-[A-Z]$'
        primary_voice = voice_config['primary_voice']['name']

        assert re.match(voice_pattern, primary_voice), f"Invalid voice name format: {primary_voice}"

        # Check fallback voices too
        for voice in voice_config['fallback_voices']:
            assert re.match(voice_pattern, voice['name']), f"Invalid fallback voice format: {voice['name']}"
```

#### 4.6.4 Voice Integration Testing

**File:** `tests/test_{language}_voice_integration.py`

```python
import pytest
from languages.{language}.{language}_analyzer import {Language}Analyzer
from unittest.mock import patch, MagicMock

class Test{Language}VoiceIntegration:
    """Test voice integration with text-to-speech"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    def test_voice_config_accessible(self, analyzer):
        """Test analyzer can access voice configuration"""
        voice_config = analyzer.config.get_voice_config()
        assert voice_config is not None
        assert 'primary_voice' in voice_config

    @patch('google.cloud.texttospeech.TextToSpeechClient')
    def test_voice_synthesis_call(self, mock_tts_client, analyzer):
        """Test voice synthesis API call structure"""
        # Mock the TTS client
        mock_client = MagicMock()
        mock_tts_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.audio_content = b'fake_audio_data'
        mock_client.synthesize_speech.return_value = mock_response

        # Test voice synthesis (would need actual implementation)
        voice_config = analyzer.config.get_primary_voice()

        # Verify voice config is properly structured for API call
        assert 'name' in voice_config
        assert 'ssml_gender' in voice_config
        assert voice_config['ssml_gender'] in ['MALE', 'FEMALE', 'NEUTRAL']

    def test_voice_fallback_mechanism(self, analyzer):
        """Test fallback voice selection works"""
        primary_voice = analyzer.config.get_primary_voice()
        fallback_voices = analyzer.config.get_fallback_voices()

        # Ensure primary and fallback voices are different
        assert primary_voice['name'] != fallback_voices[0]['name'], \
            "Primary and fallback voices should be different"

        # Ensure all voices have required attributes
        all_voices = [primary_voice] + fallback_voices
        for voice in all_voices:
            assert 'name' in voice
            assert 'ssml_gender' in voice
```

**Operational Tip:** If users only see default/fallback voices in the UI, instruct them to verify or rotate the Google TTS API key and ensure the Text-to-Speech API is enabled and billing is active.

### Phase 4.7: Custom Sentence Generation Verification (30 minutes)

**CRITICAL:** All language analyzers must implement custom sentence generation prompts instead of generic fallbacks.

#### 4.7.1 Method Implementation Check

**File:** `{language}_analyzer.py`

Verify the `get_sentence_generation_prompt` method exists and is properly implemented:

```python
def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                 enriched_meaning: str = "", min_length: int = 3,
                                 max_length: int = 15, difficulty: str = "intermediate",
                                 topics: Optional[List[str]] = None) -> Optional[str]:
    """Get {Language}-specific sentence generation prompt"""
    # Implementation must include:
    # 1. Language-specific prompt template
    # 2. Appropriate transcription method (IPA, Pinyin, Romanization)
    # 3. Language-specific grammatical constraints
    # 4. Cultural context variety requirements
    # 5. Structured output format
    return prompt
```

#### 4.7.2 Implementation Validation Tests

**File:** `tests/test_{language}_sentence_generation.py`

```python
import pytest
from languages.{language}.{language}_analyzer import {Language}Analyzer

class Test{Language}SentenceGeneration:
    """Test custom sentence generation implementation"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    def test_method_exists(self, analyzer):
        """Test get_sentence_generation_prompt method exists"""
        assert hasattr(analyzer, 'get_sentence_generation_prompt'), \
            "get_sentence_generation_prompt method missing"

    def test_method_callable(self, analyzer):
        """Test method is callable and returns string"""
        prompt = analyzer.get_sentence_generation_prompt('test', 'test', 4)
        assert isinstance(prompt, str), "Method must return string"
        assert len(prompt) > 1000, "Prompt should be substantial (>1000 chars)"

    def test_language_specific_content(self, analyzer):
        """Test prompt contains language-specific elements"""
        prompt = analyzer.get_sentence_generation_prompt('test', 'test', 4)

        # Check for language name in prompt
        language_name = analyzer.config.language_name
        assert language_name.lower() in prompt.lower(), \
            f"Prompt should mention language name: {language_name}"

        # Check for structured output format
        assert 'MEANING:' in prompt, "Prompt should have MEANING section"
        assert 'SENTENCES:' in prompt, "Prompt should have SENTENCES section"
        assert 'TRANSLATIONS:' in prompt, "Prompt should have TRANSLATIONS section"

    def test_transcription_method_appropriate(self, analyzer):
        """Test appropriate transcription method for language"""
        prompt = analyzer.get_sentence_generation_prompt('test', 'test', 4)

        language_code = analyzer.config.language_code

        # Language-specific transcription checks
        if language_code in ['ar', 'de', 'es']:
            assert 'IPA' in prompt, f"{language_code} should use IPA transcription"
        elif language_code in ['zh', 'zh-tw']:
            assert 'PINYIN' in prompt, f"{language_code} should use Pinyin transcription"
        elif language_code == 'hi':
            assert 'ROMANIZATION' in prompt, f"{language_code} should use Romanization"

    def test_grammatical_constraints_included(self, analyzer):
        """Test language-specific grammatical constraints are mentioned"""
        prompt = analyzer.get_sentence_generation_prompt('test', 'test', 4)

        # Check for language-specific grammatical features
        language_specific_terms = {
            'ar': ['root', 'case', 'verb forms'],
            'zh': ['aspect', 'particles', 'measure words'],
            'zh-tw': ['aspect', 'particles', 'measure words'],
            'de': ['case', 'separable', 'gender'],
            'hi': ['postposition', 'gender', 'Devanagari'],
            'es': ['gender', 'conjugation', 'regional']
        }

        language_code = analyzer.config.language_code
        if language_code in language_specific_terms:
            terms = language_specific_terms[language_code]
            found_terms = [term for term in terms if term.lower() in prompt.lower()]
            assert len(found_terms) > 0, \
                f"Prompt should include language-specific terms: {terms}"

    def test_output_format_validation(self, analyzer):
        """Test output format is properly structured"""
        prompt = analyzer.get_sentence_generation_prompt('test', 'test', 4)

        # Check for numbered output format
        assert '1. [sentence 1' in prompt, "Should have numbered sentence format"
        assert '1. [natural English translation' in prompt, "Should have numbered translation format"

        # Check for keyword format
        assert 'keyword1, keyword2, keyword3' in prompt, "Should have keyword format"

    def test_parameter_handling(self, analyzer):
        """Test method handles parameters correctly"""
        # Test with topics
        topics = ['food', 'travel']
        prompt_with_topics = analyzer.get_sentence_generation_prompt('test', 'test', 4, topics=topics)

        for topic in topics:
            assert topic in prompt_with_topics, f"Topic {topic} should be in prompt"

        # Test with enriched meaning
        enriched_meaning = '{"definition": "test meaning"}'
        prompt_with_meaning = analyzer.get_sentence_generation_prompt('test', 'test', 4, enriched_meaning=enriched_meaning)

        assert 'test meaning' in prompt_with_meaning, "Enriched meaning should be processed"

    def test_no_generic_fallback(self, analyzer):
        """Test that custom prompt is used, not generic fallback"""
        prompt = analyzer.get_sentence_generation_prompt('test', 'test', 4)

        # Should not contain generic language references
        assert 'language' not in prompt.lower() or analyzer.config.language_name.lower() in prompt.lower(), \
            "Prompt should be language-specific, not generic"

        # Should contain specific language name
        assert analyzer.config.language_name.lower() in prompt.lower(), \
            "Prompt should contain specific language name"
```

#### 4.7.3 Cross-Language Comparison Tests

**File:** `tests/test_sentence_generation_comparison.py`

```python
import pytest
from languages.arabic.ar_analyzer import ArAnalyzer
from languages.chinese_traditional.zh_tw_analyzer import ZhTwAnalyzer
from languages.german.de_analyzer import DeAnalyzer
from languages.hindi.hi_analyzer import HiAnalyzer
from languages.spanish.es_analyzer import EsAnalyzer
from languages.chinese_simplified.zh_analyzer import ZhAnalyzer

class TestSentenceGenerationComparison:
    """Compare sentence generation across all implemented languages"""

    @pytest.fixture
    def analyzers(self):
        return {
            'ar': ArAnalyzer(),
            'zh-tw': ZhTwAnalyzer(),
            'de': DeAnalyzer(),
            'hi': HiAnalyzer(),
            'es': EsAnalyzer(),
            'zh': ZhAnalyzer()
        }

    def test_all_languages_have_custom_prompts(self, analyzers):
        """Test all languages implement custom sentence generation"""
        for lang_code, analyzer in analyzers.items():
            assert hasattr(analyzer, 'get_sentence_generation_prompt'), \
                f"{lang_code} missing get_sentence_generation_prompt method"

            prompt = analyzer.get_sentence_generation_prompt('test', lang_code, 4)
            assert isinstance(prompt, str), f"{lang_code} prompt should be string"
            assert len(prompt) > 1000, f"{lang_code} prompt should be substantial"

    def test_transcription_methods_vary_by_language(self, analyzers):
        """Test different transcription methods used per language"""
        transcription_methods = {
            'ar': 'IPA',
            'zh-tw': 'PINYIN',
            'de': 'IPA',
            'hi': 'ROMANIZATION',
            'es': 'IPA',
            'zh': 'PINYIN'
        }

        for lang_code, expected_transcription in transcription_methods.items():
            analyzer = analyzers[lang_code]
            prompt = analyzer.get_sentence_generation_prompt('test', lang_code, 4)
            assert expected_transcription in prompt, \
                f"{lang_code} should use {expected_transcription} transcription"

    def test_language_names_in_prompts(self, analyzers):
        """Test each prompt contains correct language name"""
        expected_names = {
            'ar': 'Arabic',
            'zh-tw': 'Chinese Traditional',
            'de': 'German',
            'hi': 'Hindi',
            'es': 'Spanish',
            'zh': 'Chinese Simplified'
        }

        for lang_code, expected_name in expected_names.items():
            analyzer = analyzers[lang_code]
            prompt = analyzer.get_sentence_generation_prompt('test', lang_code, 4)
            assert expected_name.lower() in prompt.lower(), \
                f"{lang_code} prompt should contain '{expected_name}'"

    def test_prompts_are_unique_per_language(self, analyzers):
        """Test each language has unique prompt characteristics"""
        prompts = {}
        for lang_code, analyzer in analyzers.items():
            prompt = analyzer.get_sentence_generation_prompt('test', lang_code, 4)
            prompts[lang_code] = prompt

        # Check that prompts are different (basic uniqueness test)
        prompt_lengths = {lang: len(prompt) for lang, prompt in prompts.items()}
        unique_lengths = len(set(prompt_lengths.values()))
        assert unique_lengths >= 4, "Prompts should have varied lengths indicating customization"

    def test_structured_output_format_consistent(self, analyzers):
        """Test all prompts use consistent output format"""
        required_sections = ['MEANING:', 'SENTENCES:', 'TRANSLATIONS:', 'KEYWORDS:']

        for lang_code, analyzer in analyzers.items():
            prompt = analyzer.get_sentence_generation_prompt('test', lang_code, 4)

            for section in required_sections:
                assert section in prompt, \
                    f"{lang_code} prompt missing required section: {section}"

### Phase 4.8: Language Registry Integration (30 minutes - 1 hour)

**CRITICAL:** The analyzer is not discoverable by the application until it's registered in the language registry system. This phase makes your implementation available to the application.

**Why This Matters:** Without proper registration, the application will fall back to generic analysis even though your language-specific analyzer exists. The Turkish implementation discovered this issue in production - the analyzer was built correctly but not registered, causing grammar analysis to fail with "No analyzer available for language."

#### 4.8.1 Language Registry Integration

**File:** `streamlit_app/language_registry.py`

Add your language to the central language registry. This is the source of truth for language metadata and ISO code mapping:

```python
from dataclasses import dataclass

@dataclass
class LanguageConfig:
    """Configuration for a language"""
    iso_code: str                    # ISO 639-3 code (e.g., 'tr', 'ar', 'zh')
    epitran_code: str                # Epitran transliteration code
    phonemizer_code: str             # Festival/phonemizer language code
    family: str                       # Language family
    script_type: str                 # Writing system
    complexity: str                  # 'easy', 'intermediate', 'hard'

def get_language_registry():
    """Initialize and return language registry"""
    registry = {}

    # ... existing languages ...

    # ADD YOUR LANGUAGE HERE:
    registry['Turkish'] = LanguageConfig(
        iso_code='tr',                          # Critical: Turkish ISO code
        epitran_code='tur-Latn',                # Epitran transliteration code
        phonemizer_code='tr',                   # Festival/phonemizer code
        family='Altaic',                        # Language family
        script_type='Latin',                    # Writing system
        complexity='intermediate'               # Learning complexity
    )

    return registry
```

**Critical Details:**
- **`iso_code`**: MUST match the analyzer filename and folder name (e.g., 'tr' for `tr_analyzer.py`)
- **`epitran_code`**: Required for IPA transliteration (https://epitran.readthedocs.io/)
- **`phonemizer_code`**: Required for pronunciation (https://github.com/bootphon/phonemizer)
- **`script_type`**: Used for sentence processing ('Latin', 'Arabic', 'Devanagari', 'Han', etc.)

#### 4.8.2 Analyzer Registry Folder Mapping

**File:** `streamlit_app/language_analyzers/analyzer_registry.py`

Add your language code to the folder-to-code mapping. This enables auto-discovery of your analyzer:

```python
def get_analyzer(language_code: str) -> Optional[BaseGrammarAnalyzer]:
    """Get analyzer for specified language code"""
    
    # Folder name to language code mapping
    folder_to_code = {
        'arabic': 'ar',
        'chinese_traditional': 'zh-tw',
        'german': 'de',
        'hindi': 'hi',
        'spanish': 'es',
        'zh': 'zh',
        'turkish': 'tr',              # ADD YOUR LANGUAGE HERE
    }
    
    # Rest of implementation...
```

**Critical Details:**
- **folder name**: Must match the folder in `languages/` directory (e.g., `languages/turkish/`)
- **language_code**: Must match the ISO code in language_registry.py (e.g., 'tr')

#### 4.8.3 Required Validator Interface Methods

**File:** `languages/{language}/{language_code}_validator.py`

The validator MUST implement these two methods for the analyzer to function correctly:

```python
class {Language}Validator(BaseDomainValidator):
    """Validator for {Language} grammar analysis"""

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """
        Validate and score grammar analysis result
        
        REQUIRED: This method is called by the analyzer to validate results
        
        Args:
            result: Grammar analysis result from response parser
            sentence: Original sentence being analyzed
            
        Returns:
            Validated result dict with:
            - confidence_score (0.0-1.0): Accuracy confidence
            - is_fallback (bool): Whether using fallback analysis
            - word_explanations (list): List of word explanation objects
            
        Example:
            {
                'confidence_score': 0.85,
                'is_fallback': False,
                'word_explanations': [
                    {'word': 'the', 'explanation': '...', 'role': 'article'},
                    ...
                ]
            }
        """
        # 1. Check if result is from fallback analysis
        is_fallback = result.get('is_fallback', False)
        
        # 2. Validate word_explanations format
        word_explanations = result.get('word_explanations', [])
        if not isinstance(word_explanations, list):
            word_explanations = []
        
        # 3. Calculate confidence score
        if is_fallback:
            confidence_score = 0.1  # Low confidence for fallback
        elif not word_explanations:
            confidence_score = 0.2  # Low confidence if no explanations
        else:
            # Score based on explanation quality
            valid_explanations = [
                w for w in word_explanations 
                if isinstance(w, dict) and 'explanation' in w
            ]
            confidence_score = min(0.95, len(valid_explanations) / len(word_explanations))
        
        # 4. Return validated result
        result['confidence_score'] = confidence_score
        result['is_fallback'] = is_fallback
        result['word_explanations'] = word_explanations
        
        return result

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate explanation quality metrics
        
        REQUIRED: This method ensures explanation quality meets standards
        
        Args:
            result: Grammar analysis result after validate_result
            
        Returns:
            Enhanced result dict with quality metrics:
            - explanation_quality (str): 'poor', 'fair', 'good', 'excellent'
            - quality_score (0.0-1.0): Quality metric
            - improvement_areas (list): List of areas to improve
            
        Example:
            {
                ...
                'explanation_quality': 'good',
                'quality_score': 0.82,
                'improvement_areas': []
            }
        """
        word_explanations = result.get('word_explanations', [])
        
        if not word_explanations:
            result['explanation_quality'] = 'poor'
            result['quality_score'] = 0.0
            result['improvement_areas'] = ['No explanations found']
            return result
        
        # Calculate quality metrics
        explanations_with_detail = sum(
            1 for w in word_explanations 
            if isinstance(w, dict) and len(w.get('explanation', '')) > 50
        )
        
        explanations_with_role = sum(
            1 for w in word_explanations 
            if isinstance(w, dict) and 'role' in w
        )
        
        quality_ratio = (explanations_with_detail + explanations_with_role) / (2 * len(word_explanations))
        
        # Determine quality level
        if quality_ratio >= 0.9:
            quality_level = 'excellent'
        elif quality_ratio >= 0.75:
            quality_level = 'good'
        elif quality_ratio >= 0.5:
            quality_level = 'fair'
        else:
            quality_level = 'poor'
        
        result['explanation_quality'] = quality_level
        result['quality_score'] = quality_ratio
        result['improvement_areas'] = []
        
        if explanations_with_detail < len(word_explanations):
            result['improvement_areas'].append('Add more detailed explanations')
        
        if explanations_with_role < len(word_explanations):
            result['improvement_areas'].append('Add grammatical roles')
        
        return result
```

#### 4.8.4 Verification Commands

Run these commands to verify language registry integration before testing:

```bash
# 1. Verify language appears in registry
python -c "from streamlit_app.language_registry import get_language_registry; r = get_language_registry(); print('Turkish ISO code:', r.get_iso_code('Turkish'))"

# Expected output: Turkish ISO code: tr

# 2. Verify analyzer is discoverable
python -c "from streamlit_app.language_analyzers.analyzer_registry import get_analyzer; analyzer = get_analyzer('tr'); print('Turkish analyzer:', analyzer)"

# Expected output: Turkish analyzer: <languages.turkish.tr_analyzer.TrAnalyzer object at ...>

# 3. Verify analyzer methods exist
python -c "
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer
analyzer = get_analyzer('tr')
print('Has analyze_grammar:', hasattr(analyzer, 'analyze_grammar'))
print('Has get_sentence_generation_prompt:', hasattr(analyzer, 'get_sentence_generation_prompt'))
print('Has config:', hasattr(analyzer, 'config'))
"

# Expected output:
# Has analyze_grammar: True
# Has get_sentence_generation_prompt: True
# Has config: True

# 4. Verify analyzer can be instantiated and used
python -c "
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer
analyzer = get_analyzer('tr')
result = analyzer.analyze_grammar('Bunu yapmalÄ±sÄ±n.', 'Bunu yapmalÄ±sÄ±n.')
print('Analysis type:', type(result).__name__)
print('Has word_explanations:', hasattr(result, 'word_explanations'))
print('Has html_output:', hasattr(result, 'html_output'))
"

# Expected output:
# Analysis type: GrammarAnalysis
# Has word_explanations: True
# Has html_output: True
```

#### 4.8.5 Language Registry Integration Checklist

**Use this checklist to ensure your language is properly registered:**

```
Language Registration Checklist for {Language}:

â˜ LANGUAGE REGISTRY (streamlit_app/language_registry.py)
  â˜ Added language to get_language_registry() function
  â˜ Set correct iso_code (matches analyzer filename)
  â˜ Set correct epitran_code (for IPA transliteration)
  â˜ Set correct phonemizer_code (for pronunciation)
  â˜ Set language family
  â˜ Set script_type correctly
  â˜ Set complexity level
  â˜ Verified: registry.get_iso_code('Language') returns correct code

â˜ ANALYZER REGISTRY (streamlit_app/language_analyzers/analyzer_registry.py)
  â˜ Added folder name to folder_to_code mapping
  â˜ Folder name matches languages/ subdirectory
  â˜ Language code matches iso_code in language_registry
  â˜ Verified: get_analyzer('{language_code}') returns analyzer instance

â˜ VALIDATOR METHODS (languages/{language}/{language_code}_validator.py)
  â˜ Implemented validate_result() method
  â˜ Implemented validate_explanation_quality() method
  â˜ Both methods handle edge cases (empty input, fallback analysis)
  â˜ validate_result() returns dict with confidence_score, is_fallback, word_explanations
  â˜ validate_explanation_quality() returns dict with quality metrics

â˜ ANALYZER CLASS (languages/{language}/{language_code}_analyzer.py)
  â˜ Inherits from BaseGrammarAnalyzer
  â˜ Calls self.validator.validate_result() in analyze_grammar()
  â˜ Calls self.validator.validate_explanation_quality() in analyze_grammar()
  â˜ Returns GrammarAnalysis object with valid structure

â˜ FILESYSTEM STRUCTURE
  â˜ Folder: languages/{language}/
  â˜ File: languages/{language}/{language_code}_config.py
  â˜ File: languages/{language}/{language_code}_prompt_builder.py
  â˜ File: languages/{language}/{language_code}_response_parser.py
  â˜ File: languages/{language}/{language_code}_validator.py
  â˜ File: languages/{language}/{language_code}_analyzer.py
  â˜ File: languages/{language}/prompt_sentences_{language_code}.txt
  â˜ File: languages/{language}/tests/

â˜ VERIFICATION
  â˜ Run: registry.get_iso_code('Language') returns correct code
  â˜ Run: get_analyzer('{language_code}') returns TrAnalyzer instance
  â˜ Run: analyzer.analyze_grammar() returns GrammarAnalysis with word_explanations
  â˜ Run: Full test suite passes (Phase 5)
  â˜ Run: Compare with gold standard (Phase 5.3)
  â˜ Test in Streamlit app: Grammar analysis uses language-specific analyzer
```

#### 4.8.6 Troubleshooting - Analyzer Not Found

If you see "No analyzer available for language" error:

**Step 1: Verify Language Registry**
```bash
python << 'EOF'
from streamlit_app.language_registry import get_language_registry
registry = get_language_registry()

language_name = 'Turkish'  # Change to your language
iso_code = registry.get_iso_code(language_name)
print(f"Step 1 - Language Registry Check:")
print(f"  Language '{language_name}' registered: {iso_code is not None}")
print(f"  ISO code: {iso_code}")

if iso_code is None:
    print("  FIX: Add language to streamlit_app/language_registry.py")
EOF
```

**Step 2: Verify Analyzer Registry**
```bash
python << 'EOF'
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

language_code = 'tr'  # Change to your language code
analyzer = get_analyzer(language_code)
print(f"Step 2 - Analyzer Registry Check:")
print(f"  Analyzer found: {analyzer is not None}")
print(f"  Analyzer type: {type(analyzer).__name__}")

if analyzer is None:
    print("  FIX: Check analyzer_registry.py folder_to_code mapping")
    print("  FIX: Verify languages/{language}/_{language_code}_analyzer.py exists")
EOF
```

**Step 3: Verify Analyzer Class**
```bash
python << 'EOF'
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

analyzer = get_analyzer('tr')  # Change to your language code
if analyzer:
    print(f"Step 3 - Analyzer Class Check:")
    print(f"  Config exists: {hasattr(analyzer, 'config')}")
    print(f"  analyze_grammar exists: {hasattr(analyzer, 'analyze_grammar')}")
    print(f"  Validator exists: {hasattr(analyzer, 'validator')}")
    
    if hasattr(analyzer, 'validator'):
        validator = analyzer.validator
        print(f"  Validator.validate_result exists: {hasattr(validator, 'validate_result')}")
        print(f"  Validator.validate_explanation_quality exists: {hasattr(validator, 'validate_explanation_quality')}")
else:
    print("Analyzer not found - check previous steps")
EOF
```

**Step 4: Verify Grammar Analysis**
```bash
python << 'EOF'
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer

analyzer = get_analyzer('tr')  # Change to your language code
if analyzer:
    try:
        result = analyzer.analyze_grammar('Test sentence', 'Test sentence')
        print(f"Step 4 - Grammar Analysis Check:")
        print(f"  Analysis result type: {type(result).__name__}")
        print(f"  Has word_explanations: {hasattr(result, 'word_explanations')}")
        print(f"  Has html_output: {hasattr(result, 'html_output')}")
        print(f"  Classification: {'Success!' if hasattr(result, 'html_output') else 'Failed'}")
    except Exception as e:
        print(f"  Error during analysis: {e}")
        print("  FIX: Check analyzer.analyze_grammar() implementation")
EOF
```

### Phase 5: Comprehensive Testing Implementation (1-2 weeks)

**CRITICAL:** This phase prevents iterative failures by using automated validation and testing frameworks.

#### 5.1 Pre-Implementation Validation
```bash
# Validate implementation structure before detailed testing
python language_grammar_generator/validate_implementation.py --language {language_code}

# This catches missing files, methods, and structural issues early
```

#### 5.2 Automated Test Suite Execution
```bash
# Run all tests with coverage reporting
python language_grammar_generator/run_all_tests.py --language {language_code} --coverage

# Run tests in parallel for speed
python language_grammar_generator/run_all_tests.py --language {language_code} --parallel

# Run specific test categories
python -m pytest languages/{language_code}/tests/test_{language_code}_config.py -v
python -m pytest languages/{language_code}/tests/test_integration.py -v
```

#### 5.3 Gold Standard Comparison
```bash
# Compare with Chinese Simplified and Hindi analyzers
python language_grammar_generator/compare_with_gold_standard.py --language {language_code}

# Detailed comparison with results export
python language_grammar_generator/compare_with_gold_standard.py --language {language_code} --detailed --export-results
```

#### 5.4 Test File Structure (Auto-Generated)
The testing framework automatically creates comprehensive test files:

```
languages/{language}/tests/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ conftest.py                    # Pytest configuration
â”œâ”€â”€ test_{language}_analyzer.py    # Main facade tests
â”œâ”€â”€ test_{language}_config.py      # Configuration tests
â”œâ”€â”€ test_{language}_prompt_builder.py
â”œâ”€â”€ test_{language}_response_parser.py
â”œâ”€â”€ test_{language}_validator.py
â”œâ”€â”€ test_integration.py            # Component integration
â”œâ”€â”€ test_system.py                 # End-to-end tests (auto-generated)
â”œâ”€â”€ test_performance.py            # Performance benchmarks (auto-generated)
â”œâ”€â”€ test_gold_standard_comparison.py # Gold standard validation (auto-generated)
â”œâ”€â”€ test_regression.py             # Prevent bug reintroduction (auto-generated)
â”œâ”€â”€ test_linguistic_accuracy.py    # Linguistic validation (auto-generated)
â””â”€â”€ fixtures/
    â”œâ”€â”€ sample_sentences.json      # Test sentences
    â”œâ”€â”€ expected_outputs.json      # Expected results
    â””â”€â”€ mock_responses.json        # Mock AI responses
```

#### 5.5 Standardized Testing Procedures for All Languages

After implementation, all language analyzers must pass these standardized tests:

**Component Isolation Tests:**
```python
# Test config loading and grammatical roles
def test_config_loading():
    config = {Language}Config()
    assert hasattr(config, 'grammatical_roles')
    assert len(config.grammatical_roles) > 0

# Test prompt generation with all complexity levels
@pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
def test_prompt_generation(analyzer, complexity):
    prompt = analyzer.get_grammar_prompt(complexity, 'Test sentence', 'test')
    assert complexity in prompt
    assert 'Test sentence' in prompt
```

**Integration Tests:**
```python
# Test complete analyzer workflow
def test_analyzer_creation():
    analyzer = {Language}Analyzer()
    assert analyzer.config is not None
    assert analyzer.prompt_builder is not None
    assert analyzer.response_parser is not None
    assert analyzer.validator is not None

# Test component interaction
def test_component_orchestration(analyzer):
    result = analyzer.analyze_grammar("Test", "test", "beginner", "mock_key")
    assert result is not None
    assert hasattr(result, 'word_explanations')
```

**System Tests:**
```python
# Test end-to-end with real API calls
def test_full_analysis_workflow(analyzer):
    result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", "real_api_key")
    assert result.sentence == "Test sentence"
    assert len(result.word_explanations) > 0
    assert result.confidence_score > 0
    assert result.html_output is not None
```

**Performance Tests:**
```python
# Test response time requirements
def test_analysis_speed(analyzer):
    import time
    start = time.time()
    result = analyzer.analyze_grammar("Test", "test", "intermediate", "key")
    duration = time.time() - start
    assert duration < 30  # 30 second limit

# Test memory stability
def test_memory_usage(analyzer):
    import psutil
    import os
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Run multiple analyses
    for i in range(10):
        analyzer.analyze_grammar(f"Test sentence {i}", "test", "beginner", "key")

    final_memory = process.memory_info().rss
    growth = final_memory - initial_memory
    assert growth < 50 * 1024 * 1024  # Less than 50MB growth
```

**Gold Standard Comparison Tests:**
```python
# Compare with Chinese Simplified patterns
def test_gold_standard_compliance(analyzer):
    # Load gold standard results
    gold_standard = load_gold_standard_results('zh')  # Chinese Simplified

    # Run same analysis
    result = analyzer.analyze_grammar(gold_standard['sentence'], gold_standard['target'], "beginner", "key")

    # Compare structure and quality
    assert len(result.word_explanations) >= len(gold_standard['expected_roles'])
    assert result.confidence_score >= gold_standard['min_confidence']
```

#### 5.6 Testing Best Practices

**Unit Tests - Component Isolation:**
```python
# Test individual components in isolation
def test_config_loading():
    config = {Language}Config()
    assert hasattr(config, 'grammatical_roles')
    assert len(config.grammatical_roles) > 0

def test_prompt_generation():
    builder = {Language}PromptBuilder(config)
    prompt = builder.build_single_prompt("Test", "word", "intermediate")
    assert "Test" in prompt
    assert "word" in prompt
```

**Integration Tests - Component Interaction:**
```python
# Test components working together
def test_analyzer_creation():
    analyzer = {Language}Analyzer()
    assert analyzer.config is not None
    assert analyzer.prompt_builder is not None
    assert analyzer.response_parser is not None
    assert analyzer.validator is not None
```

**System Tests - End-to-End Workflow:**
```python
# Test complete analysis workflow
def test_full_analysis_workflow(analyzer):
    result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", "mock_key")
    assert result is not None
    assert hasattr(result, 'word_explanations')
    assert hasattr(result, 'html_output')
    assert hasattr(result, 'confidence')
```

**Performance Tests - Speed and Resources:**
```python
# Test performance requirements
def test_analysis_speed(analyzer):
    import time
    start = time.time()
    result = analyzer.analyze_grammar("Test", "test", "intermediate", "key")
    duration = time.time() - start
    assert duration < 30  # 30 second limit
```

#### 5.6 Troubleshooting Test Failures

**âŒ Import Errors:**
```bash
# Check Python path and imports
python -c "from languages.{language_code}.{language_code}_analyzer import {LanguageCode}Analyzer; print('Import successful')"
```

**âŒ Method Missing Errors:**
```bash
# List all available methods
python -c "from languages.{language_code}.{language_code}_analyzer import {LanguageCode}Analyzer; print([m for m in dir({LanguageCode}Analyzer) if not m.startswith('_')])"
```

**âŒ Configuration Loading Errors:**
```bash
# Test config file access
python -c "from languages.{language_code}.domain.{language_code}_config import {LanguageCode}Config; c = {LanguageCode}Config(); print('Config loaded:', c.language_code)"
```

**âŒ Component Integration Errors:**
```bash
# Test component instantiation
python -c "
try:
    from languages.{language_code}.{language_code}_analyzer import {LanguageCode}Analyzer
    a = {LanguageCode}Analyzer()
    print('âœ“ Analyzer created successfully')
except Exception as e:
    print(f'âœ— Error: {e}')
"
```

**âŒ Gold Standard Comparison Failures:**
```bash
# Get detailed comparison report
python language_grammar_generator/compare_with_gold_standard.py --language {language_code} --detailed --export-results

# Check the exported JSON for specific issues
```

#### 5.7 Final Validation Checklist
- [ ] Pre-implementation validation passes
- [ ] All unit tests pass (100% component coverage)
- [ ] All integration tests pass (component interaction)
- [ ] All system tests pass (end-to-end workflow)
- [ ] Performance tests pass (speed requirements)
- [ ] Gold standard comparison passes (quality standards)
- [ ] Linguistic accuracy tests pass (grammatical role validation)
- [ ] Regression tests pass (no bug reintroduction)
- [ ] Memory usage tests pass (no memory leaks)
- [ ] Concurrent request tests pass (thread safety)
- [ ] All test categories run successfully:
  - `test_{language}_config.py` - Configuration validation
  - `test_{language}_prompt_builder.py` - Prompt generation
  - `test_{language}_response_parser.py` - Response parsing
  - `test_{language}_validator.py` - Result validation
  - `test_{language}_integration.py` - Component orchestration
  - `test_{language}_system.py` - End-to-end workflows
  - `test_{language}_performance.py` - Speed and resources
  - `test_{language}_linguistic_accuracy.py` - Linguistic validation
  - `test_{language}_regression.py` - Bug prevention

**ðŸš¨ DEPLOYMENT BLOCKED UNTIL ALL CHECKS PASS!**

### Phase 6: Integration and Deployment (2-4 hours)

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

## âœ… Success Criteria

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

## ðŸš¨ Common Implementation Pitfalls

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

## ðŸ“Š Implementation Timeline

- **Phase 1:** Research Validation - 1-2 days
- **Phase 2:** Directory Setup - 2-4 hours
- **Phase 3:** Domain Components - 1-2 weeks
- **Phase 4:** Main Analyzer & Integration - 5-7 hours
  - 4.1-4.7: Analyzer Implementation (4-6 hours)
  - **4.8: Language Registry Integration (30 mins - 1 hour)** âš ï¸ **CRITICAL FOR DISCOVERY**
- **Phase 5:** Testing - 1-2 weeks
- **Phase 6:** Integration - 2-4 hours

**Total Time:** 3-5 weeks for complete implementation

## ðŸŽ¯ Next Steps

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

## ðŸ§ª **Comprehensive Quality Testing Framework**

### Phase 5.8: Quality Assurance Testing Suite

After implementation, all language analyzers must pass these **comprehensive quality tests** covering external configurations, AI generation quality, and linguistic accuracy.

#### 5.8.1 YAML/JSON Configuration File Validation Tests

**Critical:** External configuration files must be validated for structure, content, and consistency.

**File:** `tests/test_{language}_config_files.py`

```python
import pytest
import yaml
import json
from pathlib import Path
from languages.{language}.domain.{language}_config import {Language}Config

class Test{Language}ConfigFiles:
    """Test YAML/JSON configuration file validation"""

    @pytest.fixture
    def config_dir(self):
        """Get configuration directory path"""
        return Path(__file__).parent.parent / "domain" / "config"

    def test_yaml_files_exist(self, config_dir):
        """Test all required YAML files exist"""
        required_files = [
            "{language}_grammatical_roles.yaml",
            "{language}_analysis_patterns.yaml",
            "{language}_color_schemes.yaml",
            "{language}_prompt_templates.yaml"
        ]

        for filename in required_files:
            filepath = config_dir / filename
            assert filepath.exists(), f"Missing required file: {filename}"
            assert filepath.stat().st_size > 0, f"Empty file: {filename}"

    def test_json_files_exist(self, config_dir):
        """Test all required JSON files exist"""
        required_files = [
            "{language}_word_meanings.json",
            "{language}_exception_words.json",
            "{language}_test_sentences.json"
        ]

        for filename in required_files:
            filepath = config_dir / filename
            assert filepath.exists(), f"Missing required file: {filename}"
            assert filepath.stat().st_size > 0, f"Empty file: {filename}"

    def test_yaml_file_structure(self, config_dir):
        """Test YAML files have valid structure"""
        yaml_files = list(config_dir.glob("*.yaml"))

        for yaml_file in yaml_files:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                try:
                    data = yaml.safe_load(f)
                    assert isinstance(data, (dict, list)), f"Invalid YAML structure in {yaml_file.name}"
                    assert len(data) > 0, f"Empty YAML file: {yaml_file.name}"
                except yaml.YAMLError as e:
                    pytest.fail(f"YAML parsing error in {yaml_file.name}: {e}")

    def test_json_file_structure(self, config_dir):
        """Test JSON files have valid structure"""
        json_files = list(config_dir.glob("*.json"))

        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    assert isinstance(data, (dict, list)), f"Invalid JSON structure in {json_file.name}"
                    assert len(data) > 0, f"Empty JSON file: {json_file.name}"
                except json.JSONDecodeError as e:
                    pytest.fail(f"JSON parsing error in {json_file.name}: {e}")

    def test_grammatical_roles_completeness(self, config_dir):
        """Test grammatical roles YAML has all required categories"""
        roles_file = config_dir / "{language}_grammatical_roles.yaml"

        with open(roles_file, 'r', encoding='utf-8') as f:
            roles = yaml.safe_load(f)

        # Check for required complexity levels
        assert 'beginner' in roles, "Missing beginner roles"
        assert 'intermediate' in roles, "Missing intermediate roles"
        assert 'advanced' in roles, "Missing advanced roles"

        # Check each level has content
        for level in ['beginner', 'intermediate', 'advanced']:
            assert len(roles[level]) > 0, f"Empty {level} roles"

        # Check for essential categories
        beginner_roles = roles['beginner']
        essential_roles = ['noun', 'verb', 'adjective']
        for role in essential_roles:
            assert role in beginner_roles, f"Missing essential role: {role}"

    def test_word_meanings_completeness(self, config_dir):
        """Test word meanings JSON has comprehensive coverage"""
        meanings_file = config_dir / "{language}_word_meanings.json"

        with open(meanings_file, 'r', encoding='utf-8') as f:
            meanings = json.load(f)

        # Should have meaningful content
        assert len(meanings) > 50, "Insufficient word meanings coverage"

        # Check structure of entries
        for word, data in list(meanings.items())[:10]:  # Check first 10
            assert 'meaning' in data, f"Missing meaning for word: {word}"
            assert 'category' in data, f"Missing category for word: {word}"
            assert len(data['meaning']) > 5, f"Meaning too short for word: {word}"

    def test_color_scheme_consistency(self, config_dir):
        """Test color schemes are valid and consistent"""
        colors_file = config_dir / "{language}_color_schemes.yaml"

        with open(colors_file, 'r', encoding='utf-8') as f:
            schemes = yaml.safe_load(f)

        # Check all complexity levels
        for level in ['beginner', 'intermediate', 'advanced']:
            assert level in schemes, f"Missing color scheme for {level}"

            level_colors = schemes[level]
            assert len(level_colors) > 0, f"Empty color scheme for {level}"

            # Validate hex color format
            for role, color in level_colors.items():
                assert color.startswith('#'), f"Invalid color format for {role}: {color}"
                assert len(color) == 7, f"Invalid color length for {role}: {color}"

                # Check if it's a valid hex color
                try:
                    int(color[1:], 16)
                except ValueError:
                    pytest.fail(f"Invalid hex color for {role}: {color}")

    def test_config_file_encoding(self, config_dir):
        """Test all config files use UTF-8 encoding"""
        all_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.json"))

        for config_file in all_files:
            # Try to read with UTF-8
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert len(content) > 0, f"Empty file: {config_file.name}"
            except UnicodeDecodeError:
                pytest.fail(f"File not UTF-8 encoded: {config_file.name}")

    def test_config_consistency_with_code(self):
        """Test configuration files match code expectations"""
        config = {Language}Config()

        # Test that config can load all its expected files
        try:
            # This should not raise exceptions if files are properly structured
            roles = config.grammatical_roles
            assert len(roles) > 0, "Config couldn't load grammatical roles"
        except Exception as e:
            pytest.fail(f"Config loading failed: {e}")
```

#### 5.8.2 AI Sentence Generation Quality Tests

**Critical:** AI-generated sentences must meet character limits and quality standards. **FINAL TEST REQUIREMENT:** Take a random word from the frequency list, generate 3 sentences 8-10 words long with a random topic from the list of topics.

**File:** `tests/test_{language}_sentence_generation.py`

```python
import pytest
import random
from languages.{language}.{language}_analyzer import {Language}Analyzer

class Test{Language}SentenceGeneration:
    """Test AI sentence generation quality and constraints"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    @pytest.fixture
    def frequency_list(self):
        """Load frequency list for random word selection"""
        # Assuming frequency list is available in the project
        # This would load from 77 Languages Frequency Word Lists/ or similar
        return ["house", "run", "book", "water", "friend", "school", "car", "food", "time", "work"]  # Example

    @pytest.fixture
    def topics_list(self):
        """Load list of topics for random topic selection"""
        # Assuming topics are defined in the project
        return ["daily life", "education", "travel", "food", "family", "work", "sports", "nature", "technology", "health"]

    def test_final_sentence_generation_test(self, analyzer, frequency_list, topics_list):
        """FINAL TEST: Generate 3 sentences 8-10 words long with random word and topic"""
        # Select random word from frequency list
        random_word = random.choice(frequency_list)
        
        # Select random topic
        random_topic = random.choice(topics_list)
        
        # Generate 3 sentences
        num_sentences = 3
        sentences = []
        
        for i in range(num_sentences):
            result = analyzer.generate_sentences(
                word=random_word,
                language="{language_code}",
                num_sentences=1,
                topics=[random_topic],
                min_length=8,
                max_length=10,
                difficulty="intermediate"
            )
            
            assert result.success, f"Sentence generation {i+1} failed for word: {random_word}"
            assert hasattr(result, 'sentences'), "Missing sentences in result"
            assert len(result.sentences) == 1, "Should generate exactly 1 sentence per call"
            
            sentence = result.sentences[0]
            sentences.append(sentence)
            
            # Check sentence length (8-10 words)
            word_count = len(sentence.split())
            assert 8 <= word_count <= 10, f"Sentence {i+1} has {word_count} words, should be 8-10: {sentence}"
            
            # Check that target word is included
            assert random_word.lower() in sentence.lower(), f"Target word '{random_word}' not in sentence: {sentence}"
            
            # Check that sentence relates to the topic (basic check)
            # This would require more sophisticated topic validation
            # For now, just ensure sentence is not empty and contains the word
        
        # Store sentences for use in grammar analysis test
        self.generated_sentences = sentences
        self.test_word = random_word
        self.test_topic = random_topic

    def test_word_explanation_character_limits(self, analyzer):
        """Test word explanations stay within character limits"""
        test_sentences = [
            "Simple sentence.",
            "More complex sentence with multiple words.",
            "Sentence with target word here."
        ]

        for sentence in test_sentences:
            for complexity in ['beginner', 'intermediate', 'advanced']:
                result = analyzer.analyze_grammar(sentence, "word", complexity, "mock_key")

                if result.success and hasattr(result, 'word_explanations'):
                    for word_exp in result.word_explanations:
                        if len(word_exp) >= 4:  # Has meaning
                            meaning = word_exp[3]  # Meaning is at index 3
                            assert len(meaning) <= 75, f"Word explanation too long: '{meaning}' ({len(meaning)} chars)"

    def test_grammar_summary_character_limits(self, analyzer):
        """Test grammar summaries stay within character limits"""
        test_sentences = [
            "Simple sentence.",
            "Complex sentence with grammar.",
            "Very complex sentence requiring detailed analysis."
        ]

        for sentence in test_sentences:
            for complexity in ['beginner', 'intermediate', 'advanced']:
                result = analyzer.analyze_grammar(sentence, "word", complexity, "mock_key")

                if result.success and hasattr(result, 'grammar_summary'):
                    summary = result.grammar_summary
                    assert len(summary) <= 60, f"Grammar summary too long: '{summary}' ({len(summary)} chars)"

    def test_sentence_generation_completeness(self, analyzer):
        """Test generated sentences have all required components"""
        test_words = ["test", "word", "example"]

        for word in test_words:
            for complexity in ['beginner', 'intermediate', 'advanced']:
                result = analyzer.generate_sentence(word, complexity, "mock_key")

                assert result.success, f"Sentence generation failed for word: {word}"
                assert hasattr(result, 'sentence'), "Missing sentence"
                assert hasattr(result, 'word_explanations'), "Missing word explanations"
                assert hasattr(result, 'grammar_summary'), "Missing grammar summary"

                # Check sentence contains the target word
                assert word.lower() in result.sentence.lower(), f"Target word '{word}' not in generated sentence"

    def test_prevention_at_source_quality(self, analyzer):
        """Test prevention-at-source eliminates repetitive explanations"""
        # Test with German-style prevention-at-source prompts
        test_words = ["noun_word", "verb_word", "adjective_word"]

        for word in test_words:
            result = analyzer.generate_sentence(word, "intermediate", "mock_key")

            if result.success and result.word_explanations:
                explanations = [exp[3] for exp in result.word_explanations if len(exp) >= 4]

                # Check for prevention of repetitive patterns
                repetitive_patterns = [
                    f"{word} is a",
                    f"{word} means",
                    f"The word {word}",
                    f"{word} functions as"
                ]

                for explanation in explanations:
                    # Should not start with repetitive word + "is/means"
                    for pattern in repetitive_patterns:
                        assert not explanation.lower().startswith(pattern.lower()), \
                            f"Repetitive explanation: '{explanation}'"

    def test_educational_depth_by_complexity(self, analyzer):
        """Test that complexity levels provide appropriate educational depth"""
        word = "complex_word"

        results = {}
        for complexity in ['beginner', 'intermediate', 'advanced']:
            result = analyzer.generate_sentence(word, complexity, "mock_key")
            if result.success:
                results[complexity] = result

        # Beginner should be simplest
        if 'beginner' in results and 'advanced' in results:
            beginner_exp = results['beginner'].word_explanations
            advanced_exp = results['advanced'].word_explanations

            # Advanced should have more detailed explanations
            if beginner_exp and advanced_exp:
                beginner_len = len(beginner_exp[0][3]) if len(beginner_exp[0]) >= 4 else 0
                advanced_len = len(advanced_exp[0][3]) if len(advanced_exp[0]) >= 4 else 0

                # Advanced explanations should be more detailed (but still within limits)
                assert advanced_len >= beginner_len, \
                    "Advanced explanations should be at least as detailed as beginner"

    def test_linguistic_accuracy_validation(self, analyzer):
        """Test that generated content follows language-specific rules"""
        # Language-specific validation rules
        test_cases = [
            ("test_noun", "beginner", "noun_rules"),
            ("test_verb", "intermediate", "verb_rules"),
            ("test_complex", "advanced", "complex_rules")
        ]

        for word, complexity, rule_type in test_cases:
            result = analyzer.generate_sentence(word, complexity, "mock_key")

            if result.success:
                # Validate against language-specific rules
                # This would be customized per language
                self._validate_language_rules(result, rule_type)

    def _validate_language_rules(self, result, rule_type):
        """Language-specific validation (customize per language)"""
        if rule_type == "noun_rules":
            # Check noun-specific patterns
            pass
        elif rule_type == "verb_rules":
            # Check verb-specific patterns
            pass
        # Add language-specific validations here
```

#### 5.8.3 Word Explanation Quality Tests (German Prevention-at-Source)

**Critical:** Word explanations must follow prevention-at-source methodology like German/Spanish analyzers.

**File:** `tests/test_{language}_word_explanations.py`

```python
import pytest
from languages.{language}.{language}_analyzer import {Language}Analyzer

class Test{Language}WordExplanations:
    """Test word explanation quality using prevention-at-source methodology"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    def test_prevention_at_source_eliminates_repetition(self, analyzer):
        """Test that explanations don't repeat grammatical role information"""
        test_cases = [
            ("house", "noun", "beginner"),
            ("run", "verb", "intermediate"),
            ("beautiful", "adjective", "advanced")
        ]

        for word, expected_role, complexity in test_cases:
            result = analyzer.analyze_grammar(f"This is a {word}.", word, complexity, "mock_key")

            if result.success and result.word_explanations:
                for word_exp in result.word_explanations:
                    if len(word_exp) >= 4 and word_exp[0].lower() == word.lower():
                        explanation = word_exp[3]  # Meaning

                        # Should NOT contain repetitive patterns
                        forbidden_patterns = [
                            f"{word} is a {expected_role}",
                            f"{word} is an {expected_role}",
                            f"{word} is the {expected_role}",
                            f"The {expected_role} {word}",
                            f"{word} functions as a {expected_role}",
                            f"{word} serves as a {expected_role}"
                        ]

                        for pattern in forbidden_patterns:
                            assert not explanation.lower().startswith(pattern.lower()), \
                                f"Repetitive explanation avoided prevention-at-source: '{explanation}'"

    def test_educational_context_provided(self, analyzer):
        """Test that explanations provide educational context beyond basic definition"""
        test_words = ["test_word", "complex_word", "technical_word"]

        for word in test_words:
            result = analyzer.analyze_grammar(f"Example with {word}.", word, "intermediate", "mock_key")

            if result.success and result.word_explanations:
                for word_exp in result.word_explanations:
                    if len(word_exp) >= 4 and word_exp[0].lower() == word.lower():
                        explanation = word_exp[3]

                        # Should provide contextual/grammatical insight
                        educational_indicators = [
                            "serves as", "functions as", "indicates", "shows",
                            "represents", "expresses", "demonstrates", "conveys",
                            "establishes", "creates", "forms", "acts as"
                        ]

                        has_educational_content = any(indicator in explanation.lower()
                                                    for indicator in educational_indicators)

                        # Allow basic definitions for simple words, but check for educational depth
                        if len(explanation) > 20:  # Longer explanations should be educational
                            assert has_educational_content, \
                                f"Long explanation lacks educational context: '{explanation}'"

    def test_language_specific_features_highlighted(self, analyzer):
        """Test that explanations highlight language-specific grammatical features"""
        # Language-specific features to check for
        language_features = self._get_language_specific_features()

        test_sentences = [
            "Complex sentence with grammar.",
            "Another sentence with linguistic features.",
            "Sentence demonstrating language patterns."
        ]

        for sentence in test_sentences:
            result = analyzer.analyze_grammar(sentence, "grammar", "advanced", "mock_key")

            if result.success and result.word_explanations:
                all_explanations = " ".join([exp[3] for exp in result.word_explanations if len(exp) >= 4])

                # Should mention at least some language-specific features
                mentioned_features = [feature for feature in language_features
                                    if feature.lower() in all_explanations.lower()]

                # For advanced complexity, should demonstrate language knowledge
                if len(all_explanations) > 100:  # Substantial analysis
                    assert len(mentioned_features) > 0, \
                        f"Advanced analysis should mention language features. Found: {mentioned_features}"

    def test_explanation_uniqueness(self, analyzer):
        """Test that each word gets a unique, contextual explanation"""
        sentence = "The quick brown fox jumps over the lazy dog."

        result = analyzer.analyze_grammar(sentence, "fox", "intermediate", "mock_key")

        if result.success and result.word_explanations:
            explanations = [exp[3] for exp in result.word_explanations if len(exp) >= 4]

            # Check for duplicate explanations
            unique_explanations = set(explanations)
            assert len(unique_explanations) == len(explanations), \
                f"Duplicate explanations found: {explanations}"

            # Check that explanations are contextual (not generic)
            generic_patterns = [
                "is a word", "means", "refers to", "represents a",
                "is an example of", "is a type of"
            ]

            for explanation in explanations:
                is_generic = any(pattern in explanation.lower() for pattern in generic_patterns)
                if len(explanation) < 30:  # Short explanations might be generic
                    continue
                assert not is_generic, f"Generic explanation: '{explanation}'"

    def test_complexity_level_appropriate_depth(self, analyzer):
        """Test that complexity levels provide appropriate explanation depth"""
        word = "complex_word"
        sentence = f"This is a {word} example."

        results = {}
        for complexity in ['beginner', 'intermediate', 'advanced']:
            result = analyzer.analyze_grammar(sentence, word, complexity, "mock_key")
            if result.success:
                results[complexity] = result

        if len(results) >= 2:
            # Compare explanation lengths and complexity
            beginner_exp = None
            advanced_exp = None

            for complexity, result in results.items():
                if result.word_explanations:
                    for exp in result.word_explanations:
                        if len(exp) >= 4 and exp[0].lower() == word.lower():
                            if complexity == 'beginner':
                                beginner_exp = exp[3]
                            elif complexity == 'advanced':
                                advanced_exp = exp[3]

            if beginner_exp and advanced_exp:
                # Advanced should provide more detailed analysis
                assert len(advanced_exp) >= len(beginner_exp), \
                    f"Advanced explanation should be more detailed: beginner({len(beginner_exp)}) vs advanced({len(advanced_exp)})"

    def _get_language_specific_features(self):
        """Get list of language-specific features to check for in explanations"""
        # Customize this for each language
        return [
            # Add language-specific grammatical features here
            # e.g., for German: "case", "gender", "strong verb"
            # e.g., for Spanish: "gender", "ser/estar", "subjunctive"
            # e.g., for Turkish: "vowel harmony", "agglutination", "case"
        ]

    def test_grammatical_accuracy_validation(self, analyzer):
        """Test that explanations accurately reflect grammatical analysis"""
        # Test cases with known grammatical structures
        test_cases = [
            ("basic_noun_sentence", "noun", "subject"),
            ("verb_sentence", "verb", "predicate"),
            ("complex_structure", "multiple_roles", "various")
        ]

        for sentence_key, target_role, expected_function in test_cases:
            # This would require predefined test sentences
            # Implementation depends on language-specific test data
            pass
```

#### 5.8.4 APKG Export Field Validation Tests

**Critical:** Final field values exported to APKG must meet quality standards for bright poppy colors, parsing logic, HTML output, sentence coloring, word explanations, and gold standard compliance.

**File:** `tests/test_{language}_apkg_export.py`

```python
import pytest
import re
from languages.{language}.{language}_analyzer import {Language}Analyzer
from streamlit_app.deck_exporter import DeckExporter  # Assuming this handles APKG export

class Test{Language}ApkgExportFields:
    """Test APKG export field values for quality and compliance"""

    @pytest.fixture
    def analyzer(self):
        return {Language}Analyzer()

    @pytest.fixture
    def deck_exporter(self):
        return DeckExporter()

    def test_final_grammar_analysis_apkg_test(self, analyzer, deck_exporter):
        """FINAL TEST: Take 1 of the 3 generated sentences and check word-by-word analysis in APKG output"""
        # This test depends on the sentence generation test having run first
        # In practice, you might need to run the sentence generation test separately
        # or mock the generated sentences
        
        # For this test, we'll simulate having generated sentences
        # In real implementation, this would use sentences from test_final_sentence_generation_test
        simulated_sentences = [
            "The house on the hill is very beautiful and spacious.",
            "She decided to run quickly to catch the early train.",
            "Reading a good book can be quite relaxing after work."
        ]
        test_word = "house"  # From frequency list
        test_sentence = simulated_sentences[0]  # Take first sentence
        
        # Perform grammar analysis on the selected sentence
        result = analyzer.analyze_grammar(test_sentence, test_word, "intermediate", "real_api_key")
        
        assert result.success, f"Grammar analysis failed for sentence: {test_sentence}"
        assert hasattr(result, 'word_explanations'), "Missing word explanations"
        assert hasattr(result, 'html_output'), "Missing HTML output"
        
        # Check word-by-word analysis
        word_explanations = result.word_explanations
        assert len(word_explanations) > 0, "No word explanations generated"
        
        # Verify each word has proper analysis (word, role, color, meaning)
        for word_exp in word_explanations:
            assert len(word_exp) >= 4, f"Incomplete word explanation: {word_exp}"
            word, role, color, meaning = word_exp[:4]
            
            # Validate word is present in sentence
            assert word.lower() in test_sentence.lower(), f"Word '{word}' not found in sentence: {test_sentence}"
            
            # Validate role is not empty
            assert role.strip(), f"Empty grammatical role for word '{word}'"
            
            # Validate color is a valid hex color
            assert color.startswith('#') and len(color) == 7, f"Invalid color format: {color}"
            
            # Validate meaning is within character limits
            assert len(meaning) <= 75, f"Word explanation too long: {len(meaning)} chars > 75 limit"
            assert len(meaning.strip()) > 0, f"Empty meaning for word '{word}'"
        
        # Check HTML output has proper coloring and marking
        html_output = result.html_output
        assert '<span' in html_output, "HTML output missing span elements for coloring"
        assert 'style=' in html_output, "HTML output missing style attributes"
        
        # Verify target word is properly highlighted
        assert test_word.lower() in html_output.lower(), f"Target word '{test_word}' not highlighted in HTML"
        
        # Check for proper color application (at least one color from scheme)
        color_scheme = analyzer.get_color_scheme("intermediate")
        colors_used = set()
        for color in color_scheme.values():
            if color in html_output:
                colors_used.add(color)
        assert len(colors_used) > 0, f"No colors from scheme applied in HTML: {color_scheme}"
        
        # Simulate APKG export and verify final output
        apkg_fields = deck_exporter.extract_apkg_fields(result)
        
        # Verify APKG fields contain the analyzed data
        assert 'sentence' in apkg_fields, "APKG missing sentence field"
        assert 'word_explanations' in apkg_fields, "APKG missing word_explanations field"
        assert 'html_output' in apkg_fields, "APKG missing html_output field"
        
        # Verify the sentence in APKG matches the analyzed sentence
        assert apkg_fields['sentence'] == test_sentence, "APKG sentence doesn't match analyzed sentence"
        
        # Verify HTML in APKG has proper formatting
        apkg_html = apkg_fields['html_output']
        assert '<span' in apkg_html, "APKG HTML missing span elements"
        assert len(apkg_html) > len(test_sentence), "APKG HTML not properly formatted with colors"

    def test_bright_poppy_colors_applied(self, analyzer):
        """Test that bright poppy colors are correctly applied to grammatical roles"""
        result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", "mock_key")
        
        # Check that HTML contains bright poppy color codes
        bright_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
        html_output = result.html_output
        
        # Verify at least one bright color is used
        color_found = any(color in html_output for color in bright_colors)
        assert color_found, f"No bright poppy colors found in HTML: {html_output}"

    def test_parsing_logic_accuracy(self, analyzer):
        """Test that parsing logic correctly extracts and structures data"""
        result = analyzer.analyze_grammar("The quick brown fox jumps", "fox", "intermediate", "mock_key")
        
        # Verify word_explanations structure
        assert hasattr(result, 'word_explanations')
        assert isinstance(result.word_explanations, list)
        assert len(result.word_explanations) > 0
        
        # Check each word explanation has required fields
        for word_exp in result.word_explanations:
            assert len(word_exp) >= 4, f"Word explanation incomplete: {word_exp}"
            word, role, color, meaning = word_exp[:4]
            assert isinstance(word, str) and word.strip()
            assert isinstance(role, str) and role.strip()
            assert isinstance(color, str) and color.startswith('#')
            assert isinstance(meaning, str) and len(meaning.strip()) > 0

    def test_html_output_structure(self, analyzer):
        """Test that HTML output has proper structure and formatting"""
        result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", "mock_key")
        html_output = result.html_output
        
        # Check for required HTML elements
        assert '<span' in html_output, "HTML should contain span elements for coloring"
        assert 'style=' in html_output, "HTML should contain style attributes"
        assert '</span>' in html_output, "HTML should have closing span tags"
        
        # Verify no malformed HTML
        span_count = html_output.count('<span')
        close_count = html_output.count('</span>')
        assert span_count == close_count, f"Mismatched span tags: {span_count} open, {close_count} close"

    def test_sentence_coloring_consistency(self, analyzer):
        """Test that sentence coloring is consistent and properly applied"""
        result = analyzer.analyze_grammar("The cat sat on the mat", "cat", "intermediate", "mock_key")
        html_output = result.html_output
        
        # Extract colors used in the sentence
        color_pattern = r'color:#([A-Fa-f0-9]{6})'
        colors_used = re.findall(color_pattern, html_output)
        
        # Verify colors are from the defined color scheme
        color_scheme = analyzer.get_color_scheme("intermediate")
        valid_colors = set(color_scheme.values())
        
        for color in colors_used:
            full_color = f"#{color}"
            assert full_color in valid_colors, f"Color {full_color} not in color scheme: {valid_colors}"

    def test_word_explanations_quality(self, analyzer):
        """Test that word explanations meet quality standards for APKG export"""
        result = analyzer.analyze_grammar("The student reads the book", "reads", "intermediate", "mock_key")
        
        explanations = result.word_explanations
        
        for word_exp in explanations:
            word, role, color, meaning = word_exp[:4]
            
            # Check character limits for APKG compatibility
            assert len(meaning) <= 75, f"Word explanation too long: {len(meaning)} chars > 75 limit"
            
            # Verify no repetitive role information (prevention-at-source)
            role_lower = role.lower()
            meaning_lower = meaning.lower()
            assert role_lower not in meaning_lower, f"Role '{role}' repeated in meaning: {meaning}"
            
            # Check for educational value
            assert len(meaning.split()) >= 3, f"Explanation too brief: {meaning}"

    def test_gold_standard_comparison(self, analyzer):
        """Test that results compare favorably against gold standard analyzers"""
        # Load gold standard results (Chinese Simplified as reference)
        gold_standard_result = self._load_gold_standard_result("zh", "intermediate")
        
        # Run analysis on same sentence
        result = analyzer.analyze_grammar(
            gold_standard_result['sentence'], 
            gold_standard_result['target_word'], 
            "intermediate", 
            "mock_key"
        )
        
        # Compare key metrics
        assert len(result.word_explanations) >= len(gold_standard_result['word_explanations']), \
            "Fewer word explanations than gold standard"
        
        # Check confidence score meets minimum threshold
        assert result.confidence_score >= gold_standard_result['min_confidence'], \
            f"Confidence {result.confidence_score} below gold standard {gold_standard_result['min_confidence']}"
        
        # Verify HTML output quality
        assert len(result.html_output) >= len(gold_standard_result['html_output']) * 0.8, \
            "HTML output significantly shorter than gold standard"

    def test_apkg_field_values_final_format(self, analyzer, deck_exporter):
        """Test that final APKG field values are properly formatted"""
        result = analyzer.analyze_grammar("Sample sentence for testing", "sample", "intermediate", "mock_key")
        
        # Simulate APKG field extraction
        fields = deck_exporter.extract_apkg_fields(result)
        
        # Verify required fields exist
        required_fields = ['sentence', 'word_explanations', 'html_output', 'confidence_score']
        for field in required_fields:
            assert field in fields, f"Missing required APKG field: {field}"
            assert fields[field] is not None, f"APKG field {field} is None"
        
        # Check field value types and formats
        assert isinstance(fields['sentence'], str)
        assert isinstance(fields['word_explanations'], (list, str))
        assert isinstance(fields['html_output'], str)
        assert isinstance(fields['confidence_score'], (int, float))
        
        # Verify HTML field contains proper coloring
        assert '<span' in fields['html_output'], "APKG HTML field missing span elements"

    def _load_gold_standard_result(self, language_code: str, complexity: str) -> dict:
        """Load gold standard result for comparison"""
        # Implementation would load from test fixtures
        # This is a placeholder for the actual implementation
        return {
            'sentence': 'Test sentence',
            'target_word': 'test',
            'word_explanations': [['test', 'noun', '#FF6B6B', 'A sample word']],
            'html_output': '<span style="color:#FF6B6B">Test</span> sentence',
            'min_confidence': 0.7
        }

**ðŸŽ¯ FINAL COMPREHENSIVE TEST COMPLETE**

This concludes the comprehensive quality testing framework. The final test combines sentence generation (taking a random word from the frequency list and generating 3 sentences 8-10 words long with a random topic) with grammar analysis validation (checking word-by-word analysis, proper coloring, and marking in the final APKG output). All language analyzers must pass these tests to be considered production-ready and matching the quality standards of existing implementations.

## ðŸ“Š **DETAILED REPORTING REQUIREMENT**

**CRITICAL:** All final tests must provide detailed reporting of generated sentences with ALL available details. This ensures transparency and allows for quality assessment of AI-generated content.

### **Required Reporting Format:**

When running final tests, the output must include:

1. **Random Word Selection Details:**
   - Selected word from frequency list
   - Word frequency rank (if available)
   - Word category/classification

2. **Random Topic Selection Details:**
   - Selected topic from curated list
   - Topic category (e.g., "daily life", "education", "nature")

3. **Sentence Generation Results:**
   - All 3 generated sentences (8-10 words each)
   - Word count for each sentence
   - Target word inclusion verification
   - Topic relevance assessment (if available)
   - API response status (success/fallback used)

4. **Grammar Analysis Details (for APKG test):**
   - Selected sentence for analysis
   - Word-by-word breakdown with:
     - Grammatical role
     - Color code assigned
     - Meaning/explanation
     - Confidence score
   - HTML output with coloring
   - APKG field validation results

5. **Quality Metrics:**
   - Sentence length compliance (8-10 words)
   - Word explanation character limits (< 75 chars)
   - Color scheme validation
   - Confidence score thresholds

### **Example Detailed Report Output:**

```
=== FINAL COMPREHENSIVE TEST REPORT ===

ðŸ“ Random Word Selection:
- Word: "olur" (becomes/happens)
- Frequency Rank: 45
- Category: Verb

ðŸŽ¯ Random Topic Selection:
- Topic: "Science"
- Category: Academic

ðŸ“š Generated Sentences:
1. "Bilimsel araÅŸtÄ±rmalar olur ve yeni keÅŸifler getirir." (8 words) âœ“
   - Target word included: âœ“
   - Topic relevance: High

2. "Teknolojik geliÅŸmeler olur ve hayatÄ±mÄ±zÄ± kolaylaÅŸtÄ±rÄ±r." (7 words) âš ï¸ (slightly short)
   - Target word included: âœ“
   - Topic relevance: Medium

3. "Ä°klim deÄŸiÅŸikliÄŸi olur ve doÄŸal dengeyi bozar." (8 words) âœ“
   - Target word included: âœ“
   - Topic relevance: High

ðŸ” Grammar Analysis (Sentence 1):
Word-by-word breakdown:
- Bilimsel: adjective, #45B7D1, "Scientific/related to science"
- araÅŸtÄ±rmalar: noun, #FF6B6B, "Researches/studies"
- olur: verb, #4ECDC4, "Happens/becomes"
- ve: conjunction, #FFEAA7, "And"
- yeni: adjective, #45B7D1, "New"
- keÅŸifler: noun, #FF6B6B, "Discoveries"
- getirir: verb, #4ECDC4, "Brings"

HTML Output: <span style="color:#FF6B6B">Bilimsel</span> <span style="color:#45B7D1">araÅŸtÄ±rmalar</span>...

APKG Validation: âœ“ All fields valid
Confidence Score: 0.85

âœ… TEST PASSED - Production Ready
```

### **Implementation Requirement:**

Update test methods to include detailed logging/printing of all generation and analysis details. Use structured output with clear sections and validation markers (âœ“/âš ï¸/âŒ).
```

**ðŸš€ Ready to start implementing?** Begin with Phase 1: Research Validation, then follow each phase sequentially. Remember: quality over speed - take time to do it right!

**Need help?** Refer to the [Architecture Guide](architecture_guide.md) for design patterns, [Testing Guide](testing_guide.md) for testing strategies, or [Troubleshooting Guide](troubleshooting_guide.md) for common issues.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\implementation_guide.md
