import streamlit as st
from dotenv import dotenv_values
import json
import os
import pandas as pd
import time

# Remove any system-level GOOGLE_API_KEY to prevent SDK conflicts
os.environ.pop("GOOGLE_API_KEY", None)

# Core Modules
from core.extractor import extract_clinical_entities
from core.rag_sim import validate_and_recompile
from core.engine import call_clinical_assistant
from core.filters import heuristic_pre_filter, pii_redactor
from core.sentinel import check_injection_hf

# Load environment variables
env_vars = dotenv_values(".env")
api_key = env_vars.get("GEMINI_API_KEY")

from benchmark_runner import execute_benchmarks

def run_benchmarks():
    st.info("Initiating Live Security Sandbox Evaluation (100 Samples)...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Run the tests dynamically
    metrics, results = execute_benchmarks(is_streamlit=True, progress_bar=progress_bar, status_text=status_text)
    
    if "error" in metrics:
        st.error(metrics["error"])
        return
        
    status_text.text(f"✅ Evaluated 100 queries. Overall Accuracy: {metrics.get('accuracy', 0) * 100:.1f}%")
    
    # Plotting Data (Converting percentages 0.0-1.0 to 0-100 scales)
    data = {
        'System': ['Baseline (No Protection)', 'MediGuard Architecture'],
        'False Refusal Rate (%)': [0.0, metrics['false_refusal_rate'] * 100],
        'Prompt Injection Block Rate (%)': [0.0, metrics['injection_block_rate'] * 100]
    }
    
    df = pd.DataFrame(data).set_index('System')
    st.subheader("Comprehensive Security Test Results")
    st.bar_chart(df)
    
    col1, col2 = st.columns(2)
    col1.metric("MediGuard False Refusals", f"{metrics['false_refusal_rate'] * 100:.1f}%", "-0% (Target)", delta_color="inverse")
    col2.metric("MediGuard Injection Block", f"{metrics['injection_block_rate'] * 100:.1f}%", "+100% (Target)")

def main():
    st.set_page_config(
        page_title="🛡️ MediGuard: Air-Gapped Semantic Reconstruction",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🛡️ MediGuard: Air-Gapped Semantic Reconstruction")
    st.markdown("---")
    
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.subheader("🏥 Clinical Input")
        user_query = st.text_area(
            "Enter Patient History / Query:", 
            height=200, 
            placeholder="Mrs. Gupta is a 67-year-old female..."
        )
        submit_button = st.button("🚀 Process Secure Query", type="primary", use_container_width=True)

    with col_output:
        st.subheader("📜 Reconstructed Clinical Analysis")
        answer_placeholder = st.empty()
        answer_placeholder.info("Waiting for security clearance to display output...")

    st.markdown("---")
    st.subheader("⚙️ System Architecture Monitor")
    
    status_holder = st.empty()
    
    with st.expander("🛠️ View Defense-in-Depth Layer Details (L1 - L5)", expanded=False):
        st.markdown("#### Real-time Air-Gap Reconstruction Status")
        l1_col, a1, l3_col, a2, l2_col, a3, l4_col, a4, l5_col = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2, 0.5, 2])
        
        with l1_col:
            st.markdown("**L1: Anomaly**")
            l1_holder = st.empty()
            l1_holder.info("Nothing reached here")
        with a1: st.markdown("### >")
            
        with l3_col:
            st.markdown("**L3: Sentinel**")
            l3_holder = st.empty()
            l3_holder.info("Nothing reached here")
        with a2: st.markdown("### >")
            
        with l2_col:
            st.markdown("**L2: Sandbox**")
            l2_holder = st.empty()
            l2_holder.info("Nothing reached here")
        with a3: st.markdown("### >")
            
        with l4_col:
            st.markdown("**L4: Grounding**")
            l4_holder = st.empty()
            l4_holder.info("Nothing reached here")
        with a4: st.markdown("### >")
            
        with l5_col:
            st.markdown("**L5: Redactor**")
            l5_holder = st.empty()
            l5_holder.info("Nothing reached here")

    st.markdown("---")
    with st.expander("📊 Run Security Benchmarks", expanded=False):
        st.write("Evaluate MediGuard efficiency against Standard Semantic Injections.")
        if st.button("Execute Stress Test"):
            run_benchmarks()

    if submit_button:
        if not user_query.strip():
            st.warning("Please enter a query.")
            return

        l1_holder.info("Nothing reached here")
        l3_holder.info("Nothing reached here")
        l2_holder.info("Nothing reached here")
        l4_holder.info("Nothing reached here")
        l5_holder.info("Nothing reached here")
        answer_placeholder.empty()
        
        with status_holder.status("🚀 MediGuard Pipeline Initialized...", expanded=True) as status:
            # L1
            l1_holder.warning("⏳ Processing...")
            st.write("Checking L1: Anomaly...")
            is_safe, error_msg = heuristic_pre_filter(user_query)
            if not is_safe:
                l1_holder.error("❌ Blocked")
                status.update(label="🚨 REJECTED AT L1", state="error")
                answer_placeholder.error(f"**Security Violation (L1):** {error_msg}")
                return
            l1_holder.success("✅ Passed L1")
                
            # L3
            l3_holder.warning("⏳ Processing...")
            st.write("Checking L3: Sentinel...")
            is_injection = check_injection_hf(user_query)
            if is_injection:
                l3_holder.error("❌ Blocked")
                status.update(label="🚨 REJECTED AT L3", state="error")
                answer_placeholder.error("**Security Violation (L3):** Malicious intent detected.")
                return
            l3_holder.success("✅ Passed L3")
            
            try:
                # L2
                l2_holder.warning("⏳ Processing...")
                st.write("Executing L2: Sandbox...")
                json_data = extract_clinical_entities(user_query)
                if json_data.get("action_requested") == "INVALID":
                     l2_holder.error("❌ Blocked")
                     status.update(label="🚨 REJECTED AT L2", state="error")
                     answer_placeholder.error("**Security Violation (L2):** Non-clinical patterns.")
                     return
                l2_holder.success("✅ Extracted L2")
                l2_holder.json(json_data)

                # L4
                l4_holder.warning("⏳ Processing...")
                st.write("Executing L4: Grounding...")
                sterile_prompt, error_msg = validate_and_recompile(json_data)
                if sterile_prompt is None:
                    l4_holder.error("❌ Blocked")
                    status.update(label="🚨 REJECTED AT L4", state="error")
                    answer_placeholder.error(f"**Security Violation (L4):** {error_msg}")
                    return
                l4_holder.success("✅ Grounded L4")
                
                # L5
                l5_holder.warning("⏳ Processing...")
                st.write("Executing L5: Final Reasoner...")
                raw_response = call_clinical_assistant(sterile_prompt)
                final_answer = pii_redactor(raw_response)
                l5_holder.success("✅ Finalized L5")
                
                status.update(label="✨ Pipeline Complete", state="complete", expanded=False)
                answer_placeholder.success(f"{final_answer}")

            except Exception as e:
                status.update(label="System Error", state="error")
                answer_placeholder.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
