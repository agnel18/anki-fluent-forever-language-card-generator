# Test content generation with keywords
import os
import sys
from dotenv import load_dotenv

# Add streamlit_app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# Load environment variables from streamlit_app/.env
env_path = os.path.join(os.path.dirname(__file__), 'streamlit_app', '.env')
load_dotenv(env_path)

def test_content_generation():
    """Test if keywords are generated with sentences"""
    try:
        from streamlit_app.services.generation.content_generator import get_content_generator

        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ No GOOGLE_API_KEY found")
            return

        print("✅ API Key found")

        # Create content generator
        generator = get_content_generator()

        # Test generation
        print("🔄 Generating content for word 'apple' in English...")
        result = generator.generate_word_meaning_sentences_and_keywords(
            word="apple",
            language="English",
            num_sentences=2,
            gemini_api_key=api_key,
            min_length=3,
            max_length=15,
            difficulty="intermediate"
        )

        print("\n📊 RESULTS:")
        print(f"Meaning: {result.get('meaning', 'N/A')}")
        print(f"Sentences: {len(result.get('sentences', []))}")
        print(f"Keywords: {len(result.get('keywords', []))}")

        print("\n📝 DETAILS:")
        sentences = result.get('sentences', [])
        keywords = result.get('keywords', [])

        for i, (sentence, kw) in enumerate(zip(sentences, keywords)):
            print(f"{i+1}. Sentence: {sentence}")
            print(f"   Keywords: {kw}")
            print()

        # Check if keywords are properly formatted
        if keywords:
            first_kw = keywords[0]
            if ',' in first_kw:
                kw_list = [k.strip() for k in first_kw.split(',')]
                print(f"✅ Keywords parsed: {kw_list}")
            else:
                print("⚠️ Keywords not comma-separated")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_content_generation()