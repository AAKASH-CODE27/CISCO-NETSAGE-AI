"""
Unit tests for evaluation matching algorithms and evaluator engine (Phase 6).
"""

from __future__ import annotations

import pytest

from ai.models import DiagnosisResponse
from data.models import TroubleshootingCase
from evaluation import (
    evaluate_case,
    evaluate_evidence_grounding,
    evaluate_root_cause_match,
    evaluate_severity_match,
)
from rule_checker.models import RuleResult, RuleStatus


def test_root_cause_exact_match():
    """Exact root cause string matches."""
    fault = "PC1 and PC2 are assigned to different VLANs (10 and 20)."
    ai_cause = "PC1 and PC2 are assigned to different VLANs (10 and 20)."
    assert evaluate_root_cause_match(ai_cause, fault) is True


def test_root_cause_normalized_controlled_equivalence():
    """Normalized controlled equivalence matches."""
    fault = "Missing VLAN 10 in database"
    ai_cause = "VLAN 10 is missing from the switch database"
    assert evaluate_root_cause_match(ai_cause, fault) is True


def test_root_cause_unrelated_mismatch():
    """Unrelated causes do not match."""
    fault = "Missing VLAN 10"
    ai_cause = "Outbound ACL blocks traffic on port 80"
    assert evaluate_root_cause_match(ai_cause, fault) is False


def test_severity_match_case_insensitive():
    """Severity matches case-insensitively."""
    assert evaluate_severity_match("High", "HIGH") is True
    assert evaluate_severity_match("medium", "Medium") is True


def test_severity_mismatch():
    """Mismatched severities do not match."""
    assert evaluate_severity_match("Medium", "High") is False
    assert evaluate_severity_match("Low", "Critical") is False


def test_evidence_grounding_valid():
    """Evidence citing valid input entities is grounded."""
    case = TroubleshootingCase(
        case_id="NET-001",
        concept="VLAN",
        symptom="PC1 cannot ping PC2",
        topology_note="PC1 -> SW1 -> SW2 -> PC2",
        show_outputs="SW1# show vlan brief\n10 Sales active Fa0/1",
        expected_fault="VLAN mismatch",
        osi_layer="Layer 2",
        severity="Medium",
        expected_fix="Fix VLAN",
        verification="show vlan",
    )

    ai_evidence = ["SW1 interface Fa0/1 is assigned to VLAN 10"]
    assert evaluate_evidence_grounding(ai_evidence, case) is True


def test_evidence_grounding_hallucinated_interface():
    """Evidence citing non-existent interface is marked ungrounded."""
    case = TroubleshootingCase(
        case_id="NET-001",
        concept="VLAN",
        symptom="PC1 cannot ping PC2",
        topology_note="PC1 -> SW1 -> SW2 -> PC2",
        show_outputs="SW1# show interface Gi0/1 switchport",
        expected_fault="VLAN mismatch",
        osi_layer="Layer 2",
        severity="Medium",
        expected_fix="Fix VLAN",
        verification="show vlan",
    )

    # Gi0/99 does not exist in show outputs
    ai_evidence = ["Interface GigabitEthernet0/99 has 100% packet loss"]
    assert evaluate_evidence_grounding(ai_evidence, case) is False


def test_rule_checker_findings_passed_as_evidence():
    """Rule checker findings are passed to evaluation."""
    case = TroubleshootingCase(
        case_id="NET-005",
        concept="Gateway",
        symptom="Host cannot reach router",
        topology_note="Host -> R1",
        show_outputs="R1# show ip interface brief",
        expected_fault="Gateway mismatch",
        osi_layer="Layer 3",
        severity="High",
        expected_fix="Fix GW",
        verification="ping",
    )

    rf = [RuleResult(rule="gateway_mismatch", status=RuleStatus.FAIL, severity="High", message="Gateway 192.168.1.254 outside subnet", evidence=["Gateway 192.168.1.254"])]

    diag = DiagnosisResponse(
        case_id="NET-005",
        root_cause="Incorrect default gateway 192.168.1.254",
        confidence=0.9,
        evidence=["Gateway 192.168.1.254 is outside host subnet"],
        next_command="ipconfig",
        fix_steps=["Change gateway"],
        severity="High",
    )

    res = evaluate_case(case, diag, rule_findings=rf)
    assert res.ai_success is True
    assert res.root_cause_match is True
    assert len(res.rule_checker_findings) == 1
    assert "Gateway 192.168.1.254" in res.rule_checker_findings[0]


def test_invalid_ai_response_handling():
    """Evaluator handles None / failed AI response cleanly."""
    case = TroubleshootingCase(
        case_id="NET-001",
        concept="VLAN",
        symptom="PC1 cannot ping PC2",
        topology_note="PC1 -> SW1",
        show_outputs="SW1# show vlan",
        expected_fault="VLAN mismatch",
        osi_layer="Layer 2",
        severity="Medium",
        expected_fix="Fix VLAN",
        verification="show vlan",
    )

    res = evaluate_case(case, diagnosis_response=None, error="API timeout")
    assert res.ai_success is False
    assert res.root_cause_match is False
    assert res.error == "API timeout"


if __name__ == "__main__":
    pytest.main([__file__])
