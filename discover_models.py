import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Checking available models...")
try:
    # We use the native SDK to list models
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\n💡 TIP: If you see an SSL error here, your Python installation's certificates are outdated.")