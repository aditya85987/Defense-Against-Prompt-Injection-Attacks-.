import json
import os

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
    protocol_text = "RAG Database Offline or Unreachable. Proceed with standard medical guidelines."
    
    if RAG_AVAILABLE:
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
    
    # Recompile into a clean, system-level request with RAG grounding
    # This separation ensures that raw strings never reach the next layer.
    sterile_prompt = (
        f"Clinical Context: {domain.upper()}\n"
        f"Medical Protocol: {protocol_text}\n"
        f"Target Subject: {json_data.get('target_entity', 'Not specified')}\n"
        f"Action Required: {action}\n"
        f"Patient Parameters: {json_data.get('patient_parameters', 'None')}\n\n"
        f"Task: Please execute the action required based exclusively on the provided Medical Protocol and parameters."
    )
    
    return sterile_prompt, None
