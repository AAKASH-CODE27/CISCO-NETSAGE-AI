"""
Ground-Truth Isolation Regression Tests for NetSage AI (Phase 6).

Verifies that ground-truth fields (expected_fault, expected_fix, osi_layer,
concept, severity) CANNOT leak into AI-facing requests or prompt strings.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from ai.diagnosis import build_user_prompt
from ai.models import DiagnosisRequest
from data.models import TroubleshootingCase, build_ai_input

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_ground_truth_isolation_model():
    """Verify that DiagnosisRequest Pydantic model does not contain ground-truth fields."""
    req_fields = set(DiagnosisRequest.model_fields.keys())
    
    # Strictly prohibited fields in AI input
    forbidden_fields = {"expected_fault", "expected_fix", "osi_layer", "concept", "severity", "expected_root_cause"}
    
    leaked = req_fields.intersection(forbidden_fields)
    assert not leaked, f"Ground-truth fields found in DiagnosisRequest model: {leaked}"


def test_ground_truth_isolation_builder():
    """Verify that build_ai_input() produces an object without ground-truth attributes."""
    case = TroubleshootingCase(
        case_id="NET-999",
        concept="VLAN",
        symptom="Hosts cannot communicate across switches",
        topology_note="PC1 -> SW1 -> SW2 -> PC2",
        show_outputs="SW1# show vlan brief...",
        expected_fault="VLAN 30 is missing on SW2 database",
        osi_layer="Layer 2",
        severity="High",
        expected_fix="Create VLAN 30 on SW2",
        verification="show vlan brief",
    )

    ai_input = build_ai_input(case)

    # Assert object type
    assert isinstance(ai_input, DiagnosisRequest)
    
    # Assert public fields are preserved
    assert ai_input.case_id == "NET-999"
    assert ai_input.symptom == case.symptom
    assert ai_input.topology_note == case.topology_note
    assert ai_input.show_outputs == case.show_outputs

    # Assert ground-truth attributes are not on the DiagnosisRequest object
    assert not hasattr(ai_input, "expected_fault")
    assert not hasattr(ai_input, "expected_fix")
    assert not hasattr(ai_input, "osi_layer")
    assert not hasattr(ai_input, "concept")
    assert not hasattr(ai_input, "severity")


def test_ground_truth_isolation_prompt_string():
    """Verify prompt formatting does not leak ground-truth text into the LLM prompt."""
    case = TroubleshootingCase(
        case_id="NET-888",
        concept="DHCP",
        symptom="Clients fail to get IP address",
        topology_note="Clients -> Switch -> Router",
        show_outputs="show ip dhcp pool LAN...",
        expected_fault="SECRET_FAULT_STRING_DHCP_POOL_EXHAUSTED",
        osi_layer="Layer 7",
        severity="Critical",
        expected_fix="SECRET_FIX_STRING_EXPAND_POOL",
        verification="SECRET_VERIFICATION_CMD",
    )

    ai_input = build_ai_input(case)
    prompt = build_user_prompt(ai_input)

    assert "SECRET_FAULT_STRING" not in prompt
    assert "SECRET_FIX_STRING" not in prompt
    assert "SECRET_VERIFICATION_CMD" not in prompt
    assert "Critical" not in prompt
    assert "Layer 7" not in prompt


def test_all_35_cases_ground_truth_isolation():
    """Verify ground-truth isolation across all 35 cases in data/cases.csv."""
    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cases = [TroubleshootingCase(**row) for row in reader]

    assert len(cases) == 35

    for case in cases:
        ai_input = build_ai_input(case)
        prompt = build_user_prompt(ai_input)

        # Confirm exact expected_fault is not present in prompt unless it literally repeats the symptom/output
        # (Check unique ground-truth terms like expected_fix)
        fix_tokens = case.expected_fix.split()
        if len(fix_tokens) > 3:
            long_fix_phrase = " ".join(fix_tokens[:4])
            assert long_fix_phrase.lower() not in prompt.lower() or long_fix_phrase.lower() in case.show_outputs.lower()


if __name__ == "__main__":
    pytest.main([__file__])
