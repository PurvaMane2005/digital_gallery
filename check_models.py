import os
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = httpx.get(url)
    models = response.json().get('models', [])
    print("📋 YOUR AVAILABLE MODELS:")
    for m in models:
        # We only care about models that support 'generateContent'
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f" - {m['name']}")
except Exception as e:
    print(f"❌ Error fetching models: {e}")