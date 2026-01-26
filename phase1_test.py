#!/usr/bin/env python3
"""
Phase 1 Testing Script - Circular Import Fix Validation
Tests the resolution of circular import issues and basic deck generation functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'streamlit_app'))

def test_imports():
    """Test that all critical imports work without circular dependencies."""
    logger.info("Testing critical imports...")

    try:
        from streamlit_app.sentence_generator import generate_word_meaning_sentences_and_keywords
        logger.info("✅ sentence_generator import successful")
    except ImportError as e:
        logger.error(f"❌ sentence_generator import failed: {e}")
        return False

    try:
        from streamlit_app.services.generation.content_generator import get_content_generator
        logger.info("✅ content_generator service import successful")
    except ImportError as e:
        logger.error(f"❌ content_generator service import failed: {e}")
        return False

    try:
        from streamlit_app.services.generation.grammar_processor import get_grammar_processor
        logger.info("✅ grammar_processor service import successful")
    except ImportError as e:
        logger.error(f"❌ grammar_processor service import failed: {e}")
        return False

    try:
        from streamlit_app.services.generation.deck_assembler import get_deck_assembler
        logger.info("✅ deck_assembler service import successful")
    except ImportError as e:
        logger.error(f"❌ deck_assembler service import failed: {e}")
        return False

    try:
        from streamlit_app.shared_utils import get_gemini_model, cached_api_call, retry_with_exponential_backoff
        logger.info("✅ shared_utils import successful")
    except ImportError as e:
        logger.error(f"❌ shared_utils import failed: {e}")
        return False

    return True

def test_service_initialization():
    """Test that services can be initialized without errors."""
    logger.info("Testing service initialization...")

    try:
        from streamlit_app.services.generation.content_generator import get_content_generator
        content_gen = get_content_generator()
        logger.info("✅ Content generator service initialized")
    except Exception as e:
        logger.error(f"❌ Content generator initialization failed: {e}")
        return False

    try:
        from streamlit_app.services.generation.grammar_processor import get_grammar_processor
        grammar_proc = get_grammar_processor()
        logger.info("✅ Grammar processor service initialized")
    except Exception as e:
        logger.error(f"❌ Grammar processor initialization failed: {e}")
        return False

    try:
        from streamlit_app.services.generation.deck_assembler import get_deck_assembler
        deck_assembler = get_deck_assembler()
        logger.info("✅ Deck assembler service initialized")
    except Exception as e:
        logger.error(f"❌ Deck assembler initialization failed: {e}")
        return False

    return True

def test_shared_utils_functionality():
    """Test that shared utilities work correctly."""
    logger.info("Testing shared utilities functionality...")

    try:
        from streamlit_app.shared_utils import get_gemini_model, get_cache_manager, LANGUAGE_NAME_TO_CODE

        model = get_gemini_model()
        assert isinstance(model, str) and len(model) > 0
        logger.info(f"✅ Gemini model: {model}")

        cache_manager = get_cache_manager()
        assert cache_manager is not None
        logger.info("✅ Cache manager initialized")

        lang_code = LANGUAGE_NAME_TO_CODE.get('chinese_simplified')
        assert lang_code == 'zh'
        logger.info("✅ Language code mapping works")

    except Exception as e:
        logger.error(f"❌ Shared utils functionality test failed: {e}")
        return False

    return True

def test_deck_generation_dry_run():
    """Test deck generation with mock API key (dry run)."""
    logger.info("Testing deck generation dry run...")

    try:
        from streamlit_app.sentence_generator import generate_word_meaning_sentences_and_keywords

        # Test with a mock API key that will fail gracefully
        result = generate_word_meaning_sentences_and_keywords(
            word="都",
            language="chinese_simplified",
            num_sentences=3,  # Reduced for testing
            min_length=5,
            max_length=20,
            difficulty="intermediate",
            gemini_api_key="mock_key_that_will_fail"
        )

        # Should return a result even if API fails (fallback behavior)
        assert isinstance(result, dict)
        assert 'sentences' in result
        logger.info(f"✅ Deck generation returned result with {len(result.get('sentences', []))} sentences")

    except Exception as e:
        logger.error(f"❌ Deck generation dry run failed: {e}")
        return False

    return True

def main():
    """Run all Phase 1 tests."""
    logger.info("🚀 Starting Phase 1 Testing - Circular Import Fix Validation")
    logger.info("=" * 60)

    tests = [
        ("Import Resolution", test_imports),
        ("Service Initialization", test_service_initialization),
        ("Shared Utils Functionality", test_shared_utils_functionality),
        ("Deck Generation Dry Run", test_deck_generation_dry_run),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: EXCEPTION - {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 PHASE 1 TESTING SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"  {test_name}: {status}")

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 PHASE 1 SUCCESS: All tests passed! Circular import issues resolved.")
        logger.info("📝 Next: Proceed to user testing and Phase 2 planning.")
        return True
    else:
        logger.error("💥 PHASE 1 FAILURE: Some tests failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)