# NetSage AI — Troubleshooting Case Dataset Documentation (Phase 5)

## 1. Dataset Purpose

The NetSage AI Troubleshooting Case Dataset provides a benchmark of **35 realistic Cisco/Packet Tracer lab scenarios** across 8 core networking domains. 

The dataset is designed for:
1. **Deterministic Rule-Checker Evaluation**: Verifying basic network configuration checks.
2. **AI Diagnosis Evaluation**: Testing the LLM's multi-step reasoning capabilities.
3. **Human Review & Feedback**: Benchmarking engineer decision-making in Phase 5/6.
4. **Responsible AI & Metric Analysis**: Measuring accuracy, hallucination rates, and confidence calibration.
5. **Packet Tracer Demonstrations**: Driving interactive lab walkthroughs.

---

## 2. Ground-Truth Separation Architecture

To prevent data leakage during LLM evaluation, each case is strictly divided into **Public Evidence** (accessible to the AI) and **Ground Truth** (reserved strictly for evaluation).

```text
                           Full Troubleshooting Case (data/cases.csv)
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
      Public Evidence                                         Ground Truth
      (AI-Safe Input)                                     (Evaluation Only)
             │                                                     │
   ├── case_id                                            ├── expected_fault
   ├── symptom                                            ├── osi_layer
   ├── topology_note                                      ├── concept
   ├── show_outputs                                       ├── severity
   └── (rule_checker_findings)                            ├── expected_fix
             │                                            └── verification
             ▼                                                     │
       Python Rule Checker                                         │
             │                                                     │
             ▼                                                     │
         LLM Engine                                                │
             │                                                     │
             ▼                                                     │
     DiagnosisResponse                                             │
             │                                                     │
             └──────────────────────────┬──────────────────────────┘
                                        ▼
                               Evaluation Engine
```

---

## 3. Dataset Schema & Pydantic Models

Dataset records are validated by the `TroubleshootingCase` model in `data/models.py`:

| Field | Access Level | Type | Description |
|-------|--------------|------|-------------|
| `case_id` | Public | `str` | Unique identifier (e.g. `NET-001`) |
| `concept` | Ground Truth | `IssueCategory` | One of the 8 issue types (`VLAN`, `Gateway`, etc.) |
| `symptom` | Public | `str` | User-visible problem description |
| `topology_note` | Public | `str` | Topology and device connections |
| `show_outputs` | Public | `str` | Realistic Cisco IOS show command outputs |
| `expected_fault` | Ground Truth | `str` | Definitive root cause explanation |
| `osi_layer` | Ground Truth | `OSILayer` | OSI layer (`Layer 1` - `Layer 7`) |
| `severity` | Ground Truth | `SeverityLevel` | Severity rating (`Low`, `Medium`, `High`, `Critical`) |
| `expected_fix` | Ground Truth | `str` | Recommended remediation configuration steps |
| `verification` | Ground Truth | `str` | Verification command or procedure |

---

## 4. Required Issue Categories & Distribution

The dataset contains **35 cases** across 8 required networking categories:

| Category | Target Count | Actual Count | Key Coverage Areas |
|----------|--------------|--------------|-------------------|
| **VLAN** | 5 | 5 | Access VLAN mismatch, missing database VLAN, trunk allowed list, native VLAN mismatch, unassigned access port. |
| **Gateway** | 4 | 4 | Incorrect default gateway, router interface admin down, gateway outside subnet, router-on-a-stick subinterface missing dot1q. |
| **DHCP** | 5 | 5 | Pool exhaustion, incorrect default-router, missing helper-address, unexcluded router IP, wrong subnet statement. |
| **DNS** | 4 | 4 | Loopback DNS IP, ACL blocking UDP port 53, mistyped DNS IP, missing router `ip name-server`. |
| **Routing** | 5 | 5 | Missing static route, wrong default route next-hop, OSPF network mismatch, EIGRP AS mismatch, RIP passive interface. |
| **ACL** | 4 | 4 | Extended ACL denying HTTP, standard ACL near source blocking all traffic, reversed src/dst ports, ACL applied in wrong direction/interface. |
| **NAT** | 4 | 4 | Missing `ip nat inside`, missing `overload` keyword, NAT ACL excluding new subnet, static NAT mapping wrong internal IP. |
| **Wireless** | 4 | 4 | Guest WLAN mapped to wrong VLAN, 802.1X vs PSK mismatch, WLC DHCP scope disabled, Guest isolation ACL missing from switch interface. |
| **TOTAL** | **35** | **35** | **100% Target Met** |

---

## 5. AI-Safe Input Conversion

The helper function `build_ai_input(case)` (or `case.to_ai_request()`) extracts public fields into a `DiagnosisRequest`:

```python
from data.models import TroubleshootingCase, build_ai_input

# Load case from CSV/DB
case = TroubleshootingCase(...)

# Generate AI-safe input (strips expected_fault, osi_layer, expected_fix, severity, concept)
ai_request = build_ai_input(case)

# Send ai_request to generate_diagnosis(ai_request)
```

---

## 6. Severity & OSI Layer Definitions

### Severity Levels
- **Low**: Minor configuration mismatch or cosmetic issue; single host or diagnostic feature affected.
- **Medium**: Single department, host, or non-critical service unable to reach network resources.
- **High**: Entire VLAN, subnet, or major service (DHCP, NAT, Wireless) failing.
- **Critical**: Complete branch/WAN outage, default route failure, or internal infrastructure security breach.

### OSI Layers
- **Layer 1 (Physical)**: Interface `administratively down`, duplex/speed mismatch, cable disconnects.
- **Layer 2 (Data Link)**: VLAN database mismatch, trunking errors, native VLAN, WLC WLAN profile mapping, port security.
- **Layer 3 (Network)**: Gateway settings, subnet mismatches, static/dynamic routing (OSPF, EIGRP, RIP), IP helper relay, NAT inside/outside.
- **Layer 4 (Transport)**: ACL port filtering (TCP/UDP), PAT port overloading, SSH/HTTP port blocks.
- **Layer 7 (Application)**: DHCP pool configuration, DNS resolution settings, name-server options.

---

## 7. Validation Procedure

Run the dataset validation script:

```bash
python -m scripts.validate_cases
```

Validation rules enforced:
1. Exactly 35 cases present in `data/cases.csv`.
2. All 35 `case_id` values are unique.
3. Every required column is present and non-empty.
4. Category distribution matches the 35 target breakdown (5 VLAN, 4 Gateway, 5 DHCP, 4 DNS, 5 Routing, 4 ACL, 4 NAT, 4 Wireless).
5. All 35 records pass Pydantic schema validation (`TroubleshootingCase`).
6. Zero ground-truth leakage when converted via `build_ai_input()`.

---

## 8. How to Add New Cases

1. Open `data/cases.csv`.
2. Append a new row following the 10-column schema (`case_id`, `symptom`, `topology_note`, `show_outputs`, `expected_fault`, `osi_layer`, `concept`, `severity`, `expected_fix`, `verification`).
3. Ensure `case_id` follows sequential naming (e.g. `NET-036`).
4. Keep show outputs realistic using standard Cisco IOS format.
5. Run `python -m scripts.validate_cases` and `pytest` to ensure all checks pass.
