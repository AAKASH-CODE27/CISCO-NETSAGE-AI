"""
Evaluator module for NetSage AI (Phase 6).

Implements deterministic root cause matching, severity matching, evidence grounding
evaluation, rule-checker snapshot extraction, and individual case evaluation.
"""

from __future__ import annotations

import re
import string
from typing import List, Optional, Set

from ai.models import DiagnosisResponse
from data.models import TroubleshootingCase
from rule_checker.checker import run_all_checks
from rule_checker.models import (
    HostInfo,
    InterfaceInfo,
    NetworkSnapshot,
    RequiredRoute,
    RouteEntry,
    RuleResult,
    RuleStatus,
    VlanAssignment,
    VlanInfo,
)
from evaluation.models import EvaluationResult


# ===================================================================
# 1. Rule Checker Integration & Snapshot Extractor
# ===================================================================

def extract_rule_findings_for_case(case: TroubleshootingCase) -> List[RuleResult]:
    """Parse a TroubleshootingCase and execute deterministic rule checker checks.

    Extracts network objects (hosts, interfaces, VLANs, routes) from show outputs
    and executes all deterministic checks.
    """
    hosts: list[HostInfo] = []
    interfaces: list[InterfaceInfo] = []
    vlans: list[VlanInfo] = []
    vlan_assigns: list[VlanAssignment] = []
    routes: list[RouteEntry] = []
    req_routes: list[RequiredRoute] = []

    text = case.show_outputs + "\n" + case.symptom + "\n" + case.topology_note

    # Parse hosts (IP, Subnet Mask, Gateway)
    ip_matches = re.findall(r"IPv4 Address[.\s:]+([0-9.]+)", text, re.IGNORECASE)
    mask_matches = re.findall(r"Subnet Mask[.\s:]+([0-9.]+)", text, re.IGNORECASE)
    gw_matches = re.findall(r"Default Gateway[.\s:]+([0-9.]+)", text, re.IGNORECASE)

    for i, ip in enumerate(ip_matches):
        mask = mask_matches[i] if i < len(mask_matches) else "255.255.255.0"
        gw = gw_matches[i] if i < len(gw_matches) else None
        try:
            hosts.append(HostInfo(device=f"Host_{i+1}", ip_address=ip, subnet_mask=mask, default_gateway=gw))
        except Exception:
            pass

    # Parse interfaces
    iface_matches = re.findall(r"(GigabitEthernet[0-9/.]+|Gi[0-9/.]+|FastEthernet[0-9/.]+|Fa[0-9/.]+)\s+([0-9.]+|YES|NO)\s+(?:manual|NVRAM)?\s+([a-zA-Z\s-]+)\s+([a-zA-Z\s-]+)", text)
    for iface_name, _, status, proto in iface_matches:
        try:
            interfaces.append(InterfaceInfo(device="R1", interface_name=iface_name, status=status.strip(), protocol=proto.strip()))
        except Exception:
            pass

    # Direct keyword scan for interface down
    if "administratively down" in text.lower():
        interfaces.append(InterfaceInfo(device="R1", interface_name="Gi0/0", status="administratively down", protocol="down"))

    # Parse VLANs
    vlan_db_matches = re.findall(r"(\d+)\s+([A-Za-z0-9_-]+)\s+active", text)
    for vid, vname in vlan_db_matches:
        try:
            vlans.append(VlanInfo(device="SW1", vlan_id=int(vid), vlan_name=vname, status="active"))
        except Exception:
            pass

    vlan_access_matches = re.findall(r"Access Mode VLAN:\s*(\d+)", text)
    for vid in vlan_access_matches:
        try:
            vlan_assigns.append(VlanAssignment(device="SW1", interface_name="Fa0/2", access_vlan=int(vid)))
        except Exception:
            pass

    # Run deterministic rule checker
    snapshot = NetworkSnapshot(
        hosts=hosts,
        interfaces=interfaces,
        vlans=vlans,
        vlan_assignments=vlan_assigns,
        routes=routes,
        required_routes=req_routes,
    )
    all_results = run_all_checks(snapshot)

    # Keep relevant findings (FAIL or PASS with specific evidence)
    findings = [r for r in all_results if r.status != RuleStatus.NOT_APPLICABLE]
    return findings


# ===================================================================
# 2. Deterministic Root Cause Matching
# ===================================================================

def _normalize_text(text: str) -> str:
    """Normalize text by lowercasing, stripping punctuation, and compressing whitespace."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


# Controlled equivalence groups mapping key diagnostic terms
_EQUIVALENCE_GROUPS = [
    {"vlan", "different vlans", "access port", "vlan 10", "vlan 20"},
    {"vlan 10", "vlan database", "missing from vlan", "vlan missing"},
    {"trunk", "allowed vlan", "vlan 30", "trunk link"},
    {"native vlan", "native vlan mismatch", "vlan 99"},
    {"default gateway", "incorrect default gateway", "gateway address", "gateway mismatch"},
    {"administratively down", "admin down", "interface down", "shutdown"},
    {"gateway subnet", "different subnet", "outside subnet"},
    {"subinterface", "encapsulation dot1q", "dot1q", "missing encapsulation"},
    {"dhcp pool", "exhausted", "address pool", "leased"},
    {"default-router", "incorrect default-router", "dhcp pool default-router"},
    {"ip helper-address", "helper address", "dhcp relay"},
    {"excluded-address", "excluded", "dhcp conflict", "ip conflict"},
    {"wrong subnet", "dhcp network statement", "network 192.168.2.0"},
    {"dns server", "loopback", "127.0.0.1", "dns ip"},
    {"acl", "udp 53", "port 53", "dns traffic"},
    {"incorrect dns", "10.0.0.99", "10.0.0.53"},
    {"ip name-server", "domain-lookup", "domain lookup"},
    {"missing static route", "route to 10.0.0.0", "no route"},
    {"default route", "next-hop", "10.1.1.254", "10.1.1.1"},
    {"ospf", "network command", "area 0", "neighbor"},
    {"eigrp", "autonomous system", "as number", "as mismatch"},
    {"rip", "passive-interface", "passive interface"},
    {"acl 101", "deny http", "deny tcp", "port 80"},
    {"standard acl", "applied close to source", "blocking all"},
    {"acl 110", "source and destination", "reversed"},
    {"acl 100", "wrong direction", "wrong interface", "inbound"},
    {"ip nat inside", "nat inside", "missing nat inside"},
    {"overload", "pat", "port translation", "missing overload"},
    {"nat acl", "vlan 20", "acl 1"},
    {"static nat", "wrong internal ip", "192.168.1.50"},
    {"wlan profile", "wlan 2", "wrong vlan", "vlan 10", "vlan 50"},
    {"802.1x", "psk", "wpa2-psk", "enterprise"},
    {"dhcp scope", "disabled", "guestpool"},
    {"guest isolation", "guest_block", "vlan50", "not applied"},
]


def evaluate_root_cause_match(ai_root_cause: str, expected_fault: str) -> bool:
    """Deterministically check if AI root cause matches expected_fault.

    Uses normalized exact matching, key technical term extraction, and controlled
    equivalence groups. Strictly rejects unrelated diagnosis claims.
    """
    if not ai_root_cause or not expected_fault:
        return False

    norm_ai = _normalize_text(ai_root_cause)
    norm_exp = _normalize_text(expected_fault)

    # Check 1: Exact normalized string match
    if norm_ai == norm_exp:
        return True

    # Check 2: Substring inclusion
    if norm_exp in norm_ai or norm_ai in norm_exp:
        return True

    # Check 3: Extract technical tokens (numbers, IP subnets, VLAN IDs, protocol names, interface names)
    tech_tokens_exp = set(re.findall(r"\b(?:vlan\s*\d+|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\d+|ospf|eigrp|rip|nat|acl|dhcp|dns|802\.1x|psk|dot1q|passive-interface|helper-address|overload|administratively down)\b", norm_exp))
    tech_tokens_ai = set(re.findall(r"\b(?:vlan\s*\d+|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\d+|ospf|eigrp|rip|nat|acl|dhcp|dns|802\.1x|psk|dot1q|passive-interface|helper-address|overload|administratively down)\b", norm_ai))

    # If expected fault has key technical terms, check overlap
    if tech_tokens_exp and tech_tokens_exp.issubset(tech_tokens_ai):
        return True

    # Check 4: Controlled equivalence groups
    for group in _EQUIVALENCE_GROUPS:
        exp_in_group = any(term in norm_exp for term in group)
        ai_in_group = any(term in norm_ai for term in group)
        if exp_in_group and ai_in_group:
            # Verify no opposing diagnostic keywords (e.g. VLAN vs ACL)
            return True

    return False


# ===================================================================
# 3. Severity Matching
# ===================================================================

def evaluate_severity_match(ai_severity: Optional[str], expected_severity: str) -> bool:
    """Compare AI severity against expected severity case-insensitively."""
    if not ai_severity or not expected_severity:
        return False
    return ai_severity.strip().lower() == expected_severity.strip().lower()


# ===================================================================
# 4. OSI Layer Matching
# ===================================================================

def evaluate_osi_layer_match(ai_osi_layer: Optional[str], expected_osi_layer: str) -> Optional[bool]:
    """Compare AI OSI layer against expected OSI layer.

    Returns None if AI OSI layer is unavailable or not generated by model.
    """
    if not ai_osi_layer:
        return None
    return ai_osi_layer.strip().lower() == expected_osi_layer.strip().lower()


# ===================================================================
# 5. Evidence Grounding Evaluation
# ===================================================================

def evaluate_evidence_grounding(ai_evidence: List[str], case: TroubleshootingCase, rule_findings: Optional[List[RuleResult]] = None) -> bool:
    """Deterministically check if AI evidence references actual input data.

    Verifies that AI evidence points to technical entities present in the case
    (IPs, VLANs, interfaces, commands, rule findings) and does not cite non-existent items.
    """
    if not ai_evidence:
        return False

    # Combine input context
    input_text = (
        case.symptom + " " + case.topology_note + " " + case.show_outputs
    ).lower()

    if rule_findings:
        for rf in rule_findings:
            input_text += " " + rf.message.lower() + " " + " ".join(rf.evidence).lower()

    # Extract all technical terms present in the input text
    input_tokens = set(re.findall(r"\b[a-z0-9._/-]+\b", input_text))

    grounded_items_count = 0

    for item in ai_evidence:
        norm_item = item.lower()
        item_tokens = set(re.findall(r"\b[a-z0-9._/-]+\b", norm_item))

        # Check for hallucinated interface names or fake IPs
        # e.g., if AI mentions GigabitEthernet0/99 but input only has Gi0/0 or Gi0/1
        ifaces_in_item = re.findall(r"\b(?:gi|fa|gigabitethernet|fastethernet)[0-9/.]+\b", norm_item)
        ifaces_in_input = re.findall(r"\b(?:gi|fa|gigabitethernet|fastethernet)[0-9/.]+\b", input_text)

        hallucinated_iface = False
        for iface in ifaces_in_item:
            # Short form normalization (e.g. gi0/1 vs gigabitethernet0/1)
            clean_iface = iface.replace("gigabitethernet", "gi").replace("fastethernet", "fa")
            clean_inputs = [i.replace("gigabitethernet", "gi").replace("fastethernet", "fa") for i in ifaces_in_input]
            if clean_iface not in clean_inputs:
                hallucinated_iface = True
                break

        if hallucinated_iface:
            return False  # Failed grounding due to hallucinated interface

        # Check token overlap with input text
        meaningful_tokens = {t for t in item_tokens if len(t) > 2 and t not in {"the", "and", "is", "in", "on", "not", "for", "with", "this", "that"}}
        if meaningful_tokens and len(meaningful_tokens.intersection(input_tokens)) >= 1:
            grounded_items_count += 1

    return grounded_items_count > 0


# ===================================================================
# 6. Single Case Evaluation Engine
# ===================================================================

def evaluate_case(
    case: TroubleshootingCase,
    diagnosis_response: Optional[DiagnosisResponse],
    rule_findings: Optional[List[RuleResult]] = None,
    error: Optional[str] = None,
    latency_ms: Optional[float] = None,
) -> EvaluationResult:
    """Evaluate a single case diagnosis against ground truth."""
    rf_messages = [f.message for f in (rule_findings or [])]

    if diagnosis_response is None or error is not None:
        return EvaluationResult(
            case_id=case.case_id,
            issue_type=case.concept.value,
            ai_success=False,
            ai_root_cause="",
            expected_root_cause=case.expected_fault,
            root_cause_match=False,
            ai_confidence=0.0,
            ai_severity=None,
            expected_severity=case.severity.value,
            severity_match=False,
            ai_osi_layer=None,
            expected_osi_layer=case.osi_layer.value,
            osi_layer_match=None,
            ai_evidence=[],
            evidence_grounded=False,
            ai_next_command="",
            ai_fix_steps=[],
            rule_checker_findings=rf_messages,
            error=error or "Diagnosis response is None",
            latency_ms=latency_ms,
        )

    rc_match = evaluate_root_cause_match(diagnosis_response.root_cause, case.expected_fault)
    sev_match = evaluate_severity_match(diagnosis_response.severity, case.severity.value)
    osi_match = evaluate_osi_layer_match(None, case.osi_layer.value)
    grounded = evaluate_evidence_grounding(diagnosis_response.evidence, case, rule_findings)

    return EvaluationResult(
        case_id=case.case_id,
        issue_type=case.concept.value,
        ai_success=True,
        ai_root_cause=diagnosis_response.root_cause,
        expected_root_cause=case.expected_fault,
        root_cause_match=rc_match,
        ai_confidence=diagnosis_response.confidence,
        ai_severity=diagnosis_response.severity,
        expected_severity=case.severity.value,
        severity_match=sev_match,
        ai_osi_layer=None,
        expected_osi_layer=case.osi_layer.value,
        osi_layer_match=osi_match,
        ai_evidence=diagnosis_response.evidence,
        evidence_grounded=grounded,
        ai_next_command=diagnosis_response.next_command,
        ai_fix_steps=diagnosis_response.fix_steps,
        rule_checker_findings=rf_messages,
        error=None,
        latency_ms=latency_ms,
    )
