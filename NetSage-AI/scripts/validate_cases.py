"""
Dataset Validation Script for NetSage AI (Phase 5).

Validates:
1. data/cases.csv file presence and readability.
2. Exactly 35 cases present with unique case_id values.
3. 8 required issue categories with exact target counts.
4. Non-empty evidence and ground-truth fields.
5. Pydantic validation via TroubleshootingCase model.
6. Ground-truth separation (AI-safe DiagnosisRequest construction).
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.models import TroubleshootingCase, IssueCategory, SeverityLevel, OSILayer, build_ai_input


def validate_dataset() -> bool:
    csv_path = PROJECT_ROOT / "data" / "cases.csv"

    print("=" * 60)
    print("NetSage AI — Dataset Validation (Phase 5)")
    print("=" * 60)

    if not csv_path.exists():
        print(f"FAIL: {csv_path} does not exist.")
        return False

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"File loaded: {csv_path.name}")
    print(f"Total cases found: {len(rows)}")

    # Check 1: Target count
    if len(rows) != 35:
        print(f"FAIL: Expected exactly 35 cases, got {len(rows)}.")
        return False
    print("Count check (35 cases): PASS")

    # Check 2: Unique IDs
    case_ids = [r["case_id"] for r in rows]
    if len(set(case_ids)) != len(case_ids):
        print(f"FAIL: Duplicate case IDs found: {case_ids}")
        return False
    print("Unique IDs: PASS")

    # Check 3: Pydantic Validation & Ground Truth Exclusion
    parsed_cases: list[TroubleshootingCase] = []
    category_counts: dict[str, int] = {cat.value: 0 for cat in IssueCategory}

    for i, row in enumerate(rows, start=1):
        try:
            case = TroubleshootingCase(**row)
            parsed_cases.append(case)
            category_counts[case.concept.value] += 1
        except Exception as exc:
            print(f"FAIL: Row {i} ({row.get('case_id')}) failed Pydantic validation: {exc}")
            return False

        # Test AI-safe conversion (ground truth exclusion)
        ai_input = build_ai_input(case)
        if hasattr(ai_input, "expected_fault") or hasattr(ai_input, "osi_layer") or hasattr(ai_input, "expected_fix"):
            print(f"FAIL: AI input for {case.case_id} leaks ground-truth fields!")
            return False

    print("Pydantic Schema & Ground-Truth Exclusion: PASS")

    # Check 4: Category Distribution
    expected_distribution = {
        "VLAN": 5,
        "Gateway": 4,
        "DHCP": 5,
        "DNS": 4,
        "Routing": 5,
        "ACL": 4,
        "NAT": 4,
        "Wireless": 4,
    }

    print("\nCoverage Breakdown:")
    distribution_pass = True
    for category, expected in expected_distribution.items():
        actual = category_counts.get(category, 0)
        status = "PASS" if actual == expected else f"FAIL (Expected {expected}, got {actual})"
        if actual != expected:
            distribution_pass = False
        print(f"  - {category:<10}: {actual}  [{status}]")

    if not distribution_pass:
        print("\nFAIL: Category distribution mismatch!")
        return False

    print("\n" + "=" * 60)
    print("RESULT: PASS")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
