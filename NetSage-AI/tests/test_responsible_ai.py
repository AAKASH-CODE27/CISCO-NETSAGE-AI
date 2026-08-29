"""
Unit tests for Responsible AI Audit Logging and Human Correction Analysis (Phase 8).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from data.models import TroubleshootingCase
from review.models import HumanReviewRecord, load_human_review_records
from evaluation.responsible_ai import (
    CorrectionCategory,
    ResponsibleAIRecord,
    build_responsible_ai_record,
    classify_correction,
    compute_responsible_ai_report,
    export_responsible_ai_csv,
    export_responsible_ai_json,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_case():
    return TroubleshootingCase(
        case_id="NET-001",
        concept="VLAN",
        symptom="PC1 cannot ping PC2",
        topology_note="PC1 -> SW1 -> SW2 -> PC2",
        show_outputs="SW1# show vlan brief\n10 Sales Fa0/1",
        expected_fault="VLAN mismatch between access ports",
        osi_layer="Layer 2",
        severity="Medium",
        expected_fix="Configure switchport access vlan 10 on SW2 Fa0/1",
        verification="show vlan brief",
    )


def test_responsible_ai_record_validation(sample_case):
    """Verify ResponsibleAIRecord schema and validation."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="VLAN mismatch",
        ai_confidence=0.92,
        human_decision="ACCEPT",
        human_correction="",
        reason="AI diagnosis accepted",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    assert rec.record_id == "RAI-001"
    assert rec.case_id == "NET-001"
    assert rec.issue_type == "VLAN"
    assert rec.ai_root_cause == "VLAN mismatch"
    assert rec.correction_made is False
    assert rec.correction_category == CorrectionCategory.NOT_APPLICABLE_ACCEPTED


def test_accept_record_handling(sample_case):
    """ACCEPT decision preserves original AI diagnosis as human root cause."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="VLAN mismatch",
        ai_confidence=0.90,
        human_decision="ACCEPT",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    assert rec.human_decision == "ACCEPT"
    assert rec.human_root_cause == "VLAN mismatch"
    assert rec.correction_made is False


def test_edit_record_handling(sample_case):
    """EDIT decision preserves original AI cause and stores human correction."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="Unassigned switch port Fa0/1",
        ai_confidence=0.85,
        human_decision="EDIT",
        human_correction="Fa0/1 assigned to VLAN 1 default instead of VLAN 10",
        reason="AI correctly identified port issue but reviewer specified target VLAN 10",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    assert rec.human_decision == "EDIT"
    assert rec.ai_root_cause == "Unassigned switch port Fa0/1"
    assert rec.human_root_cause == "Fa0/1 assigned to VLAN 1 default instead of VLAN 10"
    assert rec.correction_made is True


def test_reject_record_handling(sample_case):
    """REJECT decision marks diagnosis incorrect and stores human reason."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="Global routing engine fault",
        ai_confidence=0.88,
        human_decision="REJECT",
        human_correction="VLAN 10 missing in switch database",
        reason="AI wrongly blamed routing engine when issue was Layer 2 VLAN database",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    assert rec.human_decision == "REJECT"
    assert rec.ai_root_cause == "Global routing engine fault"
    assert rec.human_root_cause == "VLAN 10 missing in switch database"
    assert rec.correction_made is True
    assert rec.correction_category in (CorrectionCategory.WRONG_ROOT_CAUSE, CorrectionCategory.OVERCONFIDENT_DIAGNOSIS)


def test_immutable_ai_root_cause_preservation(sample_case):
    """Verify that original AI root cause is never overwritten by human correction."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="ORIGINAL_AI_CLAIM",
        ai_confidence=0.85,
        human_decision="EDIT",
        human_correction="HUMAN_CORRECTED_CLAIM",
        reason="Correction applied",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    assert rec.ai_root_cause == "ORIGINAL_AI_CLAIM"
    assert rec.human_root_cause == "HUMAN_CORRECTED_CLAIM"
    assert rec.ai_root_cause != rec.human_root_cause


def test_correction_category_controlled_vocabulary(sample_case):
    """Verify controlled vocabulary category assignment."""
    review_overconf = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="Wrong claim",
        ai_confidence=0.95,
        human_decision="REJECT",
        human_correction="Correct claim",
        reason="AI diagnosis was overconfident and wrong",
    )
    cat = classify_correction(review_overconf, sample_case)
    assert cat in list(CorrectionCategory)
    assert cat == CorrectionCategory.OVERCONFIDENT_DIAGNOSIS


def test_evidence_traceability(sample_case):
    """Verify supporting evidence from Cisco show commands is retained."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="VLAN mismatch",
        ai_confidence=0.90,
        human_decision="ACCEPT",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    assert "show vlan brief" in rec.supporting_evidence or len(rec.supporting_evidence) > 0


def test_high_confidence_error_detection(sample_case):
    """Identify high-confidence error cases (confidence >= 80% with EDIT/REJECT)."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="Wrong claim",
        ai_confidence=0.92,
        human_decision="REJECT",
        human_correction="Right claim",
        reason="Overconfident AI failure",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    report = compute_responsible_ai_report([rec])

    assert len(report.high_confidence_errors) == 1
    err = report.high_confidence_errors[0]
    assert err["case_id"] == "NET-001"
    assert err["ai_confidence"] == 0.92
    assert err["human_decision"] == "REJECT"


def test_at_least_five_corrected_cases():
    """Verify dataset human reviews contain at least 5 genuine corrected cases."""
    review_csv = PROJECT_ROOT / "review" / "human_review.csv"
    reviews = load_human_review_records(review_csv)
    corrected_count = sum(1 for r in reviews if r.human_decision in ("EDIT", "REJECT"))
    assert corrected_count >= 5, f"Expected at least 5 corrected cases, found {corrected_count}"


def test_export_csv_and_json(tmp_path: Path, sample_case):
    """Verify CSV and JSON file exporters."""
    review = HumanReviewRecord(
        case_id="NET-001",
        ai_root_cause="VLAN mismatch",
        ai_confidence=0.90,
        human_decision="ACCEPT",
    )
    rec = build_responsible_ai_record(1, review, sample_case)
    report = compute_responsible_ai_report([rec])

    csv_file = tmp_path / "responsible_ai_log.csv"
    json_file = tmp_path / "responsible_ai_report.json"

    export_responsible_ai_csv([rec], csv_file)
    export_responsible_ai_json(report, json_file)

    assert csv_file.exists()
    assert json_file.exists()

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["total_reviewed"] == 1
        assert data["accepted"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
