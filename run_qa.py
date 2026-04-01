"""Wrapper to capture qa_stress_test output cleanly on Windows."""
import subprocess, sys

result = subprocess.run(
    [sys.executable, "qa_stress_test.py"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=r"c:\Users\ASUS\Desktop\Satya\SEM8_project"
)

with open(r"c:\Users\ASUS\Desktop\Satya\SEM8_project\qa_output.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n\n--- STDERR ---\n")
        f.write(result.stderr)
