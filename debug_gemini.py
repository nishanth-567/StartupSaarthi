
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = "gemini-2.0-flash-exp"

print(f"Testing Gemini API...")
print(f"Key: {api_key[:5]}...{api_key[-5:]}")
print(f"Model: {model_name}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, world!")
    print("\n✅ SUCCESS!")
    print(f"Response: {response.text}")
except Exception as e:
    print("\n❌ FAILURE!")
    print(f"Error: {e}")
