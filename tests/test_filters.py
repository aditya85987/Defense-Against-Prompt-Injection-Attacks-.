from core.filters import heuristic_pre_filter, pii_redactor

def test_heuristic_pre_filter():
    print("Testing Layer 1: Heuristic Pre-filter...")
    
    # Test 1: Normal input
    is_safe, msg = heuristic_pre_filter("What is the treatment for hypertension?")
    assert is_safe == True
    print("  Test 1 (Normal): PASSED")
    
    # Test 2: Long input (> 1000)
    long_input = "A" * 1001
    is_safe, msg = heuristic_pre_filter(long_input)
    assert is_safe == False
    assert "maximum allowed length" in msg
    print("  Test 2 (Long): PASSED")
    
    # Test 3: Base64 padding
    b64_input = "SGVsbG8gd29ybGQ=="
    is_safe, msg = heuristic_pre_filter(b64_input)
    assert is_safe == False
    assert "High-entropy character patterns" in msg
    print("  Test 3 (Base64): PASSED")

def test_pii_redactor():
    print("\nTesting Layer 5: PII Redaction...")
    
    # Test 1: SSN
    text = "The patient's SSN is 123-45-6789 and 987654321."
    redacted = pii_redactor(text)
    assert "123-45-6789" not in redacted
    assert "987654321" not in redacted
    assert redacted.count("[REDACTED]") == 2
    print("  Test 1 (SSN): PASSED")
    
    # Test 2: Phone
    text = "Call me at 555-123-4567 or +1 (123) 456-7890."
    redacted = pii_redactor(text)
    assert "555-123-4567" not in redacted
    assert "123) 456-7890" not in redacted
    assert "[REDACTED]" in redacted
    print("  Test 2 (Phone): PASSED")
    
    # Test 3: Email
    text = "Contact me at test.user@example.com."
    redacted = pii_redactor(text)
    assert "test.user@example.com" not in redacted
    assert "[REDACTED]" in redacted
    print("  Test 3 (Email): PASSED")

if __name__ == "__main__":
    try:
        test_heuristic_pre_filter()
        test_pii_redactor()
        print("\nAll filter tests PASSED!")
    except AssertionError as e:
        print(f"\nTest FAILED: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
