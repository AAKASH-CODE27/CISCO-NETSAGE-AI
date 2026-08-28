"""
Metrics computation and CSV/JSON exporter for NetSage AI (Phase 6).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from evaluation.models import (
    CategoryMetric,
    ConfidenceAnalysisItem,
    EvaluationResult,
    SummaryMetrics,
)


def compute_summary_metrics(results: List[EvaluationResult]) -> SummaryMetrics:
    """Compute aggregate summary metrics across all evaluated cases."""
    total = len(results)
    if total == 0:
        return SummaryMetrics(
            total_cases=0,
            successful_diagnoses=0,
            failed_diagnoses=0,
            root_cause_accuracy=0.0,
            severity_accuracy=0.0,
            osi_accuracy=None,
            evidence_grounding_rate=0.0,
            avg_confidence=0.0,
            confidence_distribution={"high": 0, "medium": 0, "low": 0},
            confidence_accuracy_breakdown={
                "high": {"total": 0, "correct": 0, "wrong": 0},
                "medium": {"total": 0, "correct": 0, "wrong": 0},
                "low": {"total": 0, "correct": 0, "wrong": 0},
            },
            category_metrics={},
        )

    successful = sum(1 for r in results if r.ai_success)
    failed = total - successful

    rc_matches = sum(1 for r in results if r.root_cause_match)
    sev_matches = sum(1 for r in results if r.severity_match)
    grounded_count = sum(1 for r in results if r.evidence_grounded)

    rc_accuracy = round(rc_matches / total, 4)
    sev_accuracy = round(sev_matches / total, 4)
    grounding_rate = round(grounded_count / total, 4)

    avg_conf = round(sum(r.ai_confidence for r in results) / total, 4)

    # OSI accuracy check
    osi_valid = [r for r in results if r.osi_layer_match is not None]
    osi_accuracy = round(sum(1 for r in osi_valid if r.osi_layer_match) / len(osi_valid), 4) if osi_valid else None

    # Confidence distribution & calibration
    conf_dist = {"high": 0, "medium": 0, "low": 0}
    conf_breakdown = {
        "high": {"total": 0, "correct": 0, "wrong": 0},
        "medium": {"total": 0, "correct": 0, "wrong": 0},
        "low": {"total": 0, "correct": 0, "wrong": 0},
    }

    for r in results:
        if r.ai_confidence >= 0.8:
            bucket = "high"
        elif r.ai_confidence >= 0.5:
            bucket = "medium"
        else:
            bucket = "low"

        conf_dist[bucket] += 1
        conf_breakdown[bucket]["total"] += 1
        if r.root_cause_match:
            conf_breakdown[bucket]["correct"] += 1
        else:
            conf_breakdown[bucket]["wrong"] += 1

    # Per-category metrics
    categories: Dict[str, List[EvaluationResult]] = {}
    for r in results:
        categories.setdefault(r.issue_type, []).append(r)

    cat_metrics: Dict[str, CategoryMetric] = {}
    for cat_name, cat_results in categories.items():
        c_total = len(cat_results)
        c_succ = sum(1 for r in cat_results if r.ai_success)
        c_rc_acc = round(sum(1 for r in cat_results if r.root_cause_match) / c_total, 4) if c_total > 0 else 0.0
        c_sev_acc = round(sum(1 for r in cat_results if r.severity_match) / c_total, 4) if c_total > 0 else 0.0
        c_ground = round(sum(1 for r in cat_results if r.evidence_grounded) / c_total, 4) if c_total > 0 else 0.0

        cat_metrics[cat_name] = CategoryMetric(
            category=cat_name,
            total_cases=c_total,
            successful=c_succ,
            root_cause_accuracy=c_rc_acc,
            severity_accuracy=c_sev_acc,
            evidence_grounding_rate=c_ground,
        )

    return SummaryMetrics(
        total_cases=total,
        successful_diagnoses=successful,
        failed_diagnoses=failed,
        root_cause_accuracy=rc_accuracy,
        severity_accuracy=sev_accuracy,
        osi_accuracy=osi_accuracy,
        evidence_grounding_rate=grounding_rate,
        avg_confidence=avg_conf,
        confidence_distribution=conf_dist,
        confidence_accuracy_breakdown=conf_breakdown,
        category_metrics=cat_metrics,
    )


def export_results_csv(results: List[EvaluationResult], filepath: Path) -> None:
    """Save per-case evaluation results to CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "issue_type",
        "ai_success",
        "ai_root_cause",
        "expected_root_cause",
        "root_cause_match",
        "ai_confidence",
        "ai_severity",
        "expected_severity",
        "severity_match",
        "ai_osi_layer",
        "expected_osi_layer",
        "osi_layer_match",
        "ai_evidence",
        "evidence_grounded",
        "ai_next_command",
        "ai_fix_steps",
        "rule_checker_findings",
        "error",
        "latency_ms",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in results:
            row = r.model_dump()
            row["ai_evidence"] = " | ".join(r.ai_evidence)
            row["ai_fix_steps"] = " | ".join(r.ai_fix_steps)
            row["rule_checker_findings"] = " | ".join(r.rule_checker_findings)
            writer.writerow(row)


def export_summary_json(summary: SummaryMetrics, filepath: Path) -> None:
    """Save summary metrics report to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = summary.model_dump()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
