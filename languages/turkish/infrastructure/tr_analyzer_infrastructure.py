"""
Turkish Language Analyzer Infrastructure
======================================

Infrastructure layer for Turkish language analysis.
Handles external dependencies: Google Gemini AI, file I/O, external APIs.

Following Clean Architecture principles and gold standard patterns.
"""

import json
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import google.generativeai as genai

from ..domain import (
    TurkishConfig,
    TurkishPromptBuilder,
    TurkishResponseParser,
    TurkishValidator,
    TurkishSentenceAnalysis
)


@dataclass
class AnalysisRequest:
    """Request for Turkish language analysis."""
    text: str
    complexity: str = 'beginner'
    options: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResponse:
    """Response from Turkish language analysis."""
    success: bool
    analysis: Optional[TurkishSentenceAnalysis] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TurkishAnalyzerInfrastructure:
    """Infrastructure layer for Turkish language analysis."""

    def __init__(self, config: TurkishConfig):
        self.config = config
        self.prompt_builder = TurkishPromptBuilder(config)
        self.response_parser = TurkishResponseParser(config)
        self.validator = TurkishValidator(config)

        # Initialize AI client
        self._initialize_ai_client()

        # Load external configurations
        self.external_configs = self._load_external_configs()

    def _initialize_ai_client(self) -> None:
        """Initialize Google Gemini AI client."""
        try:
            # Get API key from environment or config
            api_key = self._get_api_key()
            if not api_key:
                raise ValueError("Google AI API key not found")

            genai.configure(api_key=api_key)

            # Configure model
            self.model = genai.GenerativeModel(
                model_name=self.config.ai_model_settings['model'],
                generation_config={
                    'temperature': self.config.ai_model_settings['temperature'],
                    'max_output_tokens': self.config.ai_model_settings['max_tokens'],
                }
            )

        except Exception as e:
            raise RuntimeError(f"Failed to initialize AI client: {e}")

    def _get_api_key(self) -> Optional[str]:
        """Get Google AI API key from various sources."""
        # Try environment variable
        import os
        api_key = os.getenv('GOOGLE_AI_API_KEY')

        if api_key:
            return api_key

        # Try config file
        config_path = Path.home() / '.google_ai_config'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key')
            except:
                pass

        # Try application config
        return None

    def _load_external_configs(self) -> Dict[str, Any]:
        """Load external configuration files."""
        configs = {}

        for config_type, filename in self.config.config_files.items():
            config_path = self.config.get_config_file_path(config_type)
            if config_path and config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if filename.endswith('.yaml'):
                            import yaml
                            configs[config_type] = yaml.safe_load(f)
                        else:
                            configs[config_type] = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load {config_type} config: {e}")
                    configs[config_type] = {}
            else:
                configs[config_type] = {}

        return configs

    def analyze_text(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze Turkish text using AI and validation pipeline."""

        try:
            # Build prevention-at-source prompt
            prompt = self.prompt_builder.build_analysis_prompt(
                request.text,
                request.complexity
            )

            # Call AI model
            ai_response = self._call_ai_model(prompt)

            # Parse response
            analysis = self.response_parser.parse_response(
                ai_response,
                request.complexity
            )

            # Validate analysis
            validation_result = self.validator.validate_analysis(analysis)

            # Prepare metadata
            metadata = {
                'complexity': request.complexity,
                'validation_summary': validation_result.summary,
                'processing_time': time.time(),
                'model_used': self.config.ai_model_settings['model'],
                'prompt_tokens': self._estimate_tokens(prompt),
                'response_tokens': self._estimate_tokens(ai_response)
            }

            # Check if analysis is valid enough to return
            if validation_result.is_valid or self._is_analysis_usable(validation_result):
                return AnalysisResponse(
                    success=True,
                    analysis=analysis,
                    metadata=metadata
                )
            else:
                return AnalysisResponse(
                    success=False,
                    error_message="Analysis failed validation",
                    metadata={
                        **metadata,
                        'validation_issues': [issue.message for issue in validation_result.issues]
                    }
                )

        except Exception as e:
            return AnalysisResponse(
                success=False,
                error_message=f"Analysis failed: {str(e)}",
                metadata={'error_type': type(e).__name__}
            )

    def _call_ai_model(self, prompt: str) -> str:
        """Call Google Gemini AI model."""
        try:
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise ValueError("Empty response from AI model")

            return response.text

        except Exception as e:
            raise RuntimeError(f"AI model call failed: {e}")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def _is_analysis_usable(self, validation_result) -> bool:
        """Determine if analysis is usable despite validation issues."""
        summary = validation_result.summary

        # Allow if error rate is below threshold
        return summary.get('error_rate', 1.0) < 0.5

    def get_supported_complexities(self) -> List[str]:
        """Get list of supported complexity levels."""
        return self.config.complexity_levels

    def validate_configuration(self) -> List[str]:
        """Validate infrastructure configuration."""
        errors = []

        # Check AI client
        if not hasattr(self, 'model'):
            errors.append("AI model not initialized")

        # Check API key
        if not self._get_api_key():
            errors.append("Google AI API key not configured")

        # Check config validity
        config_errors = self.config.validate_configuration()
        errors.extend(config_errors)

        return errors

    def reload_external_configs(self) -> bool:
        """Reload external configuration files."""
        try:
            self.external_configs = self._load_external_configs()
            return True
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get infrastructure health status."""
        status = {
            'ai_client': hasattr(self, 'model'),
            'api_key_configured': bool(self._get_api_key()),
            'external_configs_loaded': bool(self.external_configs),
            'config_valid': len(self.config.validate_configuration()) == 0
        }

        status['overall_healthy'] = all(status.values())
        return status