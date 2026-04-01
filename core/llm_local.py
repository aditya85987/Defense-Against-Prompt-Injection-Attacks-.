import requests
import json
import logging

logger = logging.getLogger("OllamaClient")

def call_local_ollama(prompt, system_instruction=None, json_mode=False):
    """
    Standardizes interaction with local Ollama instance (gemma3:4b).
    Eliminates all API rate limits and costs by running locally.
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "gemma3:4b",
        "prompt": prompt,
        "format": "json" if json_mode else "",
        "stream": False,
        "options": {
            "temperature": 0.1 # Keep it clinical and deterministic
        }
    }
    
    if system_instruction:
        payload["system"] = system_instruction

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        raw_text = result.get("response", "").strip()
        
        if json_mode:
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                # If the model didn't return perfect JSON despite the format flag
                # (though gemma3 is usually good at this)
                return {"action_requested": "INVALID", "error": "JSON Decode Error from Local LLM"}
        
        return raw_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama local connection failed (is Ollama desktop app running?): {e}")
        if json_mode:
            return {"action_requested": "INVALID", "error": "Ollama Connection Error"}
        return f"Local LLM Error: {str(e)}"
