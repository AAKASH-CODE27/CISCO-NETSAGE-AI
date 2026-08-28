# NetSage AI — AI Diagnosis Evaluation Pipeline (Phase 6)

## 1. Phase 6 Objective

Phase 6 implements a measurable, deterministic evaluation pipeline for NetSage AI. It takes the **35 troubleshooting cases**, executes deterministic rule-checker checks, generates AI-safe inputs, invokes AI diagnosis (via Google Gemini or Mock mode), and evaluates the LLM's responses against ground truth.

---

## 2. Evaluation Architecture

```text
                cases.csv
                    │
                    ▼
               Case Loader
                    │
                    ▼
             Ground Truth Split
                │          │
                │          └──────────────┐
                ▼                         │
           AI-Safe Input                 │
                │                         │
                ▼                         │
          Rule Checker                   │
                │                         │
                ▼                         │
         Evidence Bundle                 │
                │                         │
                ▼                         │
           Gemini Diagnosis              │
                │                         │
                ▼                         │
       DiagnosisResponse                 │
                │                         │
                └──────────┬──────────────┘
                           ▼
                       Evaluator
                           │
                  ┌────────┼────────┐
                  ▼        ▼        ▼
              Accuracy  Evidence  Confidence
                  │        │        │
                  └────────┼────────┘
                           ▼
                    CSV + JSON Results
```

---

## 3. Dataset Input & AI-Safe Separation

The dataset (`data/cases.csv`) contains 35 validated cases across 8 core networking categories. Each case is divided into:

- **Public Evidence** (accessible to AI): `case_id`, `symptom`, `topology_note`, `show_outputs`, `rule_findings`.
- **Ground Truth** (reserved strictly for evaluation): `expected_fault`, `expected_fix`, `expected_osi_layer`, `concept`, `severity`, `verification`.

The transformation helper `build_ai_input(case, rule_findings)` creates a `DiagnosisRequest` containing **zero ground truth**, protecting evaluation integrity.

---

## 4. Rule Checker Integration

Before AI diagnosis execution, each case is parsed into a `NetworkSnapshot` and passed to `run_all_checks(snapshot)`.

The resulting `RuleResult` findings (e.g. `gateway_mismatch`, `missing_vlan`, `interface_down`) are added to the evidence bundle supplied to the AI assistant.

---

## 5. Root Cause Evaluation

Root cause matching is strictly deterministic (no LLM judge):
1. **Normalized String Matching**: Strips whitespace, lowercases text, and removes punctuation.
2. **Controlled Terminology Equivalence**: Maps equivalent technical representations of the same fault (e.g. `"VLAN 10 is missing"` <-> `"Missing VLAN 10 in database"`).
3. **Strict Rejection**: Unrelated diagnosis claims (e.g. `"Missing VLAN"` vs `"ACL blocks traffic"`) return a mismatch.

---

## 6. Severity & OSI Layer Evaluation

- **Severity Matching**: Compares AI-predicted severity against expected severity case-insensitively (`High`, `Medium`, `Low`, `Critical`).
- **OSI Layer Evaluation**: Expected OSI layer is tracked. If AI outputs an OSI prediction, it is compared; otherwise, OSI accuracy is marked as unavailable (`None`) without altering Phase 4 Pydantic schema.

---

## 7. Evidence Grounding Evaluation

Evidence grounding verifies whether the AI response references legitimate input evidence:
- Extracts technical entities (IP addresses, VLAN IDs, interfaces, commands, status flags).
- Verifies that technical terms cited in `DiagnosisResponse.evidence` exist in the case input.
- Automatically marks diagnoses **ungrounded** if the AI references non-existent interfaces (e.g., `Gi0/99`) or fabricated metrics.

---

## 8. CLI Usage & Execution Modes

### Mock Mode (Offline)
Runs batch evaluation using simulated deterministic diagnoses without invoking external APIs:

```bash
python -m scripts.evaluate_ai --mock
```

### Real AI Mode (Gemini)
Runs batch evaluation against live Google Gemini API:

```bash
python -m scripts.evaluate_ai
```

---

## 9. Output Result Files

All outputs are saved to the `results/` directory:

1. **`results/ai_evaluation_results.csv`**: Detailed per-case breakdown containing `case_id`, `issue_type`, `ai_success`, `ai_root_cause`, `expected_root_cause`, `root_cause_match`, `ai_confidence`, `ai_severity`, `expected_severity`, `severity_match`, `ai_evidence`, `evidence_grounded`, `ai_next_command`, `ai_fix_steps`, `rule_checker_findings`, `error`, `latency_ms`.
2. **`results/ai_evaluation_summary.json`**: Aggregate summary metrics, confidence calibration breakdown, and per-category metrics.

---

## 10. Error Handling & Isolation

The batch evaluation pipeline wraps each case execution in an isolated `try/except` block. If an individual API call or parsing operation fails, the error is recorded for that specific case, and execution immediately continues to the next case.

---

## 11. Known Limitations

1. **Deterministic Grounding Scope**: Evidence grounding relies on entity and keyword overlap verification. Complex semantic paraphrasing without shared technical tokens may require manual review in Phase 7.
2. **Recommendation-Only**: All fix steps and next commands remain recommendations and are never auto-executed on network infrastructure.
