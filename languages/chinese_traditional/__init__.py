# languages/chinese_traditional/__init__.py
"""
Chinese Traditional Language Analyzer Package

Following Chinese Simplified Clean Architecture gold standard:
- Clean package structure with domain separation
- External configuration files for maintainability
- Type-safe interfaces and comprehensive error handling
- Integrated fallback mechanisms within domain layer

PACKAGE STRUCTURE:
├── domain/                    # Domain layer components
│   ├── zh_tw_config.py       # Configuration management
│   ├── zh_tw_prompt_builder.py # AI prompt generation
│   ├── zh_tw_response_parser.py # Response parsing with fallbacks
│   ├── zh_tw_validator.py    # Validation and confidence scoring
│   └── zh_tw_patterns.py     # Pattern matching and validation
├── infrastructure/           # Infrastructure layer
│   └── data/                 # External configuration files
│       ├── zh_tw_grammatical_roles.yaml
│       ├── zh_tw_word_meanings.json
│       ├── zh_tw_aspect_markers.yaml
│       ├── zh_tw_modal_particles.yaml
│       ├── zh_tw_structural_particles.yaml
│       ├── zh_tw_common_classifiers.yaml
│       └── zh_tw_patterns.yaml
├── tests/                    # Test suite
└── zh_tw_analyzer.py         # Main facade

USAGE:
    from languages.chinese_traditional import ZhTwAnalyzer

    analyzer = ZhTwAnalyzer()
    result = analyzer.analyze_sentence("這是一個測試句子。")

ARCHITECTURAL PRINCIPLES:
- Domain-driven design with clean separation
- External configuration for easy maintenance
- Comprehensive error handling and fallbacks
- Type safety throughout the codebase
- Chinese Traditional linguistic accuracy

DEPENDENCIES:
- PyYAML: For configuration file parsing
- Jinja2: For template-based prompt generation
- Standard library: For core functionality
"""

from .zh_tw_analyzer import ZhTwAnalyzer, AnalysisRequest, AnalysisResult, BatchAnalysisResult

__version__ = "1.0.0"
__author__ = "GitHub Copilot"
__description__ = "Chinese Traditional Grammar Analyzer following Clean Architecture"

# Export main classes
__all__ = [
    "ZhTwAnalyzer",
    "AnalysisRequest",
    "AnalysisResult",
    "BatchAnalysisResult"
]

# Package metadata
PACKAGE_INFO = {
    "name": "chinese-traditional-analyzer",
    "version": __version__,
    "language": "Chinese Traditional (Taiwan)",
    "architecture": "Clean Architecture",
    "components": [
        "ZhTwConfig",
        "ZhTwPromptBuilder",
        "ZhTwResponseParser",
        "ZhTwValidator",
        "ZhTwPatterns",
        "ZhTwAnalyzer"
    ],
    "configuration_files": [
        "zh_tw_grammatical_roles.yaml",
        "zh_tw_word_meanings.json",
        "zh_tw_aspect_markers.yaml",
        "zh_tw_modal_particles.yaml",
        "zh_tw_structural_particles.yaml",
        "zh_tw_common_classifiers.yaml",
        "zh_tw_patterns.yaml"
    ]
}