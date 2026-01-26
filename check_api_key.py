# Check which project an API key belongs to
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('streamlit_app/.env', override=True)

def check_api_key_project():
    """Try to determine which project an API key belongs to"""
    api_key = os.getenv('GOOGLE_API_KEY')

    if not api_key:
        print("❌ No API key found")
        return

    print(f"🔍 Checking API key: {api_key[:15]}...")

    # Try a simple Google API that should work if the key is valid
    # Using Google OAuth2 tokeninfo endpoint to get project info
    url = f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={api_key}'

    try:
        response = requests.get(url, timeout=10)
        print(f"Token info status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API key is valid")
            print(f"Project info: {data}")
        else:
            print(f"❌ API key validation failed: {response.text}")

    except Exception as e:
        print(f"❌ Error checking API key: {e}")

    # Try the Custom Search API again with more details
    print("\n🔍 Testing Custom Search API...")
    search_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': 'c19b7d98fba0d49ee',  # Your search engine ID
        'q': 'test',
        'searchType': 'image',
        'num': 1
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        print(f"Custom Search status: {response.status_code}")

        if response.status_code == 403:
            error_data = response.json()
            error = error_data.get('error', {})
            print(f"Error details: {error}")
        elif response.status_code == 200:
            print("✅ Custom Search API working!")
        else:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error testing Custom Search: {e}")

if __name__ == "__main__":
    check_api_key_project()