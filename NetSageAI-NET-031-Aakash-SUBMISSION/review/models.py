"""
Human review models and CSV loader for NetSage AI (Phase 7 / Phase 8).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class HumanReviewRecord(BaseModel):
    """Represents a human engineer's review decision for an AI diagnosis."""
    case_id: str = Field(..., description="Unique case ID (e.g. NET-001)")
    ai_root_cause: str = Field(..., description="Original AI diagnosed root cause")
    ai_confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    human_decision: str = Field(..., description="Decision: ACCEPT, EDIT, or REJECT")
    human_correction: str = Field(default="", description="Human corrected diagnosis if EDIT or REJECT")
    reason: str = Field(default="", description="Explanation for human decision or correction")
    reviewer: str = Field(default="Senior Network Engineer", description="Identifier of the human reviewer")
    review_timestamp: str = Field(default="2026-08-28T12:00:00Z", description="ISO timestamp of review")


def load_human_review_records(filepath: Path) -> List[HumanReviewRecord]:
    """Load human review records from CSV file."""
    if not filepath.exists():
        return []

    records: list[HumanReviewRecord] = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("case_id"):
                continue
            try:
                conf = float(row.get("ai_confidence", 0.90))
            except ValueError:
                conf = 0.90
            records.append(
                HumanReviewRecord(
                    case_id=row["case_id"],
                    ai_root_cause=row.get("ai_root_cause", ""),
                    ai_confidence=conf,
                    human_decision=row.get("human_decision", "ACCEPT").upper(),
                    human_correction=row.get("human_correction", ""),
                    reason=row.get("reason", ""),
                    reviewer=row.get("reviewer", "Senior Network Engineer"),
                    review_timestamp=row.get("review_timestamp", "2026-08-28T12:00:00Z"),
                )
            )
    return records
