"""
NetSage AI — Responsible AI Log Generator (Phase 8).

Consumes Phase 7 human review records, builds auditable ResponsibleAIRecord entries,
preserves original AI outputs alongside human corrections, validates the 5-case minimum
correction requirement, and exports results/responsible_ai_log.csv and
results/responsible_ai_report.json.

Usage:
    python -m scripts.generate_responsible_ai_log
    python -m scripts.generate_responsible_ai_log --summary
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.models import TroubleshootingCase
from review.models import load_human_review_records
from evaluation.responsible_ai import (
    ResponsibleAIRecord,
    build_responsible_ai_record,
    compute_responsible_ai_report,
    export_responsible_ai_csv,
    export_responsible_ai_json,
)


def generate_log(show_summary_only: bool = False) -> bool:
    """Load human reviews, generate audit records, and export results."""
    print("=" * 70)
    print("NetSage AI — Responsible AI Log & Human Correction Analysis (Phase 8)")
    print("=" * 70)

    cases_csv = PROJECT_ROOT / "data" / "cases.csv"
    review_csv = PROJECT_ROOT / "review" / "human_review.csv"

    if not cases_csv.exists() or not review_csv.exists():
        print("ERROR: Required data/cases.csv or review/human_review.csv missing.")
        return False

    # 1. Load cases and reviews
    with open(cases_csv, "r", encoding="utf-8") as f:
        cases_dict = {row["case_id"]: TroubleshootingCase(**row) for row in csv.DictReader(f)}

    reviews = load_human_review_records(review_csv)
    if not reviews:
        print("ERROR: No review records found in review/human_review.csv.")
        return False

    print(f"Loaded {len(cases_dict)} dataset cases and {len(reviews)} human review records.\n")

    # 2. Build Responsible AI audit records
    records: list[ResponsibleAIRecord] = []
    for idx, rev in enumerate(reviews, start=1):
        case = cases_dict.get(rev.case_id)
        if not case:
            continue
        rai_rec = build_responsible_ai_record(idx, rev, case)
        records.append(rai_rec)

    # 3. Compute report metrics
    report = compute_responsible_ai_report(records)

    # 4. Save results to disk
    results_dir = PROJECT_ROOT / "results"
    log_csv_path = results_dir / "responsible_ai_log.csv"
    report_json_path = results_dir / "responsible_ai_report.json"

    export_responsible_ai_csv(records, log_csv_path)
    export_responsible_ai_json(report, report_json_path)

    # 5. Print Responsible AI Validation Table
    req_pass = report.corrected_cases >= 5

    print("Responsible AI validation")
    print("=========================")
    print(f"Total reviewed:     {report.total_reviewed}")
    print(f"Accepted:           {report.accepted}")
    print(f"Edited:             {report.edited}")
    print(f"Rejected:           {report.rejected}")
    print(f"AI corrected cases: {report.corrected_cases}")
    print(f"Minimum required:   5")
    print(f"Requirement:        {'PASS' if req_pass else 'FAIL'}")
    print("=" * 70)

    # 6. Detailed breakdown output
    print("\nCorrection Category Breakdown:")
    for cat_name, count in report.correction_categories.items():
        print(f"  - {cat_name:<25}: {count} case(s)")

    print("\nHigh-Confidence Incorrect Diagnoses (AI Confidence >= 80% with Human Correction):")
    if report.high_confidence_errors:
        for err in report.high_confidence_errors:
            print(f"  [{err['case_id']}] Category: {err['issue_type']:<8} | Decision: {err['human_decision']} | Conf: {err['ai_confidence']*100:.0f}%")
            print(f"     AI Said  : {err['ai_root_cause']}")
            print(f"     Human Fix: {err['human_root_cause']}")
            print(f"     Reason   : {err['reason']}\n")
    else:
        print("  None detected.")

    print(f"Saved audit log to: {log_csv_path}")
    print(f"Saved summary report to: {report_json_path}")
    print("=" * 70)

    if not req_pass:
        print("\nERROR: Phase 8 cannot be considered complete because fewer than 5 genuine human-corrected cases are available.")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="NetSage AI Responsible AI Log Generator")
    parser.add_argument("--summary", action="store_true", help="Print summary report metrics")
    args = parser.parse_args()

    success = generate_log(show_summary_only=args.summary)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
