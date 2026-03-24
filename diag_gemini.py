import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Explicitly ensure no system key interference
os.environ.pop("GOOGLE_API_KEY", None)
api_key = os.getenv("GEMINI_API_KEY")

print(f"Using key: {api_key[:10]}...")

client = genai.Client(api_key=api_key)

prompt = "What is the standard protocol for managing acute myocardial infarction?"

print("\n--- Testing Layer 2 (Extraction) ---")
try:
    system_prompt = "Extract clinical domain and target entity into JSON."
    start = time.time()
    resp1 = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json"
        )
    )
    print(f"Layer 2 Success in {time.time()-start:.2f}s")
    print("Output:", resp1.text[:200])
except Exception as e:
    print(f"Layer 2 Failed: {e}")

time.sleep(2) # Small gap as in the app

print("\n--- Testing Layer 5 (Reasoner) ---")
try:
    system_instruction = "You are a clinical assistant. Provide medical info based on context."
    sterile_prompt = "Clinical Context: Cardiology. Protocol: Aspirin, ECG, reperfusion."
    start = time.time()
    resp2 = client.models.generate_content(
        model='gemini-flash-latest',
        contents=sterile_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    print(f"Layer 5 Success in {time.time()-start:.2f}s")
    print("Output:", resp2.text[:200])
except Exception as e:
    print(f"Layer 5 Failed: {e}")
