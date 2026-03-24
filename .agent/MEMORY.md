# Project MediGuard: 5-Layer Security Architecture Memory

This document tracks the current implementation status of the defense layers as requested.

## 🛡️ Architecture Status

| Layer | Component | Status | Description |
| :--- | :--- | :--- | :--- |
| **Layer 1** | Heuristic String/Entropy Filter | 🟢 **Implemented** | `heuristic_pre_filter` (in `core/filters.py`) checks for high-entropy strings and anomalies. |
| **Layer 2** | Deterministic JSON Extraction & Validation | 🟢 **Implemented** | LLM-based extraction into a rigid JSON schema via `core/extractor.py`. |
| **Layer 3** | DeBERTa-v3 Intent Sentinel API | 🟢 **Implemented** | Semantic injection detection using Hugging Face Inference API via `core/sentinel.py`. |
| **Layer 4** | Simulated RAG Dictionary | 🟢 **Implemented** | `validate_and_recompile` (in `core/rag_sim.py`) for contextual verification using medical protocols. |
| **Layer 5** | Regex PII Redaction | 🟢 **Implemented** | `pii_redactor` (in `core/filters.py`) for final output scrubbing of patient identifiers. |

---

## 📅 Log
- **2026-03-24:** Layer 1 (Heuristic Pre-filter) and Layer 5 (PII Redactor) implemented in `core/filters.py`.
- **2026-03-24:** Layer 3 (Semantic Intent Sentinel) integrated using Hugging Face DeBERTa-v3 sequence classification.
- **2026-03-24:** Layer 4 (Simulated RAG) dictionary and sterilization logic finalized.
- **2026-03-24:** Full 5-Layer Defense-in-Depth pipeline orchestrated in `app.py`.
- **2026-03-24:** Core Engineering Principles in `SKILL.md` refined to enforce architecture, error transparency, and historical logging.

## 📜 Detailed Technical History & Milestone Challenges

This section maintains a detailed record of implementation decisions, architectural pivots, and the technical difficulties navigated during development.

### Milestone 1: Phase 1 Production Upgrades
- **Objective**: Transition from simulation to academic rigor in security filtering.
- **Implemented Layer 1 (Anomaly Detection)**: Replaced basic keyword heuristics with a **True Shannon Entropy** calculation.
- **Implemented Layer 5 (PII Redaction)**: Integrated **Microsoft Presidio** (Analyzer and Anonymizer engines) with **Spacy (`en_core_web_lg`)** for NLP-driven entity masking.
- **Challenges Faced**: 
    - *Dependency Sensitivity*: The Spacy model (`en_core_web_lg`) is a heavy dependency (~400MB) prone to loading failures in restricted environments.
    - *Resolution*: Wrapped Presidio initialization in a global `try/except` block with a `PRESIDIO_AVAILABLE` flag, implementing a legacy regex fallback (SSN, Phone, Email) to ensure the Streamlit app never crashes.

### Milestone 2: Phase 2 Enterprise Refactoring
- **Objective**: Enhance observability and refine mathematical logic for edge cases.
- **Implemented Normalized Entropy**: Upgraded Shannon entropy to a **Normalized Ratio** (Entropy / Max Potential Entropy). This prevents short Base64 strings from slipping under fixed bit-count thresholds. Set a strict rejection boundary at **> 0.85**.
- **Observability System**: Created a `@security_logger` Python decorator. It intercepts all security rejections, logging function names, failure reasons, and a safely truncated 20-character snippet of the offending payload to a `SecurityPipeline` logger.
- **Isolated Unit Testing**: Created `core/test_filters.py` using `pytest`. Successfully validated Layer 1 (Entropy/Length) and Layer 5 (PII mapping) without needing the Streamlit runtime.
- **Challenges Faced**: 
    - *Short String False Negatives*: Standard Shannon bit-counts scaled poorly for short inputs. 
    - *Resolution*: Normalizing the entropy score relative to the input length solved the precision issue for short, dense obfuscated strings.

### Milestone 3: Phase 3 Local RAG Architecture
- **Objective**: Replace hardcoded clinical dictionaries with a true local vector database (Local LLM Grounding).
- **Implemented Knowledge Base**: Created `medical_guidelines.txt` covering 6 distinct clinical domains (Hypertension, DKA, Asthma, etc.).
- **Implemented Ingestion Engine**: Built `ingest_knowledge.py` using **ChromaDB** and **Sentence-Transformers**. This tool chunks protocols and embeds them into a local `./chroma_db` collection.
- **Layer 4 Recompilation**: Modified `core/rag_sim.py` to query the ChromaDB collection using a semantic vector search (`n_results=2`) based on the extracted `clinical_domain`, injecting real grounding context into the sterile prompt.
- **Challenges Faced**: 
    - *Environmental Terminal Hangs*: ChromaDB's default configuration attempted to download a separate ONNX model on the first query, which hung indefinitely in the terminal environment.
    - *Resolution*: Explicitly instantiated the `SentenceTransformer("all-MiniLM-L6-v2")` inside Layer 4 and switched the ChromaDB query to use `query_embeddings` directly, bypassing the ONNX download and ensuring instant local retrieval.
    - *Extraction Rigidity*: During QA testing, casual medical phrasing (e.g., "for my patient...") triggered the extraction model's "INVALID action" flag too early, preventing the prompt from reaching the RAG layer.
    - *Design Decision*: We maintained the strict "INVALID" block to prioritize system safety over query flexibility, adhering to the **Zero-Trust** implementation protocol.

