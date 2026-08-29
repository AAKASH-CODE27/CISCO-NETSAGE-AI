# NetSage AI Architecture

## 1. Project objective
Build an AI-assisted troubleshooting helper for Cisco-style Packet Tracer/networking lab problems.

## 2. High-level architecture

```text
Packet Tracer
      |
      v
Troubleshooting Case
      |
      +--------------------+
      |                    |
      v                    v
Python Rule Checker       LLM
      |                    |
      +---------+----------+
                |
                v
        Diagnosis JSON
                |
                v
          Human Review
          /    |    \
      Accept Edit Reject
                |
                v
          Fix + Verify
                |
                v
            Dashboard
```

## 3. Component responsibilities
- **Python Rule Checker**: Deterministically checks for common config mistakes.
- **LLM Diagnosis**: Reasons over symptoms, notes, and outputs.
- **Human Review**: A human-in-the-loop step to approve, modify, or reject AI suggestions.
- **Dashboard**: Displays issue types, severity, and AI-vs-human agreement metrics.

## 4. Data flow
Symptoms and show commands -> deterministic rules & AI evaluation -> structured JSON -> Human review -> Fix resolution -> Dashboard updates.

## 5. Human-in-the-loop design
AI suggests recommendations. A human must manually accept, edit, or reject the AI diagnosis.

## 6. Deterministic rules vs AI reasoning
Deterministic checks ensure fast identification of known basic faults. The AI handles ambiguous cases and synthesizes findings.

## 7. Planned inputs and outputs
Inputs: Symptoms, Topology notes, CLI show outputs.
Outputs: Structured JSON with root cause, confidence, evidence, next commands, and fix steps.

## 8. Security considerations
- LLM API keys must not be hardcoded or logged.
- AI is not allowed to run external commands automatically.
- No direct external network modification without human review.

## 9. Future extensibility
- New deterministic rules.
- Expanding AI prompts for different scenarios.
- Enhancing the dashboard with analytics.
