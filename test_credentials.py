import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Environment Variables:")
print("=" * 60)

api_key = os.getenv('OPENAI_API_KEY')
api_base = os.getenv('OPENAI_API_BASE')

if api_key:
    print(f"✅ OPENAI_API_KEY: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
else:
    print("❌ OPENAI_API_KEY: NOT SET")

if api_base:
    print(f"✅ OPENAI_API_BASE: {api_base}")
else:
    print("❌ OPENAI_API_BASE: NOT SET")

print("\n" + "=" * 60)
print("\nNOTE: OpenRouter API keys start with 'sk-or-v1-'")
print("If your key doesn't look right, please check your .env file")
