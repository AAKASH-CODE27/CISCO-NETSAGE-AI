"""
Tests for the NetSage AI Troubleshooting Cases Dataset (Phase 5).

Validates dataset loading, uniqueness, schema compliance, category distribution,
and strict ground-truth separation when converting cases into AI-safe inputs.
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.models import (
    TroubleshootingCase,
    IssueCategory,
    SeverityLevel,
    OSILayer,
    build_ai_input,
)
from ai.models import DiagnosisRequest


def test_dataset_file_exists():
    """Verify that data/cases.csv exists."""
    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    assert csv_path.exists(), "data/cases.csv does not exist"


def test_dataset_case_count_and_uniqueness():
    """Verify dataset contains exactly 35 cases with unique case_id values."""
    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 35, f"Expected 35 cases, got {len(rows)}"
    case_ids = [r["case_id"] for r in rows]
    assert len(set(case_ids)) == 35, f"Duplicate case IDs found in dataset"


def test_dataset_pydantic_parsing():
    """Verify all 35 rows parse cleanly into TroubleshootingCase objects."""
    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cases = [TroubleshootingCase(**row) for row in reader]

    assert len(cases) == 35
    for case in cases:
        assert case.case_id.startswith("NET-")
        assert len(case.symptom) > 0
        assert len(case.topology_note) > 0
        assert len(case.show_outputs) > 0
        assert len(case.expected_fault) > 0
        assert len(case.expected_fix) > 0
        assert len(case.verification) > 0


def test_category_distribution():
    """Verify exact category counts across the 8 required networking categories."""
    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cases = [TroubleshootingCase(**row) for row in reader]

    counts = {cat.value: 0 for cat in IssueCategory}
    for c in cases:
        counts[c.concept.value] += 1

    expected = {
        "VLAN": 5,
        "Gateway": 4,
        "DHCP": 5,
        "DNS": 4,
        "Routing": 5,
        "ACL": 4,
        "NAT": 4,
        "Wireless": 4,
    }

    assert counts == expected, f"Category distribution mismatch. Expected {expected}, got {counts}"


def test_valid_enums():
    """Verify all severities and OSI layers conform to predefined enum sets."""
    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cases = [TroubleshootingCase(**row) for row in reader]

    valid_severities = {s.value for s in SeverityLevel}
    valid_layers = {l.value for l in OSILayer}

    for c in cases:
        assert c.severity.value in valid_severities
        assert c.osi_layer.value in valid_layers


def test_ai_safe_transformation_ground_truth_exclusion():
    """Verify that converting a TroubleshootingCase to DiagnosisRequest excludes ground truth."""
    case = TroubleshootingCase(
        case_id="NET-099",
        concept=IssueCategory.VLAN,
        symptom="Cannot ping across switches",
        topology_note="PC1 -> SW1 -> SW2 -> PC2",
        show_outputs="show vlan brief...",
        expected_fault="VLAN 10 is missing on SW2",
        osi_layer=OSILayer.LAYER_2,
        severity=SeverityLevel.HIGH,
        expected_fix="Create VLAN 10 on SW2",
        verification="show vlan brief",
    )

    ai_req = build_ai_input(case)

    assert isinstance(ai_req, DiagnosisRequest)
    assert ai_req.case_id == "NET-099"
    assert ai_req.symptom == case.symptom
    assert ai_req.topology_note == case.topology_note
    assert ai_req.show_outputs == case.show_outputs

    # Verify ground-truth fields are completely absent from the AI request object
    assert not hasattr(ai_req, "expected_fault")
    assert not hasattr(ai_req, "expected_fix")
    assert not hasattr(ai_req, "osi_layer")
    assert not hasattr(ai_req, "concept")
    assert not hasattr(ai_req, "severity")

    # Confirm ground truth cannot be leaked via prompt formatting
    from ai.diagnosis import build_user_prompt
    user_prompt = build_user_prompt(ai_req)

    assert "missing on sw2" not in user_prompt.lower()
    assert "create vlan 10" not in user_prompt.lower()
    assert "layer 2" not in user_prompt.lower()


if __name__ == "__main__":
    print("Running test_cases_dataset.py...")
    test_dataset_file_exists()
    test_dataset_case_count_and_uniqueness()
    test_dataset_pydantic_parsing()
    test_category_distribution()
    test_valid_enums()
    test_ai_safe_transformation_ground_truth_exclusion()
    print("ALL DATASET TESTS PASSED.")
