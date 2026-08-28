"""
Unit tests for metrics calculation and CSV/JSON export functions (Phase 6).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from evaluation.models import EvaluationResult
from evaluation.metrics import (
    compute_summary_metrics,
    export_results_csv,
    export_summary_json,
)


def test_compute_summary_metrics():
    """Verify summary metrics computation across sample evaluation results."""
    results = [
        EvaluationResult(
            case_id="NET-001",
            issue_type="VLAN",
            ai_success=True,
            ai_root_cause="VLAN mismatch",
            expected_root_cause="VLAN mismatch",
            root_cause_match=True,
            ai_confidence=0.9,
            ai_severity="Medium",
            expected_severity="Medium",
            severity_match=True,
            ai_osi_layer=None,
            expected_osi_layer="Layer 2",
            osi_layer_match=None,
            ai_evidence=["Fa0/1 in VLAN 10"],
            evidence_grounded=True,
        ),
        EvaluationResult(
            case_id="NET-002",
            issue_type="VLAN",
            ai_success=False,
            ai_root_cause="",
            expected_root_cause="Missing VLAN 10",
            root_cause_match=False,
            ai_confidence=0.0,
            ai_severity=None,
            expected_severity="Medium",
            severity_match=False,
            ai_osi_layer=None,
            expected_osi_layer="Layer 2",
            osi_layer_match=None,
            ai_evidence=[],
            evidence_grounded=False,
            error="API timeout",
        ),
    ]

    summary = compute_summary_metrics(results)

    assert summary.total_cases == 2
    assert summary.successful_diagnoses == 1
    assert summary.failed_diagnoses == 1
    assert summary.root_cause_accuracy == 0.5
    assert summary.severity_accuracy == 0.5
    assert summary.evidence_grounding_rate == 0.5
    assert summary.avg_confidence == 0.45

    assert "VLAN" in summary.category_metrics
    assert summary.category_metrics["VLAN"].total_cases == 2
    assert summary.category_metrics["VLAN"].successful == 1


def test_export_results_csv_and_json(tmp_path: Path):
    """Verify CSV and JSON file exports."""
    results = [
        EvaluationResult(
            case_id="NET-001",
            issue_type="VLAN",
            ai_success=True,
            ai_root_cause="VLAN mismatch",
            expected_root_cause="VLAN mismatch",
            root_cause_match=True,
            ai_confidence=0.9,
            ai_severity="Medium",
            expected_severity="Medium",
            severity_match=True,
            expected_osi_layer="Layer 2",
            ai_evidence=["Evidence line 1"],
            evidence_grounded=True,
        )
    ]

    summary = compute_summary_metrics(results)

    csv_file = tmp_path / "results.csv"
    json_file = tmp_path / "summary.json"

    export_results_csv(results, csv_file)
    export_summary_json(summary, json_file)

    assert csv_file.exists()
    assert json_file.exists()

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["total_cases"] == 1
        assert data["successful_diagnoses"] == 1
        assert data["root_cause_accuracy"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__])
