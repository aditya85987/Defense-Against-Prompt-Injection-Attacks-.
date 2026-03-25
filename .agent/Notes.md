# MediGuard Project Notes & Issue Tracker

## Issue 1: False Refusals via Layer 1 ML Anomaly Detector
**Component:** `core/filters.py` -> `heuristic_pre_filter` (IsolationForest model)
**Description:** The ML anomaly detector (Layer 1) triggers false positives on safe clinical queries that contain specific patient names (e.g., "What are the hypertension guidelines for patient John Doe?"). The model flags these normal variations as having a "Suspicious mathematical signature".
**Impact:** Legitimate requests are halted entirely before reaching the JSON Extraction Sandbox. This breaks the downstream pipeline, preventing the RAG Injection and PII Redaction layers from ever activating on legitimate medical queries that simply contain names.
**Next Steps/Proposed Fixes:**
1. Update `prompts_dataset.csv` with a broader set of synthetic "Safe" prompts containing different name variations, demographic phrases, and varied sentence lengths.
2. Retrain and export a new `IsolationForest` binary (`anomaly_detector.joblib`).
3. Alternatively, implement a quick bypass or preprocessing step in Layer 1 to mask standard demographic markers before entropy and feature extraction is calculated.
