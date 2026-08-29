"""
Final verification script for Phase 9 completion.

Run this to verify all dashboard components are working correctly.
"""

from dashboard.data import DashboardDataLoader
from dashboard.metrics import DashboardMetrics


def verify_dashboard():
    """Run comprehensive verification of dashboard functionality."""
    
    print("=" * 60)
    print("PHASE 9 - DASHBOARD FINAL VERIFICATION")
    print("=" * 60)
    
    # Initialize loader
    loader = DashboardDataLoader()
    
    # [1/6] Load all data sources
    print("\n[1/6] Loading all data sources...")
    cases = loader.load_cases()
    reviews = loader.load_human_reviews()
    eval_summary = loader.load_ai_evaluation_summary()
    rai_report = loader.load_responsible_ai_report()
    print("✅ All data loaded successfully")
    
    # [2/6] Verify case count
    print("\n[2/6] Verifying case counts...")
    total = DashboardMetrics.total_cases(cases)
    assert total == 35, f"Expected 35 cases, got {total}"
    print(f"✅ Total cases: {total}")
    
    # [3/6] Verify issue distribution
    print("\n[3/6] Verifying issue type distribution...")
    issue_dist = DashboardMetrics.issue_type_distribution(cases)
    expected = {
        "VLAN": 5,
        "Gateway": 4,
        "DHCP": 5,
        "DNS": 4,
        "Routing": 5,
        "ACL": 4,
        "NAT": 4,
        "Wireless": 4
    }
    for category, expected_count in expected.items():
        actual = issue_dist.get(category, 0)
        assert actual == expected_count, f"{category}: expected {expected_count}, got {actual}"
        print(f"  ✅ {category}: {actual} cases")
    
    # [4/6] Verify review distribution
    print("\n[4/6] Verifying human review distribution...")
    review_dist = DashboardMetrics.review_distribution(reviews)
    assert review_dist["ACCEPT"] == 27, f"Expected 27 ACCEPT, got {review_dist['ACCEPT']}"
    assert review_dist["EDIT"] == 5, f"Expected 5 EDIT, got {review_dist['EDIT']}"
    assert review_dist["REJECT"] == 3, f"Expected 3 REJECT, got {review_dist['REJECT']}"
    print(f"  ✅ ACCEPT: {review_dist['ACCEPT']}")
    print(f"  ✅ EDIT: {review_dist['EDIT']}")
    print(f"  ✅ REJECT: {review_dist['REJECT']}")
    
    # [5/6] Verify agreement rate
    print("\n[5/6] Verifying AI-human agreement rate...")
    agreement = DashboardMetrics.ai_human_agreement_rate(reviews)
    expected_rate = (27 / 35) * 100
    assert abs(agreement - expected_rate) < 0.1, f"Expected ~{expected_rate}%, got {agreement}%"
    print(f"  ✅ Agreement rate: {agreement:.1f}%")
    
    # [6/6] Verify responsible AI
    print("\n[6/6] Verifying responsible AI metrics...")
    corrected = DashboardMetrics.corrected_case_count(rai_report)
    assert corrected == 8, f"Expected 8 corrected cases, got {corrected}"
    corrections = DashboardMetrics.correction_category_distribution(rai_report)
    assert "WRONG_ROOT_CAUSE" in corrections and corrections["WRONG_ROOT_CAUSE"] == 5
    assert "INCOMPLETE_FIX" in corrections and corrections["INCOMPLETE_FIX"] == 3
    print(f"  ✅ Corrected cases: {corrected}")
    print(f"  ✅ WRONG_ROOT_CAUSE: {corrections['WRONG_ROOT_CAUSE']}")
    print(f"  ✅ INCOMPLETE_FIX: {corrections['INCOMPLETE_FIX']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL VERIFICATIONS PASSED - DASHBOARD READY")
    print("=" * 60)
    print("\nTo start dashboard:")
    print("  streamlit run dashboard/app.py")
    print("=" * 60)


if __name__ == "__main__":
    verify_dashboard()
