import os
import json
import logging
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
logger = logging.getLogger("SecurityPipeline")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "protectai/deberta-v3-base-prompt-injection-v2"

def check_injection_hf(prompt):
    """
    Layer 2: Semantic Intent Sentinel (DeBERTa-v3 via Hugging Face).
    Returns True if injection detected, False if safe.
    FAIL-SECURE: Returns True (assume injection) on any failure.
    """
    if not HF_TOKEN:
        logger.critical("HF_TOKEN not set. FAIL-SECURE: Assuming injection.")
        return True

    try:
        client = InferenceClient(token=HF_TOKEN)
        result = client.text_classification(prompt, model=MODEL_ID)

        for pred in result:
            if pred.label == 'INJECTION' and pred.score > 0.5:
                return True

        return False
    except Exception as e:
        logger.critical(f"HF Sentinel API failure. FAIL-SECURE: Assuming injection. Error: {e}")
        return True
