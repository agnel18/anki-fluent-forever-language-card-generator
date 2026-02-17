# language_grammar_generator/phase4_infrastructure_prompt.py
"""
Phase 4: Infrastructure Components Prompt

This prompt creates the infrastructure layer for a language analyzer.
Includes AI service integration, error recovery, and external concerns.

UPDATED: Incorporates production-ready infrastructure from French analyzer v2.0 including:
- Advanced fallback analysis with rule-based parsing
- Comprehensive error handling with structured logging
- Performance optimization with caching and monitoring
- Graceful degradation and fallback system integration
"""

PHASE4_INFRASTRUCTURE_PROMPT = """
You are a software infrastructure expert specializing in resilient, production-ready AI service integration. Your task is to create the infrastructure layer for a language analyzer with enterprise-grade reliability and monitoring.

LANGUAGE: {LANGUAGE_NAME} ({LANGUAGE_CODE})

Create the complete infrastructure layer with production-ready components:

1. ADVANCED FALLBACKS COMPONENT ({language_code}_fallbacks.py):
- Rule-based grammatical analysis using language-specific patterns
- Morphological analysis with agreement validation
- Complexity-appropriate explanation generation
- Seamless integration with response parser fallback chains
- Performance monitoring and accuracy tracking

2. CONFIGURATION DATA FILES:
- External YAML/JSON files for grammatical roles and patterns
- Word meanings dictionaries with language-specific terminology
- Color schemes and APKG formatting specifications
- Language patterns and morphological rules
- Validation rules and error detection patterns
- Service health monitoring with detailed metrics
- Graceful degradation with fallback activation
- Alerting integration for operational monitoring
- Statistical tracking of failure patterns and recovery times

4. MONITORING AND OBSERVABILITY:
- Structured logging with correlation IDs and performance metrics
- API usage tracking with cost monitoring
- Error rate monitoring with alerting thresholds
- Cache hit rate and performance monitoring
- Memory usage tracking and optimization

5. CONFIGURATION MANAGEMENT:
- Environment-specific configuration loading
- API key rotation and security management
- Circuit breaker threshold tuning
- Cache size and TTL configuration
- Rate limiting parameter adjustment

KEY PRODUCTION REQUIREMENTS:
- **Reliability**: 99.9% uptime with circuit breaker protection
- **Performance**: Sub-2 second response times for single sentences, optimized batch processing
- **Monitoring**: Comprehensive observability with alerting and metrics
- **Security**: Secure API key management and request validation
- **Scalability**: Connection pooling and resource optimization
- **Error Recovery**: Multi-level fallback chains with graceful degradation

TECHNICAL SPECIFICATIONS:
- Circuit breaker states: Closed (normal) → Open (failing) → Half-Open (testing) → Closed/Open
- Retry strategy: Exponential backoff with jitter (1s, 2s, 4s, 8s, 16s max)
- Caching: LRU cache with configurable TTL and size limits
- Monitoring: Structured JSON logging with performance histograms
- Error classification: Network, API, Parsing, Validation, Timeout errors

ADAPT FOR {LANGUAGE_NAME}: Ensure fallback patterns reflect {LANGUAGE_NAME}'s grammatical structure, common analysis scenarios, and language-specific error patterns while maintaining compatibility with the proven French analyzer infrastructure.
"""