"""
Mock AI Diagnosis Provider for NetSage AI (Phase 6).

Generates deterministic, schema-valid DiagnosisResponse objects for testing
and offline evaluation without invoking external LLM APIs.
"""

from __future__ import annotations

from ai.models import DiagnosisRequest, DiagnosisResponse
from data.models import TroubleshootingCase


def generate_mock_diagnosis(request: DiagnosisRequest, case: TroubleshootingCase) -> DiagnosisResponse:
    """Generate a realistic mock DiagnosisResponse for a case."""
    # Use ground-truth case data to construct a valid response for mock testing
    # Note: Mock provider is strictly for pipeline validation during offline evaluation
    return DiagnosisResponse(
        case_id=request.case_id,
        root_cause=case.expected_fault,
        confidence=0.90,
        evidence=[
            f"Observed symptom: {request.symptom[:60]}",
            f"Topology connection: {request.topology_note[:60]}",
            f"Show command finding: {request.show_outputs.splitlines()[0] if request.show_outputs else 'Outputs checked'}",
        ],
        next_command=case.verification,
        fix_steps=[case.expected_fix],
        severity=case.severity.value,
    )
