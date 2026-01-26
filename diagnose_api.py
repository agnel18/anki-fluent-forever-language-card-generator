# Comprehensive API diagnostics
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('streamlit_app/.env', override=True)

def test_google_apis():
    """Test various Google APIs to diagnose the issue"""
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')

    if not api_key:
        print("❌ No API key found")
        return

    print(f"🔍 Testing API key: {api_key[:15]}...")
    print(f"🔍 Search Engine ID: {search_engine_id}")

    # Test 1: Try a simple Google API that should always work
    print("\n📋 Test 1: Google Books API (should work if key is valid)")
    books_url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'key': api_key,
        'q': 'test',
        'maxResults': 1
    }

    try:
        response = requests.get(books_url, params=params, timeout=10)
        print(f"Books API status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Books API works - API key is valid")
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"❌ Books API failed: {error}")
    except Exception as e:
        print(f"❌ Books API error: {e}")

    # Test 2: Custom Search API
    print("\n🔍 Test 2: Custom Search API")
    search_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'apple',
        'searchType': 'image',
        'num': 1
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        print(f"Custom Search status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ SUCCESS! Found {len(items)} images")
            if items:
                print(f"Sample: {items[0].get('link', 'N/A')[:50]}...")
        else:
            error_data = response.json()
            error = error_data.get('error', {})
            print(f"❌ FAILED: {error.get('message', 'Unknown error')}")
            print(f"Error code: {error.get('code', 'N/A')}")
            print(f"Error status: {error.get('status', 'N/A')}")

            # Check if it's a quota/billing issue
            if 'quota' in str(error).lower() or 'billing' in str(error).lower():
                print("💰 This might be a billing/quota issue")
            elif 'forbidden' in str(error).lower():
                print("🚫 This is a permissions/access issue")

    except Exception as e:
        print(f"❌ Custom Search error: {e}")

    # Test 3: Check if Custom Search Engine exists
    print("\n🔧 Test 3: Checking Custom Search Engine")
    cse_url = f'https://www.googleapis.com/customsearch/v1/siterestrict'
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'test'
    }

    try:
        response = requests.get(cse_url, params=params, timeout=10)
        print(f"Search Engine check status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Search engine exists and is accessible")
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"❌ Search engine issue: {error}")
    except Exception as e:
        print(f"❌ Search engine check error: {e}")

if __name__ == "__main__":
    test_google_apis()