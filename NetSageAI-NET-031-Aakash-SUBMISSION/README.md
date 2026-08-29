# NetSage AI

## Project Overview

NetSage AI is an AI-assisted network troubleshooting helper for Cisco-style Packet Tracer/networking labs.

## Domain

Networking Labs

## Main Course

Modern AI

## Safety Rule

Human Review

## Problem

Junior network engineers often struggle to connect symptoms with root causes such as VLAN, routing, DHCP, DNS, ACL, NAT and related networking faults. This project provides an AI-assisted diagnostic pipeline to aid in troubleshooting.

## Proposed Solution

The eventual pipeline:
Packet Tracer / Lab
-> Symptoms
-> Topology + Show Commands
-> Python Rule Checker
-> AI Diagnosis
-> Evidence-backed JSON
-> Human Review
-> Fix
-> Verification
-> Dashboard

## Core Components

1. Case dataset
2. AI prompt library
3. Python rule checker
4. AI diagnosis
5. Human review
6. Dashboard
7. Responsible AI log
8. Packet Tracer demonstration

## Phase Plan

Phase 1: Project foundation and architecture ✅
Phase 2: Packet Tracer scenarios and 30+ case dataset ✅
Phase 3: Deterministic Python rule checker ✅
Phase 4: AI diagnosis and structured JSON output ✅
Phase 5: Case dataset and evaluation ✅
Phase 6: AI evaluation pipeline ✅
Phase 7: Human review and Responsible AI logging ✅
Phase 8: Responsible AI evaluation ✅
Phase 9: Dashboard and Case Explorer ✅

## Safety Principle

AI must recommend rather than autonomously apply network fixes. Human review is required before accepting a diagnosis/fix.

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### Run Tests

```bash
python -m pytest tests/ -q
```

## Dashboard Features

- **Overview**: KPI cards showing total cases, reviews, and AI metrics
- **Issue Analysis**: Distribution of cases by category and severity
- **Case Explorer**: Interactive search and filter for individual cases
- **Responsible AI**: Metrics on human corrections and feedback
- **Full Case Details**: Symptom, evidence, AI diagnosis, and human review side-by-side

See [Dashboard Documentation](docs/dashboard.md) for detailed guide.

## Demo Walkthrough

For a 5-10 minute demonstration, see [Demo Script](docs/demo_walkthrough.md).

## Packet Tracer Scenario

For instructions on creating a demo network in Packet Tracer, see [Packet Tracer Demo](docs/packet_tracer_demo.md).

## Project Status

Phase 1-9: COMPLETE ✅
