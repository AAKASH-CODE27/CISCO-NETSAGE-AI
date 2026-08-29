"""
Data loading functions for NetSage AI Dashboard (Phase 9).

Loads cases, evaluation results, human reviews, and responsible AI logs
from CSV and JSON files.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd


class DashboardDataLoader:
    """Loads all data sources for the dashboard."""

    def __init__(self, base_path: Path = None):
        """Initialize loader with base project path."""
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        self.base_path = base_path
        self.data_path = base_path / "data"
        self.results_path = base_path / "results"
        self.review_path = base_path / "review"

    def load_cases(self) -> pd.DataFrame:
        """Load all troubleshooting cases from cases.csv."""
        cases_file = self.data_path / "cases.csv"
        if not cases_file.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(cases_file)
            # Normalize column names
            df.columns = df.columns.str.lower()
            return df
        except Exception as e:
            print(f"Error loading cases: {e}")
            return pd.DataFrame()

    def load_human_reviews(self) -> pd.DataFrame:
        """Load human review records from human_review.csv."""
        review_file = self.review_path / "human_review.csv"
        if not review_file.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(review_file)
            df.columns = df.columns.str.lower()
            return df
        except Exception as e:
            print(f"Error loading human reviews: {e}")
            return pd.DataFrame()

    def load_ai_evaluation_results(self) -> pd.DataFrame:
        """Load AI evaluation results from ai_evaluation_results.csv."""
        results_file = self.results_path / "ai_evaluation_results.csv"
        if not results_file.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(results_file)
            df.columns = df.columns.str.lower()
            return df
        except Exception as e:
            print(f"Error loading AI evaluation results: {e}")
            return pd.DataFrame()

    def load_ai_evaluation_summary(self) -> Dict[str, Any]:
        """Load AI evaluation summary from ai_evaluation_summary.json."""
        summary_file = self.results_path / "ai_evaluation_summary.json"
        if not summary_file.exists():
            return {}
        
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading AI evaluation summary: {e}")
            return {}

    def load_responsible_ai_report(self) -> Dict[str, Any]:
        """Load responsible AI report from responsible_ai_report.json."""
        report_file = self.results_path / "responsible_ai_report.json"
        if not report_file.exists():
            return {}
        
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading responsible AI report: {e}")
            return {}

    def load_responsible_ai_log(self) -> pd.DataFrame:
        """Load responsible AI log from responsible_ai_log.csv."""
        log_file = self.results_path / "responsible_ai_log.csv"
        if not log_file.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(log_file)
            df.columns = df.columns.str.lower()
            return df
        except Exception as e:
            print(f"Error loading responsible AI log: {e}")
            return pd.DataFrame()

    def get_case_by_id(self, case_id: str, cases_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Retrieve a specific case by case_id."""
        if cases_df.empty:
            return None
        
        matching = cases_df[cases_df['case_id'] == case_id]
        if matching.empty:
            return None
        
        return matching.iloc[0].to_dict()

    def get_case_review(self, case_id: str, reviews_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Retrieve human review for a specific case."""
        if reviews_df.empty:
            return None
        
        matching = reviews_df[reviews_df['case_id'] == case_id]
        if matching.empty:
            return None
        
        return matching.iloc[0].to_dict()

    def get_case_evaluation(self, case_id: str, eval_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Retrieve AI evaluation for a specific case."""
        if eval_df.empty:
            return None
        
        matching = eval_df[eval_df['case_id'] == case_id]
        if matching.empty:
            return None
        
        return matching.iloc[0].to_dict()
