# language_grammar_generator/phase2_directory_structure_prompt.py
"""
Phase 2: Directory Structure & Core Files Prompt

This prompt creates the complete directory structure and core files for a new language analyzer.
Run this after Phase 1 research is complete.

UPDATED: Incorporates production-ready architecture from French analyzer v2.0 including:
- Enhanced domain components with robust parsing and validation
- Comprehensive infrastructure layer with circuit breaker patterns
- Advanced testing framework with gold standard validation
- APKG-ready output formatting and HTML color coding
- Production monitoring and error recovery systems
"""

PHASE2_DIRECTORY_PROMPT = """
You are an expert software architect specializing in production-ready Clean Architecture implementations. Your task is to create the complete directory structure and core files for a new language analyzer, incorporating the latest proven patterns from successful implementations.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})
BASE PATH: languages/{language_folder}/

Create the complete file structure following the gold standard Clean Architecture pattern with production-ready enhancements. Generate ALL the following files:

1. ENHANCED DIRECTORY STRUCTURE:
```
languages/{language_folder}/
├── {language_code}_analyzer.py              # Main facade class with advanced error handling
├── {language_code}_grammar_concepts.md      # Comprehensive research documentation
├── domain/                                  # Business logic layer
│   ├── __init__.py
│   ├── {language_code}_config.py           # Enhanced configuration with validation
│   ├── {language_code}_prompt_builder.py   # Advanced AI prompt generation with Jinja2
│   ├── {language_code}_response_parser.py  # Robust parsing with 5 fallback strategies
│   ├── {language_code}_validator.py        # Quality validation with confidence scoring
│   └── {language_code}_fallbacks.py        # Rule-based fallback analysis
├── infrastructure/                         # External concerns layer
│   ├── __init__.py
│   ├── data/                               # Configuration files
│   │   ├── {language_code}_grammatical_roles.yaml
│   │   ├── {language_code}_word_meanings.json
│   │   └── {language_code}_color_schemes.json
│   └── {language_code}_fallbacks.py        # Infrastructure-level fallback analysis
└── tests/                                  # Comprehensive test suites
    ├── __init__.py
    ├── test_{language_code}_analyzer.py    # Unit tests with mocking
    ├── test_{language_code}_integration.py # Integration tests with API
    ├── test_{language_code}_gold_standard.py # Gold standard validation
    └── test_{language_code}_performance.py # Performance benchmarking
```

2. PRODUCTION-READY MAIN ANALYZER ({language_code}_analyzer.py):
- Clean Architecture facade pattern with comprehensive error handling
- Advanced domain component orchestration with fallback chains
- Confidence scoring and quality validation
- APKG-ready output formatting with HTML color coding
- Performance monitoring and caching
- Integration with existing analyzer registry

3. COMPREHENSIVE GRAMMAR CONCEPTS ({language_code}_grammar_concepts.md):
- Detailed language overview with production considerations
- Complete grammatical inventory with complexity hierarchies
- AI analysis requirements and confidence scoring criteria
- APKG output specifications and HTML formatting requirements
- Error patterns and fallback strategies
- Performance optimization guidelines

4. ADVANCED TEST SUITE:
- Unit tests with comprehensive mocking and edge case coverage
- Integration tests with real API calls and circuit breaker testing
- Gold standard validation against reference patterns
- Performance tests with benchmarking and memory profiling
- Error scenario testing with fallback validation

5. PRODUCTION MONITORING:
- Structured logging with performance metrics
- Error tracking and alerting integration
- API usage monitoring and rate limiting
- Cache performance and hit rate tracking

KEY PRODUCTION REQUIREMENTS:
- Include 5-level fallback parsing strategy (direct JSON → markdown → JSON repair → text → rule-based)
- Ensure 80%+ confidence scores for production deployment
- Support real-time analysis with sub-2 second response times
- Generate APKG-ready output with detailed word explanations
- Include comprehensive error handling and graceful degradation

ADAPT FOR {LANGUAGE_NAME}: Ensure all components reflect {LANGUAGE_NAME}'s specific linguistic features while maintaining compatibility with the proven French analyzer architecture.

Generate complete, runnable code for all files. Use the French analyzer as reference for structure and patterns.

CRITICAL: Adapt the analyzer structure to {LANGUAGE_NAME}'s specific linguistic requirements while maintaining Clean Architecture principles.
"""