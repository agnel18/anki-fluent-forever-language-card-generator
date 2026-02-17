# language_grammar_generator/phase6_testing_integration_prompt.py
"""
Phase 6: Testing & Integration Prompt

This prompt creates comprehensive tests and integration code for a language analyzer.
Includes unit tests, integration tests, and registry integration.
"""

# language_grammar_generator/phase6_testing_integration_prompt.py
"""
Phase 6: Testing & Integration Prompt

This prompt creates comprehensive tests and integration code for a language analyzer.
Includes unit tests, integration tests, and registry integration.

UPDATED: Incorporates comprehensive testing framework from French analyzer v2.0 including:
- Gold standard validation against reference patterns
- Performance benchmarking with memory profiling
- API integration testing with circuit breaker validation
- Confidence scoring validation and quality metrics
- Comprehensive error scenario testing
"""

PHASE6_TESTING_INTEGRATION_PROMPT = """
You are a quality assurance expert specializing in production-ready language analyzer testing. Your task is to create comprehensive tests and integration code for a language analyzer with enterprise-grade quality assurance.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})

Create the complete testing suite and integration code with production-ready validation:

1. UNIT TESTS (test_{language_code}_analyzer.py):
- Component isolation testing with comprehensive mocking
- Domain component testing (config, prompt builder, parser, validator)
- Error handling and edge case validation
- Configuration loading and validation testing
- Fallback system testing with rule-based analysis
- Confidence scoring algorithm validation
- APKG formatting compliance testing

2. INTEGRATION TESTS (test_{language_code}_integration.py):
- End-to-end analysis pipeline testing
- AI service integration with error handling testing
- Real API call validation with response parsing
- Batch processing performance and accuracy testing
- Cross-component interaction and data flow validation
- Memory usage and resource leak testing
- Error recovery and fallback chain testing

3. GOLD STANDARD VALIDATION (test_{language_code}_gold_standard.py):
- Reference sentence analysis validation
- Confidence score benchmarking against known good analyses
- Grammatical role accuracy testing
- Word explanation quality assessment
- APKG output format compliance validation
- Language-specific pattern recognition testing

4. PERFORMANCE TESTING (test_{language_code}_performance.py):
- Response time benchmarking (target: <2 seconds for single sentences)
- Memory usage profiling and optimization validation
- Concurrent request handling capacity testing
- Cache performance and hit rate validation
- Batch processing scalability testing
- Error handling performance under load

5. LANGUAGE REGISTRY INTEGRATION:
- Update streamlit_app/language_registry.py with proper LanguageConfig
- Add analyzer to analyzer_registry.py mapping
- Validate registry loading and analyzer instantiation
- Test integration with existing analyzer framework

6. SENTENCE GENERATION INTEGRATION:
- Implement get_sentence_generation_prompt() method
- Character limits validation (< 75 chars meanings, < 60 chars restrictions)
- Word count range support and topic filtering validation
- Multi-sentence batch processing integration

7. QUALITY ASSURANCE METRICS:
- Confidence score distribution analysis
- Error rate monitoring and alerting
- Performance regression detection
- Accuracy validation against gold standards
- User experience quality metrics

8. CI/CD INTEGRATION:
- Automated test execution in pipeline
- Performance regression gates
- Code coverage requirements (target: 90%+)
- Integration test environment setup
- Deployment validation testing

KEY PRODUCTION REQUIREMENTS:
- **No artificial confidence boosting** in tests or production
- **Comprehensive error scenario coverage** (network, API, parsing, validation)
- **Gold standard validation** with reference accuracy benchmarks
- **Performance benchmarking** with automated regression detection
- **Integration testing** with real API calls and circuit breaker validation
- **Quality metrics** with automated monitoring and alerting

TECHNICAL SPECIFICATIONS:
- Test coverage: Unit (90%+), Integration (95%+), E2E (100%)
- Performance targets: P95 <2s single, P95 <5s batch
- Confidence thresholds: Min 0.70, Target 0.80+, Excellent 0.85+
- Error rates: <1% for valid inputs, graceful handling for edge cases
- Memory usage: <100MB per analyzer instance

VALIDATION CRITERIA:
- All tests must pass in CI/CD pipeline
- Gold standard accuracy must meet or exceed 95%
- Performance benchmarks must be maintained
- No memory leaks or resource exhaustion
- Circuit breaker must activate and recover correctly
- Fallback systems must provide meaningful results

ADAPT FOR {LANGUAGE_NAME}: Include {LANGUAGE_NAME}-specific test cases, gold standard reference sentences, and language-specific validation patterns while maintaining compatibility with the existing testing framework.

- Proper mocking and fixtures

Generate complete test suites and integration code.

ADAPT FOR {LANGUAGE_NAME}: Include language-specific test cases that validate {LANGUAGE_NAME} unique grammatical features and analysis requirements.
"""