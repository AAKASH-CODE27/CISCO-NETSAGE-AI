"""
Data models for NetSage AI troubleshooting cases (Phase 5).

Defines the TroubleshootingCase Pydantic model representing a complete
lab scenario, including ground-truth fields for evaluation and helper
methods for creating AI-safe inputs (DiagnosisRequest).
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from ai.models import DiagnosisRequest
from rule_checker.models import RuleResult


class IssueCategory(str, Enum):
    """Supported issue categories for troubleshooting cases."""
    VLAN = "VLAN"
    GATEWAY = "Gateway"
    DHCP = "DHCP"
    DNS = "DNS"
    ROUTING = "Routing"
    ACL = "ACL"
    NAT = "NAT"
    WIRELESS = "Wireless"


class SeverityLevel(str, Enum):
    """Controlled set of severity levels for network issues."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class OSILayer(str, Enum):
    """Valid OSI layers for network faults."""
    LAYER_1 = "Layer 1"
    LAYER_2 = "Layer 2"
    LAYER_3 = "Layer 3"
    LAYER_4 = "Layer 4"
    LAYER_7 = "Layer 7"


class TroubleshootingCase(BaseModel):
    """Pydantic model representing a complete network troubleshooting case.

    Includes both public evidence (symptom, topology, show command outputs)
    and evaluation ground-truth (expected fault, OSI layer, fix, verification).
    """
    case_id: str = Field(..., description="Unique case identifier (e.g. NET-001)")
    concept: IssueCategory = Field(..., description="Category tag matching one of the 8 issue types")
    symptom: str = Field(..., min_length=5, description="User-visible symptom description")
    topology_note: str = Field(..., min_length=5, description="Network topology overview")
    show_outputs: str = Field(..., min_length=5, description="Cisco IOS show command outputs")
    
    # Ground-truth evaluation fields
    expected_fault: str = Field(..., min_length=5, description="Root cause explanation (Ground Truth)")
    osi_layer: OSILayer = Field(..., description="OSI layer of the fault (Ground Truth)")
    severity: SeverityLevel = Field(..., description="Severity rating of the issue (Ground Truth)")
    expected_fix: str = Field(..., min_length=5, description="Recommended remediation steps (Ground Truth)")
    verification: str = Field(..., min_length=3, description="Command or procedure to verify fix (Ground Truth)")

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, v: str) -> str:
        if not v.startswith("NET-"):
            raise ValueError(f"case_id must start with 'NET-', got: {v}")
        return v

    def to_ai_request(self, rule_findings: Optional[List[RuleResult]] = None) -> DiagnosisRequest:
        """Transform this full case into an AI-safe DiagnosisRequest.

        CRITICAL: All ground-truth fields (expected_fault, osi_layer,
        expected_fix, severity, concept) are stripped out to prevent leakage.
        """
        return DiagnosisRequest(
            case_id=self.case_id,
            symptom=self.symptom,
            topology_note=self.topology_note,
            show_outputs=self.show_outputs,
            rule_findings=rule_findings or [],
        )


def build_ai_input(case: TroubleshootingCase, rule_findings: Optional[List[RuleResult]] = None) -> DiagnosisRequest:
    """Helper function to build an AI-safe DiagnosisRequest from a case.

    Ensures zero leakage of ground-truth evaluation fields.
    """
    return case.to_ai_request(rule_findings=rule_findings)
