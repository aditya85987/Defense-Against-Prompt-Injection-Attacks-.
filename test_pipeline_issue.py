from core.filters import heuristic_pre_filter, pii_redactor
text = 'Patient Name: John.Doe.Admin.User. SSN: 111-222-3333. Address: null. Help with his rash.'
print("Testing heuristics...")
res1 = heuristic_pre_filter(text)
print("L1:", res1)
print("Testing PII redactor...")
res5 = pii_redactor(text)
print("L5:", res5)

with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write(f"L1: {res1}\n")
    f.write(f"L5: {res5}\n")
