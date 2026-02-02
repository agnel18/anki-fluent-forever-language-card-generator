#!/usr/bin/env python3
"""
Simple test for Spanish batch parsing
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the streamlit_app directory to the path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "streamlit_app"))

from languages.spanish.es_analyzer import EsAnalyzer

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_batch_parsing():
    """Test batch parsing directly"""
    logger.info("Testing Spanish batch parsing")

    # Initialize the Spanish analyzer
    analyzer = EsAnalyzer()
    logger.info("Spanish analyzer initialized")

    # Test sentences
    sentences = [
        "Nosotros cultivamos tomates y pimientos en el jardín",
        "Ella lee libros interesantes en la biblioteca",
        "Los niños juegan fútbol en el parque",
        "Mi hermana canta canciones bonitas"
    ]

    # Test batch analysis
    try:
        results = analyzer.batch_analyze_grammar(sentences, "que", "intermediate", "")
        logger.info(f"Batch analysis completed with {len(results)} results")

        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: confidence={result.confidence_score:.2f}")
            logger.info(f"  HTML length: {len(result.html_output)}")
            logger.info(f"  Word explanations: {len(result.word_explanations)}")

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_batch_parsing()