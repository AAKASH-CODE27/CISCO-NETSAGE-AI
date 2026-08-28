"""
NetSage AI — Evaluation Package (Phase 6)
=========================================

Provides evaluation models, deterministic root cause matching, severity matching,
evidence grounding checks, metric aggregation, and report exporters for AI diagnosis.
"""

from .models import (
    EvaluationResult,
    CategoryMetric,
    ConfidenceAnalysisItem,
    SummaryMetrics,
)
from .evaluator import (
    evaluate_case,
    evaluate_root_cause_match,
    evaluate_severity_match,
    evaluate_evidence_grounding,
    extract_rule_findings_for_case,
)
from .metrics import (
    compute_summary_metrics,
    export_results_csv,
    export_summary_json,
)

__all__ = [
    "EvaluationResult",
    "CategoryMetric",
    "ConfidenceAnalysisItem",
    "SummaryMetrics",
    "evaluate_case",
    "evaluate_root_cause_match",
    "evaluate_severity_match",
    "evaluate_evidence_grounding",
    "extract_rule_findings_for_case",
    "compute_summary_metrics",
    "export_results_csv",
    "export_summary_json",
]
