#!/usr/bin/env python3
"""Script to run tests and generate coverage report."""

import subprocess
import sys

# List of test modules and their test counts
test_files = [
    ("tests/test_agents.py", 24),
    ("tests/test_base_crew.py", 13),
    ("tests/test_commit_summary.py", 10),
    ("tests/test_crews_additional.py", 27),
    ("tests/test_enrichment.py", 10),
    ("tests/test_evaluators.py", 6),
    ("tests/test_improvement.py", 8),
    ("tests/test_init.py", 6),
    ("tests/test_init_additional.py", 11),
    ("tests/test_pipeline.py", 24),
    ("tests/test_wiki_selector.py", 10),
]

# Run tests with coverage
cmd = ["coverage", "run", "-m", "pytest", "tests/", "-v", "--tb=short", "-x"]
print("Running tests with coverage...")
result = subprocess.run(cmd, capture_output=True, text=True)

# Print test output
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Generate coverage report
print("\n" + "="*80)
print("COVERAGE REPORT")
print("="*80)

# Run coverage report
report_cmd = ["coverage", "report", "-m", "--skip-covered", "--skip-empty"]
report_result = subprocess.run(report_cmd, capture_output=True, text=True)
print(report_result.stdout)

# Also generate HTML report
html_cmd = ["coverage", "html"]
subprocess.run(html_cmd)

# Get coverage percentage
total_cmd = ["coverage", "report", "--format=total"]
total_result = subprocess.run(total_cmd, capture_output=True, text=True)
coverage_pct = float(total_result.stdout.strip())

print(f"\nTotal Coverage: {coverage_pct}%")

if coverage_pct >= 95:
    print("✅ Coverage target of 95% achieved!")
    sys.exit(0)
else:
    print(f"❌ Coverage is {coverage_pct}%, need 95%")
    sys.exit(1)