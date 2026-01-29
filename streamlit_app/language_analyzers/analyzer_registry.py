# Language Analyzer Registry
# Manages all language-specific grammar analyzers

import importlib
import logging
import sys
from typing import Dict, Type, Optional, List, Any
from pathlib import Path

# Use absolute import instead of relative
try:
    from language_analyzers.base_analyzer import BaseGrammarAnalyzer
except ImportError:
    # Fallback for when running from different locations
    try:
        from .base_analyzer import BaseGrammarAnalyzer
    except ImportError:
        # Last resort - try importing from streamlit_app
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        streamlit_app_dir = os.path.dirname(current_dir)
        if streamlit_app_dir not in sys.path:
            sys.path.insert(0, streamlit_app_dir)
        from language_analyzers.base_analyzer import BaseGrammarAnalyzer

logger = logging.getLogger(__name__)

class AnalyzerRegistry:
    """
    Registry for managing language-specific grammar analyzers.

    Provides centralized access to all language analyzers and handles
    dynamic loading, validation, and selection.
    """

    def __init__(self):
        self._analyzers: Dict[str, Type[BaseGrammarAnalyzer]] = {}
        self._instances: Dict[str, BaseGrammarAnalyzer] = {}
        self._loaded_languages: set = set()

        # Auto-discover available analyzers
        self._discover_analyzers()

    def _discover_analyzers(self):
        """Auto-discover available analyzer modules"""
        languages_dir = Path(__file__).parent.parent.parent / "languages"

        if not languages_dir.exists():
            logger.warning(f"Languages directory not found: {languages_dir}")
            return

        # Add the root directory to sys.path so we can import languages modules
        root_dir = languages_dir.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        
        # Also add streamlit_app to sys.path for analyzer imports
        streamlit_app_dir = languages_dir.parent / "streamlit_app"
        if str(streamlit_app_dir) not in sys.path:
            sys.path.insert(0, str(streamlit_app_dir))

        # Mapping from folder names to language codes
        folder_to_code = {
            'arabic': 'ar',
            'hindi': 'hi',
            'spanish': 'es',
            'chinese_traditional': 'zh-tw'
        }

        # Look for language subdirectories
        for lang_dir in languages_dir.iterdir():
            if lang_dir.is_dir():
                folder_name = lang_dir.name
                language_code = folder_to_code.get(folder_name, folder_name)
                # Normalize filename (replace hyphens with underscores)
                normalized_code = language_code.replace('-', '_')
                analyzer_file = lang_dir / f"{normalized_code}_analyzer.py"
                
                if analyzer_file.exists():
                    try:
                        # Import the analyzer module
                        module_name = f"languages.{folder_name}.{normalized_code}_analyzer"
                        module = importlib.import_module(module_name)

                        # Find the analyzer class
                        # Handle language codes with hyphens (e.g., zh-tw -> ZhTw)
                        normalized_code = language_code.replace('-', '_')
                        class_name = ''.join(word.capitalize() for word in normalized_code.split('_')) + 'Analyzer'
                        analyzer_class = getattr(module, class_name, None)

                        if analyzer_class:
                            logger.info(f"Found class {class_name} in {module_name}")
                            logger.info(f"BaseGrammarAnalyzer id: {id(BaseGrammarAnalyzer)}")
                            logger.info(f"analyzer_class MRO: {[cls.__name__ for cls in analyzer_class.__mro__]}")
                            try:
                                # Check if it's a subclass by MRO instead of issubclass, to avoid import issues
                                mro_names = [cls.__name__ for cls in analyzer_class.__mro__]
                                is_subclass = 'BaseGrammarAnalyzer' in mro_names
                                logger.info(f"'BaseGrammarAnalyzer' in MRO of {class_name}: {is_subclass}")
                                if is_subclass:
                                    self._analyzers[language_code] = analyzer_class
                                    logger.info(f"Discovered analyzer for {language_code}")
                                else:
                                    logger.warning(f"Class {class_name} does not inherit from BaseGrammarAnalyzer")
                            except Exception as e:
                                logger.error(f"Error checking inheritance for {class_name}: {e}")
                        else:
                            logger.warning(f"No class {class_name} found in module {module_name}")

                        # Old code:
                        # if analyzer_class and issubclass(analyzer_class, BaseGrammarAnalyzer):
                        #     self._analyzers[language_code] = analyzer_class
                        #     logger.info(f"Discovered analyzer for {language_code}")
                        # else:
                        #     logger.warning(f"No valid analyzer class found in {analyzer_file}")

                    except Exception as e:
                        logger.error(f"Failed to load analyzer {language_code}: {e}")

    def get_analyzer(self, language_code: str) -> Optional[BaseGrammarAnalyzer]:
        """
        Get analyzer instance for the specified language.

        Args:
            language_code: ISO language code (e.g., 'zh', 'ja', 'es')

        Returns:
            Analyzer instance or None if not available
        """
        # Check if we have the analyzer class
        if language_code not in self._analyzers:
            logger.warning(f"No analyzer available for language: {language_code}")
            return None

        # Return cached instance if available
        if language_code in self._instances:
            return self._instances[language_code]

        # Create new instance
        try:
            analyzer_class = self._analyzers[language_code]
            instance = analyzer_class()
            self._instances[language_code] = instance
            self._loaded_languages.add(language_code)
            return instance

        except Exception as e:
            logger.error(f"Failed to create analyzer instance for {language_code}: {e}")
            return None

    def get_available_languages(self) -> List[str]:
        """Get list of all available language codes"""
        return list(self._analyzers.keys())

    def get_supported_languages_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all supported languages"""
        info = {}

        for code, analyzer_class in self._analyzers.items():
            try:
                # Create temporary instance to get info
                temp_instance = analyzer_class()
                info[code] = {
                    'name': temp_instance.language_name,
                    'native_name': getattr(temp_instance.config, 'native_name', temp_instance.language_name),
                    'family': temp_instance.config.family,
                    'complexity_levels': temp_instance.supported_levels,
                    'features': temp_instance.get_supported_features(),
                    'version': temp_instance.version
                }
            except Exception as e:
                logger.error(f"Failed to get info for {code}: {e}")
                info[code] = {
                    'name': f"Language {code}",
                    'error': str(e)
                }

        return info

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported"""
        return language_code in self._analyzers

    def get_fallback_analyzer(self, language_family: str = None) -> Optional[BaseGrammarAnalyzer]:
        """
        Get a fallback analyzer for unsupported languages.

        Args:
            language_family: Preferred language family for fallback

        Returns:
            Fallback analyzer instance
        """
        # Try to find analyzer from same family
        if language_family:
            for code, analyzer_class in self._analyzers.items():
                try:
                    temp_instance = analyzer_class()
                    if temp_instance.config.family == language_family:
                        return self.get_analyzer(code)
                except:
                    continue

        # Default fallback to English if available
        return self.get_analyzer('en') or self.get_analyzer('zh')

    def validate_analyzer(self, language_code: str) -> Dict[str, Any]:
        """
        Validate that an analyzer meets quality standards.

        Args:
            language_code: Language code to validate

        Returns:
            Validation results dictionary
        """
        results = {
            'language_code': language_code,
            'is_available': False,
            'meets_standards': False,
            'issues': []
        }

        analyzer = self.get_analyzer(language_code)
        if not analyzer:
            results['issues'].append('Analyzer not available')
            return results

        results['is_available'] = True

        # Check version
        if not hasattr(analyzer, 'VERSION'):
            results['issues'].append('Missing version information')

        # Check supported complexity levels
        if not analyzer.supported_levels:
            results['issues'].append('No complexity levels defined')
        elif not all(level in ['beginner', 'intermediate', 'advanced']
                    for level in analyzer.supported_levels):
            results['issues'].append('Invalid complexity levels')

        # Check color schemes
        for level in analyzer.supported_levels:
            try:
                colors = analyzer.get_color_scheme(level)
                if not colors or len(colors) < 3:
                    results['issues'].append(f'Insufficient colors for {level} level')
            except Exception as e:
                results['issues'].append(f'Color scheme error for {level}: {e}')

        # Check grammar prompt generation
        try:
            test_prompt = analyzer.get_grammar_prompt('beginner', 'Test sentence', 'test')
            if not test_prompt or len(test_prompt) < 50:
                results['issues'].append('Grammar prompt generation failed')
        except Exception as e:
            results['issues'].append(f'Prompt generation error: {e}')

        results['meets_standards'] = len(results['issues']) == 0
        return results

    def reload_analyzer(self, language_code: str) -> bool:
        """
        Reload an analyzer (useful for development/testing).

        Args:
            language_code: Language code to reload

        Returns:
            True if reload successful
        """
        try:
            # Remove from cache
            if language_code in self._instances:
                del self._instances[language_code]
            self._loaded_languages.discard(language_code)

            # Re-import module
            module_name = f".analyzers.{language_code}_analyzer"
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Re-discover
            self._discover_analyzers()

            return language_code in self._analyzers

        except Exception as e:
            logger.error(f"Failed to reload analyzer {language_code}: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_analyzers': len(self._analyzers),
            'loaded_instances': len(self._instances),
            'loaded_languages': list(self._loaded_languages),
            'available_languages': list(self._analyzers.keys())
        }

# Global registry instance
_registry = None

def get_registry() -> AnalyzerRegistry:
    """Get the global analyzer registry instance"""
    global _registry
    if _registry is None:
        _registry = AnalyzerRegistry()
    return _registry

def get_analyzer(language_code: str) -> Optional[BaseGrammarAnalyzer]:
    """Convenience function to get analyzer for a language"""
    return get_registry().get_analyzer(language_code)

def get_available_languages() -> List[str]:
    """Convenience function to get all available language codes"""
    return get_registry().get_available_languages()

def is_language_supported(language_code: str) -> bool:
    """Convenience function to check if language is supported"""
    return get_registry().is_language_supported(language_code)