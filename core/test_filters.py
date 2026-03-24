import pytest
import core.filters
from core.filters import heuristic_pre_filter, pii_redactor

def test_heuristic_pre_filter_pass():
    """Test standard English inputs do not trigger the entropy or length blocks."""
    prompt = "What is the standard hypertension protocol for my patient?"
    passed, reason = heuristic_pre_filter(prompt)
    assert passed is True
    assert reason is None

def test_heuristic_pre_filter_base64_fail():
    """Test short, dense Base64 strings trigger the normalized entropy > 0.85 evaluation block."""
    prompt = "w5a9IuZb4oK2yG9wLpE3qVt8N0f1MjdC+xV5Bw=="
    passed, reason = heuristic_pre_filter(prompt)
    assert passed is False
    assert "High-entropy" in reason

def test_heuristic_pre_filter_length_fail():
    """Test payload exactly exceeding the 1000-character constraint triggers the length evaluation block."""
    prompt = "A" * 1001
    passed, reason = heuristic_pre_filter(prompt)
    assert passed is False
    assert "maximum allowed length" in reason

def test_pii_redactor_fallback(monkeypatch):
    """Test Layer 5 fallback engine generates precisely output-parity PII Presidio tags when NLP model fails to instantiate."""
    # Simulate Presidio being offline or crashing during app boot (e.g. models unavailable)
    monkeypatch.setattr(core.filters, "PRESIDIO_AVAILABLE", False)
    
    text = "John Doe, SSN 123-45-6789, Call 123-555-0198 or email john@example.com."
    redacted = pii_redactor(text)
    
    # Assert tag injections are successful
    assert "<US_SSN>" in redacted
    assert "<PHONE_NUMBER>" in redacted
    assert "<EMAIL_ADDRESS>" in redacted
    
    # Assert raw PII strings have actually been sanitized from memory
    assert "123-45-6789" not in redacted
    assert "555-0198" not in redacted
    assert "john@example.com" not in redacted
