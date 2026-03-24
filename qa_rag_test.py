from core.rag_sim import validate_and_recompile

def run_test(test_name, payload):
    print(f"\n{'='*50}")
    print(f"--- Running Test: {test_name} ---")
    print(f"Payload: {payload}")
    
    # Directly invoke Layer 4 retrieval function
    result, error = validate_and_recompile(payload)
    
    if error:
        print(f"Pipeline blocked the request: {error}")
        return
        
    assert result is not None, "Failed: validate_and_recompile returned None without an error."
    assert "Medical Protocol:" in result, "Failed: 'Medical Protocol' section missing from prompt output."
    
    # Extract just the "Medical Protocol:" section for easy reading in terminal
    try:
        protocol_start = result.index("Medical Protocol:") + len("Medical Protocol:")
        protocol_end = result.index("Target Subject:")
        retrieved_text = result[protocol_start:protocol_end].strip()
    except ValueError:
        retrieved_text = "Could not parse retrieved text from prompt string."
        
    print(f"\n=> RETRIEVED CHUNKS:\n\n{retrieved_text}\n")
    print(f"{'='*50}")
    
    # Split by double newline to count effectively how many chunks were injected
    chunks = [c for c in retrieved_text.split('\n\n') if c.strip()]
    if chunks:
        print(f"-> Successfully retrieved {len(chunks)} chunk(s).")
    else:
        print("-> No chunks retrieved.")

def main():
    print("\nInitializing ChromaDB RAG QA...\n")
    
    # 1. The Direct Hit
    direct_hit_payload = {
        "clinical_domain": "Hypertension",
        "action_requested": "management strategies",
        "target_entity": "patient"
    }
    run_test("The Direct Hit (Clear Medical Query)", direct_hit_payload)
    
    # 2. The Total Miss
    total_miss_payload = {
        "clinical_domain": "chocolate cake",
        "action_requested": "baking instructions",
        "target_entity": "cake"
    }
    run_test("The Total Miss (Non-Medical Domain)", total_miss_payload)
    
    # 3. The Edge Case
    edge_case_payload = {
        "clinical_domain": "blood",
        "action_requested": "",
        "target_entity": ""
    }
    run_test("The Edge Case (Vague/Short Keyword)", edge_case_payload)
    
    print("\n✅ All RAG tests executed successfully with no crashes.")

if __name__ == "__main__":
    main()
