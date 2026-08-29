# NetSage AI — Responsible AI Log & Human Correction Analysis (Phase 8)

## 1. Purpose of Responsible AI Logging

Phase 8 implements a transparent, auditable **Responsible AI Audit Logging** architecture for NetSage AI. In enterprise network operations, AI systems must act in a recommendation-only capacity where human network engineers review every AI diagnosis before configuration changes occur.

The Responsible AI log provides complete auditability:
- **What the AI diagnosed** (original recommendation, preserved immutably).
- **Whether the AI was correct** (human decision: `ACCEPT`, `EDIT`, or `REJECT`).
- **What the human changed** (exact corrected root cause and fix steps).
- **Why the AI was wrong** (human reviewer explanation & classification).
- **What evidence supported the correction** (Cisco show commands & topology evidence).
- **What the final operational decision was**.

---

## 2. Responsible AI Audit Workflow Diagram

```text
                 AI Diagnosis
                      │
                      ▼
                 Human Review
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       ACCEPT        EDIT       REJECT
          │           │           │
          │           └────┬──────┘
          │                │
          │                ▼
          │        Human Correction
          │                │
          └────────┬───────┘
                   ▼
          Responsible AI Record
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Reason   Evidence   Lesson
          │        │        │
          └────────┼────────┘
                   ▼
             Audit Report
```

---

## 3. Human Decision Interpretation

- **ACCEPT**: Human engineer concurred with the AI diagnosis and recommendations. No substantive correction was required.
- **EDIT**: Human engineer modified specific components of the AI recommendation (e.g., specifying exact target VLAN, correcting host IP configuration, or providing missing Cisco IOS syntax commands).
- **REJECT**: Human engineer determined that the AI diagnosis was incorrect, overconfident, or unsafe, and substituted a complete human diagnosis.

---

## 4. Controlled Correction Vocabulary

Every human correction is classified using a controlled vocabulary:

| Category | Description |
|---|---|
| `WRONG_ROOT_CAUSE` | AI identified an incorrect fault mechanism (e.g., claiming routing error instead of Layer 2 VLAN issue). |
| `WRONG_SEVERITY` | AI incorrectly classified incident severity level. |
| `INSUFFICIENT_EVIDENCE` | AI drew conclusions without supporting Cisco show command evidence. |
| `UNSUPPORTED_CLAIM` | AI made unsupported assertions not present in input context. |
| `WRONG_NEXT_COMMAND` | AI suggested inappropriate or invalid verification commands. |
| `UNSAFE_FIX` | AI recommended fix steps that could disrupt production traffic. |
| `INCOMPLETE_FIX` | AI provided vague recommendations lacking exact Cisco IOS command syntax. |
| `OVERCONFIDENT_DIAGNOSIS` | AI output high confidence (≥ 80%) despite incorrect or incomplete evidence. |
| `MISINTERPRETED_EVIDENCE` | AI misread show command output parameters. |
| `N/A_ACCEPTED` | Diagnosis accepted without modification. |

---

## 5. Evidence Traceability & Immutability

### Original AI Output Preservation
The original AI output (`ai_root_cause`) is preserved **immutably** and is never overwritten by human corrections (`human_root_cause`). This preserves an accurate historical record of AI performance.

### Audit Traceability Path
```text
Cisco Show Command Evidence
          ↓
AI Model Reasoning & Confidence
          ↓
Human Engineer Decision & Reason
          ↓
Corrected Operational Diagnosis
```

---

## 6. Sample Responsible AI Log Record

```text
Case ID              : NET-033
Issue Category       : DHCP
AI Confidence        : 82% (High)

Original AI Cause    : DHCP server service is turned off globally.
Human Decision       : REJECT
Human Correction     : DHCP network statement subnet 192.168.2.0/24 mismatches interface Gi0/1 IP 192.168.10.1/24.

Correction Category  : WRONG_ROOT_CAUSE
Correction Reason    : AI wrongly claimed service dhcp was disabled. Show run showed service enabled but wrong network statement.
Supporting Evidence  : show running-config (ip dhcp pool LAN / network 192.168.2.0)
Lesson Learned       : High confidence scores must be corroborated with deterministic Layer 1/Layer 2 show outputs.
Timestamp            : 2026-08-28T11:05:00Z
```

---

## 7. CLI Execution & Report Generation

Generate Responsible AI audit records and summary reports:

```bash
python -m scripts.generate_responsible_ai_log --summary
```

### Generated Result Files
- **`results/responsible_ai_log.csv`**: Detailed audit log containing all 35 cases with original AI claims, human decisions, corrections, categories, evidence, and timestamps.
- **`results/responsible_ai_report.json`**: Aggregate metrics report containing counts of accepted/edited/rejected cases, correction category breakdown, and high-confidence error list.

---

## 8. Known Limitations

1. **Deterministic Categorization**: Initial category classification is based on controlled keyword analysis of human review reasons. Complex edge cases may be refined during Phase 9 dashboard operations.
2. **Offline Review Context**: Human review records reflect static snapshot evaluation and do not interactively re-prompt the LLM.
