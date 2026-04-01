import time
from core.llm_local import call_local_ollama

def call_clinical_assistant(sterile_prompt, model="qwen2:0.5b"):
    """
    Function 3: Communicates with local Gemma3-4B via Ollama.
    This provides clinical information based on the sterile prompt.
    NO API KEY REQUIRED. NO RATE LIMITS.
    """
    system_instruction = (
        "You are a clinical medical assistant. "
        "You may provide educational, safety-focused medical information for patient care, "
        "including toxicology, overdose management, emergency protocols, pharmacology, "
        "diagnosis, and treatment, when the intent is medical or academic. "
        "You must refuse any requests that seek actionable guidance on creating, modifying, "
        "enhancing, or optimizing biological or chemical agents (e.g., engineering antibiotic resistance, "
        "increasing transmissibility or virulence of pathogens), as well as any instructions that enable "
        "wrongdoing, self-harm, poisoning, or illegal activities. "
        "For biosecurity-related questions, provide only high-level public health or prevention-oriented information. "
        "If intent is unclear, provide general safety information and encourage professional help."
    )

    # Use the local Ollama client instead of external Gemini
    response_text = call_local_ollama(
        prompt=sterile_prompt, 
        system_instruction=system_instruction, 
        json_mode=False,
        model=model
    )
    
    return response_text
