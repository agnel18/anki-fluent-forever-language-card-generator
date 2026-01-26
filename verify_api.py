# Quick verification script for Custom Search API
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('streamlit_app/.env', override=True)

def verify_custom_search_api():
    """Quick check if Custom Search API is working"""
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        print("❌ Missing API key or search engine ID")
        return False

    print(f"🔍 Testing Custom Search API access...")
    print(f"API Key: {api_key[:15]}...")
    print(f"Search Engine: {search_engine_id}")

    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'test apple',
        'searchType': 'image',
        'num': 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ SUCCESS! Found {len(items)} images")
            if items:
                print(f"Sample image URL: {items[0].get('link', 'N/A')[:50]}...")
            return True
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"❌ FAILED: {error}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = verify_custom_search_api()
    print(f"\nResult: {'🎉 WORKING!' if success else '❌ Still broken'}")