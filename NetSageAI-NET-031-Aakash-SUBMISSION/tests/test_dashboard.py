"""
Tests for NetSage AI Dashboard (Phase 9).

Tests dashboard data loading, metric calculations, and logic without
testing screenshots or pixel positions.
"""

import pytest
from pathlib import Path
from dashboard.data import DashboardDataLoader
from dashboard.metrics import DashboardMetrics
import pandas as pd


class TestDashboardDataLoader:
    """Test data loading functionality."""
    
    @pytest.fixture
    def loader(self):
        """Initialize data loader."""
        return DashboardDataLoader()
    
    def test_load_cases(self, loader):
        """Test that cases are loaded successfully."""
        cases = loader.load_cases()
        assert not cases.empty, "Cases dataframe should not be empty"
        assert len(cases) == 35, "Should load exactly 35 cases"
        assert 'case_id' in cases.columns, "case_id column should exist"
    
    def test_load_human_reviews(self, loader):
        """Test that human reviews are loaded."""
        reviews = loader.load_human_reviews()
        assert not reviews.empty, "Reviews dataframe should not be empty"
        assert 'human_decision' in reviews.columns, "human_decision column should exist"
    
    def test_load_ai_evaluation_results(self, loader):
        """Test AI evaluation results loading."""
        results = loader.load_ai_evaluation_results()
        assert not results.empty, "Evaluation results should not be empty"
        assert 'case_id' in results.columns, "case_id column should exist"
    
    def test_load_ai_evaluation_summary(self, loader):
        """Test AI evaluation summary loading."""
        summary = loader.load_ai_evaluation_summary()
        assert isinstance(summary, dict), "Summary should be a dictionary"
        assert "total_cases" in summary, "Should have total_cases"
        assert summary["total_cases"] == 35, "Should have 35 cases in summary"
    
    def test_load_responsible_ai_report(self, loader):
        """Test responsible AI report loading."""
        report = loader.load_responsible_ai_report()
        assert isinstance(report, dict), "Report should be a dictionary"
        assert "total_reviewed" in report, "Should have total_reviewed"
        assert "corrected_cases" in report, "Should have corrected_cases"
    
    def test_load_responsible_ai_log(self, loader):
        """Test responsible AI log loading."""
        log = loader.load_responsible_ai_log()
        assert isinstance(log, pd.DataFrame), "Log should be a DataFrame"
    
    def test_get_case_by_id(self, loader):
        """Test case retrieval by ID."""
        cases = loader.load_cases()
        case = loader.get_case_by_id("NET-001", cases)
        assert case is not None, "Should find NET-001"
        assert case['case_id'] == "NET-001", "Should return correct case"
    
    def test_get_case_by_id_not_found(self, loader):
        """Test case retrieval with non-existent ID."""
        cases = loader.load_cases()
        case = loader.get_case_by_id("NET-999", cases)
        assert case is None, "Should return None for non-existent case"
    
    def test_get_case_review(self, loader):
        """Test review retrieval by case ID."""
        reviews = loader.load_human_reviews()
        review = loader.get_case_review("NET-001", reviews)
        assert review is not None, "Should find review for NET-001"
        assert review['case_id'] == "NET-001", "Should return correct review"


class TestDashboardMetrics:
    """Test metric calculation functions."""
    
    @pytest.fixture
    def loader(self):
        """Initialize data loader."""
        return DashboardDataLoader()
    
    @pytest.fixture
    def cases_df(self, loader):
        """Load test cases."""
        return loader.load_cases()
    
    @pytest.fixture
    def reviews_df(self, loader):
        """Load test reviews."""
        return loader.load_human_reviews()
    
    @pytest.fixture
    def eval_summary(self, loader):
        """Load evaluation summary."""
        return loader.load_ai_evaluation_summary()
    
    @pytest.fixture
    def rai_report(self, loader):
        """Load responsible AI report."""
        return loader.load_responsible_ai_report()
    
    def test_total_cases(self, cases_df):
        """Test total cases count."""
        total = DashboardMetrics.total_cases(cases_df)
        assert total == 35, "Should have 35 total cases"
    
    def test_total_cases_empty(self):
        """Test total cases with empty dataframe."""
        empty_df = pd.DataFrame()
        total = DashboardMetrics.total_cases(empty_df)
        assert total == 0, "Empty dataframe should return 0"
    
    def test_issue_type_distribution(self, cases_df):
        """Test issue type distribution."""
        distribution = DashboardMetrics.issue_type_distribution(cases_df)
        
        # Check that all 8 categories are present
        expected_categories = ["VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"]
        for category in expected_categories:
            assert category in distribution, f"Missing category {category}"
        
        # Check that total equals 35
        total = sum(distribution.values())
        assert total == 35, f"Total should be 35, got {total}"
        
        # Check specific expected counts (from Phase 5)
        assert distribution["VLAN"] == 5, "Should have 5 VLAN cases"
        assert distribution["Gateway"] == 4, "Should have 4 Gateway cases"
        assert distribution["DHCP"] == 5, "Should have 5 DHCP cases"
        assert distribution["DNS"] == 4, "Should have 4 DNS cases"
        assert distribution["Routing"] == 5, "Should have 5 Routing cases"
        assert distribution["ACL"] == 4, "Should have 4 ACL cases"
        assert distribution["NAT"] == 4, "Should have 4 NAT cases"
        assert distribution["Wireless"] == 4, "Should have 4 Wireless cases"
    
    def test_severity_distribution(self, cases_df):
        """Test severity distribution."""
        distribution = DashboardMetrics.severity_distribution(cases_df)
        
        # Check that all levels are present
        expected_levels = ["Low", "Medium", "High", "Critical"]
        for level in expected_levels:
            assert level in distribution, f"Missing severity level {level}"
        
        # Check that total equals 35
        total = sum(distribution.values())
        assert total == 35, f"Total should be 35, got {total}"
    
    def test_severity_distribution_empty(self):
        """Test severity distribution with empty dataframe."""
        empty_df = pd.DataFrame()
        distribution = DashboardMetrics.severity_distribution(empty_df)
        assert all(v == 0 for v in distribution.values()), "All counts should be 0"
    
    def test_review_distribution(self, reviews_df):
        """Test review distribution."""
        distribution = DashboardMetrics.review_distribution(reviews_df)
        
        # Check that all decisions are present
        expected_decisions = ["ACCEPT", "EDIT", "REJECT"]
        for decision in expected_decisions:
            assert decision in distribution, f"Missing decision {decision}"
        
        # Check expected counts from Phase 8
        assert distribution["ACCEPT"] == 27, "Should have 27 ACCEPT"
        assert distribution["EDIT"] == 5, "Should have 5 EDIT"
        assert distribution["REJECT"] == 3, "Should have 3 REJECT"
        
        # Total should be 35
        total = sum(distribution.values())
        assert total == 35, f"Total should be 35, got {total}"
    
    def test_ai_human_agreement_rate(self, reviews_df):
        """Test AI-human agreement rate calculation."""
        rate = DashboardMetrics.ai_human_agreement_rate(reviews_df)
        
        # Agreement rate should be 27/35 * 100 = 77.14%
        expected_rate = (27 / 35) * 100
        assert abs(rate - expected_rate) < 0.1, f"Rate should be ~{expected_rate}%, got {rate}%"
        
        # Rate should be between 0 and 100
        assert 0.0 <= rate <= 100.0, f"Rate should be between 0-100, got {rate}"
    
    def test_agreement_rate_empty(self):
        """Test agreement rate with empty dataframe."""
        empty_df = pd.DataFrame()
        rate = DashboardMetrics.ai_human_agreement_rate(empty_df)
        assert rate == 0.0, "Empty dataframe should return 0%"
    
    def test_corrected_case_count(self, rai_report):
        """Test corrected case count from RAI report."""
        count = DashboardMetrics.corrected_case_count(rai_report)
        assert count == 8, "Should have 8 corrected cases from Phase 8"
    
    def test_correction_category_distribution(self, rai_report):
        """Test correction category distribution."""
        distribution = DashboardMetrics.correction_category_distribution(rai_report)
        
        # Should have WRONG_ROOT_CAUSE and INCOMPLETE_FIX
        assert "WRONG_ROOT_CAUSE" in distribution, "Should have WRONG_ROOT_CAUSE"
        assert "INCOMPLETE_FIX" in distribution, "Should have INCOMPLETE_FIX"
        
        # Check counts from Phase 8
        assert distribution["WRONG_ROOT_CAUSE"] == 5, "Should have 5 WRONG_ROOT_CAUSE"
        assert distribution["INCOMPLETE_FIX"] == 3, "Should have 3 INCOMPLETE_FIX"
    
    def test_ai_diagnoses_count(self, reviews_df):
        """Test AI diagnoses count."""
        count = DashboardMetrics.ai_diagnoses_count(reviews_df)
        assert count == 35, "All 35 cases should have AI diagnoses"
    
    def test_human_reviews_count(self, reviews_df):
        """Test human reviews count."""
        count = DashboardMetrics.human_reviews_count(reviews_df)
        assert count == 35, "All 35 cases should have human reviews"
    
    def test_ai_evaluation_metrics(self, eval_summary):
        """Test AI evaluation metrics extraction."""
        metrics = DashboardMetrics.ai_evaluation_metrics(eval_summary)
        
        # Check that expected metrics are present
        assert "Root Cause Accuracy" in metrics, "Should have Root Cause Accuracy"
        assert "Severity Accuracy" in metrics, "Should have Severity Accuracy"
        assert "Average Confidence" in metrics, "Should have Average Confidence"
        
        # From Phase 6, all should be 100% or 0.9
        assert "100.0%" in metrics["Root Cause Accuracy"], "Root cause accuracy should be 100%"
        assert "100.0%" in metrics["Severity Accuracy"], "Severity accuracy should be 100%"
    
    def test_issue_type_metrics(self, eval_summary):
        """Test per-category metrics extraction."""
        metrics = DashboardMetrics.issue_type_metrics(eval_summary)
        
        # Should have metrics for all 8 categories
        expected_categories = ["VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"]
        for category in expected_categories:
            assert category in metrics, f"Missing metrics for {category}"
            assert "total_cases" in metrics[category], f"Missing total_cases for {category}"
    
    def test_corrected_cases_by_type(self, rai_report):
        """Test corrected cases by issue type."""
        by_type = DashboardMetrics.corrected_cases_by_type(rai_report)
        
        # Should have one corrected case per issue type (from Phase 8)
        expected_types = ["VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"]
        for issue_type in expected_types:
            assert issue_type in by_type, f"Missing correction count for {issue_type}"
            assert by_type[issue_type] == 1, f"Should have 1 corrected {issue_type} case"
    
    def test_highest_correction_category(self, rai_report):
        """Test finding highest correction category."""
        highest = DashboardMetrics.highest_correction_category(rai_report)
        
        assert highest is not None, "Should find highest correction category"
        category, count = highest
        assert category == "WRONG_ROOT_CAUSE", "Highest should be WRONG_ROOT_CAUSE"
        assert count == 5, "WRONG_ROOT_CAUSE should have 5 cases"
    
    def test_highest_correction_category_empty(self):
        """Test highest correction with no corrections."""
        empty_report = {}
        highest = DashboardMetrics.highest_correction_category(empty_report)
        assert highest is None, "Empty report should return None"


class TestDashboardIntegration:
    """Integration tests for dashboard components working together."""
    
    @pytest.fixture
    def loader(self):
        """Initialize data loader."""
        return DashboardDataLoader()
    
    def test_full_data_pipeline(self, loader):
        """Test complete data loading pipeline."""
        # Load all data
        cases = loader.load_cases()
        reviews = loader.load_human_reviews()
        eval_results = loader.load_ai_evaluation_results()
        eval_summary = loader.load_ai_evaluation_summary()
        rai_report = loader.load_responsible_ai_report()
        
        # Verify all data loaded
        assert not cases.empty, "Cases should load"
        assert not reviews.empty, "Reviews should load"
        assert eval_summary, "Eval summary should load"
        assert rai_report, "RAI report should load"
        
        # Verify consistency
        case_ids_in_cases = set(cases['case_id'])
        case_ids_in_reviews = set(reviews['case_id'])
        
        # All reviewed cases should be in cases
        assert case_ids_in_reviews.issubset(case_ids_in_cases), "All reviewed cases should be in cases dataset"
    
    def test_metrics_consistency(self, loader):
        """Test that metrics are internally consistent."""
        cases = loader.load_cases()
        reviews = loader.load_human_reviews()
        
        # Get distributions
        review_dist = DashboardMetrics.review_distribution(reviews)
        total_reviews = DashboardMetrics.human_reviews_count(reviews)
        
        # Sum of distribution should equal total
        dist_total = sum(review_dist.values())
        assert dist_total == total_reviews, f"Distribution sum {dist_total} should equal total {total_reviews}"
        
        # Issue distribution total should equal total cases
        issue_dist = DashboardMetrics.issue_type_distribution(cases)
        issue_total = sum(issue_dist.values())
        total_cases = DashboardMetrics.total_cases(cases)
        assert issue_total == total_cases, f"Issue distribution sum {issue_total} should equal total cases {total_cases}"
    
    def test_no_hardcoded_values(self, loader):
        """Verify that no values are hardcoded - all calculated from actual data."""
        cases = loader.load_cases()
        reviews = loader.load_human_reviews()
        eval_summary = loader.load_ai_evaluation_summary()
        
        # Calculate key metrics
        total_cases = DashboardMetrics.total_cases(cases)
        review_dist = DashboardMetrics.review_distribution(reviews)
        agreement_rate = DashboardMetrics.ai_human_agreement_rate(reviews)
        
        # Verify calculations match expected values (not hardcoded)
        assert total_cases == len(cases), "Total should come from actual data"
        assert sum(review_dist.values()) == len(reviews), "Review counts should sum to actual reviews"
        
        # Verify agreement rate is calculated, not hardcoded
        expected_agreement = (review_dist["ACCEPT"] / len(reviews)) * 100
        assert abs(agreement_rate - expected_agreement) < 0.01, "Agreement rate should be calculated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
