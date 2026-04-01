# Project MediGuard: 5-Layer Security Architecture Memory

This document tracks the current implementation status of the defense layers as requested.

## 🛡️ Architecture Status

| Layer | Component | Status | Description |
| :--- | :--- | :--- | :--- |
| **Layer 1** | Heuristic String/Entropy Filter | 🟢 **Implemented** | `heuristic_pre_filter` (in `core/filters.py`) checks for high-entropy strings and anomalies. |
| **Layer 2** | DeBERTa-v3 Intent Sentinel API | 🟢 **Implemented** | Semantic injection detection using Hugging Face Inference API via `core/sentinel.py`. |
| **Layer 3** | Deterministic JSON Extraction & Validation | 🟢 **Implemented** | LLM-based extraction into a rigid JSON schema via `core/extractor.py`. |
| **Layer 4** | Simulated RAG Dictionary | 🟢 **Implemented** | `validate_and_recompile` (in `core/rag_sim.py`) for contextual verification using medical protocols. |
| **Layer 5** | Regex PII Redaction | 🟢 **Implemented** | `pii_redactor` (in `core/filters.py`) for final output scrubbing of patient identifiers. |

---

## 📅 Log
- **2026-03-24:** Layer 1 (Heuristic Pre-filter) and Layer 5 (PII Redactor) implemented in `core/filters.py`.
- **2026-03-24:** Layer 2 (Semantic Intent Sentinel) integrated using Hugging Face DeBERTa-v3 sequence classification.
- **2026-03-24:** Layer 4 (Simulated RAG) dictionary and sterilization logic finalized.
- **2026-03-24:** Full 5-Layer Defense-in-Depth pipeline orchestrated in `app.py`.
- **2026-03-24:** Core Engineering Principles in `SKILL.md` refined to enforce architecture, error transparency, and historical logging.
- **2026-03-31:** Milestone 7 Production-Hardening Audit applied — 6 critical/high fixes across all layers.

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

### Milestone 4: Phase 4 Local ML Anomaly Detection
- **Objective**: Replace strict threshold logic with adaptive numerical classification via `scikit-learn` algorithms.
- **Implemented Synthetic Datasets**: Procedurally generated `prompts_dataset.csv` balancing 55 safe clinical queries against 55 adversarial payloads (Base64, Hex, Special Character spam).
- **Implemented Feature Matrices**: Extracted 3-dimensional features from strings: Total Length, Shannon Entropy, and Special Character Ratios.
- **Implemented IsolationForest**: Fitted and exported a local unsupervised `IsolationForest` (`anomaly_detector.joblib`) specifically tuned to detect the mathematical footprint of obfuscated prompt matrices.
- **Validation**: Demonstrated that the `.joblib` model cleanly bisected plain-text medical inquiries (1 / SAFE) from dense Base64 instructions (-1 / MALICIOUS).

### Milestone 5: Phase 5 ML Pipeline Integration
- **Objective**: Deploy the trained anomaly detector to actively intercept user queries within Layer 1.
- **Implemented Model Integration**: Updated `core/filters.py` to dynamically load `ml_training/anomaly_detector.joblib` on startup. 
- **Upgraded Heuristic Filter**: Modified `heuristic_pre_filter` to translate prompts via `extract_features` into a shape compatible with the `IsolationForest` weights, prioritizing dynamic algorithmic blocking over static thresholds.
- **Fail-Secure Architecture**: Wrapped the ML instantiation in a module-level `try/except` block, ensuring that if the `.joblib` binary goes offline, Layer 1 gracefully falls back to the static hardcoded limits implemented during Phase 2.

### Milestone 6: ML Dataset Augmentation and Entropy Alignment
- **Objective**: Resolve Issue 1 regarding False Refusals via the Layer 1 ML Anomaly Detector on queries containing patient demographic names.
- **Implemented Dataset Augmentation**: Expanded the synthetic safe query generation in `prompts_dataset.csv` from 110 to 400 total samples, successfully teaching the `IsolationForest` model to accept common patient names (e.g., "John Doe") and length variations without flagging them as anomalous signatures.
- **Implemented Mathematical Alignment**: Corrected a critical mathematical divergence where the training pipeline calculated raw Shannon entropy, but the inference pipeline calculated normalized entropy. Both pipelines now use identical `calculate_shannon_entropy` normalization formulas.
- **Implemented Advanced Edge Cases**: Fortified the malicious prompt class with extreme length tests (1500+ repetitive characters) and encoded null-byte strings (`\x00`) to guarantee the ML model boundary remains intact against sophisticated evasion payloads without relying solely on the fallback heuristic filters.

### Milestone 7: Production-Hardening Audit — End-to-End Pipeline Fix
- **Objective**: Conduct a full Senior Staff Security Engineer audit and apply all fixes to make the pipeline work end-to-end: safe prompts get answers, prompt injections get blocked, false refusals eliminated.
- **CRIT Fix 1 — Layer 1 ML Early Return**: Added `return True, None` after ML model approves a prompt. Previously, safe prompts approved by ML still fell through to legacy heuristics, causing false refusals on valid queries >1000 chars. Heuristics now only run when ML is offline.
- **CRIT Fix 2 — Layer 2 Sentinel Fail-Secure**: Rewrote `core/sentinel.py` to return `True` (assume injection) when HF_TOKEN is missing or the API call fails. Previously returned `False` (safe), which meant ALL injections passed through when the HF API was down — a critical fail-open vulnerability.
- **HIGH Fix 3 — Layer 3 Extractor Hardening**: Added 5 additional security rules to the extraction system prompt: no raw echo, no encoded payloads, 100-char field limit, no PII in fields. This closes the "injection-within-extraction" vector where attacker text could leak into JSON fields and reach the sterile prompt.
- **HIGH Fix 4 — Layer 4 RAG Offline Blocking + JSON Sanitization**: Added `_sanitize_field()` function with regex-based injection pattern detection for all JSON field values before sterile prompt interpolation. Pipeline now blocks when ChromaDB is offline instead of proceeding with zero grounding (prevents hallucinated drug dosages).
- **Fix 5 — Layer Numbering Standardization**: Fixed all comments and UI strings in `app.py` to use canonical order: L1=Heuristic, L2=Sentinel, L3=Extractor, L4=RAG, L5=Reasoner+Redactor.
- **Fix 6 — Test Infrastructure**: Rewrote `core/test_core_filters.py` and `tests/test_filters.py` with ML-aware assertions, monkeypatched heuristic-specific tests, and added patient-name false-refusal regression test. All 9 tests pass.
