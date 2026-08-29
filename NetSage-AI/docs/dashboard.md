# NetSage AI Dashboard - User Guide

## Overview

The NetSage AI Dashboard is a web-based interface for visualizing network troubleshooting cases, AI diagnoses, human reviews, and responsible AI metrics.

**Technology Stack:**

- Streamlit (web framework)
- Plotly (interactive visualizations)
- Pandas (data processing)

## Features

### 1. Overview Page

Displays key performance indicators (KPIs):

- **Total Cases**: 35 network troubleshooting scenarios
- **AI Diagnoses**: Cases that received AI diagnosis
- **Human Reviews**: Cases reviewed by network engineers
- **Corrected Cases**: Cases where human review corrected AI diagnosis
- **Review Distribution**: Count of ACCEPT, EDIT, and REJECT decisions
- **AI-Human Agreement Rate**: Percentage of cases accepted by humans (77.1% in current dataset)
- **AI Evaluation Metrics**: Root cause accuracy, severity accuracy, evidence grounding, and average confidence

### 2. Issue Analysis Page

Breaks down troubleshooting cases by category and severity:

- **Issue Type Distribution**: Shows cases across all 8 categories:
  - VLAN (5 cases)
  - Gateway (4 cases)
  - DHCP (5 cases)
  - DNS (4 cases)
  - Routing (5 cases)
  - ACL (4 cases)
  - NAT (4 cases)
  - Wireless (4 cases)
- **Severity Distribution**: Cases by Low, Medium, High, and Critical severity
- **Per-Category Metrics**: AI performance metrics for each issue type

### 3. Case Explorer

Interactive search and filtering for individual cases:

- **Filters**:
  - Issue Type (single or multiple)
  - Severity (single or multiple)
  - Review Decision (ACCEPT, EDIT, REJECT)
- **Search**: By case ID (e.g., "NET-001")
- **Case Details**: Full view of selected case including:
  - Case information (ID, type, severity, OSI layer)
  - Symptom description
  - Network topology
  - Show command evidence
  - Expected fix (ground truth)
  - AI diagnosis with confidence score
  - Human review decision
  - Original AI diagnosis preserved alongside human correction

### 4. Responsible AI Page

Metrics on how human review improved AI diagnoses:

- **Correction Metrics**: Total reviewed, accepted, edited, rejected, and corrected cases
- **Correction Categories**: Distribution of correction types:
  - WRONG_ROOT_CAUSE (5 cases)
  - INCOMPLETE_FIX (3 cases)
- **Corrections by Issue Type**: One corrected case per category
- **Detailed Log**: Table of all corrections with reasons

## Data Sources

All dashboard data is loaded from actual project files (no hardcoded values):

| Data           | Source                               | Purpose                                                 |
| -------------- | ------------------------------------ | ------------------------------------------------------- |
| Cases          | `data/cases.csv`                     | Troubleshooting scenarios, symptoms, topology, evidence |
| AI Evaluations | `results/ai_evaluation_summary.json` | AI accuracy metrics, confidence scores                  |
| Human Reviews  | `review/human_review.csv`            | Accept/Edit/Reject decisions and corrections            |
| Responsible AI | `results/responsible_ai_report.json` | Correction categories and metrics                       |
| Correction Log | `results/responsible_ai_log.csv`     | Detailed correction records                             |

## Key Metrics

### AI-Human Agreement Rate

**Definition**: (Accepted Reviews / Total Reviews) × 100%

**Current**: 27 accepted / 35 total = **77.1%**

This measures how often human engineers agreed with AI diagnoses.

### Root Cause Accuracy

**Definition**: Percentage of cases where AI correctly identified the root cause

**Current**: **100.0%** (35/35 cases)

### Evidence Grounding Rate

**Definition**: Percentage of cases where AI evidence citations are valid

**Current**: **100.0%** (35/35 cases)

## Workflow Visualization

The dashboard demonstrates the complete troubleshooting workflow:

```
Broken Network
    ↓
Symptom & Show Evidence
    ↓
Rule Checker (Deterministic)
    ↓
AI Diagnosis (Gemini)
    ↓
Human Review (ACCEPT/EDIT/REJECT)
    ↓
Recommended Fix
    ↓
Verification Steps
```

## Safety Features

✅ **Read-Only Design**: Dashboard does not modify any data or execute commands

✅ **Original AI Preserved**: For EDIT or REJECT cases, original AI diagnosis is displayed alongside human correction

✅ **No Auto-Fix**: Dashboard shows recommended fixes but does not automatically execute Cisco commands

✅ **Graceful Error Handling**: Missing data files are handled without crashes

## Running the Dashboard

### Prerequisites

```bash
pip install streamlit plotly pandas pydantic python-dotenv
```

### Start Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### Alternative: Direct Python

```bash
python -m streamlit run e:\COLLEGE\AI\PROJECT\CISCO\NetSage-AI\dashboard\app.py
```

## Architecture

### Data Loading (`dashboard/data.py`)

- `DashboardDataLoader`: Handles loading all CSV and JSON files
- Normalizes column names
- Handles missing files gracefully
- Provides case lookup methods

### Metrics Calculation (`dashboard/metrics.py`)

- `DashboardMetrics`: Calculates all displayed metrics
- All values computed from actual data (no hardcoding)
- Includes methods for:
  - Total case counts
  - Distribution calculations (by issue, severity, review)
  - Agreement rate
  - Evaluation metrics extraction
  - Responsible AI metrics

### UI Components (`dashboard/components.py`)

Reusable components for consistent display:

- `render_kpi_card()`: Metric cards
- `render_distribution_chart()`: Bar/pie charts
- `render_section_header()`: Page sections
- `render_case_summary()`: Case overview
- `render_review_status()`: Review decision with styling
- Error and empty state handlers

### Main Application (`dashboard/app.py`)

- Streamlit page configuration
- Session state management
- Data caching (@st.cache_resource)
- Page routing (Overview, Issue Analysis, Case Explorer, Responsible AI)
- Sidebar navigation

## Testing

### Run Dashboard Tests

```bash
python -m pytest tests/test_dashboard.py -v
```

### Run All Tests

```bash
python -m pytest tests/ -q
```

### Current Test Results

- Dashboard tests: **29 passing**
- Total tests: **115 passing** (86 existing + 29 new)

### Test Coverage

Tests verify:
✅ All data files load correctly  
✅ All 35 cases loaded  
✅ All 8 issue categories present  
✅ Issue distribution totals 35  
✅ Severity distribution includes all levels  
✅ Review counts match (27 ACCEPT, 5 EDIT, 3 REJECT)  
✅ AI-human agreement rate calculated correctly  
✅ 8 corrected cases identified  
✅ Correction categories match actual data  
✅ No hardcoded metric values  
✅ Metrics internally consistent

## Troubleshooting

### Dashboard won't start

```bash
# Verify Streamlit is installed
pip show streamlit

# Check file permissions
ls -la dashboard/app.py

# Try with verbose output
streamlit run dashboard/app.py --logger.level=debug
```

### Data not loading

1. Verify files exist:
   - `data/cases.csv`
   - `review/human_review.csv`
   - `results/ai_evaluation_summary.json`
   - `results/responsible_ai_report.json`
   - `results/responsible_ai_log.csv`

2. Check file format (CSV files should have headers)

3. Dashboard will show "No data available" if files are missing - this is expected

### Charts not rendering

- Check that Plotly is installed: `pip show plotly`
- Ensure data is not empty
- Try refreshing the page

## Performance

- Dashboard caches all data on first load
- Subsequent page navigation is instant
- Data refresh requires page reload or cache clear

## Limitations

- **No automatic network fixes**: Recommendations are display-only
- **No real-time updates**: Data is static from files
- **Single-instance**: Not designed for multi-user concurrent access
- **No authentication**: Designed for local demonstration

## Future Enhancements (Not in Phase 9)

- Real-time case submission
- Live network integration
- Multi-user collaboration
- Persistent human review in database
- Advanced filtering with full-text search
- Export to PDF/Excel reports

---

**Version**: Phase 9  
**Last Updated**: 2026-08-29  
**Status**: Production Ready
