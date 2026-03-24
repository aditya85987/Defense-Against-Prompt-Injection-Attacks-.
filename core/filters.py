import re

def heuristic_pre_filter(prompt: str) -> tuple[bool, str | None]:
    """
    Layer 1: Anomaly Detection (Heuristic Pre-filter)
    Rejects inputs longer than 1000 characters or containing high-entropy patterns 
    (specifically Base64 padding '==').
    """
    if len(prompt) > 1000:
        return False, "Security Violation: Input exceeds maximum allowed length (1000 characters)."
    
    if "==" in prompt:
        return False, "Security Violation: High-entropy character patterns (Base64-like) detected."
    
    return True, None

def pii_redactor(text: str) -> str:
    """
    Layer 5: PII Redaction
    Masks 9-digit SSNs, phone numbers, and email addresses with '[REDACTED]'.
    """
    # SSN: 000-00-0000 or 000000000
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'
    
    # Phone numbers: various formats
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    
    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    redacted_text = text
    redacted_text = re.sub(ssn_pattern, '[REDACTED]', redacted_text)
    redacted_text = re.sub(phone_pattern, '[REDACTED]', redacted_text)
    redacted_text = re.sub(email_pattern, '[REDACTED]', redacted_text)
    
    return redacted_text
