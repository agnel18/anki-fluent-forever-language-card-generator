"""Quick test for Google TTS API with Malayalam"""
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_TTS_API_KEY')
print(f"API Key found: {api_key[:15]}..." if api_key else "No API key found!")

url = 'https://texttospeech.googleapis.com/v1/text:synthesize'
payload = {
    'input': {'text': 'നമസ്കാരം'},  # "Hello" in Malayalam
    'voice': {'languageCode': 'ml', 'ssmlGender': 'NEUTRAL'},
    'audioConfig': {'audioEncoding': 'MP3', 'speakingRate': 0.8}
}

print("\nTesting Google TTS API...")
response = requests.post(url, json=payload, params={'key': api_key})

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ SUCCESS! Google TTS API is working correctly!")
    audio_content = base64.b64decode(response.json()["audioContent"])
    print(f"Audio size: {len(audio_content)} bytes")
    
    # Save test file
    with open('test_audio.mp3', 'wb') as f:
        f.write(audio_content)
    print("✅ Test audio saved to test_audio.mp3")
else:
    print(f"❌ ERROR: {response.text}")
