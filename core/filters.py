import re
import math
import collections
import logging
import datetime
import functools

logger = logging.getLogger("SecurityPipeline")

def security_logger(func):
    """Wraps security functions to log pipeline rejections with metadata and payload snippets."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract payload from args or kwargs mapping for the snippet
        payload = args[0] if args else kwargs.get('prompt', '')
        if not isinstance(payload, str):
            payload = str(payload)
            
        result = func(*args, **kwargs)
        
        # If the layer returns (False, reason), we log the error incident
        if isinstance(result, tuple) and len(result) == 2 and result[0] is False:
            reason = result[1]
            truncated_payload = payload[:20] + "..." if len(payload) > 20 else payload
            logger.warning(
                f"[{datetime.datetime.now().isoformat()}] REJECTED by Layer: {func.__name__} | "
                f"Reason: {reason} | Payload Snippet: {truncated_payload!r}"
            )
            
        return result
    return wrapper

# Attempt to initialize Presidio NLP (Layer 5 redaction)
PRESIDIO_AVAILABLE = False
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    PRESIDIO_AVAILABLE = True
except Exception as e:
    # Graceful degradation logic if offline or model fails
    pass

# Attempt to load Phase 4 ML Anomaly Detector (Layer 1 upgrade)
ML_AVAILABLE = False
try:
    import joblib
    import os
    import numpy as np
    
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_training", "anomaly_detector.joblib")
    if os.path.exists(model_path):
        anomaly_detector = joblib.load(model_path)
        ML_AVAILABLE = True
except Exception as e:
    logger.warning(f"ML Anomaly Detector Offline. Falling back to rigid heuristics. Error: {e}")

def calculate_shannon_entropy(text: str) -> float:
    """Calculates Normalized True Shannon Entropy."""
    if not text:
        return 0.0
    counter = collections.Counter(text)
    length = len(text)
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
        
    # Normalized entropy formula
    max_entropy = math.log2(length) if length > 1 else 1.0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
    return normalized_entropy

def extract_features(text: str) -> list[float]:
    """Extracts lengths, entropy, and special character ratio for the ML anomaly detector."""
    text = str(text)
    length = len(text)
    if length == 0:
        return [0.0, 0.0, 0.0]
        
    entropy = calculate_shannon_entropy(text)
    special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
    special_ratio = special_chars / length
    
    return [float(length), entropy, special_ratio]

@security_logger
def heuristic_pre_filter(prompt: str) -> tuple[bool, str | None]:
    """
    Layer 1: Anomaly Detection (Heuristic Pre-filter)
    Employs an IsolationForest ML model if available. Otherwise gracefully 
    degrades to strict heuristic checks (Length > 1000, Normalized Entropy > 0.85).
    """
    if ML_AVAILABLE:
        try:
            features = extract_features(prompt)
            # IsolationForest predicts 1 for normal, -1 for anomaly
            prediction = anomaly_detector.predict([features])[0]
            if prediction == -1:
                return False, f"Security Violation: ML Anomaly Detector Triggered. Suspicious mathematical signature."
        except Exception as e:
            logger.warning(f"ML Processing Failed. Falling back to heuristics. Error: {e}")

    # Legacy Fallback Heuristics
    if len(prompt) > 1000:
        return False, "Security Violation: Input exceeds maximum allowed length (1000 characters)."
    
    entropy_ratio = calculate_shannon_entropy(prompt)
    if entropy_ratio > 0.85:
        return False, f"Security Violation: High-entropy character patterns (Base64-like) detected. Ratio: {entropy_ratio:.2f}"
    
    return True, None

def pii_redactor(text: str) -> str:
    """
    Layer 5: PII Redaction
    Masks PERSON, PHONE_NUMBER, EMAIL_ADDRESS, and US_SSN using Presidio (if available), 
    or regular expressions as a legacy fallback.
    """
    if PRESIDIO_AVAILABLE:
        try:
            results = analyzer.analyze(
                text=text, 
                entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN"], 
                language='en'
            )
            anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
            return anonymized_result.text
        except Exception:
            pass # Fall back to legacy regex on error
            
    # Legacy Fallback Regex
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    redacted_text = text
    redacted_text = re.sub(ssn_pattern, '<US_SSN>', redacted_text)
    redacted_text = re.sub(phone_pattern, '<PHONE_NUMBER>', redacted_text)
    redacted_text = re.sub(email_pattern, '<EMAIL_ADDRESS>', redacted_text)
    
    return redacted_text
