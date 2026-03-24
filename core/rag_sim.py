import json

# Simulated Clinical Protocol Database (RAG Layer)
# Extended to cover a wide range of clinical domains
CLINICAL_PROTOCOLS = {
    "toxicology": (
        "Protocol 4.2-TOX: Standard protocol requires verifying patient weight and administering "
        "Naloxone (0.4-2.0mg IV/IM/SC) for suspected opioid overdose. Monitor respiratory rate "
        "and maintain airway. Re-dose every 2-3 minutes if no response, up to 10mg."
    ),
    "cardiology": (
        "Protocol 5.1-CARD: Management of acute myocardial infarction requires immediate "
        "administration of Aspirin (162-325mg chewed), 12-lead ECG monitor, and evaluation for "
        "reperfusion therapy (PCI or Fibrinolytics) within 90 minutes of medical contact."
    ),
    "endocrinology": (
        "Protocol 3.8-ENDO: Diabetic Ketoacidosis (DKA) management involves initial fluid "
        "resuscitation with 1L Normal Saline over 1 hour, followed by continuous insulin "
        "infusion (0.1 units/kg/hr) once potassium levels are confirmed >3.3 mEq/L."
    ),
    "nephrology": (
        "Protocol 6.4-NEPH: Hyperkalemia management requires Calcium Gluconate (10ml of 10%) "
        "for membrane stabilization if ECG changes are present, followed by 10 units of IV "
        "Regular Insulin with 50ml of D50W to shift potassium intracellularly."
    ),
    "pulmonology": (
        "Protocol 7.1-PULM: For suspected Pulmonary Embolism (PE), initiate CT Pulmonary "
        "Angiography (CTPA) for diagnosis. Start anticoagulation with Heparin (80 units/kg IV "
        "bolus then 18 units/kg/hr infusion) if clinical probability is high. For massive PE "
        "with hemodynamic instability, consider thrombolysis with Alteplase (100mg IV over 2 hours)."
    ),
    "respiratory": (
        "Protocol 7.2-RESP: Asthma management follows a stepwise approach. Step 1: SABA as needed. "
        "Step 2: Low-dose ICS. Step 3: Low-dose ICS/LABA. Step 4: Medium-dose ICS/LABA. "
        "Step 5: High-dose ICS/LABA + add-on therapy (e.g., tiotropium, biologics). "
        "Acute exacerbations: Salbutamol nebulizer, systemic corticosteroids, supplemental O2."
    ),
    "pharmacology": (
        "Protocol 8.1-PHARM: When reviewing drug safety profiles, consider: mechanism of action, "
        "therapeutic index, common adverse effects, drug-drug interactions, contraindications, "
        "dose adjustments for renal/hepatic impairment, and monitoring parameters. "
        "Always consult current prescribing information for specific agents."
    ),
    "neurology": (
        "Protocol 9.1-NEURO: Acute ischemic stroke management requires CT head to exclude "
        "hemorrhage, then IV Alteplase (0.9mg/kg, max 90mg) within 4.5hr window. "
        "Consider mechanical thrombectomy for large vessel occlusion within 24hr. "
        "Monitor BP, glucose, temperature. Start antiplatelet therapy after 24hr."
    ),
    "psychiatry": (
        "Protocol 10.1-PSYCH: SSRI mechanism of action involves selective inhibition of "
        "serotonin reuptake transporter (SERT), increasing serotonin availability in the "
        "synaptic cleft. Common SSRIs include fluoxetine, sertraline, paroxetine, citalopram. "
        "Monitor for serotonin syndrome, suicidality in young adults, and discontinuation symptoms."
    ),
    "hematology": (
        "Protocol 11.1-HEMA: Warfarin interactions are extensive. Major interactions include "
        "CYP2C9 inhibitors (amiodarone, fluconazole), CYP3A4 inhibitors, Vitamin K-rich foods, "
        "NSAIDs (increased bleeding risk), and antibiotics. Monitor INR regularly with target "
        "2.0-3.0 for most indications. Bridging with LMWH may be needed perioperatively."
    ),
    "general": (
        "Protocol 1.0-GEN: For general medical inquiries, apply evidence-based clinical "
        "reasoning. Consult current clinical guidelines (e.g., WHO, NICE, AHA/ACC). "
        "Provide patient-centered, safety-focused information. Recommend specialist referral "
        "when the query falls outside general practice scope."
    ),
    "rheumatology": (
        "Protocol 12.1-RHEUM: NSAID dosing for adults: Ibuprofen 200-400mg every 4-6 hours "
        "(max 1200mg/day OTC, 3200mg/day Rx). Contraindicated in active GI bleed, severe renal "
        "impairment, third trimester pregnancy. Monitor renal function and GI symptoms."
    ),
    "emergency medicine": (
        "Protocol 13.1-EM: Triage and stabilize using ABCDE approach. Secure airway, ensure "
        "breathing, maintain circulation, assess disability (GCS), and fully expose patient. "
        "Obtain IV access, monitor vitals, point-of-care labs, and imaging as indicated."
    ),
    "internal medicine": (
        "Protocol 14.1-IM: Hypertension first-line treatments per JNC/ACC-AHA guidelines: "
        "Thiazide diuretics, ACE inhibitors, ARBs, or Calcium Channel Blockers. "
        "Target BP <130/80 mmHg for most adults. Lifestyle modifications: DASH diet, "
        "sodium restriction, weight management, regular exercise, alcohol moderation."
    ),
    "infectious disease": (
        "Protocol 15.1-ID: Empiric antibiotic selection should consider local resistance "
        "patterns, site of infection, patient immune status, and prior cultures. "
        "De-escalate based on culture results. Monitor for Clostridioides difficile infection "
        "with prolonged antibiotic use."
    ),
    "oncology": (
        "Protocol 16.1-ONC: Cancer treatment protocols require multidisciplinary team review. "
        "Staging, performance status, biomarkers, and patient preferences guide therapy selection. "
        "Monitor for treatment toxicities and provide supportive care."
    ),
    "gastroenterology": (
        "Protocol 17.1-GI: GERD management: lifestyle modifications, PPI therapy (omeprazole "
        "20mg daily for 8 weeks). For H. pylori: triple therapy with PPI + clarithromycin + "
        "amoxicillin for 14 days. Monitor for alarm symptoms requiring endoscopy."
    ),
    "dermatology": (
        "Protocol 18.1-DERM: Skin condition assessment requires thorough visual inspection, "
        "dermoscopy when available, and biopsy for suspicious lesions. Topical corticosteroids "
        "are first-line for inflammatory conditions. Refer for malignancy concerns."
    ),
}

def validate_and_recompile(json_data):
    """
    Function: Validates the extracted JSON and performs Simulated RAG Injection (Layer 4).
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
        
    # --- Layer 4: Simulated RAG Retrieval ---
    protocol_text = CLINICAL_PROTOCOLS.get(
        domain, 
        "No specific protocol found for this domain. Proceed with standard medical reasoning based on current clinical guidelines."
    )
    
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
