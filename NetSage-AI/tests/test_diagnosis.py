"""
Tests for the AI diagnosis layer (Phase 4).

These tests validate:
- DiagnosisRequest / DiagnosisResponse models
- Prompt construction (no ground-truth leakage)
- JSON extraction from raw LLM text
- Response parsing and validation
- Confidence bounds

NO actual LLM API calls are made.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.models import DiagnosisRequest, DiagnosisResponse
from ai.diagnosis import (
    build_user_prompt,
    _extract_json,
    _format_rule_findings,
    parse_diagnosis_response,
)
from rule_checker.models import RuleResult, RuleStatus

passed = 0
failed = 0


def assert_eq(test_name: str, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {test_name}")
        print(f"    Expected: {expected}")
        print(f"    Got:      {actual}")


def assert_true(test_name: str, condition: bool, msg: str = ""):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {test_name} {msg}")


def assert_raises(test_name: str, exc_type, fn, *args, **kwargs):
    global passed, failed
    try:
        fn(*args, **kwargs)
        failed += 1
        print(f"  FAIL: {test_name} -- no exception raised")
    except exc_type:
        passed += 1
    except Exception as e:
        failed += 1
        print(f"  FAIL: {test_name} -- wrong exception: {type(e).__name__}: {e}")


# ===================================================================
# DiagnosisRequest model tests
# ===================================================================

def test_request_creation():
    """Basic DiagnosisRequest creation."""
    req = DiagnosisRequest(
        case_id="NET-001",
        symptom="Cannot ping",
        topology_note="PC -> SW -> R",
        show_outputs="show ip route\n...",
    )
    assert_eq("req_case_id", req.case_id, "NET-001")
    assert_eq("req_symptom", req.symptom, "Cannot ping")
    assert_eq("req_findings_default", len(req.rule_findings), 0)


def test_request_with_findings():
    """DiagnosisRequest with rule-checker findings."""
    finding = RuleResult(
        rule="gateway_mismatch",
        status=RuleStatus.FAIL,
        severity="High",
        message="Gateway outside subnet",
        evidence=["IP: 10.0.0.1", "GW: 10.0.1.1"],
    )
    req = DiagnosisRequest(
        case_id="NET-005",
        symptom="No internet",
        topology_note="PC -> R",
        show_outputs="...",
        rule_findings=[finding],
    )
    assert_eq("req_with_findings", len(req.rule_findings), 1)
    assert_eq("req_finding_status", req.rule_findings[0].status, RuleStatus.FAIL)


# ===================================================================
# DiagnosisResponse model tests
# ===================================================================

def test_response_valid():
    """Valid DiagnosisResponse creation."""
    resp = DiagnosisResponse(
        case_id="NET-001",
        root_cause="Missing VLAN",
        confidence=0.92,
        evidence=["VLAN 10 absent from database"],
        next_command="show vlan brief",
        fix_steps=["Create VLAN 10", "Verify"],
    )
    assert_eq("resp_root_cause", resp.root_cause, "Missing VLAN")
    assert_eq("resp_confidence", resp.confidence, 0.92)
    assert_eq("resp_evidence_len", len(resp.evidence), 1)


def test_response_confidence_bounds():
    """Confidence must be between 0.0 and 1.0."""
    from pydantic import ValidationError
    assert_raises("confidence_above_1", ValidationError,
                  DiagnosisResponse,
                  root_cause="test", confidence=1.5,
                  evidence=[], next_command="x", fix_steps=[])
    assert_raises("confidence_below_0", ValidationError,
                  DiagnosisResponse,
                  root_cause="test", confidence=-0.1,
                  evidence=[], next_command="x", fix_steps=[])


def test_response_confidence_zero():
    """Confidence of 0.0 is valid (insufficient evidence)."""
    resp = DiagnosisResponse(
        root_cause="Unknown",
        confidence=0.0,
        evidence=[],
        next_command="show ip route",
        fix_steps=["Investigate"],
    )
    assert_eq("confidence_zero", resp.confidence, 0.0)


def test_response_confidence_one():
    """Confidence of 1.0 is valid."""
    resp = DiagnosisResponse(
        root_cause="Confirmed fault",
        confidence=1.0,
        evidence=["Direct proof"],
        next_command="verify",
        fix_steps=["Fix it"],
    )
    assert_eq("confidence_one", resp.confidence, 1.0)


# ===================================================================
# Prompt construction tests
# ===================================================================

def test_prompt_excludes_ground_truth():
    """The user prompt must NOT contain ground-truth fields."""
    req = DiagnosisRequest(
        case_id="NET-010",
        symptom="No DHCP",
        topology_note="VLAN 20 -> SW -> DHCP Server",
        show_outputs="show run interface Vlan20...",
        rule_findings=[],
    )
    prompt = build_user_prompt(req)
    assert_true("no_expected_fault", "expected_fault" not in prompt.lower())
    assert_true("no_osi_layer", "osi_layer" not in prompt.lower())
    assert_true("no_concept_field", "concept:" not in prompt.lower())
    assert_true("prompt_has_case_id", "NET-010" in prompt)
    assert_true("prompt_has_symptom", "No DHCP" in prompt)
    assert_true("prompt_has_topology", "VLAN 20" in prompt)


def test_prompt_includes_rule_findings():
    """Rule-checker findings appear in the prompt."""
    finding = RuleResult(
        rule="missing_vlan",
        status=RuleStatus.FAIL,
        severity="Medium",
        message="VLAN 10 missing",
        evidence=["SW1 Fa0/2: VLAN 10"],
    )
    req = DiagnosisRequest(
        case_id="NET-002",
        symptom="No connectivity",
        topology_note="PC -> SW",
        show_outputs="...",
        rule_findings=[finding],
    )
    prompt = build_user_prompt(req)
    assert_true("findings_in_prompt", "missing_vlan" in prompt)
    assert_true("fail_in_prompt", "FAIL" in prompt)


def test_format_rule_findings_empty():
    """Empty findings produce a descriptive message."""
    result = _format_rule_findings([])
    assert_true("empty_findings_msg", "No rule-checker findings" in result)


# ===================================================================
# JSON extraction tests
# ===================================================================

def test_extract_json_raw():
    """Extract JSON from a raw response."""
    raw = '{"root_cause": "test", "confidence": 0.9}'
    extracted = _extract_json(raw)
    data = json.loads(extracted)
    assert_eq("extract_raw_rc", data["root_cause"], "test")


def test_extract_json_with_fence():
    """Extract JSON from markdown code fence."""
    raw = 'Here is the result:\n```json\n{"root_cause": "fenced"}\n```\nDone.'
    extracted = _extract_json(raw)
    data = json.loads(extracted)
    assert_eq("extract_fence_rc", data["root_cause"], "fenced")


def test_extract_json_with_preamble():
    """Extract JSON when the LLM adds text before it."""
    raw = 'Based on my analysis:\n\n{"root_cause": "preamble_test", "confidence": 0.8}'
    extracted = _extract_json(raw)
    data = json.loads(extracted)
    assert_eq("extract_preamble", data["root_cause"], "preamble_test")


def test_extract_json_no_json():
    """Raise ValueError when no JSON is present."""
    assert_raises("extract_no_json", ValueError, _extract_json, "No JSON here at all")


def test_extract_json_nested():
    """Handle nested braces in fix_steps or evidence."""
    raw = '{"root_cause": "test", "evidence": ["item {1}"], "confidence": 0.5, "next_command": "x", "fix_steps": ["step"]}'
    extracted = _extract_json(raw)
    data = json.loads(extracted)
    assert_eq("extract_nested", data["root_cause"], "test")


# ===================================================================
# parse_diagnosis_response tests
# ===================================================================

def test_parse_valid_response():
    """Parse a well-formed LLM response."""
    raw = json.dumps({
        "case_id": "NET-007",
        "root_cause": "Gateway subnet mismatch",
        "confidence": 0.88,
        "evidence": ["Server IP: 10.0.0.10/24", "Gateway: 10.0.1.1"],
        "next_command": "show ip interface brief",
        "fix_steps": ["Correct the gateway", "Verify"],
        "severity": "High",
    })
    resp = parse_diagnosis_response(raw, case_id="NET-007")
    assert_eq("parse_case_id", resp.case_id, "NET-007")
    assert_eq("parse_confidence", resp.confidence, 0.88)
    assert_eq("parse_severity", resp.severity, "High")


def test_parse_fills_case_id():
    """If case_id is missing from LLM output, it is filled from the request."""
    raw = json.dumps({
        "root_cause": "test",
        "confidence": 0.5,
        "evidence": [],
        "next_command": "x",
        "fix_steps": [],
    })
    resp = parse_diagnosis_response(raw, case_id="NET-099")
    assert_eq("parse_fill_id", resp.case_id, "NET-099")


def test_parse_invalid_json():
    """Raise ValueError for unparseable responses."""
    assert_raises("parse_bad_json", (ValueError, Exception),
                  parse_diagnosis_response, "not json at all", "X")


# ===================================================================
# System prompt tests
# ===================================================================

def test_system_prompt_exists():
    """The production prompt file must exist and contain key sections."""
    from ai.diagnosis import _load_system_prompt
    prompt = _load_system_prompt()
    assert_true("prompt_has_role", "expert network troubleshooting" in prompt.lower())
    assert_true("prompt_has_evidence_rules", "evidence rules" in prompt.lower())
    assert_true("prompt_has_json_schema", "root_cause" in prompt)
    assert_true("prompt_has_confidence", "confidence" in prompt.lower())
    assert_true("prompt_has_worked_example", "worked example" in prompt.lower())
    assert_true("prompt_has_safety", "human review" in prompt.lower())


# ===================================================================
# Runner
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("NetSage AI -- AI Diagnosis Tests (Offline)")
    print("=" * 60)

    print("\n--- DiagnosisRequest Model ---")
    test_request_creation()
    test_request_with_findings()

    print("\n--- DiagnosisResponse Model ---")
    test_response_valid()
    test_response_confidence_bounds()
    test_response_confidence_zero()
    test_response_confidence_one()

    print("\n--- Prompt Construction ---")
    test_prompt_excludes_ground_truth()
    test_prompt_includes_rule_findings()
    test_format_rule_findings_empty()

    print("\n--- JSON Extraction ---")
    test_extract_json_raw()
    test_extract_json_with_fence()
    test_extract_json_with_preamble()
    test_extract_json_no_json()
    test_extract_json_nested()

    print("\n--- Response Parsing ---")
    test_parse_valid_response()
    test_parse_fills_case_id()
    test_parse_invalid_json()

    print("\n--- System Prompt ---")
    test_system_prompt_exists()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL AI DIAGNOSIS TESTS PASSED.")
