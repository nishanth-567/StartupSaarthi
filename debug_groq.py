
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing Groq API with key: {api_key[:10]}...")

try:
    client = Groq(api_key=api_key)
    
    # List of likely active models
    models_to_test = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama3-8b-8192"]
    
    for model_id in models_to_test:
        print(f"Testing model: {model_id}...")
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": "Explain what is a startup in one sentence."}
                ],
                model=model_id,
            )
            print(f"\n✅ SUCCESS with {model_id}!")
            print(f"Response: {chat_completion.choices[0].message.content}")
            break
        except Exception as e:
            print(f"❌ Failed with {model_id}: {e}")
            continue

except Exception as e:
    print("\n❌ FAILURE!")
    print(f"Error: {e}")
