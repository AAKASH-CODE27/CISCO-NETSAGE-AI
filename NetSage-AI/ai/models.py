"""
Pydantic models for the AI diagnosis layer.

DiagnosisRequest  — structured input sent to the LLM.
DiagnosisResponse — validated structured output from the LLM.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from rule_checker.models import RuleResult


# -------------------------------------------------------------------
# Input model
# -------------------------------------------------------------------

class DiagnosisRequest(BaseModel):
    """Everything the LLM needs to produce a diagnosis.

    NOTE: ``expected_fault``, ``osi_layer``, and other ground-truth
    fields are deliberately excluded so the AI cannot cheat.
    """
    case_id: str
    symptom: str
    topology_note: str
    show_outputs: str
    rule_findings: List[RuleResult] = []


# -------------------------------------------------------------------
# Output model
# -------------------------------------------------------------------

class DiagnosisResponse(BaseModel):
    """Structured diagnosis returned by the LLM and validated here.

    All fields required by the Cisco problem statement are present:
    root_cause, confidence, evidence, next_command, fix_steps.
    """
    case_id: str = ""
    root_cause: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str]
    next_command: str
    fix_steps: List[str]
    severity: Optional[str] = None

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return round(v, 2)
