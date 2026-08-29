"""
Metric calculation functions for NetSage AI Dashboard (Phase 9).

Calculates aggregated metrics from loaded data without hardcoding values.
All metrics are computed dynamically from actual project files.
"""

from typing import Dict, List, Any, Optional
import pandas as pd


class DashboardMetrics:
    """Calculates all dashboard metrics from loaded data."""

    @staticmethod
    def total_cases(cases_df: pd.DataFrame) -> int:
        """Calculate total number of troubleshooting cases."""
        return len(cases_df) if not cases_df.empty else 0

    @staticmethod
    def issue_type_distribution(cases_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of cases by issue type.
        
        Returns dict with counts for:
        VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT, Wireless
        """
        if cases_df.empty:
            return {}
        
        # Handle both 'concept' and 'Concept' column names
        concept_col = 'concept' if 'concept' in cases_df.columns else 'Concept' if 'Concept' in cases_df.columns else None
        if concept_col is None:
            return {}
        
        distribution = cases_df[concept_col].value_counts().to_dict()
        
        # Ensure all expected categories are present (even if count is 0)
        expected_categories = ["VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"]
        for category in expected_categories:
            if category not in distribution:
                distribution[category] = 0
        
        # Sort by category name for consistency
        return {k: distribution[k] for k in sorted(expected_categories) if k in distribution}

    @staticmethod
    def severity_distribution(cases_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of cases by severity level.
        
        Returns dict with counts for: Low, Medium, High, Critical
        """
        if cases_df.empty:
            return {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        
        # Handle both 'severity' and 'Severity' column names
        severity_col = 'severity' if 'severity' in cases_df.columns else 'Severity' if 'Severity' in cases_df.columns else None
        if severity_col is None:
            return {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        
        distribution = cases_df[severity_col].value_counts().to_dict()
        
        # Ensure all expected levels are present
        expected_levels = ["Low", "Medium", "High", "Critical"]
        result = {}
        for level in expected_levels:
            result[level] = distribution.get(level, 0)
        
        return result

    @staticmethod
    def review_distribution(reviews_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of human review decisions.
        
        Returns dict with counts for: ACCEPT, EDIT, REJECT
        """
        if reviews_df.empty:
            return {"ACCEPT": 0, "EDIT": 0, "REJECT": 0}
        
        # Handle both 'human_decision' and 'human_Decision' column names
        decision_col = 'human_decision' if 'human_decision' in reviews_df.columns else 'Human_Decision' if 'Human_Decision' in reviews_df.columns else None
        if decision_col is None:
            return {"ACCEPT": 0, "EDIT": 0, "REJECT": 0}
        
        distribution = reviews_df[decision_col].str.upper().value_counts().to_dict()
        
        # Ensure all expected decisions are present
        expected_decisions = ["ACCEPT", "EDIT", "REJECT"]
        result = {}
        for decision in expected_decisions:
            result[decision] = distribution.get(decision, 0)
        
        return result

    @staticmethod
    def ai_human_agreement_rate(reviews_df: pd.DataFrame) -> float:
        """Calculate AI-human agreement rate as percentage.
        
        Definition: (accepted_reviews / total_reviews) * 100
        
        Returns float between 0.0 and 100.0
        """
        if reviews_df.empty:
            return 0.0
        
        # Handle both 'human_decision' and 'human_Decision' column names
        decision_col = 'human_decision' if 'human_decision' in reviews_df.columns else 'Human_Decision' if 'Human_Decision' in reviews_df.columns else None
        if decision_col is None:
            return 0.0
        
        total = len(reviews_df)
        if total == 0:
            return 0.0
        
        accepted = len(reviews_df[reviews_df[decision_col].str.upper() == "ACCEPT"])
        return (accepted / total) * 100.0

    @staticmethod
    def corrected_case_count(responsible_ai_report: Dict[str, Any]) -> int:
        """Extract number of corrected cases from responsible AI report."""
        return responsible_ai_report.get("corrected_cases", 0)

    @staticmethod
    def correction_category_distribution(responsible_ai_report: Dict[str, Any]) -> Dict[str, int]:
        """Extract correction categories from responsible AI report."""
        return responsible_ai_report.get("correction_categories", {})

    @staticmethod
    def ai_diagnoses_count(reviews_df: pd.DataFrame) -> int:
        """Count of cases that received AI diagnoses (have review records)."""
        return len(reviews_df) if not reviews_df.empty else 0

    @staticmethod
    def human_reviews_count(reviews_df: pd.DataFrame) -> int:
        """Count of cases that were human reviewed."""
        return len(reviews_df) if not reviews_df.empty else 0

    @staticmethod
    def ai_evaluation_metrics(eval_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Extract AI evaluation metrics from summary JSON."""
        metrics = {}
        
        # Root cause accuracy
        if "root_cause_accuracy" in eval_summary:
            metrics["Root Cause Accuracy"] = f"{eval_summary['root_cause_accuracy'] * 100:.1f}%"
        else:
            metrics["Root Cause Accuracy"] = "N/A"
        
        # Severity accuracy
        if "severity_accuracy" in eval_summary:
            metrics["Severity Accuracy"] = f"{eval_summary['severity_accuracy'] * 100:.1f}%"
        else:
            metrics["Severity Accuracy"] = "N/A"
        
        # OSI accuracy
        if eval_summary.get("osi_accuracy") is not None:
            metrics["OSI Layer Accuracy"] = f"{eval_summary['osi_accuracy'] * 100:.1f}%"
        else:
            metrics["OSI Layer Accuracy"] = "N/A"
        
        # Evidence grounding
        if "evidence_grounding_rate" in eval_summary:
            metrics["Evidence Grounding"] = f"{eval_summary['evidence_grounding_rate'] * 100:.1f}%"
        else:
            metrics["Evidence Grounding"] = "N/A"
        
        # Average confidence
        if "avg_confidence" in eval_summary:
            metrics["Average Confidence"] = f"{eval_summary['avg_confidence']:.2f}"
        else:
            metrics["Average Confidence"] = "N/A"
        
        # Successful/Failed diagnoses
        successful = eval_summary.get("successful_diagnoses", 0)
        failed = eval_summary.get("failed_diagnoses", 0)
        metrics["Successful Diagnoses"] = f"{successful}"
        metrics["Failed Diagnoses"] = f"{failed}"
        
        return metrics

    @staticmethod
    def issue_type_metrics(eval_summary: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract per-category metrics from evaluation summary."""
        return eval_summary.get("category_metrics", {})

    @staticmethod
    def corrected_cases_by_type(responsible_ai_report: Dict[str, Any]) -> Dict[str, int]:
        """Extract count of corrected cases by issue type."""
        return responsible_ai_report.get("issue_type_corrections", {})

    @staticmethod
    def confidence_distribution(eval_summary: Dict[str, Any]) -> Dict[str, int]:
        """Extract confidence level distribution from evaluation summary."""
        return eval_summary.get("confidence_distribution", {})

    @staticmethod
    def highest_correction_category(responsible_ai_report: Dict[str, Any]) -> Optional[tuple]:
        """Find the most common correction category.
        
        Returns tuple of (category_name, count) or None if no corrections.
        """
        categories = responsible_ai_report.get("correction_categories", {})
        if not categories:
            return None
        
        max_category = max(categories.items(), key=lambda x: x[1])
        return max_category
