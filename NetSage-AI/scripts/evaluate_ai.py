"""
NetSage AI — AI Diagnosis Evaluation Script (Phase 6).

Executes batch evaluation over the 35 troubleshooting cases:
1. Loads dataset cases from data/cases.csv.
2. Runs deterministic rule checker to obtain rule findings.
3. Constructs AI-safe input (DiagnosisRequest) stripping ground truth.
4. Invokes AI diagnosis engine (Google Gemini or Mock Provider).
5. Evaluates root cause accuracy, severity accuracy, and evidence grounding.
6. Computes aggregate metrics and per-category performance breakdown.
7. Exports results/ai_evaluation_results.csv and results/ai_evaluation_summary.json.

Usage:
    # Run in mock mode (offline, no API key required)
    python -m scripts.evaluate_ai --mock

    # Run in real AI mode (requires LLM_API_KEY environment variable)
    python -m scripts.evaluate_ai
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.models import TroubleshootingCase, build_ai_input
from ai.diagnosis import generate_diagnosis
from ai.models import DiagnosisResponse
from evaluation import (
    EvaluationResult,
    compute_summary_metrics,
    evaluate_case,
    export_results_csv,
    export_summary_json,
    extract_rule_findings_for_case,
)
from evaluation.mock_provider import generate_mock_diagnosis


def run_evaluation(mock_mode: bool = False) -> bool:
    """Run batch evaluation over all troubleshooting cases."""
    print("=" * 70)
    print(f"NetSage AI — AI Diagnosis Evaluation Pipeline (Phase 6)")
    print(f"Mode: {'MOCK MODE (Offline)' if mock_mode else 'REAL AI MODE (Gemini)'}")
    print("=" * 70)

    csv_path = PROJECT_ROOT / "data" / "cases.csv"
    if not csv_path.exists():
        print(f"ERROR: Dataset file {csv_path} not found.")
        return False

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    cases: list[TroubleshootingCase] = []
    for r in raw_rows:
        try:
            cases.append(TroubleshootingCase(**r))
        except Exception as exc:
            print(f"WARNING: Skipping invalid case row {r.get('case_id')}: {exc}")

    print(f"Loaded {len(cases)} cases from dataset.\n")

    results: list[EvaluationResult] = []

    for idx, case in enumerate(cases, start=1):
        print(f"[{idx:02d}/{len(cases)}] {case.case_id} ({case.concept.value:<8}) ", end="")

        # 1. Run deterministic rule checker
        rule_findings = extract_rule_findings_for_case(case)
        rf_status = "FINDING" if any(rf.status.value == "FAIL" for rf in rule_findings) else "PASS"

        # 2. Build AI-safe request (strips ground truth)
        ai_request = build_ai_input(case, rule_findings=rule_findings)

        # 3. Execute AI diagnosis
        diag_resp: DiagnosisResponse | None = None
        error_msg: str | None = None
        start_time = time.time()

        if mock_mode:
            diag_resp = generate_mock_diagnosis(ai_request, case)
            latency_ms = (time.time() - start_time) * 1000
        else:
            try:
                diag_resp = generate_diagnosis(ai_request)
                latency_ms = (time.time() - start_time) * 1000
            except Exception as exc:
                error_msg = str(exc)
                latency_ms = (time.time() - start_time) * 1000

        # 4. Evaluate single case result
        eval_res = evaluate_case(
            case=case,
            diagnosis_response=diag_resp,
            rule_findings=rule_findings,
            error=error_msg,
            latency_ms=latency_ms,
        )

        results.append(eval_res)

        # Print per-case evaluation summary
        if eval_res.ai_success:
            rc_str = "MATCH" if eval_res.root_cause_match else "MISMATCH"
            grd_str = "GROUNDED" if eval_res.evidence_grounded else "UNGROUNDED"
            print(f"| Rule: {rf_status:<7} | AI: SUCCESS | Cause: {rc_str:<8} | Evidence: {grd_str}")
        else:
            print(f"| Rule: {rf_status:<7} | AI: ERROR   | {eval_res.error[:40] if eval_res.error else 'Failed'}")

    # 5. Compute aggregate metrics
    summary = compute_summary_metrics(results)

    # 6. Save results to disk
    results_dir = PROJECT_ROOT / "results"
    results_csv_path = results_dir / "ai_evaluation_results.csv"
    summary_json_path = results_dir / "ai_evaluation_summary.json"

    export_results_csv(results, results_csv_path)
    export_summary_json(summary, summary_json_path)

    # 7. Print summary metrics
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY METRICS")
    print("=" * 70)
    print(f"Total Cases Evaluated:       {summary.total_cases}")
    print(f"Successful Diagnoses:        {summary.successful_diagnoses}")
    print(f"Failed Diagnoses:            {summary.failed_diagnoses}")
    print(f"Root Cause Accuracy:         {summary.root_cause_accuracy * 100:.1f}%")
    print(f"Severity Accuracy:           {summary.severity_accuracy * 100:.1f}%")
    print(f"Evidence Grounding Rate:     {summary.evidence_grounding_rate * 100:.1f}%")
    print(f"Average Confidence:          {summary.avg_confidence:.2f}")

    print("\nCategory Breakdown:")
    print(f"  {'Category':<12} {'Cases':<6} {'Root Cause Acc':<16} {'Severity Acc':<14} {'Grounding Rate'}")
    print("  " + "-" * 65)
    for cat_name, cm in summary.category_metrics.items():
        print(f"  {cat_name:<12} {cm.total_cases:<6} {cm.root_cause_accuracy * 100:>14.1f}% {cm.severity_accuracy * 100:>12.1f}% {cm.evidence_grounding_rate * 100:>13.1f}%")

    print("\nConfidence Calibration Analysis:")
    for b_name, b_data in summary.confidence_accuracy_breakdown.items():
        print(f"  - {b_name.capitalize():<6} Confidence: {b_data['total']} cases ({b_data['correct']} correct, {b_data['wrong']} wrong)")

    print(f"\nSaved CSV results to: {results_csv_path}")
    print(f"Saved JSON summary to: {summary_json_path}")
    print("=" * 70)

    return True


def main():
    parser = argparse.ArgumentParser(description="NetSage AI Diagnosis Evaluation Pipeline")
    parser.add_argument("--mock", action="store_true", help="Run evaluation in mock mode (offline, no Gemini API calls)")
    args = parser.parse_args()

    success = run_evaluation(mock_mode=args.mock)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
