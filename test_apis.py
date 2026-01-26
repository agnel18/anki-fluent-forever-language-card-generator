# API Test Script for Language Learning App
# Tests Google TTS and Custom Search Image APIs

import os
import sys
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Also try loading from streamlit_app directory (with override)
streamlit_env = Path(__file__).parent / "streamlit_app" / ".env"
if streamlit_env.exists():
    load_dotenv(streamlit_env, override=True)

def test_tts_api():
    """Test Google Text-to-Speech API"""
    print("🔊 Testing Google Text-to-Speech API...")

    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in environment")
        return False

    print(f"✅ API Key found (starts with: {api_key[:10]}...)")

    # Test voice listing
    print("📋 Testing voice listing...")
    voices_url = "https://texttospeech.googleapis.com/v1/voices"
    params = {"key": api_key}

    try:
        response = requests.get(voices_url, params=params, timeout=10)
        print(f"Voice list response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            voices = data.get('voices', [])
            print(f"✅ Found {len(voices)} total voices")

            # Check for Chinese voices
            chinese_voices = [v for v in voices if 'cmn-CN' in str(v.get('languageCodes', []))]
            print(f"✅ Found {len(chinese_voices)} Chinese voices")

            if chinese_voices:
                print(f"Sample Chinese voice: {chinese_voices[0]['name']}")
        else:
            print(f"❌ Voice list failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Voice list exception: {e}")
        return False

    # Test audio synthesis
    print("🎵 Testing audio synthesis...")
    synthesis_url = "https://texttospeech.googleapis.com/v1/text:synthesize"

    request_data = {
        "input": {
            "text": "Hello, this is a test of the Google Text-to-Speech API."
        },
        "voice": {
            "languageCode": "en-US",
            "name": "en-US-Neural2-D"
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": 0.8
        }
    }

    try:
        response = requests.post(synthesis_url, params=params, json=request_data, timeout=30)
        print(f"Synthesis response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            audio_content = data.get("audioContent")

            if audio_content:
                # Decode and save audio
                audio_data = base64.b64decode(audio_content)
                output_path = Path("test_tts_output.mp3")
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                print(f"✅ Audio saved to: {output_path.absolute()}")
                print(f"   File size: {len(audio_data)} bytes")
                return True
            else:
                print("❌ No audio content in response")
                return False
        else:
            print(f"❌ Synthesis failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Synthesis exception: {e}")
        return False

def test_image_api():
    """Test Google Custom Search Image API"""
    print("\n🖼️  Testing Google Custom Search Image API...")

    # Get API keys
    search_api_key = os.getenv('GOOGLE_API_KEY')  # Same key for both
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID') or os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')

    if not search_api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found")
        return False

    if not search_engine_id:
        print("❌ ERROR: GOOGLE_SEARCH_ENGINE_ID or GOOGLE_CUSTOM_SEARCH_ENGINE_ID not found")
        return False

    print(f"✅ Search API Key found (starts with: {search_api_key[:10]}...)")
    print(f"✅ Search Engine ID found: '{search_engine_id}'")

    # Test image search
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": search_api_key,
        "cx": search_engine_id,
        "q": "apple fruit",  # Simple test query
        "searchType": "image",
        "num": 1,
        "safe": "active"
    }

    print(f"Search URL: {search_url}")
    print(f"Search Engine ID: {search_engine_id}")
    print(f"Query: {params['q']}")

    try:
        response = requests.get(search_url, params=params, timeout=10)
        print(f"Image search response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            if items:
                image_url = items[0].get('link')
                print(f"✅ Found image: {image_url}")

                # Try to download the image
                try:
                    img_response = requests.get(image_url, timeout=10)
                    if img_response.status_code == 200:
                        output_path = Path("test_image_output.jpg")
                        with open(output_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"✅ Image saved to: {output_path.absolute()}")
                        print(f"   File size: {len(img_response.content)} bytes")
                        return True
                    else:
                        print(f"❌ Image download failed: {img_response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ Image download exception: {e}")
                    return False
            else:
                print("❌ No images found in search results")
                print(f"Response data: {data}")
                return False
        else:
            print(f"❌ Image search failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Full error response: {error_data}")
                
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"Error message: {error_message}")
                
                # Specific troubleshooting
                if 'Custom Search JSON API' in error_message:
                    print("💡 SOLUTION: Enable 'Custom Search JSON API' in Google Cloud Console")
                    print("   Go to: https://console.cloud.google.com/apis/library")
                    print("   Search for: Custom Search JSON API")
                    print("   Click ENABLE")
                elif 'invalid' in error_message.lower() and 'argument' in error_message.lower():
                    print("💡 SOLUTION: Check your search engine ID format")
                    print(f"   Current ID: {search_engine_id}")
                elif 'Access Not Configured' in error_message:
                    print("💡 SOLUTION: API not enabled for this project")
                elif 'Key Management Service' in error_message:
                    print("💡 SOLUTION: Wrong API enabled - need 'Custom Search JSON API', not 'Custom Search API'")
                    
            except:
                print(f"Raw response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Image search exception: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 API Test Script for Language Learning App")
    print("=" * 50)

    # Test TTS
    tts_success = test_tts_api()

    # Test Images
    image_success = test_image_api()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"TTS API: {'✅ PASS' if tts_success else '❌ FAIL'}")
    print(f"Image API: {'✅ PASS' if image_success else '❌ FAIL'}")

    if tts_success and image_success:
        print("\n🎉 All APIs are working correctly!")
        print("Check the generated files: test_tts_output.mp3 and test_image_output.jpg")
    else:
        print("\n⚠️  Some APIs failed. Check the error messages above.")

    return 0 if (tts_success and image_success) else 1

if __name__ == "__main__":
    sys.exit(main())