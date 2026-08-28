# AI Diagnosis Documentation

## 1. Purpose

The AI diagnosis module uses a Large Language Model (LLM) to analyze network troubleshooting cases and produce structured, evidence-backed diagnoses. It sits alongside the deterministic rule checker in the NetSage AI pipeline.

## 2. Architecture

```text
DiagnosisRequest (Pydantic)
    |
    +-- case_id, symptom, topology_note, show_outputs
    +-- rule_findings (List[RuleResult] from Phase 3)
    |
    v
build_user_prompt()     -- excludes ground-truth fields
    |
    v
_load_system_prompt()   -- reads prompts/diagnose_prompt.md
    |
    v
_call_llm()             -- Google Gemini API
    |
    v
_extract_json()         -- handles code fences / preamble
    |
    v
parse_diagnosis_response()
    |
    v
DiagnosisResponse (Pydantic validated)
    |
    +-- root_cause, confidence, evidence, next_command, fix_steps, severity
```

## 3. Why LLM + Rule Checker?

| Aspect | Rule Checker | LLM |
|--------|-------------|-----|
| Speed | Microseconds | Seconds |
| Scope | 6 specific config checks | Broad reasoning |
| Reproducibility | 100% deterministic | Probabilistic |
| Hallucination risk | Zero | Non-zero |
| Cost | Free | API tokens |

**Together**: The rule checker catches obvious configuration mistakes deterministically. The LLM synthesises symptoms, topology, show-command evidence, and rule-checker findings to reason about complex or ambiguous faults. Human review is the final gate.

## 4. Input Model — DiagnosisRequest

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | str | Unique case identifier |
| `symptom` | str | What the user/operator observes |
| `topology_note` | str | Network topology description |
| `show_outputs` | str | Raw Cisco IOS show-command output |
| `rule_findings` | List[RuleResult] | Deterministic rule-checker results |

**Ground-truth fields (`expected_fault`, `osi_layer`, `concept`) are deliberately excluded** so the LLM cannot cheat during evaluation.

## 5. Output Model — DiagnosisResponse

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | str | Echoed case ID |
| `root_cause` | str | Identified root cause |
| `confidence` | float [0.0, 1.0] | Numeric confidence score |
| `evidence` | List[str] | Cited evidence items |
| `next_command` | str | Recommended next diagnostic command |
| `fix_steps` | List[str] | Ordered remediation steps |
| `severity` | str (optional) | Low / Medium / High / Critical |

## 6. Confidence Calibration

| Range | Meaning |
|-------|---------|
| 0.90 - 1.00 | Evidence strongly confirms the diagnosis |
| 0.75 - 0.89 | Strong support; additional confirmation useful |
| 0.50 - 0.74 | Plausible but evidence is incomplete |
| Below 0.50 | Insufficient evidence; recommend more diagnostics |

## 7. Prompt Design

The production prompt (`prompts/diagnose_prompt.md`) contains:

1. **Role**: Expert network troubleshooting assistant
2. **Evidence rules**: Must cite supplied evidence; never invent output
3. **Rule-checker interpretation**: Treat as independent signal, not absolute truth
4. **Confidence rules**: Numeric 0.0-1.0 with calibration guidance
5. **JSON schema**: Strict output format
6. **Safety constraints**: Recommendations only; human review required
7. **Three worked examples**: NET-002 (VLAN), NET-005 (Gateway), NET-015 (Routing)

## 8. LLM Provider

Currently configured for **Google Gemini** via the `google-generativeai` SDK.

Configuration (`.env`):
```
LLM_API_KEY=your_key_here
LLM_MODEL_NAME=gemini-2.0-flash
```

The model uses `temperature=0.2` for more deterministic responses.

## 9. Error Handling

- **Missing API key**: Raises `EnvironmentError` with instructions.
- **Missing SDK**: Raises `ImportError` with install command.
- **Malformed LLM response**: `_extract_json()` attempts fence extraction, then brace matching, then raises `ValueError`.
- **Schema validation failure**: Pydantic rejects responses with missing fields or out-of-range confidence.
- **Batch mode**: `generate_diagnosis_batch()` captures per-case errors and returns placeholder responses so one failure doesn't halt the entire batch.

## 10. Safety Constraints

1. The LLM never receives ground-truth answers during normal operation.
2. Fix steps are recommendations only — never auto-executed.
3. The LLM is explicitly instructed not to invent evidence or claim commands were executed.
4. All diagnoses go through human review (Phase 5).
5. No API keys are stored in source code.

## 11. Testing

Tests in `tests/test_diagnosis.py` validate:
- Model creation and validation
- Confidence bounds enforcement
- Prompt construction (no ground-truth leakage)
- JSON extraction from various LLM response formats
- Response parsing and case-ID backfill
- System prompt content verification

All tests run **offline** — no LLM API calls required.

## 12. Limitations

- Depends on LLM availability and API key.
- LLM responses are probabilistic; the same input may produce slightly different outputs.
- The current implementation calls the LLM sequentially; no parallelism.
- Does not implement retry logic for transient API failures.
- Complex multi-fault scenarios may require iterative diagnosis (not yet supported).
