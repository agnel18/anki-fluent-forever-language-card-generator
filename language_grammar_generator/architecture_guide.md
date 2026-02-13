# Architecture Guide
## Domain-Driven Design for Language Analyzers

**Principles:** Clean Architecture, Domain-Driven Design, Separation of Concerns  
**Primary Gold Standard:** [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py) - Clean Architecture with external configuration  
**Secondary Reference:** [Hindi](languages/hindi/hi_analyzer.py)  
**Pattern:** Clean Architecture with integrated domain components  
**Critical:** Follow Chinese Simplified patterns - external configuration, integrated fallbacks, no artificial confidence boosting

## ðŸ—ï¸ Architectural Overview

### Core Principles

#### 1. Clean Architecture - PRIMARY GOLD STANDARD (Chinese Simplified)
**Dependency Inversion** - Domain layer contains all business logic, external layers adapt to domain
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Frameworks & Drivers (External APIs, File Systems, etc.)   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Interface Adapters (Infrastructure Layer)                  â”‚
â”‚  - File I/O, API calls, external service integrations       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Application Layer (Use Cases)                             â”‚
â”‚  - Application-specific business rules                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Domain Layer (Entities & Core Business Logic) â—„â”€â”€ GOLD    â”‚
â”‚  - Language-specific grammar rules & patterns              â”‚
â”‚  - External configuration files (YAML/JSON)                â”‚
â”‚  - Integrated fallback systems                             â”‚
â”‚  - Natural validation without artificial boosting          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### 2. Domain-Driven Design (DDD) - Chinese Simplified Pattern
**Business Logic First** - Domain components contain all linguistic knowledge and rules
```
Domain Layer (Core Business Logic) - CHINESE SIMPLIFIED GOLD STANDARD
â”œâ”€â”€ Config: External YAML/JSON configuration files (zh_config.py loads external files)
â”‚   â”œâ”€â”€ Word Meanings: External JSON dictionary with specific meanings
â”‚   â”œâ”€â”€ Grammatical Roles: Color schemes and role definitions from YAML
â”‚   â””â”€â”€ Language Patterns: Scripts, character sets, segmentation rules from config
â”œâ”€â”€ Prompt Builder: Jinja2 template-based AI prompt generation (zh_prompt_builder.py)
â”œâ”€â”€ Response Parser: AI output processing with integrated fallbacks (zh_response_parser.py)
â”œâ”€â”€ Validator: Quality assessment with natural confidence scoring (zh_validator.py)
â”œâ”€â”€ Fallbacks: Error recovery integrated within response parser (zh_fallbacks.py)
â””â”€â”€ Patterns: Linguistic pattern recognition (zh_patterns.py)
```

#### 3. Separation of Concerns - Chinese Simplified Implementation
**Single Responsibility** - Each component has one clear purpose, following Clean Architecture
- **Config:** Loads external files, never processes text (like zh_config.py)
- **Prompt Builder:** Creates Jinja2 templates, never calls APIs (like zh_prompt_builder.py)
- **Response Parser:** Parses responses with integrated fallbacks, never validates quality (like zh_response_parser.py)
- **Validator:** Assesses quality with natural scoring, never generates output (NO artificial boosting)
- **Fallbacks:** Provides error recovery within domain layer, never does primary processing

### Component Architecture - Chinese Simplified Gold Standard Pattern

#### Main Analyzer (Clean Architecture Facade) - COPY FROM CHINESE SIMPLIFIED
```python
class ZhAnalyzer(BaseGrammarAnalyzer):  # Gold standard Clean Architecture
    """
    Clean Architecture facade orchestrating domain components.
    FOLLOWS CHINESE SIMPLIFIED: External config, integrated fallbacks, natural validation.
    """
    
    def __init__(self):
        # Initialize domain components first (Clean Architecture)
        self.zh_config = ZhConfig()           # Loads external YAML/JSON
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)
        self.fallbacks = ZhFallbacks(self.zh_config)  # Integrated in domain
        
        # Create language config and call parent
        config = LanguageConfig(...)
        super().__init__(config)
```

#### Domain Components - Chinese Simplified Structure
```python
# 1. Config Component (External Files) - CHINESE SIMPLIFIED PATTERN
@dataclass
class ZhConfig:
    """Configuration loaded from external YAML/JSON files"""
    grammatical_roles: Dict[str, str]     # From zh_grammatical_roles.yaml
    common_classifiers: List[str]          # From zh_common_classifiers.yaml
    aspect_markers: Dict[str, str]         # From zh_aspect_markers.yaml
    structural_particles: Dict[str, str]   # From zh_structural_particles.yaml
    word_meanings: Dict[str, str]          # From zh_word_meanings.json
    prompt_templates: Dict[str, str]       # From zh_prompt_templates.yaml
    patterns: Dict[str, Any]              # From zh_patterns.yaml

# 2. Prompt Builder (Jinja2 Templates) - CHINESE SIMPLIFIED PATTERN
class ZhPromptBuilder:
    """Jinja2 template-based prompt generation"""
    def __init__(self, config: ZhConfig):
        self.config = config
        self.templates = {}  # Load Jinja2 templates
        
    def build_single_sentence_prompt(self, sentence, target_word, complexity):
        template = self.templates.get('single_sentence')
        return template.render(sentence=sentence, target_word=target_word, complexity=complexity)

# 3. Response Parser (Integrated Fallbacks) - CHINESE SIMPLIFIED PATTERN
class ZhResponseParser:
    """AI response parsing with integrated fallback hierarchy"""
    def __init__(self, config: ZhConfig):
        self.config = config
        self.fallbacks = ZhFallbacks(config)  # Integrated in domain layer
        
    def parse_response(self, ai_response, complexity, sentence, target_word):
        # Try primary parsing, then fallbacks
        try:
            return self._parse_json_response(ai_response)
        except:
            return self.fallbacks.create_fallback(sentence, complexity)

# 4. Validator (Natural Scoring) - CHINESE SIMPLIFIED PATTERN
class ZhValidator:
    """Quality validation with natural confidence scoring"""
    def validate_result(self, result, sentence):
        # Natural validation without artificial boosting
        # Return quality_score between 0.0 and 1.0
        return self._calculate_natural_confidence(result, sentence)
```

### Infrastructure Layer - Chinese Simplified Minimal Approach

#### External Configuration Files - CHINESE SIMPLIFIED PATTERN
```
infrastructure/data/                    # Minimal infrastructure
â”œâ”€â”€ zh_grammatical_roles.yaml         # Grammatical role definitions
â”œâ”€â”€ zh_common_classifiers.yaml        # Classifier lists
â”œâ”€â”€ zh_aspect_markers.yaml           # Aspect particle patterns
â”œâ”€â”€ zh_structural_particles.yaml     # Particle system rules
â”œâ”€â”€ zh_modal_particles.yaml          # Modal particle patterns
â”œâ”€â”€ zh_word_meanings.json            # Pre-defined word meanings
â””â”€â”€ zh_patterns.yaml                 # Regex patterns and validation rules
```

**âŒ Anti-Pattern (Separate Infrastructure Layer):**
```
infrastructure/                       # AVOID THIS COMPLEXITY
â”œâ”€â”€ zh_tw_fallbacks.py              # Separate component (breaks Clean Architecture)
â””â”€â”€ data/
```

### Implementation Guidelines - Follow Chinese Simplified

#### 1. Configuration Management - EXTERNAL FILES (Chinese Simplified Pattern)
```python
# âœ… CORRECT: External configuration files
class ZhConfig:
    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "zh_grammatical_roles.yaml")
        self.word_meanings = self._load_json(config_dir / "zh_word_meanings.json")

# âŒ AVOID: Hardcoded configurations
class LanguageConfig:
    def __init__(self):
        self.grammatical_roles = {
            "noun": "#FFAA00",
            "verb": "#44FF44",
            # ... hardcoded values
        }
```

#### 2. Fallback Integration - WITHIN DOMAIN (Chinese Simplified Pattern)
```python
# âœ… CORRECT: Integrated fallbacks in response parser
class ZhResponseParser:
    def __init__(self, config: ZhConfig):
        self.config = config
        self.fallbacks = ZhFallbacks(config)  # Domain component
        
    def parse_response(self, ai_response, sentence, complexity):
        try:
            return self._parse_primary(ai_response)
        except:
            return self.fallbacks.create_fallback(sentence, complexity)

# âŒ AVOID: Separate infrastructure fallbacks
class LanguageAnalyzer:
    def __init__(self):
        self.fallbacks = LanguageFallbacks()  # Infrastructure component
```

#### 3. Prompt Engineering - JINJA2 TEMPLATES (Chinese Simplified Pattern)
```python
# âœ… CORRECT: Template-based prompts
class ZhPromptBuilder:
    def __init__(self, config: ZhConfig):
        self.config = config
        self.template = Template("""
        You are a linguist specializing in {{ language }}...
        Analyze: {{ sentence }}
        """)
        
    def build_prompt(self, sentence, complexity):
        return self.template.render(
            language=self.config.language_name,
            sentence=sentence,
            complexity=complexity
        )

# âŒ AVOID: Hardcoded string prompts
class LanguagePromptBuilder:
    def build_prompt(self, sentence, complexity):
        return f"You are a linguist... Analyze: {sentence}"  # Hardcoded
```

### Migration Path - From Complex to Clean Architecture

#### Current Issues to Address:
1. **Chinese Traditional** uses separate infrastructure layer - should integrate fallbacks into domain
2. **Chinese Traditional** has hardcoded configurations - should use external files like Chinese Simplified
3. **Chinese Traditional** uses string-based prompts - should use Jinja2 templates
4. **Complex modular architecture** should be simplified to Clean Architecture

#### Migration Steps:
1. **Extract hardcoded configs** to external YAML/JSON files
2. **Move fallback logic** from infrastructure to domain response parser
3. **Implement Jinja2 templates** for prompt generation
4. **Simplify architecture** by removing unnecessary infrastructure separation
5. **Follow Chinese Simplified patterns** for all new implementations

    def __init__(self):
        # Initialize domain components FIRST (like gold standards)
        self.config = LanguageConfig()
        self.prompt_builder = PromptBuilder(self.config)
        self.response_parser = ResponseParser(self.config)
        self.validator = Validator(self.config)

    def analyze_grammar(self, sentence, target_word, complexity, api_key):
        """Main orchestration method - LIKE GOLD STANDARD WORKFLOW"""
        # 1. Build prompt
        prompt = self.prompt_builder.build_single_prompt(...)

        # 2. Call AI (infrastructure concern)
        ai_response = self._call_ai(prompt, api_key)

        # 3. Parse response
        result = self.response_parser.parse_response(ai_response, ...)

        # 4. Validate quality (NATURAL SCORING - NO ARTIFICIAL BOOSTING)
        validated = self.validator.validate_result(result, sentence)

        # 5. Generate output
        return self._generate_html_output(validated, ...)
```

#### Critical: Rich Explanations Pattern (Chinese Gold Standard)
**Key Learning:** Base analyzers provide grammatical roles only, but gold standard analyzers provide rich explanations with individual word meanings.

**âŒ Anti-Pattern (Base Analyzer):**
```python
# Only grammatical roles - insufficient for learning
"noun in zh-tw grammar"
"verb in zh-tw grammar"
```

**âœ… Gold Standard Pattern (Chinese Analyzers):**
```python
# Rich explanations with individual meanings
"æˆ‘ (I, me - first person singular pronoun)"
"å–œæ­¡ (to like, to be fond of - verb expressing preference)"
"åƒ (to eat, to consume - verb of consumption)"
```

**Implementation Requirements:**
- **analyze_grammar method**: AI workflow â†’ parsing â†’ HTML generation â†’ GrammarAnalysis return
- **_generate_html_output method**: Position-based character/word coloring with meanings
- **Word explanations format**: `[word, role, color, meaning]` tuples for each analyzed element
- **Individual meaning extraction**: Parse `individual_meaning` from AI responses
- **HTML compatibility**: Inline styles for Anki flashcard compatibility

**Chinese Traditional Implementation Example:**
```python
# Word Meanings Dictionary Integration (CRITICAL for Sino-Tibetan)
class ZhTwConfig:
    def __init__(self):
        # Load word meanings from external JSON (provides rich explanations)
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.word_meanings = self._load_json(config_dir / "zh_tw_word_meanings.json")
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load word meanings: {e}")
            return {}

class ZhTwFallbacks:
    def _analyze_word(self, word: str) -> Dict[str, Any]:
        # Check word meanings first (provides rich explanations)
        if word in self.config.word_meanings:
            meaning = self.config.word_meanings[word]  # "three (numeral)"
            role = self._guess_grammatical_role(word)
            return {
                'word': word,
                'individual_meaning': meaning,
                'grammatical_role': role,
                'confidence': 'high'
            }
        
        # Generic fallback only if no dictionary entry
        role = self._guess_grammatical_role(word)
        meaning = self._generate_fallback_explanation(word, role)  # "numeral in zh-tw grammar"
        return {
            'word': word,
            'individual_meaning': meaning,
            'grammatical_role': role,
            'confidence': 'low'
        }
```
def analyze_grammar(self, sentence: str, target_word: str, complexity: str, api_key: str) -> GrammarAnalysis:
    """Rich explanation workflow - Chinese gold standard pattern"""
    # 1. AI call for detailed analysis
    ai_response = self._call_ai_model(prompt, api_key)

    # 2. Parse individual meanings from response
    parsed = self.response_parser.parse_response(ai_response, sentence, complexity)

    # 3. Generate HTML with colored explanations
    html = self._generate_html_output(parsed, sentence, complexity)

    return GrammarAnalysis(
        sentence=sentence,
        word_explanations=parsed.get('word_explanations', []),
        html_output=html,
        explanations=parsed.get('explanations', {})
    )

def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
    """Position-based coloring with individual meanings"""
    explanations = parsed_data.get('word_explanations', [])
    color_scheme = self.get_color_scheme(complexity)

    html_parts = []
    i = 0
    while i < len(sentence):
        matched = False
        for exp in sorted(explanations, key=lambda x: len(x[0]), reverse=True):
            if len(exp) >= 4:  # [word, role, color, meaning]
                word, role, color, meaning = exp[0], exp[1], exp[2], exp[3]
                word_len = len(word)

                if i + word_len <= len(sentence) and sentence[i:i + word_len] == word:
                    # Apply color and preserve meaning for Anki compatibility
                    safe_word = word.replace('{', '{{').replace('}', '}}')
                    colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word}</span>'
                    html_parts.append(colored_word)
                    i += word_len
                    matched = True
                    break

        if not matched:
            html_parts.append(sentence[i])
            i += 1

    return ''.join(html_parts)
```

#### Domain Components - Gold Standard Implementation

##### 1. Configuration Component - LIKE HI_CONFIG/ZH_CONFIG
```python
class LanguageConfig:
    """
    Single source of truth for language-specific settings - LIKE GOLD STANDARDS.
    No business logic - pure data and mappings.
    LOADS FROM EXTERNAL FILES like Hindi/Chinese configs.
    """

    # Language metadata (like gold standards)
    grammatical_roles: Dict[str, str]
    color_schemes: Dict[str, Dict[str, str]]  # NATURAL color schemes
    prompt_templates: Dict[str, str]  # Like gold standard templates

    def __init__(self):
        # Load from external files (like gold standards)
        self.grammatical_roles = self._load_yaml("grammatical_roles.yaml")
        self.prompt_templates = {
            "single": "[LANGUAGE-SPECIFIC PROMPT LIKE GOLD STANDARDS]",
            "batch": "[BATCH PROMPT LIKE GOLD STANDARDS]"
        }
```

##### 2. Prompt Builder Component - LIKE GOLD STANDARD BUILDERS
```python
class PromptBuilder:
    """
    Generates AI prompts using templates - LIKE HINDI/CHINESE BUILDERS.
    Uses Jinja2 templates with language-specific logic.
    CACHES prompts for performance (like gold standards).
    """
    Knows prompt engineering, not AI APIs.
    """

    def __init__(self, config: LanguageConfig):
        self.config = config
        self.templates = self._load_templates()

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single sentence analysis"""
        context = {
            'sentence': sentence,
            'target_word': target_word,
            'complexity': complexity,
            'language': self.config.language_name
        }
        return self.templates['single'].render(**context)
```

##### 3. Response Parser Component - LIKE GOLD STANDARD PARSERS
```python
class ResponseParser:
    """
    Parses AI responses into structured data - LIKE HINDI/CHINESE PARSERS.
    Handles JSON parsing, normalization, error recovery.
    NO validation logic - pure parsing (like gold standards).
    """

    def parse_response(self, ai_response, sentence, config):
        """Parse AI response - LIKE GOLD STANDARD PARSING"""
        try:
            # Parse JSON (like gold standards)
            data = json.loads(ai_response)

            # Normalize structure (like gold standards)
            return self._normalize_response(data, sentence, config)

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback parsing (like gold standards)
            return self._fallback_parse(ai_response, sentence, config)

    def _normalize_response(self, data, sentence, config):
        """Normalize parsed data - LIKE GOLD STANDARD NORMALIZATION"""
        # Apply language-specific normalization (like Hindi/Chinese)
        # Return standardized structure
        return {
            "sentence": sentence,
            "analysis": data.get("analysis", {}),
            "confidence": data.get("confidence", 0.5),  # NATURAL confidence
            "metadata": data.get("metadata", {})
        }
```

##### 4. Validator Component - NATURAL VALIDATION ONLY (NO ARTIFICIAL BOOSTING)
```python
class Validator:
    """
    Validates analysis quality with NATURAL confidence scoring - LIKE GOLD STANDARDS.
    NO artificial confidence boosting - removed from all implementations.
    Assesses data completeness, accuracy, consistency.
    """

    def validate_result(self, result, sentence):
        """Validate analysis result - NATURAL SCORING LIKE GOLD STANDARDS"""
        # Basic quality checks (like gold standards)
        checks = {
            "has_analysis": bool(result.get("analysis")),
            "sentence_matches": result.get("sentence") == sentence,
            "confidence_reasonable": 0 <= result.get("confidence", 0) <= 1
        }

        # Calculate natural confidence (NO artificial boosting)
        confidence = self._calculate_natural_confidence(result, checks)

        return {
            **result,
            "validation_checks": checks,
            "final_confidence": confidence  # NATURAL score only
        }

    def _calculate_natural_confidence(self, result, checks):
        """Natural confidence calculation - LIKE GOLD STANDARDS"""
        # Simple weighted scoring (like Hindi/Chinese)
        base_score = 0.5
        if checks["has_analysis"]:
            base_score += 0.3
        if checks["sentence_matches"]:
            base_score += 0.2

        return min(base_score, 1.0)  # NATURAL scoring, no artificial boost
```

### Infrastructure Layer - Gold Standard Implementation

#### AI Service Integration - LIKE GOLD STANDARD AI CALLS
```python
class AIService:
    """
    Handles AI API calls - LIKE GOLD STANDARD AI INTEGRATION.
    Uses Google Gemini with strict model restrictions.
    Implements circuit breaker pattern for reliability.
    """

    ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]  # STRICT

    def call_ai(self, prompt, api_key, model="gemini-2.5-flash"):
        """Call AI with gold standard error handling"""
        if model not in self.ALLOWED_MODELS:
            raise ValueError(f"Model {model} not allowed. Use: {self.ALLOWED_MODELS}")

        # Circuit breaker logic (like gold standards)
        # Retry logic with exponential backoff
        # Return raw response for parsing
```

#### External Configuration - LIKE GOLD STANDARD CONFIG LOADING
```python
class ConfigLoader:
    """
    Loads configuration from external files - LIKE HINDI/CHINESE CONFIGS.
    Supports YAML, JSON, environment variables.
    Validates configuration integrity.
    """

    def load_language_config(self, language_code):
        """Load language config - LIKE GOLD STANDARD LOADING"""
        # Load from YAML files (like gold standards)
        config_path = f"languages/{language_code}/config.yaml"
        return self._load_yaml_config(config_path)
```

### Testing Strategy - Gold Standard Testing Patterns

#### Unit Testing - LIKE GOLD STANDARD TESTS
```python
class TestLanguageAnalyzer:
    """
    Unit tests following gold standard patterns - NO confidence boosting tests.
    Tests each component in isolation.
    Uses pytest fixtures and mocking.
    """

    def test_config_loading(self):
        """Test config loads correctly - LIKE GOLD STANDARD TESTS"""
        config = LanguageConfig()
        assert config.language_code == "expected_code"

    def test_prompt_building(self):
        """Test prompt generation - LIKE GOLD STANDARD TESTS"""
        builder = PromptBuilder(config)
        prompt = builder.build_single_prompt(...)
        assert "expected_content" in prompt

    def test_response_parsing(self):
        """Test response parsing - LIKE GOLD STANDARD TESTS"""
        parser = ResponseParser(config)
        result = parser.parse_response(valid_json_response, ...)
        assert result["sentence"] == expected_sentence

    def test_natural_validation(self):
        """Test natural validation - NO artificial boosting"""
        validator = Validator(config)
        result = validator.validate_result(test_data, sentence)
        assert 0 <= result["final_confidence"] <= 1  # NATURAL range
        # NO tests for artificial confidence boosting
```

#### Integration Testing - Gold Standard Integration
```python
class TestIntegration:
    """
    End-to-end tests with real AI calls - LIKE GOLD STANDARD INTEGRATION.
    Tests complete analysis workflow.
    Uses test doubles for external dependencies.
    """

    def test_full_analysis_workflow(self):
        """Test complete analysis - LIKE GOLD STANDARD WORKFLOW"""
        analyzer = LanguageAnalyzer()
        result = analyzer.analyze_grammar(sentence, word, complexity, api_key)

        # Assertions matching gold standard expectations
        assert result["sentence"] == sentence
        assert "analysis" in result
        assert 0 <= result["confidence"] <= 1  # NATURAL confidence
```

### Implementation Checklist - Gold Standard Compliance

#### âœ… Pre-Implementation
- [ ] Study [Hindi analyzer](languages/hindi/hi_analyzer.py) thoroughly
- [ ] Study [Chinese Simplified analyzer](languages/chinese_simplified/zh_analyzer.py) thoroughly
- [ ] Understand facade pattern orchestration
- [ ] Review natural validation patterns (NO artificial boosting)

#### âœ… Domain Components
- [ ] Config component loads from external files (like gold standards)
- [ ] Prompt builder uses templates (like gold standards)
- [ ] Response parser handles JSON/normalization (like gold standards)
- [ ] Validator uses NATURAL confidence scoring (NO artificial boosting)

#### âœ… Main Analyzer
- [ ] Facade pattern implementation (like gold standards)
- [ ] Component orchestration (like gold standards)
- [ ] Error handling with fallbacks (like gold standards)
- [ ] AI integration with circuit breaker (like gold standards)

#### âœ… Testing
- [ ] Unit tests for each component (like gold standards)
- [ ] Integration tests for workflow (like gold standards)
- [ ] NO confidence boosting tests (removed like gold standards)
- [ ] Natural validation tests only

#### âœ… Documentation
- [ ] Component responsibilities documented
- [ ] API contracts specified
- [ ] Error handling documented
- [ ] Testing strategy documented

### Common Pitfalls - Avoid These

#### âŒ Artificial Confidence Boosting
```python
# WRONG - Artificial boosting (removed from all implementations)
def validate_result(self, result, sentence):
    confidence = result.get("confidence", 0.5)
    if some_condition:
        confidence = min(confidence * 1.5, 1.0)  # ARTIFICIAL BOOST - BAD
    return confidence

# CORRECT - Natural scoring (like gold standards)
def validate_result(self, result, sentence):
    checks = self._perform_quality_checks(result, sentence)
    return self._calculate_natural_confidence(checks)  # NATURAL - GOOD
```

#### âŒ Mixed Concerns
```python
# WRONG - Config doing validation
class LanguageConfig:
    def validate_result(self, result):  # Config shouldn't validate
        # Validation logic in config - BAD

# CORRECT - Separate validator (like gold standards)
class LanguageConfig:
    def get_validation_rules(self):  # Config provides rules
        return self.validation_rules

class Validator:
    def validate_result(self, result, config):  # Validator validates
        rules = config.get_validation_rules()
        # Validation logic here - GOOD
```

#### âŒ Tight Coupling
```python
# WRONG - Direct AI calls in domain
class PromptBuilder:
    def build_and_call_ai(self, sentence):  # Builder calling AI - BAD
        prompt = self._build_prompt(sentence)
        return self.ai_service.call(prompt)  # Tight coupling

# CORRECT - Separation of concerns (like gold standards)
class PromptBuilder:
    def build_prompt(self, sentence):  # Builder only builds
        return self._build_prompt(sentence)

class LanguageAnalyzer:
    def analyze_grammar(self, sentence, api_key):
        prompt = self.prompt_builder.build_prompt(sentence)
        response = self.ai_service.call_ai(prompt, api_key)  # Orchestration
```

### Migration Path - From Old to Gold Standard

#### Phase 1: Study Gold Standards
1. Read Hindi analyzer implementation
2. Read Chinese Simplified analyzer implementation
3. Identify facade pattern usage
4. Note natural validation patterns

#### Phase 2: Component Migration
1. Extract config to separate component
2. Extract prompt building to separate component
3. Extract response parsing to separate component
4. Extract validation to separate component (remove artificial boosting)

#### Phase 3: Facade Implementation
1. Create main analyzer facade
2. Implement component orchestration
3. Add error handling and fallbacks
4. Test complete workflow

#### Phase 4: Testing Migration
1. Update unit tests to match gold standard patterns
2. Remove confidence boosting tests
3. Add natural validation tests
4. Update integration tests

### Performance Considerations - Gold Standard Optimizations

#### Caching Strategy - LIKE GOLD STANDARDS
- Prompt caching in PromptBuilder
- Config caching in ConfigLoader
- Response caching for repeated analyses

#### Batch Processing - LIKE GOLD STANDARDS
- Batch prompt building for multiple sentences
- Batch AI calls for efficiency
- Batch validation for consistency

#### Memory Management
- Stream processing for large datasets
- Lazy loading of configurations
- Garbage collection hints for long-running processes

### Monitoring and Observability

#### Logging Strategy
```python
# Structured logging like gold standards
logger.info("Analysis completed", extra={
    "language": language_code,
    "sentence_length": len(sentence),
    "confidence": result["confidence"],  # NATURAL confidence
    "processing_time": processing_time
})
```

#### Metrics Collection
- Analysis success/failure rates
- Processing time distributions
- Confidence score distributions (natural ranges)
- AI API call success rates

#### Health Checks
- Component initialization status
- AI service availability
- Configuration loading status
- Cache hit/miss ratios

### Security Considerations

#### API Key Management
- Secure key storage (environment variables, key vaults)
- Key rotation strategies
- Access logging (without exposing keys)

#### Input Validation
- Sentence length limits
- Content filtering for malicious input
- Rate limiting for API protection

#### Output Sanitization
- HTML escaping for web output
- Content filtering for sensitive information
- Size limits for response data

### Deployment and Operations

#### Configuration Management
- Environment-specific configs
- Feature flags for gradual rollouts
- Configuration validation at startup

#### Scaling Strategies
- Horizontal scaling for multiple languages
- Load balancing for AI API calls
- Caching layers for performance

#### Backup and Recovery
- Configuration backups
- Analysis result caching for recovery
- Graceful degradation on failures

---

**Remember:** Always study the gold standard implementations ([Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py)) before implementing new analyzers. Follow their patterns exactly - no artificial confidence boosting, clean facade orchestration, natural validation scoring.
    def get_prompt_template(self) -> str: pass
    def get_validation_rules(self) -> Dict: pass

class BeginnerStrategy(ComplexityStrategy):
    def get_prompt_template(self) -> str:
        return "Simple analysis focusing on basic roles..."

class AdvancedStrategy(ComplexityStrategy):
    def get_prompt_template(self) -> str:
        return "Complex analysis including nuanced features..."
```

### 3. Template Method Pattern
**Purpose:** Define algorithm skeleton with customizable steps
```python
class BaseAnalyzer:
    def analyze_grammar(self, sentence, target_word, complexity, api_key):
        """Template method defining the algorithm"""
        prompt = self.get_grammar_prompt(complexity, sentence, target_word)
        ai_response = self._call_ai(prompt, api_key)
        parsed = self.parse_grammar_response(ai_response, complexity, sentence)
        validated = self.validate_analysis(parsed, sentence)
        return self._generate_output(validated)

    # Abstract methods for subclasses to implement
    def get_grammar_prompt(self, complexity, sentence, target_word): pass
    def parse_grammar_response(self, ai_response, complexity, sentence): pass
    def validate_analysis(self, parsed_data, sentence): pass
```

### 4. Builder Pattern
**Purpose:** Construct complex objects step by step
```python
class GrammarAnalysisBuilder:
    def __init__(self):
        self.analysis = GrammarAnalysis()

    def with_sentence(self, sentence):
        self.analysis.sentence = sentence
        return self

    def with_target_word(self, target_word):
        self.analysis.target_word = target_word
        return self

    def with_elements(self, elements):
        self.analysis.grammatical_elements = elements
        return self

    def build(self):
        return self.analysis
```

## ðŸ§© Component Interactions

### Data Flow Architecture
```
Input Sentence
    â†“
Prompt Builder â†’ AI Prompt
    â†“
AI API Call â†’ AI Response
    â†“
Response Parser â†’ Structured Data
    â†“
Validator â†’ Quality Assessed Data
    â†“
Output Generator â†’ HTML + Metadata
```

### Error Handling Strategy
```python
class ErrorHandlingStrategy:
    """
    Comprehensive error handling with multiple recovery levels
    """

    def handle_error(self, error: Exception, context: Dict) -> Dict:
        """Multi-level error recovery"""

        # Level 1: Retry with different model
        if isinstance(error, APIError):
            return self._retry_with_fallback_model(context)

        # Level 2: Use cached results
        if isinstance(error, TimeoutError):
            return self._try_cached_result(context)

        # Level 3: Generate fallback analysis
        if isinstance(error, ParseError):
            return self._create_fallback_analysis(context)

        # Level 4: Return error with metadata
        return self._create_error_response(error, context)
```

## ðŸ”§ Implementation Guidelines

### 1. Component Isolation
**Rule:** Components should be independently testable
```python
# âœ… Good: Testable in isolation
def test_prompt_builder():
    config = MockConfig()
    builder = PromptBuilder(config)
    prompt = builder.build_single_prompt("Hello world", "world", "beginner")
    assert "Hello world" in prompt

# âŒ Bad: Coupled components
def test_analyzer_with_real_api():
    analyzer = LanguageAnalyzer()
    result = analyzer.analyze_grammar("Hello", "world", "beginner", REAL_API_KEY)
    # Depends on external API, slow, unreliable
```

### 2. Dependency Injection
**Rule:** Inject dependencies, don't create them
```python
# âœ… Good: Injectable dependencies
class LanguageAnalyzer:
    def __init__(self, config=None, prompt_builder=None, parser=None, validator=None):
        self.config = config or LanguageConfig()
        self.prompt_builder = prompt_builder or PromptBuilder(self.config)
        # ...

# âŒ Bad: Hard-coded dependencies
class LanguageAnalyzer:
    def __init__(self):
        self.config = LanguageConfig()  # Can't mock or replace
        self.prompt_builder = PromptBuilder(self.config)
```

### 3. Interface Segregation
**Rule:** Clients depend only on methods they use
```python
# âœ… Good: Focused interfaces
class PromptBuilderInterface:
    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str: pass
    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str: pass

class ValidatorInterface:
    def validate_result(self, result: Dict, sentence: str) -> Dict: pass
    def calculate_confidence(self, result: Dict, sentence: str) -> float: pass

# âŒ Bad: Monolithic interface
class LanguageProcessorInterface:
    def build_prompt(self, *args, **kwargs) -> str: pass
    def parse_response(self, *args, **kwargs) -> Dict: pass
    def validate_result(self, *args, **kwargs) -> Dict: pass
    def generate_html(self, *args, **kwargs) -> str: pass
    # ... 20+ methods
```

### 4. Configuration as Code
**Rule:** Use code for configuration, not external files for core logic
```python
# âœ… Good: Configuration in code
class SpanishConfig:
    grammatical_roles = {
        'sustantivo': 'noun',
        'verbo': 'verb',
        'adjetivo': 'adjective',
        # ...
    }

    color_schemes = {
        'beginner': {
            'noun': '#FFAA00',
            'verb': '#4ECDC4',
            # ...
        }
    }

# âŒ Bad: Configuration in external files
# spanish_config.yaml
# grammatical_roles:
#   sustantivo: noun
#   verbo: verb
# Leads to runtime errors, hard to debug, version control issues
```

## ðŸ§ª Testing Architecture

### Unit Testing Strategy
```python
class TestLanguageAnalyzer:
    """Test individual components in isolation"""

    def test_prompt_builder(self):
        """Test prompt generation logic"""
        builder = PromptBuilder(MockConfig())
        prompt = builder.build_single_prompt("Test", "word", "beginner")
        assert "Test" in prompt
        assert "word" in prompt

    def test_response_parser(self):
        """Test parsing logic with mock responses"""
        parser = ResponseParser(MockConfig())
        mock_response = '{"words": [{"word": "test", "role": "noun"}]}'
        result = parser.parse_response(mock_response, "beginner", "Test sentence", "test")
        assert result['words'][0]['word'] == "test"

    def test_validator(self):
        """Test validation logic"""
        validator = Validator(MockConfig())
        mock_result = {'words': [{'word': 'test', 'role': 'noun'}]}
        validated = validator.validate_result(mock_result, "Test sentence")
        assert 'confidence' in validated
```

### Integration Testing Strategy
```python
class TestLanguageAnalyzerIntegration:
    """Test component interactions"""

    def test_full_analysis_workflow(self):
        """Test complete analysis pipeline with mocks"""
        # Mock AI responses
        # Test data flow between components
        # Verify output format
        pass

    def test_error_recovery(self):
        """Test error handling and fallbacks"""
        # Simulate API failures
        # Test fallback mechanisms
        # Verify graceful degradation
        pass
```

## ðŸ“Š Quality Metrics

### Code Quality
- **Cyclomatic Complexity:** < 10 per method
- **Test Coverage:** > 80% for domain components
- **Dependency Count:** < 5 dependencies per component
- **Interface Size:** < 10 methods per interface

### Architectural Quality
- **Component Coupling:** Loose coupling between components
- **Component Cohesion:** High cohesion within components
- **Testability:** All components independently testable
- **Maintainability:** Changes isolated to single components

### Performance Quality
- **Response Time:** < 3 seconds for batch analysis
- **Memory Usage:** < 100MB per analysis
- **Error Rate:** < 5% across all operations
- **Cache Hit Rate:** > 70% for repeated analyses

## ðŸš¨ Common Architectural Mistakes

### 1. God Classes
**Problem:** Single class doing too many things
```python
# âŒ Bad: Everything in one class
class LanguageAnalyzer:
    def __init__(self): pass
    def build_prompt(self): pass      # Should be in PromptBuilder
    def parse_response(self): pass    # Should be in ResponseParser
    def validate_result(self): pass   # Should be in Validator
    def generate_html(self): pass     # Should be in OutputGenerator
    def call_api(self): pass          # Should be in infrastructure
```

### 2. Tight Coupling
**Problem:** Components depend on concrete implementations
```python
# âŒ Bad: Tight coupling
class Analyzer:
    def __init__(self):
        self.parser = JsonResponseParser()  # Can't change easily

# âœ… Good: Loose coupling
class Analyzer:
    def __init__(self, parser: ResponseParserInterface):
        self.parser = parser  # Can inject any implementation
```

### 3. Mixed Concerns
**Problem:** Business logic mixed with infrastructure
```python
# âŒ Bad: Mixed concerns
class PromptBuilder:
    def build_prompt(self, sentence):
        # Business logic
        prompt = f"Analyze: {sentence}"

        # Infrastructure concern âŒ
        api_key = os.getenv('API_KEY')
        response = requests.post('https://api.example.com', json={'prompt': prompt})

        return response.json()
```

### 4. Configuration in Code
**Problem:** Hard-coded values scattered throughout
```python
# âŒ Bad: Magic numbers everywhere
class Analyzer:
    def __init__(self):
        self.max_tokens = 4000  # Magic number
        self.timeout = 30       # Magic number
        self.colors = {         # Magic values
            'noun': '#FFAA00',
            'verb': '#4ECDC4'
        }
```

## ðŸŽ¯ Implementation Levels

### Level 1: Basic Architecture
- Simple component structure
- Basic separation of concerns
- Minimal testing
- Suitable for simple languages

### Level 2: Intermediate Architecture
- Full domain-driven design
- Comprehensive testing
- Error handling and fallbacks
- Suitable for complex languages

### Level 3: Advanced Architecture
- Microservices integration
- Advanced caching and optimization
- Enterprise monitoring
- Production-ready deployment

---

**Remember:** Always study the gold standard implementations ([Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/chinese_simplified/zh_analyzer.py)) before implementing new analyzers. Follow their patterns exactly - no artificial confidence boosting, clean facade orchestration, natural validation scoring.
