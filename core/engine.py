import time
from google.genai import types

def call_clinical_assistant(ai_client, sterile_prompt):
    """
    Function 3: Communicates with Gemini to provide clinical information based on the sterile prompt.
    Includes retry logic to handle 429 RESOURCE_EXHAUSTED errors.
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

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=sterile_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = (attempt + 1) * 10  # 10s, 20s, 30s
                print(f"  [Reasoner] Rate limited (attempt {attempt+1}/{max_retries}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                return f"Clinical Assistant Error: {str(e)}"

    return "Clinical Assistant Error: Service temporarily unavailable after retries. Please try again later."
