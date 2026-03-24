# Project MediGuard: Core Engineering Principles

Project MediGuard is a 5-Layer Defense-in-Depth architecture. 

## Security Constraints
- **Control-Data Separation:** All modules must strictly enforce the separation of instructions (Control) from user-provided input (Data).
- **No Concatenation:** Never concatenate raw user input directly into the final LLM prompt. User input must be treated as untrusted data.
- **Sandbox Enforcement:** All inputs must be processed through the JSON extraction sandbox before reaching the reasoning engine.

## Project Architecture
- **Modularity:** Maintain a clean separation of concerns.
- **Backend:** All logic, filters, and sentinels must reside in the `core/` directory.
- **Frontend:** `app.py` is reserved strictly for the Streamlit UI and orchestration.

## Core Instincts
- **Research-First Instinct:** Before making any logic or structural changes, you MUST generate an `implementation_plan.md`. Detail file impacts, data flow, and security implications. Coding begins only AFTER explicit user approval.
- **Defensive Instinct:** Wrap all external I/O (APIs, environment, file system) in `try/except` blocks. Never invent library functions or use placeholder data.
- **Air-Gap Instinct:** Strictly enforce Control-Data Separation. Treat Layer 2 (Extraction Sandbox) as the only entry point for untrusted strings; Layer 4 (Reconstruction) is the only point where medical protocols join the pipeline.
- **Memory-First Instinct:** After each completed task or architectural change, you MUST update `.agent/MEMORY.md`. The update must include the current implementation status of each defense layer and a dated log of the changes.

## Implementation Protocols
- **Error Transparency:** If a security layer or API call (e.g., Hugging Face) fails, print the full error trace directly to the Streamlit UI. Do not suppress or simplify security failures.
- **Zero-Trust Logic:** Assume all user input is malicious. Validation must happen at every layer transition, and `app.py` must reflect these transitions using `st.status` or equivalent real-time monitoring.
- **Visual Integrity:** Maintain a "glass-box" design. The UI must always show the current state of extraction and reconstruction to ensure the user can audit the system's reasoning.
- **Historical Logging:** After each milestone, record implementation details, architectural pivots, and technical difficulties encountered in `.agent/MEMORY.md` to maintain a permanent history without a timestamp.


