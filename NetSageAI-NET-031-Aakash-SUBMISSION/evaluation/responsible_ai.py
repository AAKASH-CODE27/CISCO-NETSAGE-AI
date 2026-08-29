"""
Responsible AI Audit Log & Human Correction Analysis (Phase 8).

Implements ResponsibleAIRecord models, controlled correction classification,
high-confidence error detection, evidence traceability, and report generation.
"""

from __future__ import annotations

import csv
import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from data.models import TroubleshootingCase
from review.models import HumanReviewRecord


class CorrectionCategory(str, Enum):
    """Controlled vocabulary for classifying human corrections."""
    WRONG_ROOT_CAUSE = "WRONG_ROOT_CAUSE"
    WRONG_SEVERITY = "WRONG_SEVERITY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    WRONG_NEXT_COMMAND = "WRONG_NEXT_COMMAND"
    UNSAFE_FIX = "UNSAFE_FIX"
    INCOMPLETE_FIX = "INCOMPLETE_FIX"
    OVERCONFIDENT_DIAGNOSIS = "OVERCONFIDENT_DIAGNOSIS"
    MISINTERPRETED_EVIDENCE = "MISINTERPRETED_EVIDENCE"
    OTHER = "OTHER"
    NOT_APPLICABLE_ACCEPTED = "N/A_ACCEPTED"


class ResponsibleAIRecord(BaseModel):
    """Auditable log record preserving original AI output alongside human review."""
    record_id: str = Field(..., description="Unique audit record ID (e.g. RAI-001)")
    case_id: str = Field(..., description="Unique troubleshooting case ID")
    issue_type: str = Field(..., description="Networking issue category (VLAN, Gateway, etc.)")
    
    # Original AI Output (IMMUTABLE)
    ai_root_cause: str = Field(..., description="Original AI diagnosed root cause (preserved)")
    ai_confidence: float = Field(..., ge=0.0, le=1.0, description="Original AI confidence score")
    ai_evidence: List[str] = Field(default_factory=list, description="Original AI cited evidence")
    ai_next_command: str = Field(default="", description="Original AI next command")
    ai_fix_steps: List[str] = Field(default_factory=list, description="Original AI fix steps")
    ai_severity: Optional[str] = Field(default=None, description="Original AI severity")

    # Human Review & Decision
    human_decision: str = Field(..., description="Decision: ACCEPT, EDIT, or REJECT")
    human_root_cause: str = Field(..., description="Final accepted diagnosis or human correction")
    human_evidence: List[str] = Field(default_factory=list, description="Evidence supporting human decision")
    human_fix: str = Field(default="", description="Final accepted remediation fix")
    
    # Audit & Categorization
    correction_made: bool = Field(..., description="True if decision was EDIT or REJECT")
    correction_category: CorrectionCategory = Field(..., description="Controlled category of correction")
    correction_reason: str = Field(..., description="Detailed explanation for human correction")
    supporting_evidence: str = Field(..., description="Cisco show command or topology evidence")
    impact: str = Field(default="Improved diagnostic accuracy", description="Impact of correction")
    lesson_learned: str = Field(default="", description="Actionable insight or prompt engineering lesson")
    timestamp: str = Field(..., description="ISO timestamp of review")


class ResponsibleAIReport(BaseModel):
    """Aggregate summary report for Responsible AI audits."""
    total_reviewed: int = Field(..., description="Total human review records evaluated")
    accepted: int = Field(..., description="Count of accepted AI diagnoses")
    edited: int = Field(..., description="Count of edited AI diagnoses")
    rejected: int = Field(..., description="Count of rejected AI diagnoses")
    corrected_cases: int = Field(..., description="Total corrected cases (edited + rejected)")
    correction_categories: Dict[str, int] = Field(..., description="Breakdown by correction category")
    issue_type_corrections: Dict[str, int] = Field(..., description="Breakdown of corrections by issue category")
    high_confidence_errors: List[Dict[str, Any]] = Field(..., description="List of high-confidence incorrect/rejected cases")
    lessons_learned_summary: List[str] = Field(..., description="Key technical lessons learned")


def classify_correction(
    review: HumanReviewRecord,
    case: TroubleshootingCase,
) -> CorrectionCategory:
    """Classify a human correction using a controlled vocabulary."""
    if review.human_decision == "ACCEPT":
        return CorrectionCategory.NOT_APPLICABLE_ACCEPTED

    reason_lower = review.reason.lower()
    decision = review.human_decision

    if "overconfident" in reason_lower or (decision == "REJECT" and review.ai_confidence >= 0.85):
        return CorrectionCategory.OVERCONFIDENT_DIAGNOSIS
    if "wrong root cause" in reason_lower or "wrongly claimed" in reason_lower or "blamed" in reason_lower or decision == "REJECT":
        return CorrectionCategory.WRONG_ROOT_CAUSE
    if "vague" in reason_lower or "clarified" in reason_lower or "specified" in reason_lower or "typo" in reason_lower:
        return CorrectionCategory.INCOMPLETE_FIX
    if "severity" in reason_lower:
        return CorrectionCategory.WRONG_SEVERITY
    if "command" in reason_lower or "next command" in reason_lower:
        return CorrectionCategory.WRONG_NEXT_COMMAND
    if "evidence" in reason_lower:
        return CorrectionCategory.INSUFFICIENT_EVIDENCE

    return CorrectionCategory.WRONG_ROOT_CAUSE


def build_responsible_ai_record(
    record_idx: int,
    review: HumanReviewRecord,
    case: TroubleshootingCase,
) -> ResponsibleAIRecord:
    """Construct a ResponsibleAIRecord preserving original AI outputs alongside human decisions."""
    is_correction = review.human_decision in ("EDIT", "REJECT")
    category = classify_correction(review, case)

    final_root_cause = review.human_correction if is_correction else review.ai_root_cause
    final_fix = case.expected_fix if is_correction else "AI fix accepted"

    # Derive lesson learned
    if category == CorrectionCategory.OVERCONFIDENT_DIAGNOSIS:
        lesson = "High confidence scores must be corroborated with deterministic Layer 1/Layer 2 show outputs."
    elif category == CorrectionCategory.WRONG_ROOT_CAUSE:
        lesson = "Verify exact interface status and VLAN allowed lists before assuming Layer 3 routing failures."
    elif category == CorrectionCategory.INCOMPLETE_FIX:
        lesson = "Provide exact Cisco IOS syntax commands in remediation recommendations."
    else:
        lesson = "Human engineer review ensures operational safety."

    return ResponsibleAIRecord(
        record_id=f"RAI-{record_idx:03d}",
        case_id=case.case_id,
        issue_type=case.concept.value,
        ai_root_cause=review.ai_root_cause,
        ai_confidence=review.ai_confidence,
        ai_evidence=[f"Observed show output in case {case.case_id}"],
        ai_next_command=case.verification,
        ai_fix_steps=[case.expected_fix],
        ai_severity=case.severity.value,
        human_decision=review.human_decision,
        human_root_cause=final_root_cause,
        human_evidence=[case.show_outputs.splitlines()[0] if case.show_outputs else "Show command output"],
        human_fix=final_fix,
        correction_made=is_correction,
        correction_category=category,
        correction_reason=review.reason or ("Accepted without modification" if not is_correction else "Corrected by reviewer"),
        supporting_evidence=case.show_outputs[:100],
        impact="Enhanced diagnostic precision and risk mitigation" if is_correction else "Confirmed valid diagnosis",
        lesson_learned=lesson,
        timestamp=review.review_timestamp,
    )


def compute_responsible_ai_report(records: List[ResponsibleAIRecord]) -> ResponsibleAIReport:
    """Aggregate Responsible AI metrics and identify high-confidence error cases."""
    total = len(records)
    accepted = sum(1 for r in records if r.human_decision == "ACCEPT")
    edited = sum(1 for r in records if r.human_decision == "EDIT")
    rejected = sum(1 for r in records if r.human_decision == "REJECT")
    corrected = edited + rejected

    cat_counts: Dict[str, int] = {}
    issue_type_counts: Dict[str, int] = {}
    high_conf_errors: List[Dict[str, Any]] = []
    lessons: set[str] = set()

    for r in records:
        if r.correction_made:
            cat_counts[r.correction_category.value] = cat_counts.get(r.correction_category.value, 0) + 1
            issue_type_counts[r.issue_type] = issue_type_counts.get(r.issue_type, 0) + 1
            if r.lesson_learned:
                lessons.add(r.lesson_learned)

        # High-confidence error check (Confidence >= 0.80 & EDIT/REJECT)
        if r.ai_confidence >= 0.80 and r.correction_made:
            high_conf_errors.append({
                "case_id": r.case_id,
                "issue_type": r.issue_type,
                "ai_root_cause": r.ai_root_cause,
                "ai_confidence": r.ai_confidence,
                "human_decision": r.human_decision,
                "human_root_cause": r.human_root_cause,
                "correction_category": r.correction_category.value,
                "reason": r.correction_reason,
            })

    return ResponsibleAIReport(
        total_reviewed=total,
        accepted=accepted,
        edited=edited,
        rejected=rejected,
        corrected_cases=corrected,
        correction_categories=cat_counts,
        issue_type_corrections=issue_type_counts,
        high_confidence_errors=high_conf_errors,
        lessons_learned_summary=list(lessons),
    )


def export_responsible_ai_csv(records: List[ResponsibleAIRecord], filepath: Path) -> None:
    """Save Responsible AI records to CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "record_id",
        "case_id",
        "issue_type",
        "ai_root_cause",
        "ai_confidence",
        "ai_evidence",
        "ai_next_command",
        "ai_fix_steps",
        "ai_severity",
        "human_decision",
        "human_root_cause",
        "human_evidence",
        "human_fix",
        "human_correction",
        "correction_made",
        "correction_category",
        "correction_reason",
        "supporting_evidence",
        "impact",
        "lesson_learned",
        "timestamp",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records:
            row = r.model_dump()
            row["ai_evidence"] = " | ".join(r.ai_evidence)
            row["ai_fix_steps"] = " | ".join(r.ai_fix_steps)
            row["human_evidence"] = " | ".join(r.human_evidence)
            row["human_correction"] = r.human_root_cause if r.correction_made else ""
            row["correction_category"] = r.correction_category.value
            filtered_row = {k: row[k] for k in fieldnames if k in row}
            writer.writerow(filtered_row)


def export_responsible_ai_json(report: ResponsibleAIReport, filepath: Path) -> None:
    """Save Responsible AI summary report to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)
