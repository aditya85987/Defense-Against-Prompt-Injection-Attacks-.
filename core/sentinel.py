import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "protectai/deberta-v3-base-prompt-injection-v2"

def check_injection_hf(prompt):
    """
    Checks if a prompt is an injection using Hugging Face Inference API.
    Returns True if it's an injection, False otherwise.
    """
    if not HF_TOKEN:
        print("Warning: HF_TOKEN not set in environment.")
        return False
        
    try:
        client = InferenceClient(token=HF_TOKEN)
        # Use text_classification which maps to the model's pipeline
        result = client.text_classification(prompt, model=MODEL_ID)
        
        # result is a list of ClassificationOutput objects
        # Each has .label and .score attributes
        for pred in result:
            if pred.label == 'INJECTION' and pred.score > 0.5:
                return True
                
        return False
    except Exception as e:
        print(f"Error calling HF API via InferenceClient: {e}")
        return False
