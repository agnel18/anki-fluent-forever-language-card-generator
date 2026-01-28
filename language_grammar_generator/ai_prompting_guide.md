# AI Prompting Guide
## AI Integration Following Gold Standard Patterns

**Primary Gold Standard:** [Chinese Simplified](languages/zh/zh_analyzer.py) - Jinja2 templates, external configuration  
**Secondary Reference:** [Hindi](languages/hindi/hi_analyzer.py)  
**Critical:** Use Chinese Simplified Clean Architecture patterns - Jinja2 templates, external config, no artificial confidence boosting  
**Prerequisites:** Study Chinese Simplified template system before AI integration  
**Models:** Strictly limited to `gemini-2.5-flash` and `gemini-3-flash-preview` (like Chinese Simplified)  
**Time Estimate:** 2-3 weeks for gold standard compliant optimization

## 🎯 AI Integration Philosophy - Chinese Simplified Gold Standard Compliance

### Model Selection Strategy - Match Chinese Simplified
- **gemini-2.5-flash:** Complex linguistic analysis (like Chinese Simplified analyzer)
- **gemini-3-flash-preview:** Simple analysis, high-volume processing
- **No other models allowed** - strict enforcement like Chinese Simplified
- **Circuit Breaker:** Implement like Chinese Simplified for reliability

### Prompt Engineering Principles - Chinese Simplified Patterns
- **Jinja2 Templates:** Template-based prompt generation (Chinese Simplified pattern)
- **External Configuration:** Load prompt templates from YAML files (Chinese Simplified pattern)
- **Natural Confidence:** No artificial boosting - use natural AI confidence scores
- **Clean Architecture:** AI calls orchestrated through domain components
- **Integrated Fallbacks:** Fallback mechanisms within domain layer (Chinese Simplified pattern)

### Quality Assurance - Natural Validation Only
- **Natural Confidence Scoring:** Use AI-provided confidence without manipulation
- **Fallback Mechanisms:** Graceful degradation like Chinese Simplified
- **Validation Loops:** Cross-check with linguistic rules (no artificial boosting)
- **Performance Monitoring:** Track natural confidence distributions

## 📝 Prompt Template Architecture - Chinese Simplified Gold Standard Structure

### 1. Base Prompt Structure - Like Chinese Simplified

**File:** `languages/{language}/{language}_prompt_builder.py` (like zh_prompt_builder.py)
```python
from typing import Dict, Any
from jinja2 import Template

class {Language}PromptBuilder:
    """Prompt builder following Chinese Simplified Clean Architecture patterns"""

    def __init__(self, config: {Language}Config):
        self.config = config
        self.templates = self._load_templates_from_config()  # Like Chinese Simplified

    def _load_templates_from_config(self) -> Dict[str, Template]:
        """Load templates from external config - LIKE CHINESE SIMPLIFIED"""
        # Load from YAML files like Chinese Simplified config
        config_templates = self.config.prompt_templates

        return {
            'single_analysis': Template(config_templates['single']),
            'batch_analysis': Template(config_templates['batch']),
            'complexity_specific': Template(config_templates.get('complexity', '')),
        }

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build single analysis prompt - LIKE GOLD STANDARD METHOD"""
        context = {
            'sentence': sentence,
            'target_word': target_word,
            'complexity': complexity,
            'language_name': self.config.language_name,
            'grammatical_roles': self.config.grammatical_roles,  # From external config
        }

        return self.templates['single_analysis'].render(**context)

    def build_batch_prompt(self, sentences: List[Dict], complexity: str) -> str:
        """Build batch prompt - LIKE GOLD STANDARD BATCH METHOD"""
        # Batch processing like Hindi/Chinese analyzers
        formatted_sentences = []
        for item in sentences:
            formatted_sentences.append(f"Sentence: {item['sentence']}")
            formatted_sentences.append(f"Target: {item['target_word']}")

        context = {
            'sentences': '\n'.join(formatted_sentences),
            'complexity': complexity,
            'batch_size': len(sentences),
        }

        return self.templates['batch_analysis'].render(**context)
```

### 2. AI Service Integration - Like Gold Standards

**File:** `languages/{language}/ai_service.py` (separate from domain like gold standards)
```python
class AIService:
    """AI service following gold standard patterns - LIKE HINDI/CHINESE AI INTEGRATION"""

    ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]  # STRICT like gold standards

    def __init__(self):
        self.circuit_breaker = CircuitBreaker()  # Like gold standards

    def call_ai(self, prompt: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
        """Call AI with gold standard error handling"""
        if model not in self.ALLOWED_MODELS:
            raise ValueError(f"Model {model} not allowed. Use: {self.ALLOWED_MODELS}")

        # Circuit breaker pattern like gold standards
        with self.circuit_breaker:
            try:
                # AI call with retry logic like gold standards
                response = self._make_ai_call(prompt, api_key, model)

                # Validate response like gold standards
                self._validate_response(response)

                return response

            except Exception as e:
                # Fallback like gold standards
                logger.error(f"AI call failed: {e}")
                raise AIServiceError(f"AI service error: {e}")
```

### 3. Response Parser - Like Gold Standards

**File:** `languages/{language}/{language}_response_parser.py` (like hi_response_parser.py/zh_response_parser.py)
```python
class {Language}ResponseParser:
    """Response parser following gold standard patterns - LIKE HINDI/CHINESE PARSERS"""

    def __init__(self, config: {Language}Config):
        self.config = config

    def parse_response(self, ai_response: str, sentence: str, target_word: str) -> Dict:
        """Parse AI response - LIKE GOLD STANDARD PARSING"""
        try:
            # Parse JSON like gold standards
            data = json.loads(ai_response)

            # Normalize structure like gold standards
            normalized = self._normalize_response(data, sentence, target_word)

            # Language-specific processing like Hindi/Chinese
            processed = self._apply_language_specific_processing(normalized)

            return processed

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback parsing like gold standards
            return self._create_fallback_response(sentence, target_word)

    def _normalize_response(self, data: Dict, sentence: str, target_word: str) -> Dict:
        """Normalize to standard structure - LIKE GOLD STANDARD NORMALIZATION"""
        return {
            "sentence": sentence,
            "target_word": target_word,
            "analysis": data.get("analysis", {}),
            "confidence": data.get("confidence", 0.5),  # NATURAL confidence like gold standards
            "metadata": data.get("metadata", {}),
            "processing_timestamp": datetime.now().isoformat(),
        }
```

### 4. Validator - NATURAL VALIDATION ONLY

**File:** `languages/{language}/{language}_validator.py` (like gold standard validators)
```python
class {Language}Validator:
    """Validator with NATURAL confidence scoring - LIKE GOLD STANDARDS (NO ARTIFICIAL BOOSTING)"""

    def __init__(self, config: {Language}Config):
        self.config = config

    def validate_result(self, result: Dict, sentence: str) -> Dict:
        """Validate with NATURAL confidence - LIKE GOLD STANDARDS"""
        # Basic quality checks like gold standards
        checks = {
            "has_analysis": bool(result.get("analysis")),
            "sentence_matches": result.get("sentence") == sentence,
            "target_word_present": result.get("target_word") in sentence,
            "confidence_reasonable": 0 <= result.get("confidence", 0) <= 1,
        }

        # Calculate NATURAL confidence (NO artificial boosting like gold standards)
        natural_confidence = self._calculate_natural_confidence(result, checks)

        return {
            **result,
            "validation_checks": checks,
            "final_confidence": natural_confidence,  # NATURAL score only
            "validated_at": datetime.now().isoformat(),
        }

    def _calculate_natural_confidence(self, result: Dict, checks: Dict) -> float:
        """Natural confidence calculation - LIKE GOLD STANDARDS"""
        # Simple weighted scoring like Hindi/Chinese
        base_score = 0.5

        if checks["has_analysis"]:
            base_score += 0.3
        if checks["sentence_matches"]:
            base_score += 0.15
        if checks["target_word_present"]:
            base_score += 0.15

        return min(base_score, 1.0)  # NATURAL scoring, no artificial boost
```

## 🔧 Implementation Steps - Gold Standard Compliance

### Phase 1: Study Gold Standards Thoroughly
1. **Read Hindi Analyzer:** Study `hi_analyzer.py`, `hi_prompt_builder.py`, `hi_response_parser.py`
2. **Read Chinese Simplified:** Study `zh_analyzer.py`, `zh_prompt_builder.py`, `zh_response_parser.py`
3. **Identify Patterns:** Note facade orchestration, natural validation, external configs
4. **Document Differences:** Understand why they work and others don't

### Phase 2: Implement AI Components Like Gold Standards
1. **Create Prompt Builder:** Copy structure from gold standards
2. **Create Response Parser:** Copy parsing logic from gold standards
3. **Create Validator:** Implement NATURAL validation like gold standards (NO boosting)
4. **Create AI Service:** Implement circuit breaker like gold standards

### Phase 3: Integrate with Facade Pattern
1. **Update Main Analyzer:** Add AI service injection like gold standards
2. **Orchestrate Components:** Follow gold standard workflow
3. **Add Error Handling:** Implement fallbacks like gold standards
4. **Test Integration:** Verify component orchestration works

### Phase 4: Optimize and Validate
1. **Performance Testing:** Benchmark against gold standards
2. **Quality Validation:** Ensure natural confidence scoring
3. **Error Recovery:** Test fallback mechanisms
4. **Production Readiness:** Verify gold standard compliance

## 📊 Quality Metrics - Gold Standard Benchmarks

### AI Response Quality - Compare with Gold Standards
```python
# Quality metrics matching gold standards
def measure_ai_quality():
    test_cases = load_gold_standard_test_cases()  # From Hindi/Chinese tests

    results = []
    for test_case in test_cases:
        result = analyze_with_gold_standard(test_case)

        metrics = {
            "natural_confidence": result["confidence"],  # Should be 0-1 natural range
            "parsing_success": result["validation_checks"]["has_analysis"],
            "sentence_accuracy": result["validation_checks"]["sentence_matches"],
            "no_artificial_boosting": not detect_artificial_boosting(result),  # Critical check
        }

        results.append(metrics)

    return aggregate_metrics(results)
```

### Performance Benchmarks - Against Gold Standards
```python
# Performance comparison with gold standards
def benchmark_against_gold_standards():
    gold_standard_times = benchmark_gold_standard()  # Hindi/Chinese baseline

    your_times = benchmark_your_implementation()

    return {
        "response_time_ratio": your_times["average"] / gold_standard_times["average"],
        "acceptable_performance": your_times["average"] <= gold_standard_times["average"] * 1.5,
        "memory_efficiency": your_times["memory"] <= gold_standard_times["memory"] * 1.2,
    }
```

## 🚨 Common AI Issues - Gold Standard Solutions

### Issue 1: Artificial Confidence Boosting Detected
**Symptoms:** Confidence scores manipulated beyond natural AI output
**Solution - Match Gold Standards:**
```python
# WRONG - Artificial boosting (removed from all implementations)
def bad_validate_result(self, result, sentence):
    confidence = result.get("confidence", 0.5)
    if some_condition:
        confidence = min(confidence * 1.5, 1.0)  # ARTIFICIAL BOOST - BAD
    return confidence

# CORRECT - Natural scoring like gold standards
def good_validate_result(self, result, sentence):
    checks = self._perform_quality_checks(result, sentence)
    return self._calculate_natural_confidence(checks)  # NATURAL - GOOD
```

### Issue 2: Wrong AI Model Usage
**Symptoms:** Using models other than allowed ones
**Solution - Strict Model Enforcement:**
```python
# CORRECT - Like gold standards
ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]

def call_ai(self, prompt, api_key, model):
    if model not in ALLOWED_MODELS:
        raise ValueError(f"Model {model} not allowed. Use: {ALLOWED_MODELS}")
    # Proceed with call
```

### Issue 3: Tight Coupling with AI Service
**Symptoms:** Domain logic directly calls AI APIs
**Solution - Component Separation like Gold Standards:**
```python
# WRONG - Tight coupling
class LanguageAnalyzer:
    def analyze_grammar(self, sentence, api_key):
        prompt = self._build_prompt(sentence)
        response = requests.post(AI_URL, json={"prompt": prompt})  # Direct call - BAD

# CORRECT - Separation like gold standards
class LanguageAnalyzer:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service or AIService()  # Injectable

    def analyze_grammar(self, sentence, api_key):
        prompt = self.prompt_builder.build_prompt(sentence)
        response = self.ai_service.call_ai(prompt, api_key)  # Orchestrated
```

## 🔄 Optimization Strategies - Gold Standard Performance

### Prompt Optimization - Like Gold Standards
```python
# Prompt caching like gold standards
class CachedPromptBuilder:
    def __init__(self, config):
        self.config = config
        self.cache = {}  # Cache like gold standards

    def build_single_prompt(self, sentence, target_word, complexity):
        cache_key = (sentence, target_word, complexity)

        if cache_key in self.cache:
            return self.cache[cache_key]  # Cache hit

        prompt = self._build_prompt(sentence, target_word, complexity)
        self.cache[cache_key] = prompt
        return prompt
```

### Batch Processing - Like Gold Standards
```python
# Batch AI calls like Hindi/Chinese analyzers
def process_batch(self, sentences, api_key):
    """Batch processing like gold standards"""
    batch_prompt = self.prompt_builder.build_batch_prompt(sentences)

    # Single AI call for batch like gold standards
    batch_response = self.ai_service.call_ai(batch_prompt, api_key)

    # Parse batch results like gold standards
    results = self.response_parser.parse_batch_response(batch_response)

    return results
```

### Circuit Breaker Pattern - Like Gold Standards
```python
# Circuit breaker implementation like gold standards
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_count = 0
        self.last_failure_time = None
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    def __enter__(self):
        if self._is_open():
            raise CircuitBreakerOpen("Circuit breaker is open")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.failure_count += 1
            self.last_failure_time = time.time()
        else:
            self.failure_count = 0  # Reset on success
```

## 📋 AI Integration Checklist - Gold Standard Compliance

### Pre-Implementation
- [ ] **Gold Standard Study:** Thoroughly studied Hindi and Chinese Simplified AI integration?
- [ ] **Natural Validation:** Understood natural confidence scoring (no artificial boosting)?
- [ ] **Model Restrictions:** Committed to using only gemini-2.5-flash and gemini-3-flash-preview?
- [ ] **Component Separation:** Ready to separate AI service from domain logic?

### Implementation
- [ ] **Prompt Builder:** Created following gold standard structure?
- [ ] **Response Parser:** Implemented JSON parsing like gold standards?
- [ ] **Validator:** NATURAL confidence scoring only (no artificial boosting)?
- [ ] **AI Service:** Circuit breaker and error handling like gold standards?
- [ ] **Facade Integration:** AI calls orchestrated through facade pattern?

### Testing
- [ ] **Model Compliance:** Tests verify only allowed models used?
- [ ] **Natural Confidence:** Tests confirm no artificial boosting?
- [ ] **Error Handling:** Tests verify fallback mechanisms work?
- [ ] **Performance:** Benchmarks meet gold standard performance?

### Production
- [ ] **Circuit Breaker:** Active in production environment?
- [ ] **Monitoring:** AI service metrics collected?
- [ ] **Fallbacks:** Error recovery mechanisms tested?
- [ ] **Compliance:** Continuous validation against gold standards?

---

**Remember:** Always follow the gold standard AI integration patterns from [Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py). They represent the proven working approaches - natural confidence scoring, clean component separation, strict model restrictions.
            'validation_prompt': Template(self._get_validation_template()),
            'error_recovery': Template(self._get_error_recovery_template())
        }

    def _get_single_analysis_template(self) -> str:
        """Template for single sentence analysis"""
        return """
You are a linguistic expert analyzing {{language_name}} ({{native_name}}) grammar.

CONTEXT:
- Language Family: {{language_family}}
- Script: {{script_type}} ({{script_direction}} direction)
- Complexity Level: {{complexity}}

TASK: Analyze the grammatical structure of this sentence:
"{{sentence}}"{% if target_word %}
Target word: "{{target_word}}"{% endif %}

GRAMMATICAL CATEGORIES ({{complexity}} level):
{{grammatical_roles}}

OUTPUT FORMAT:
{
  "words": [
    {
      "word": "exact_word_from_sentence",
      "grammatical_role": "role_from_list",
      "meaning": "brief_explanation_in_English"
    }
  ],
  "explanations": {
    "overall_structure": "sentence_structure_explanation",
    "key_features": "important_grammatical_features"
  }
}

REQUIREMENTS:
1. Use ONLY words that appear in the sentence
2. Choose roles ONLY from the provided list
3. Provide clear, concise explanations
4. Maintain accurate word order
5. Be linguistically precise

Analyze the sentence now:"""

    def _get_batch_analysis_template(self) -> str:
        """Template for batch analysis"""
        return """
Analyze these {{count}} {{language_name}} sentences for grammatical structure:

{% for sentence in sentences %}
{{loop.index}}. "{{sentence}}"
{% endfor %}

Complexity: {{complexity}}
{{grammatical_roles}}

Return JSON format:
{
  "batch_results": [
    {
      "sentence": "exact_sentence_text",
      "words": [
        {"word": "word1", "grammatical_role": "role", "meaning": "explanation"}
      ],
      "explanations": {
        "overall_structure": "structure_explanation",
        "key_features": "key_features"
      }
    }
  ]
}

Analyze all sentences:"""

    def _get_complexity_template(self) -> str:
        """Complexity-specific template adjustments"""
        return """
{% if complexity == 'beginner' %}
Focus on basic grammatical roles: nouns, verbs, adjectives, adverbs, pronouns, prepositions, conjunctions.
Keep explanations simple and clear.
{% elif complexity == 'intermediate' %}
Include intermediate roles: {{intermediate_roles}}
Explain relationships between words.
{% else %}
Include all roles: {{advanced_roles}}
Provide detailed linguistic analysis including morphological features and syntactic relationships.
{% endif %}
"""

    def _get_validation_template(self) -> str:
        """Template for validating analysis results"""
        return """
Validate this grammatical analysis for {{language_name}}:

Sentence: "{{sentence}}"
Analysis: {{analysis_json}}

Check for:
1. Word alignment with sentence
2. Appropriate grammatical roles
3. Linguistic accuracy
4. Completeness of analysis

Return validation score (0.0-1.0) and issues found."""

    def _get_error_recovery_template(self) -> str:
        """Template for error recovery"""
        return """
The previous analysis failed. Provide a basic grammatical breakdown:

Sentence: "{{sentence}}"
{{grammatical_roles}}

Return simple analysis in the same JSON format, even if less detailed."""
```

### 2. Dynamic Prompt Generation

**File:** `domain/{language}_prompt_builder.py` (enhanced)
```python
import logging
from typing import Dict, List, Any, Optional
from .zh_prompt_builder import ZhPromptBuilder
from .language_prompt_templates import {Language}PromptTemplates

logger = logging.getLogger(__name__)

class {Language}PromptBuilder(ZhPromptBuilder):
    """Advanced prompt builder with optimization strategies"""

    def __init__(self, config: {Language}Config):
        super().__init__(config)
        self.templates = {Language}PromptTemplates(config)
        self.prompt_cache = {}  # Cache for similar prompts
        self.performance_metrics = {
            'total_prompts': 0,
            'cache_hits': 0,
            'average_tokens': 0
        }

    def build_optimized_prompt(self, sentence: str, target_word: str,
                              complexity: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build optimized prompt with context awareness"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(sentence, target_word, complexity)
            if cache_key in self.prompt_cache:
                self.performance_metrics['cache_hits'] += 1
                return self.prompt_cache[cache_key]

            # Build context-aware prompt
            prompt_context = self._build_context(sentence, target_word, complexity, context)

            # Select appropriate template
            template = self._select_template(sentence, complexity)

            # Generate prompt
            prompt = template.render(**prompt_context)

            # Optimize prompt length
            prompt = self._optimize_length(prompt)

            # Cache for future use
            self.prompt_cache[cache_key] = prompt
            self.performance_metrics['total_prompts'] += 1

            return prompt

        except Exception as e:
            logger.error(f"Failed to build optimized prompt: {e}")
            return self._create_fallback_prompt(sentence, target_word, complexity)

    def _generate_cache_key(self, sentence: str, target_word: str, complexity: str) -> str:
        """Generate cache key for similar prompts"""
        # Normalize sentence for caching
        normalized = sentence.lower().strip()
        # Create hash of key components
        import hashlib
        key_components = f"{normalized}|{target_word or ''}|{complexity}"
        return hashlib.md5(key_components.encode()).hexdigest()

    def _build_context(self, sentence: str, target_word: str, complexity: str,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build rich context for prompt generation"""
        base_context = {
            'sentence': sentence,
            'target_word': target_word or '',
            'complexity': complexity,
            'language_name': self.config.language_name,
            'native_name': self.config.native_name,
            'language_family': self.config.language_family,
            'script_type': self.config.script_type,
            'script_direction': self.config.script_direction,
            'grammatical_roles': self._format_roles_for_complexity(complexity),
            'sentence_length': len(sentence),
            'word_count': len(sentence.split()),
        }

        # Add complexity-specific context
        if complexity == 'beginner':
            base_context.update({
                'focus_areas': ['basic_word_classes', 'word_order', 'simple_relations'],
                'explanation_style': 'simple_clear',
                'max_roles': 7
            })
        elif complexity == 'intermediate':
            base_context.update({
                'focus_areas': ['grammatical_relations', 'morphology', 'syntax'],
                'explanation_style': 'detailed_but_accessible',
                'max_roles': 12
            })
        else:  # advanced
            base_context.update({
                'focus_areas': ['deep_syntax', 'morphology', 'discourse_features'],
                'explanation_style': 'linguistically_rigorous',
                'max_roles': 20
            })

        # Add external context if provided
        if context:
            base_context.update(context)

        return base_context

    def _select_template(self, sentence: str, complexity: str) -> Template:
        """Select appropriate template based on sentence characteristics"""
        # For very short sentences, use simplified template
        if len(sentence.split()) <= 3:
            return self.templates.templates['single_analysis']  # Could have simplified version

        # For complex sentences, use detailed template
        if complexity == 'advanced' or len(sentence) > 200:
            return self.templates.templates['complexity_specific']

        # Default to single analysis
        return self.templates.templates['single_analysis']

    def _format_roles_for_complexity(self, complexity: str) -> str:
        """Format grammatical roles list based on complexity"""
        roles = self.config.grammatical_roles

        if complexity == 'beginner':
            basic_roles = ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction']
            role_list = [k for k, v in roles.items() if v in basic_roles]
        elif complexity == 'intermediate':
            intermediate_roles = basic_roles + ['aspect_marker', 'classifier', 'modal_particle']
            role_list = [k for k, v in roles.items() if v in intermediate_roles]
        else:  # advanced
            role_list = list(roles.keys())

        return '\n'.join(f'- {role}' for role in role_list)

    def _optimize_length(self, prompt: str) -> str:
        """Optimize prompt length while maintaining quality"""
        # Track token usage (rough estimate)
        estimated_tokens = len(prompt.split()) * 1.3  # Rough token estimation

        # If too long, trim non-essential parts
        if estimated_tokens > 3000:  # Leave buffer for response
            logger.warning(f"Prompt too long ({estimated_tokens:.0f} tokens), optimizing")

            # Remove detailed instructions if needed
            # This is a simplified optimization - could be more sophisticated

        self.performance_metrics['average_tokens'] = (
            (self.performance_metrics['average_tokens'] * (self.performance_metrics['total_prompts'] - 1)) +
            estimated_tokens
        ) / self.performance_metrics['total_prompts']

        return prompt

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get prompt building performance metrics"""
        return {
            **self.performance_metrics,
            'cache_hit_rate': self.performance_metrics['cache_hits'] / max(self.performance_metrics['total_prompts'], 1),
            'cache_size': len(self.prompt_cache)
        }
```

## 🤖 Model Selection and Optimization

### 1. Model Router

**File:** `infrastructure/{language}_model_router.py`
```python
import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class GeminiModel(Enum):
    """Allowed Gemini models only"""
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"

class {Language}ModelRouter:
    """Routes requests to appropriate Gemini models"""

    def __init__(self, config: {Language}Config):
        self.config = config
        self.model_performance = {
            model.value: {'success_rate': 1.0, 'avg_response_time': 1.0, 'quality_score': 1.0}
            for model in GeminiModel
        }

    def select_model(self, sentence: str, complexity: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Select optimal model for the request"""
        # Complexity-based selection
        if complexity == 'advanced':
            # Advanced analysis needs more capable model
            return GeminiModel.GEMINI_2_5_FLASH.value
        elif len(sentence) > 100 or complexity == 'intermediate':
            # Medium complexity or longer sentences
            return GeminiModel.GEMINI_2_5_FLASH.value
        else:
            # Simple analysis can use faster model
            return GeminiModel.GEMINI_3_FLASH_PREVIEW.value

    def update_performance(self, model: str, success: bool, response_time: float, quality_score: float):
        """Update model performance metrics"""
        if model not in self.model_performance:
            return

        perf = self.model_performance[model]

        # Exponential moving average for metrics
        alpha = 0.1  # Learning rate

        perf['success_rate'] = alpha * (1.0 if success else 0.0) + (1 - alpha) * perf['success_rate']
        perf['avg_response_time'] = alpha * response_time + (1 - alpha) * perf['avg_response_time']
        perf['quality_score'] = alpha * quality_score + (1 - alpha) * perf['quality_score']

    def get_model_stats(self) -> Dict[str, Any]:
        """Get current model performance statistics"""
        return self.model_performance.copy()
```

### 2. AI Service Layer

**File:** `infrastructure/{language}_ai_service.py`
```python
import logging
import time
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from .language_model_router import {Language}ModelRouter, GeminiModel

logger = logging.getLogger(__name__)

class {Language}AIService:
    """AI service layer with optimization and error handling"""

    def __init__(self, config: {Language}Config):
        self.config = config
        self.model_router = {Language}ModelRouter(config)
        self.client = None
        self.request_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }

    def initialize_client(self, api_key: str):
        """Initialize Gemini client"""
        try:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(GeminiModel.GEMINI_2_5_FLASH.value)
            logger.info("AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise

    def analyze_with_ai(self, prompt: str, complexity: str, sentence: str,
                       target_word: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform AI analysis with optimization and error handling"""
        start_time = time.time()

        try:
            # Select model
            model_name = self.model_router.select_model(sentence, complexity, context)

            # Create model instance
            model = genai.GenerativeModel(model_name)

            # Configure generation parameters
            generation_config = self._get_generation_config(complexity)

            # Make request
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            response_time = time.time() - start_time

            # Parse response
            result = self._parse_ai_response(response.text)

            # Validate result quality
            quality_score = self._assess_result_quality(result, sentence)

            # Update metrics
            self._update_metrics(True, response_time, quality_score)
            self.model_router.update_performance(model_name, True, response_time, quality_score)

            logger.info(f"AI analysis completed in {response_time:.2f}s with quality {quality_score:.2f}")
            return result

        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(False, response_time, 0.0)

            logger.error(f"AI analysis failed: {e}")
            raise

    def _get_generation_config(self, complexity: str) -> Dict[str, Any]:
        """Get generation configuration based on complexity"""
        base_config = {
            "temperature": 0.1,  # Low temperature for consistent analysis
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # Adjust for complexity
        if complexity == 'advanced':
            base_config.update({
                "temperature": 0.2,  # Slightly higher for complex analysis
                "max_output_tokens": 4096,  # More tokens for detailed analysis
            })
        elif complexity == 'beginner':
            base_config.update({
                "temperature": 0.05,  # Very low for simple, consistent results
                "max_output_tokens": 1024,
            })

        return base_config

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response with robust error handling"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response_text[json_start:json_end]
            return json.loads(json_str)

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")

            # Attempt to extract partial JSON
            return self._extract_partial_json(response_text)

    def _extract_partial_json(self, response_text: str) -> Dict[str, Any]:
        """Extract partial JSON when full parsing fails"""
        # This is a fallback - in practice, you'd want more sophisticated parsing
        return {
            "words": [],
            "explanations": {
                "overall_structure": "Analysis failed - using fallback",
                "key_features": "Unable to parse AI response"
            },
            "parsing_error": True
        }

    def _assess_result_quality(self, result: Dict[str, Any], sentence: str) -> float:
        """Assess quality of AI result"""
        score = 1.0

        # Check basic structure
        if 'words' not in result:
            return 0.0

        words = result.get('words', [])
        sentence_words = sentence.split()

        # Word count alignment
        if len(words) == 0:
            return 0.0

        word_ratio = len(words) / len(sentence_words)
        if word_ratio < 0.5 or word_ratio > 2.0:
            score *= 0.7

        # Check explanations
        explanations = result.get('explanations', {})
        if not explanations.get('overall_structure'):
            score *= 0.8

        return score

    def _update_metrics(self, success: bool, response_time: float, quality_score: float):
        """Update service metrics"""
        self.request_metrics['total_requests'] += 1

        if success:
            self.request_metrics['successful_requests'] += 1
        else:
            self.request_metrics['failed_requests'] += 1

        # Update average response time
        total_requests = self.request_metrics['total_requests']
        current_avg = self.request_metrics['average_response_time']
        self.request_metrics['average_response_time'] = (
            (current_avg * (total_requests - 1)) + response_time
        ) / total_requests

    def get_service_metrics(self) -> Dict[str, Any]:
        """Get current service performance metrics"""
        metrics = self.request_metrics.copy()
        metrics['success_rate'] = (
            metrics['successful_requests'] / max(metrics['total_requests'], 1)
        )
        return metrics
```

## 🔄 Response Processing and Validation

### 1. Advanced Response Parser

**File:** `domain/{language}_response_parser.py` (enhanced)
```python
import logging
import json
import re
from typing import Dict, Any, List, Optional
from .zh_response_parser import ZhResponseParser

logger = logging.getLogger(__name__)

class {Language}ResponseParser(ZhResponseParser):
    """Advanced response parser with validation and normalization"""

    def __init__(self, config: {Language}Config):
        super().__init__(config)
        self.parsing_stats = {
            'total_parsed': 0,
            'successful_parses': 0,
            'fallback_used': 0,
            'parsing_errors': []
        }

    def parse_response(self, ai_response: str, complexity: str, sentence: str,
                      target_word: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse AI response with advanced validation"""
        self.parsing_stats['total_parsed'] += 1

        try:
            # Multiple parsing strategies
            result = self._parse_with_fallbacks(ai_response)

            if not result:
                raise ValueError("All parsing strategies failed")

            # Validate and enhance result
            validated_result = self._validate_and_enhance(result, sentence, complexity)

            # Apply language-specific transformations
            normalized_result = self._apply_language_transformations(validated_result, complexity)

            self.parsing_stats['successful_parses'] += 1
            return normalized_result

        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            self.parsing_stats['parsing_errors'].append(str(e))
            self.parsing_stats['fallback_used'] += 1

            return self._create_enhanced_fallback(sentence, complexity, target_word)

    def _parse_with_fallbacks(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Try multiple parsing strategies"""
        strategies = [
            self._parse_clean_json,
            self._parse_embedded_json,
            self._parse_partial_json,
            self._parse_structured_text
        ]

        for strategy in strategies:
            try:
                result = strategy(ai_response)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Parsing strategy failed: {e}")
                continue

        return None

    def _parse_clean_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse clean JSON response"""
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return None

    def _parse_embedded_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from mixed text"""
        # Look for JSON-like structures
        json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)

        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        return None

    def _parse_partial_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse partial JSON when full parsing fails"""
        # Try to extract key components
        result = {}

        # Extract words array
        words_match = re.search(r'"words"\s*:\s*\[([^\]]*)\]', response, re.DOTALL)
        if words_match:
            # This would need more sophisticated parsing
            pass

        return result if result else None

    def _parse_structured_text(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse structured text when JSON fails"""
        # Fallback for completely unstructured responses
        # This is a last resort - try to extract basic information
        return None

    def _validate_and_enhance(self, result: Dict[str, Any], sentence: str, complexity: str) -> Dict[str, Any]:
        """Validate and enhance parsed result"""
        enhanced = result.copy()

        # Validate word alignments
        if 'words' in enhanced:
            enhanced['words'] = self._validate_word_alignments(enhanced['words'], sentence)

        # Enhance explanations
        if 'explanations' in enhanced:
            enhanced['explanations'] = self._enhance_explanations(enhanced['explanations'], sentence, complexity)

        # Add metadata
        enhanced['parsing_metadata'] = {
            'sentence_length': len(sentence),
            'word_count': len(sentence.split()),
            'complexity': complexity,
            'validation_performed': True
        }

        return enhanced

    def _validate_word_alignments(self, words: List[Dict[str, Any]], sentence: str) -> List[Dict[str, Any]]:
        """Validate and correct word alignments"""
        validated_words = []
        sentence_words = self._tokenize_sentence(sentence)

        for word_data in words:
            word = word_data.get('word', '').strip()

            # Check if word exists in sentence
            if word and word in sentence:
                validated_words.append(word_data)
            else:
                # Try fuzzy matching or skip
                logger.warning(f"Word '{word}' not found in sentence")

        return validated_words

    def _enhance_explanations(self, explanations: Dict[str, str], sentence: str, complexity: str) -> Dict[str, str]:
        """Enhance explanations with additional context"""
        enhanced = explanations.copy()

        # Add complexity-appropriate details
        if complexity == 'advanced' and 'overall_structure' in enhanced:
            # Add more technical details for advanced users
            structure = enhanced['overall_structure']
            if len(structure) < 50:  # If explanation is too brief
                enhanced['overall_structure'] = f"{structure} (Technical analysis: {self._analyze_technical_structure(sentence)})"

        return enhanced

---

**Remember:** Always follow the gold standard AI integration patterns from [Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py). They represent the proven working approaches - natural confidence scoring, clean component separation, strict model restrictions.
            ]

        return transformed

    def _normalize_word_entry(self, word_entry: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """Normalize individual word entry"""
        normalized = word_entry.copy()

        # Normalize grammatical role
        if 'grammatical_role' in normalized:
            normalized['grammatical_role'] = self._normalize_role(normalized['grammatical_role'])

        # Enhance meaning based on complexity
        if 'meaning' in normalized and complexity == 'advanced':
            normalized['meaning'] = self._enhance_meaning(normalized['meaning'], normalized['grammatical_role'])

        return normalized

    def _normalize_role(self, role: str) -> str:
        """Normalize role to standard format"""
        # Map language-specific terms to universal roles
        role_mapping = self.config.grammatical_roles
        return role_mapping.get(role.lower(), role.lower())

    def _enhance_meaning(self, meaning: str, role: str) -> str:
        """Enhance meaning with technical details for advanced users"""
        # Add technical linguistic details
        enhancements = {
            'noun': ' (nominal category, refers to entities)',
            'verb': ' (verbal category, expresses actions/states)',
            'adjective': ' (modifier category, describes qualities)',
        }

        enhancement = enhancements.get(role, '')
        return f"{meaning}{enhancement}"

    def _create_enhanced_fallback(self, sentence: str, complexity: str, target_word: str) -> Dict[str, Any]:
        """Create enhanced fallback when parsing fails"""
        words = sentence.split()
        word_entries = []

        for word in words:
            # Basic role assignment
            role = self._guess_basic_role(word)
            color = self.config.get_color_scheme(complexity).get(role, '#888888')

            word_entries.append({
                'word': word,
                'grammatical_role': role,
                'meaning': f'Basic analysis: {role}',
                'color': color
            })

        return {
            'words': word_entries,
            'explanations': {
                'overall_structure': 'Fallback analysis due to parsing failure',
                'key_features': 'Basic word classification only'
            },
            'fallback_used': True,
            'confidence': 0.3
        }

    def _guess_basic_role(self, word: str) -> str:
        """Guess basic grammatical role"""
        word_lower = word.lower()

        # Very basic heuristics
        if word_lower in ['the', 'a', 'an']:
            return 'determiner'
        elif word_lower in ['is', 'am', 'are', 'was', 'were', 'be']:
            return 'verb'
        else:
            return 'noun'  # Default assumption

    def _tokenize_sentence(self, sentence: str) -> List[str]:
        """Advanced sentence tokenization"""
        # Basic whitespace tokenization - override for complex scripts
        return sentence.split()

    def _analyze_technical_structure(self, sentence: str) -> str:
        """Provide technical structural analysis"""
        # Placeholder for advanced linguistic analysis
        return "Sentence follows standard SVO word order with modifier placement"

    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing performance statistics"""
        stats = self.parsing_stats.copy()
        total = stats['total_parsed']
        if total > 0:
            stats['success_rate'] = stats['successful_parses'] / total
            stats['fallback_rate'] = stats['fallback_used'] / total
        return stats
```

## 📊 Performance Monitoring and Optimization

### 1. AI Performance Monitor

**File:** `infrastructure/{language}_performance_monitor.py`
```python
import logging
import time
from typing import Dict, Any, List
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class {Language}PerformanceMonitor:
    """Monitor and optimize AI performance"""

    def __init__(self, config: {Language}Config, window_size: int = 100):
        self.config = config
        self.window_size = window_size

        # Rolling windows for metrics
        self.response_times = deque(maxlen=window_size)
        self.quality_scores = deque(maxlen=window_size)
        self.token_counts = deque(maxlen=window_size)
        self.error_counts = deque(maxlen=window_size)

        # Performance thresholds
        self.thresholds = {
            'max_response_time': 5.0,  # seconds
            'min_quality_score': 0.7,
            'max_error_rate': 0.1,
            'target_tokens': 2000
        }

    def record_request(self, response_time: float, quality_score: float,
                      token_count: int, had_error: bool):
        """Record performance metrics for a request"""
        self.response_times.append(response_time)
        self.quality_scores.append(quality_score)
        self.token_counts.append(token_count)
        self.error_counts.append(1 if had_error else 0)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.response_times:
            return self._get_empty_metrics()

        return {
            'average_response_time': statistics.mean(self.response_times),
            'median_response_time': statistics.median(self.response_times),
            'p95_response_time': statistics.quantiles(self.response_times, n=20)[18],  # 95th percentile
            'average_quality_score': statistics.mean(self.quality_scores),
            'quality_score_std': statistics.stdev(self.quality_scores) if len(self.quality_scores) > 1 else 0,
            'average_tokens': statistics.mean(self.token_counts),
            'error_rate': sum(self.error_counts) / len(self.error_counts),
            'sample_size': len(self.response_times)
        }

    def check_thresholds(self) -> List[str]:
        """Check if performance meets thresholds"""
        alerts = []
        metrics = self.get_current_metrics()

        if metrics['average_response_time'] > self.thresholds['max_response_time']:
            alerts.append(f"Response time too high: {metrics['average_response_time']:.2f}s")

        if metrics['average_quality_score'] < self.thresholds['min_quality_score']:
            alerts.append(f"Quality score too low: {metrics['average_quality_score']:.2f}")

        if metrics['error_rate'] > self.thresholds['max_error_rate']:
            alerts.append(f"Error rate too high: {metrics['error_rate']:.2%}")

        if metrics['average_tokens'] > self.thresholds['target_tokens']:
            alerts.append(f"Token usage too high: {metrics['average_tokens']:.0f}")

        return alerts

    def get_optimization_suggestions(self) -> List[str]:
        """Provide optimization suggestions based on metrics"""
        suggestions = []
        metrics = self.get_current_metrics()

        if metrics['average_response_time'] > 3.0:
            suggestions.append("Consider using faster model (gemini-3-flash-preview) for simple analysis")

        if metrics['average_quality_score'] < 0.8:
            suggestions.append("Consider using more capable model (gemini-2.5-flash) for complex analysis")

        if metrics['error_rate'] > 0.05:
            suggestions.append("Review prompt templates and error handling")

        if metrics['average_tokens'] > 2500:
            suggestions.append("Optimize prompt length and consider prompt caching")

        return suggestions

    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'average_response_time': 0.0,
            'median_response_time': 0.0,
            'p95_response_time': 0.0,
            'average_quality_score': 0.0,
            'quality_score_std': 0.0,
            'average_tokens': 0,
            'error_rate': 0.0,
            'sample_size': 0
        }

    def reset_metrics(self):
        """Reset all performance metrics"""
        self.response_times.clear()
        self.quality_scores.clear()
        self.token_counts.clear()
        self.error_counts.clear()
```

## 🔧 Error Recovery and Circuit Breaker

### 1. Circuit Breaker Pattern

**File:** `infrastructure/{language}_circuit_breaker.py`
```python
import logging
import time
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered

class {Language}CircuitBreaker:
    """Circuit breaker for AI service reliability"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60,
                 expected_exception: Exception = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker half-open, testing service")
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._reset()
            elif self.failure_count > 0:
                self.failure_count = 0

            return result

        except self.expected_exception as e:
            self._record_failure()
            raise e

    def _record_failure(self):
        """Record a failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        logger.info("Circuit breaker reset to CLOSED")

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'time_since_last_failure': time.time() - (self.last_failure_time or time.time())
        }

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass
```

## ✅ Success Criteria

### AI Integration Quality
- [ ] **Model Compliance:** Only `gemini-2.5-flash` and `gemini-3-flash-preview` used
- [ ] **Response Time:** < 3 seconds average for simple analysis, < 5 seconds for complex
- [ ] **Quality Score:** > 0.8 average confidence score
- [ ] **Error Rate:** < 5% failure rate with proper fallbacks
- [ ] **Token Efficiency:** < 2000 tokens per request average

### Prompt Engineering
- [ ] **Template Coverage:** All complexity levels and sentence types covered
- [ ] **Context Richness:** Linguistic context provided for accurate analysis
- [ ] **Output Consistency:** JSON format reliably parsed
- [ ] **Language Specificity:** Tailored prompts for language characteristics

### Performance Optimization
- [ ] **Caching:** Similar prompts cached and reused
- [ ] **Model Selection:** Appropriate model chosen based on complexity
- [ ] **Batch Processing:** Multiple sentences processed efficiently
- [ ] **Monitoring:** Real-time performance tracking and alerts

### Reliability Features
- [ ] **Circuit Breaker:** Automatic failure detection and recovery
- [ ] **Fallback Mechanisms:** Graceful degradation on failures
- [ ] **Error Recovery:** Multiple parsing strategies
- [ ] **Validation Loops:** Result quality assurance

## 🚨 Common AI Integration Pitfalls

### 1. Model Selection Errors
**Problem:** Using wrong model for task complexity
**Prevention:** Implement automatic model routing based on complexity and sentence length

### 2. Prompt Engineering Issues
**Problem:** Unclear or ambiguous prompts leading to poor results
**Prevention:** Extensive prompt testing and iterative refinement

### 3. Token Limit Exceeded
**Problem:** Prompts too long, hitting API limits
**Prevention:** Prompt optimization and length monitoring

### 4. JSON Parsing Failures
**Problem:** AI returns malformed JSON
**Prevention:** Multiple parsing strategies and fallback mechanisms

### 5. Quality Degradation
**Problem:** Analysis quality drops over time
**Prevention:** Continuous monitoring and prompt refinement

---

**🎯 Ready to implement AI integration?** Start with basic prompt templates, then add optimization layers progressively. Remember: quality over speed - focus on accurate analysis first!

**Need help with AI integration?** Refer to the [Troubleshooting Guide](troubleshooting_guide.md) for common AI issues, or the [Testing Guide](testing_guide.md) for validation strategies.

**📊 Pro tip:** Monitor your AI performance metrics continuously and adjust prompts based on real usage patterns for optimal results.</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\ai_prompting_guide.md