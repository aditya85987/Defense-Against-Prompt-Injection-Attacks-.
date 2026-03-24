import json
import os
from google import genai
from google.genai import types
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
api_key = env_vars.get("GEMINI_API_KEY")

if not api_key:
    # Check if GOOGLE_API_KEY is set in environment directly
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: NO API KEY FOUND")
    exit(1)

print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")
client = genai.Client(api_key=api_key)

system_prompt = '''
You are a strictly constrained clinical data extraction assistant.
Extract information from the raw prompt into the following exact JSON schema:
{
    "clinical_domain": "string",
    "target_entity": "string",
    "action_requested": "string",
    "patient_parameters": "string"
}
'''

models_to_try = [
    'gemini-2.0-flash',
    'gemini-2.0-flash',
    'gemini-1.5-pro',
    'gemini-2.0-flash-exp'
]

for model_name in models_to_try:
    try:
        print(f"\nAttempting extraction with {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents='Tell me the cardiology protocol for AMI.',
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json"
            )
        )
        print("Success!")
        print(response.text)
        break
    except Exception as e:
        print(f"Failed with {model_name}: {str(e)}")
