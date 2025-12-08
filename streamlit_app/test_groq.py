"""Integration test for Groq API (requires API key)"""
import os
import sys
from pathlib import Path

def test_groq_integration():
    """Test Groq sentence generation with demo key (if available)"""
    
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        print("⏭️  SKIPPED: No GROQ_API_KEY env var found")
        print("   Set GROQ_API_KEY=<your_key> to run full integration test")
        return True
    
    print("Testing Groq API...")
    
    try:
        from core_functions import generate_sentences
        
        # Test with minimal params
        print("  Generating test sentence...")
        sentences = generate_sentences(
            word="hello",
            meaning="greeting",
            language="English",
            num_sentences=2,
            min_length=3,
            max_length=10,
            difficulty="beginner",
            groq_api_key=groq_key,
        )
        
        if not sentences:
            print("  ❌ No sentences generated")
            return False
        
        if len(sentences) < 2:
            print(f"  ⚠️  Expected 2 sentences, got {len(sentences)}")
        
        print(f"  ✅ Generated {len(sentences)} sentences:")
        for i, sent in enumerate(sentences, 1):
            print(f"     {i}. {sent['sentence']}")
            print(f"        → {sent['english_translation']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_groq_integration()
    sys.exit(0 if success else 1)
