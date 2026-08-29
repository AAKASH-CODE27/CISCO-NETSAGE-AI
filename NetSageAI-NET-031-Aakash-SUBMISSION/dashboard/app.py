"""
NetSage AI Dashboard - Main Streamlit Application (Phase 9).

A web-based dashboard for visualizing troubleshooting cases, AI diagnoses,
human reviews, and responsible AI metrics.

Run with: streamlit run app.py
"""

import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from dashboard.data import DashboardDataLoader
from dashboard.metrics import DashboardMetrics
from dashboard import components


# Page configuration
st.set_page_config(
    page_title="NetSage AI Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    .success-badge {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
    }
    .warning-badge {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
    }
    .error-badge {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state and data
@st.cache_resource
def load_dashboard_data():
    """Load all dashboard data with caching."""
    loader = DashboardDataLoader()
    return {
        "cases": loader.load_cases(),
        "reviews": loader.load_human_reviews(),
        "eval_results": loader.load_ai_evaluation_results(),
        "eval_summary": loader.load_ai_evaluation_summary(),
        "rai_report": loader.load_responsible_ai_report(),
        "rai_log": loader.load_responsible_ai_log(),
        "loader": loader
    }


# Main application
def main():
    """Main dashboard application."""
    
    # Load data
    data = load_dashboard_data()
    
    # Header
    st.title("🔍 NetSage AI Dashboard")
    st.markdown("**AI-Assisted Network Troubleshooting System**")
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "Select a page:",
            ["Overview", "Issue Analysis", "Case Explorer", "Responsible AI"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### Data Status")
        
        # Data status indicators
        cases_count = DashboardMetrics.total_cases(data["cases"])
        reviews_count = DashboardMetrics.human_reviews_count(data["reviews"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cases Loaded", cases_count)
        with col2:
            st.metric("Reviews", reviews_count)
        
        if cases_count == 0:
            st.warning("⚠️ No cases loaded. Check data path.")
        else:
            st.success(f"✓ {cases_count} cases ready")
    
    # Page routing
    if page == "Overview":
        render_overview_page(data)
    elif page == "Issue Analysis":
        render_issue_analysis_page(data)
    elif page == "Case Explorer":
        render_case_explorer_page(data)
    elif page == "Responsible AI":
        render_responsible_ai_page(data)


def render_overview_page(data: Dict[str, Any]):
    """Render the overview page with KPIs and key metrics."""
    
    # Load data
    cases_df = data["cases"]
    reviews_df = data["reviews"]
    eval_summary = data["eval_summary"]
    rai_report = data["rai_report"]
    
    if cases_df.empty:
        components.render_error_state("No cases data available. Please check the data/cases.csv file.")
        return
    
    # Calculate metrics
    total_cases = DashboardMetrics.total_cases(cases_df)
    ai_diagnoses = DashboardMetrics.ai_diagnoses_count(reviews_df)
    human_reviews = DashboardMetrics.human_reviews_count(reviews_df)
    
    review_dist = DashboardMetrics.review_distribution(reviews_df)
    agreement_rate = DashboardMetrics.ai_human_agreement_rate(reviews_df)
    
    corrected_count = DashboardMetrics.corrected_case_count(rai_report)
    
    # KPI Cards
    components.render_section_header("Project Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cases", total_cases)
    with col2:
        st.metric("AI Diagnoses", ai_diagnoses)
    with col3:
        st.metric("Human Reviews", human_reviews)
    with col4:
        st.metric("Corrected Cases", corrected_count)
    
    # Review distribution and agreement
    components.render_section_header("Human Review Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Review distribution
        components.render_distribution_chart(
            review_dist,
            "Review Decision Distribution",
            chart_type="bar"
        )
    
    with col2:
        # Agreement rate
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("ACCEPT", review_dist.get("ACCEPT", 0))
        with col_b:
            st.metric("EDIT", review_dist.get("EDIT", 0))
        with col_c:
            st.metric("REJECT", review_dist.get("REJECT", 0))
        
        st.markdown("---")
        st.metric("AI-Human Agreement Rate", f"{agreement_rate:.1f}%")
    
    # AI Evaluation Metrics
    components.render_section_header("AI Evaluation Metrics")
    
    eval_metrics = DashboardMetrics.ai_evaluation_metrics(eval_summary)
    
    # Render metrics in columns
    metric_items = list(eval_metrics.items())
    cols = st.columns(3)
    for idx, (title, value) in enumerate(metric_items):
        with cols[idx % 3]:
            st.metric(title, value)


def render_issue_analysis_page(data: Dict[str, Any]):
    """Render page with issue and severity analysis."""
    
    cases_df = data["cases"]
    eval_summary = data["eval_summary"]
    
    if cases_df.empty:
        components.render_error_state("No cases data available.")
        return
    
    components.render_section_header("Issue Type Distribution")
    
    issue_dist = DashboardMetrics.issue_type_distribution(cases_df)
    
    if not issue_dist:
        components.render_empty_state("No issue type data available.")
        return
    
    # Calculate percentages
    total = sum(issue_dist.values())
    issue_pct = {k: f"{v} ({v/total*100:.1f}%)" if total > 0 else f"{v}" for k, v in issue_dist.items()}
    
    col1, col2 = st.columns(2)
    
    with col1:
        components.render_distribution_chart(issue_dist, "Cases by Issue Type", chart_type="bar")
    
    with col2:
        components.render_distribution_chart(issue_dist, "Issue Type Distribution", chart_type="pie")
    
    # Severity distribution
    components.render_section_header("Severity Distribution", "Expected Severity Levels")
    
    severity_dist = DashboardMetrics.severity_distribution(cases_df)
    
    if severity_dist:
        col1, col2 = st.columns(2)
        
        with col1:
            components.render_distribution_chart(severity_dist, "Cases by Severity", chart_type="bar")
        
        with col2:
            components.render_distribution_chart(severity_dist, "Severity Distribution", chart_type="pie")
    else:
        components.render_empty_state("No severity data available.")
    
    # Per-category metrics
    components.render_section_header("Metrics by Issue Type")
    
    category_metrics = DashboardMetrics.issue_type_metrics(eval_summary)
    
    if category_metrics:
        st.markdown("### AI Performance by Issue Category")
        
        for category, metrics in sorted(category_metrics.items()):
            with st.expander(f"{category} ({metrics.get('total_cases', 0)} cases)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    root_cause_acc = metrics.get('root_cause_accuracy', 0)
                    st.metric("Root Cause Accuracy", f"{root_cause_acc * 100:.1f}%" if root_cause_acc is not None else "N/A")
                
                with col2:
                    severity_acc = metrics.get('severity_accuracy', 0)
                    st.metric("Severity Accuracy", f"{severity_acc * 100:.1f}%" if severity_acc is not None else "N/A")
                
                with col3:
                    evidence_rate = metrics.get('evidence_grounding_rate', 0)
                    st.metric("Evidence Grounding", f"{evidence_rate * 100:.1f}%" if evidence_rate is not None else "N/A")
    else:
        components.render_empty_state("No category metrics available.")


def render_case_explorer_page(data: Dict[str, Any]):
    """Render the interactive case explorer page."""
    
    cases_df = data["cases"]
    reviews_df = data["reviews"]
    eval_results_df = data["eval_results"]
    loader = data["loader"]
    
    if cases_df.empty:
        components.render_error_state("No cases data available.")
        return
    
    components.render_section_header("Case Explorer", "Search and filter troubleshooting cases")
    
    # Filters in sidebar
    st.sidebar.markdown("### Case Filters")
    
    # Get unique values for filters
    issue_types = sorted(cases_df['concept'].unique()) if 'concept' in cases_df.columns else []
    severities = sorted(cases_df['severity'].unique()) if 'severity' in cases_df.columns else []
    
    # Filter options
    selected_issue = st.sidebar.multiselect(
        "Issue Type",
        options=issue_types if issue_types else [],
        default=None
    )
    
    selected_severity = st.sidebar.multiselect(
        "Severity",
        options=severities if severities else [],
        default=None
    )
    
    selected_review_decision = st.sidebar.multiselect(
        "Review Decision",
        options=["ACCEPT", "EDIT", "REJECT"],
        default=None
    )
    
    # Search box
    search_term = st.sidebar.text_input(
        "Search by Case ID",
        placeholder="e.g., NET-001"
    )
    
    # Apply filters
    filtered_cases = cases_df.copy()
    
    if selected_issue:
        filtered_cases = filtered_cases[filtered_cases['concept'].isin(selected_issue)]
    
    if selected_severity:
        filtered_cases = filtered_cases[filtered_cases['severity'].isin(selected_severity)]
    
    if search_term:
        filtered_cases = filtered_cases[filtered_cases['case_id'].str.contains(search_term, case=False, na=False)]
    
    # Filter by review decision if available
    if selected_review_decision and not reviews_df.empty:
        decision_col = 'human_decision' if 'human_decision' in reviews_df.columns else None
        if decision_col:
            review_cases = reviews_df[reviews_df[decision_col].str.upper().isin(selected_review_decision)]['case_id'].tolist()
            filtered_cases = filtered_cases[filtered_cases['case_id'].isin(review_cases)]
    
    st.markdown(f"### Found {len(filtered_cases)} case(s)")
    
    if filtered_cases.empty:
        components.render_empty_state("No cases match the selected filters.")
        return
    
    # Case selection
    case_ids = sorted(filtered_cases['case_id'].tolist())
    selected_case_id = st.selectbox(
        "Select a case to view details:",
        options=case_ids,
        format_func=lambda x: x
    )
    
    if selected_case_id:
        render_case_detail_view(
            selected_case_id,
            cases_df,
            reviews_df,
            eval_results_df,
            loader
        )


def render_case_detail_view(
    case_id: str,
    cases_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
    eval_results_df: pd.DataFrame,
    loader: DashboardDataLoader
):
    """Render detailed view for a selected case."""
    
    # Get case data
    case = loader.get_case_by_id(case_id, cases_df)
    review = loader.get_case_review(case_id, reviews_df)
    evaluation = loader.get_case_evaluation(case_id, eval_results_df)
    
    if not case:
        components.render_error_state(f"Case {case_id} not found.")
        return
    
    st.markdown("---")
    st.markdown(f"## Case Details: {case_id}")
    
    # Case information
    components.render_section_header("Case Information")
    components.render_case_summary(case)
    
    # Symptom
    components.render_case_section(
        "Symptom",
        case.get('symptom', '')
    )
    
    # Topology
    components.render_case_section(
        "Network Topology",
        case.get('topology_note', '')
    )
    
    # Show command evidence
    components.render_case_section(
        "Show Command Evidence",
        case.get('show_outputs', '')
    )
    
    # Expected fix and verification (from ground truth)
    components.render_case_section(
        "Expected Fix (Ground Truth)",
        case.get('expected_fix', '')
    )
    
    components.render_case_section(
        "Verification Procedure (Ground Truth)",
        case.get('verification', '')
    )
    
    # AI Diagnosis (from evaluation if available)
    if evaluation:
        components.render_section_header("AI Diagnosis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Root Cause", evaluation.get('ai_root_cause', 'N/A')[:50] + "...")
        with col2:
            st.metric("Confidence", f"{evaluation.get('ai_confidence', 0):.2f}")
        with col3:
            st.metric("Severity", evaluation.get('ai_severity', 'N/A'))
        
        with st.expander("Full AI Diagnosis Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Root Cause:**")
                st.markdown(evaluation.get('ai_root_cause', 'N/A'))
                
                st.markdown("**Evidence:**")
                evidence = evaluation.get('ai_evidence', [])
                if evidence:
                    for item in evidence:
                        st.markdown(f"- {item}")
                else:
                    st.markdown("No evidence recorded")
            
            with col2:
                st.markdown("**Next Command:**")
                st.markdown(evaluation.get('ai_next_command', 'N/A'))
                
                st.markdown("**Severity:**")
                st.markdown(evaluation.get('ai_severity', 'N/A'))
    
    # Human Review (CRITICAL: Preserve original AI diagnosis)
    if review:
        components.render_section_header("Human Review")
        
        decision = review.get('human_decision', 'UNKNOWN')
        components.render_review_status(
            decision,
            review.get('reason', ''),
            review.get('human_correction', '')
        )
        
        # Show original AI diagnosis and human correction side-by-side
        if str(decision).upper() in ["EDIT", "REJECT"]:
            st.markdown("---")
            st.markdown("### Original AI vs. Human Review")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Original AI Diagnosis")
                st.markdown(f"**Root Cause:** {review.get('ai_root_cause', 'N/A')}")
                st.markdown(f"**Confidence:** {review.get('ai_confidence', 0):.2f}")
            
            with col2:
                st.markdown("#### Human Correction")
                if review.get('human_correction'):
                    st.markdown(f"**Correction:** {review.get('human_correction')}")
                else:
                    st.markdown("_No correction provided_")
    else:
        st.info("No human review available for this case.")
    
    # Responsible AI (if corrected)
    if review and str(review.get('human_decision', '')).upper() in ["EDIT", "REJECT"]:
        components.render_section_header("Responsible AI - Correction Analysis")
        st.info("This case received human correction. See details above.")


def render_responsible_ai_page(data: Dict[str, Any]):
    """Render responsible AI metrics and corrections."""
    
    rai_report = data["rai_report"]
    rai_log = data["rai_log"]
    cases_df = data["cases"]
    reviews_df = data["reviews"]
    
    if not rai_report:
        components.render_error_state("No responsible AI report available.")
        return
    
    components.render_section_header("Responsible AI Metrics")
    
    # Key metrics
    total_reviewed = rai_report.get("total_reviewed", 0)
    accepted = rai_report.get("accepted", 0)
    edited = rai_report.get("edited", 0)
    rejected = rai_report.get("rejected", 0)
    corrected = rai_report.get("corrected_cases", 0)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Reviewed", total_reviewed)
    with col2:
        st.metric("Accepted", accepted)
    with col3:
        st.metric("Edited", edited)
    with col4:
        st.metric("Rejected", rejected)
    with col5:
        st.metric("Corrected Cases", corrected)
    
    # Correction categories
    components.render_section_header("Correction Categories")
    
    correction_categories = DashboardMetrics.correction_category_distribution(rai_report)
    
    if correction_categories:
        components.render_distribution_chart(
            correction_categories,
            "Correction Categories Distribution",
            chart_type="bar"
        )
        
        st.markdown("### Category Details")
        for category, count in sorted(correction_categories.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- **{category}**: {count} cases")
    else:
        components.render_empty_state("No correction categories found.")
    
    # Corrections by issue type
    components.render_section_header("Corrections by Issue Type")
    
    corrections_by_type = DashboardMetrics.corrected_cases_by_type(rai_report)
    
    if corrections_by_type:
        components.render_distribution_chart(
            corrections_by_type,
            "Corrected Cases by Issue Type",
            chart_type="bar"
        )
    else:
        components.render_empty_state("No correction data by issue type.")
    
    # Highest correction category
    highest = DashboardMetrics.highest_correction_category(rai_report)
    if highest:
        category, count = highest
        st.markdown(f"### Most Common Correction Category")
        st.success(f"**{category}** - {count} occurrences")
    
    # Correction log details
    components.render_section_header("Detailed Correction Log")
    
    if not rai_log.empty:
        st.dataframe(rai_log, use_container_width=True)
    else:
        components.render_empty_state("No detailed correction log available.")


if __name__ == "__main__":
    main()
