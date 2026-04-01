import json
import os
import re

# Layer 4 RAG Database Connection
DB_PATH = os.path.join(os.getcwd(), "chroma_db")

# We defer import or wrap it safely so the app doesn't crash if ChromaDB is missing
RAG_AVAILABLE = False
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    if os.path.exists(DB_PATH):
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name="clinical_protocols")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        RAG_AVAILABLE = True
except Exception:
    pass

# Regex pattern for common injection phrases that should never appear in extracted fields
_INJECTION_PATTERN = re.compile(
    r'(ignore|forget|disregard|override|bypass|pretend|simulate|you are now|system prompt|'
    r'developer mode|disable filter|print prompt|output.*key|drop table)',
    re.IGNORECASE
)

def _sanitize_field(value, max_len=200):
    """
    Sanitize extracted JSON field values before they enter the sterile prompt.
    Strips injection patterns and enforces length limits.
    """
    if not isinstance(value, str):
        return "Not specified"
    value = value.strip()[:max_len]
    if _INJECTION_PATTERN.search(value):
        return "REDACTED"
    return value


def validate_and_recompile(json_data):
    """
    Function: Validates the extracted JSON and performs Vector RAG Injection (Layer 4).
    If invalid or empty domain, returns None & error.
    Otherwise, retrieves the relevant medical protocol and constructs a clean, sterile prompt.
    """
    if "error" in json_data:
        return None, f"Extraction failed: {json_data['error']}"

    action = json_data.get("action_requested", "").strip()
    domain = json_data.get("clinical_domain", "").strip().lower()

    if action.upper() == "INVALID":
        return None, "Security Error: Prompt injection or invalid request detected. Access denied."

    if not domain or domain in ["none", "unknown", ""]:
        return None, "Validation Error: No valid clinical domain identified in the request."

    # --- Layer 4: True RAG Retrieval ---
    # FAIL-SECURE: If RAG is offline, block the pipeline to prevent ungrounded hallucination
    if not RAG_AVAILABLE:
        return None, "Safety Error: Clinical knowledge base is offline. Cannot generate ungrounded medical responses."

    protocol_text = ""
    try:
        # Generate the embedding using the local sentence-transformer model
        query_str = f"{domain} clinical protocol management guidelines {action}"
        query_embedding = embedding_model.encode([query_str]).tolist()

        # Query the collection
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=2
        )
        # Flatten extracted documents
        if results and results.get("documents") and results["documents"][0]:
            protocol_text = "\n\n".join(results["documents"][0])
    except Exception as e:
        protocol_text = f"Vector Query Failed: {str(e)}"

    if not protocol_text:
        protocol_text = "No matching clinical protocol found in the knowledge base."

    # Recompile into a clean, system-level request with RAG grounding
    # Sanitize all JSON-derived fields before interpolation
    sterile_prompt = (
        f"Clinical Context: {domain.upper()}\n"
        f"Medical Protocol: {protocol_text}\n"
        f"Target Subject: {_sanitize_field(json_data.get('target_entity', 'Not specified'))}\n"
        f"Action Required: {_sanitize_field(action)}\n"
        f"Patient Parameters: {_sanitize_field(json_data.get('patient_parameters', 'None'))}\n\n"
        f"Task: Please execute the action required based exclusively on the provided Medical Protocol and parameters."
    )

    return sterile_prompt, None
