from google import genai

# Test with a dummy API key (will fail but test import)
try:
    client = genai.Client(api_key="dummy_key")
    print("Client created successfully")
    print("GenAI new API imported and client initialized")
except Exception as e:
    print(f"Expected error with dummy key: {e}")
    print("But import and Client class work!")