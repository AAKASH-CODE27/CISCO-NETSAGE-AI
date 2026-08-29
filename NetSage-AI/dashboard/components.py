"""
Reusable UI components for NetSage AI Dashboard (Phase 9).

Provides building blocks for consistent dashboard layout and styling.
"""

import streamlit as st
from typing import Dict, List, Any, Optional


def render_kpi_card(title: str, value: Any, description: str = "", metric_type: str = "number"):
    """Render a KPI card with title, value, and optional description."""
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label=title, value=value, delta=description if description else None)


def render_metric_row(metrics: Dict[str, Any], columns: int = 3):
    """Render a row of metrics using columns."""
    cols = st.columns(columns)
    for idx, (title, value) in enumerate(metrics.items()):
        with cols[idx % columns]:
            st.metric(label=title, value=value)


def render_distribution_chart(distribution: Dict[str, int], title: str, chart_type: str = "bar"):
    """Render a distribution chart (bar or pie)."""
    import plotly.express as px
    
    if not distribution:
        st.info(f"No data available for {title}")
        return
    
    df_data = {
        "category": list(distribution.keys()),
        "count": list(distribution.values())
    }
    
    if chart_type == "pie":
        fig = px.pie(df_data, names="category", values="count", title=title)
    else:  # bar
        fig = px.bar(df_data, x="category", y="count", title=title, labels={"count": "Count", "category": "Category"})
        fig.update_xaxes(tickangle=-45)
    
    st.plotly_chart(fig, use_container_width=True)


def render_section_header(title: str, description: str = ""):
    """Render a section header with optional description."""
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"_{description}_")


def render_case_summary(case: Dict[str, Any]):
    """Render a summary card for a troubleshooting case."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Case ID:** {case.get('case_id', 'N/A')}")
        st.markdown(f"**Issue Type:** {case.get('concept', 'N/A')}")
        st.markdown(f"**Severity:** {case.get('severity', 'N/A')}")
    
    with col2:
        st.markdown(f"**OSI Layer:** {case.get('osi_layer', 'N/A')}")
        st.markdown(f"**Concept:** {case.get('concept', 'N/A')}")


def render_case_section(title: str, content: str):
    """Render a case detail section with title and content."""
    with st.expander(title, expanded=True):
        if content and str(content).strip():
            st.markdown(content)
        else:
            st.info("No information available")


def render_review_status(decision: str, reason: str = "", correction: str = ""):
    """Render human review decision with styling."""
    decision_upper = str(decision).upper() if decision else "UNKNOWN"
    
    if decision_upper == "ACCEPT":
        st.success(f"✓ Human Decision: {decision_upper}")
    elif decision_upper == "EDIT":
        st.warning(f"✎ Human Decision: {decision_upper}")
    elif decision_upper == "REJECT":
        st.error(f"✗ Human Decision: {decision_upper}")
    else:
        st.info(f"Human Decision: {decision_upper}")
    
    if reason and str(reason).strip():
        st.markdown(f"**Reason:** {reason}")
    
    if correction and str(correction).strip() and decision_upper in ["EDIT", "REJECT"]:
        st.markdown(f"**Human Correction:** {correction}")


def render_comparison_box(ai_content: Dict[str, str], human_content: Dict[str, str] = None):
    """Render side-by-side comparison of AI and Human views."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Original AI Diagnosis")
        for key, value in ai_content.items():
            st.markdown(f"**{key}:** {value}")
    
    if human_content:
        with col2:
            st.markdown("### Human Correction")
            for key, value in human_content.items():
                st.markdown(f"**{key}:** {value}")


def render_empty_state(message: str):
    """Render empty state message."""
    st.info(f"ℹ️ {message}")


def render_error_state(message: str):
    """Render error state message."""
    st.error(f"❌ {message}")
