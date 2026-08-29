"""
NetSage AI -- AI Diagnosis Module
==================================

Orchestrates the full diagnosis pipeline:

1. Accept a DiagnosisRequest (symptom, topology, show outputs, rule findings).
2. Build a prompt from the production template.
3. Call the configured LLM.
4. Parse and validate the response into a DiagnosisResponse.

The module supports Google Gemini via the ``google-generativeai`` SDK.
The LLM provider and API key are read from environment variables.

No network configuration changes are made.  All diagnoses are
recommendations subject to human review.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from .models import DiagnosisRequest, DiagnosisResponse
from rule_checker.models import RuleResult, RuleStatus

# Load .env from project root (if present)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------

_PROMPT_PATH = _PROJECT_ROOT / "prompts" / "diagnose_prompt.md"


def _load_system_prompt() -> str:
    """Read the production prompt template from disk."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _format_rule_findings(findings: List[RuleResult]) -> str:
    """Convert rule-checker results to a human-readable block for the LLM."""
    if not findings:
        return "No rule-checker findings available."

    lines: list[str] = []
    for f in findings:
        lines.append(
            f"- {f.rule}: {f.status.value} | {f.message}"
        )
        if f.evidence:
            lines.append(f"  Evidence: {'; '.join(f.evidence)}")
    return "\n".join(lines)


def build_user_prompt(request: DiagnosisRequest) -> str:
    """Build the user-facing portion of the prompt from a DiagnosisRequest.

    The prompt deliberately excludes ground-truth fields
    (``expected_fault``, ``osi_layer``, ``concept``, ``severity``)
    so the LLM cannot cheat during evaluation.
    """
    return (
        f"Case ID: {request.case_id}\n"
        f"Symptom: {request.symptom}\n"
        f"Topology: {request.topology_note}\n"
        f"Show Command Output:\n{request.show_outputs}\n\n"
        f"Rule Checker Findings:\n{_format_rule_findings(request.rule_findings)}"
    )


# ---------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------

def _extract_json(text: str) -> str:
    """Extract a JSON object from the LLM response.

    Handles cases where the model wraps the JSON in markdown code
    fences or adds explanatory text before/after.
    """
    # Try to find a JSON code fence first
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # Try to find a raw JSON object
    brace_start = text.find("{")
    if brace_start == -1:
        raise ValueError("No JSON object found in LLM response.")

    # Find the matching closing brace
    depth = 0
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start : i + 1]

    raise ValueError("Malformed JSON object in LLM response (unmatched braces).")


def parse_diagnosis_response(
    raw_text: str, case_id: str = ""
) -> DiagnosisResponse:
    """Parse and validate the raw LLM text into a DiagnosisResponse.

    Raises ``ValueError`` if the response cannot be parsed or
    validated.
    """
    json_str = _extract_json(raw_text)
    data = json.loads(json_str)

    # Ensure case_id is present
    if "case_id" not in data or not data["case_id"]:
        data["case_id"] = case_id

    return DiagnosisResponse(**data)


# ---------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------

def _get_gemini_model():
    """Lazily import and configure the Google Gemini client."""
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise ImportError(
            "google-generativeai is required for AI diagnosis. "
            "Install it with: pip install google-generativeai"
        ) from exc

    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "LLM_API_KEY environment variable is not set. "
            "Copy .env.example to .env and add your API key."
        )

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash"),
        system_instruction=_load_system_prompt(),
    )
    return model


def _call_llm(user_prompt: str) -> str:
    """Send the prompt to the configured LLM and return the raw text."""
    model = _get_gemini_model()
    response = model.generate_content(
        user_prompt,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 1024,
        },
    )
    return response.text


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

def generate_diagnosis(request: DiagnosisRequest) -> DiagnosisResponse:
    """Run the full AI diagnosis pipeline.

    1. Build the prompt from the request.
    2. Call the LLM.
    3. Parse and validate the structured JSON response.

    Parameters
    ----------
    request : DiagnosisRequest
        Contains case_id, symptom, topology_note, show_outputs,
        and optional rule_findings.

    Returns
    -------
    DiagnosisResponse
        Validated structured diagnosis.

    Raises
    ------
    ValueError
        If the LLM response cannot be parsed or validated.
    EnvironmentError
        If the API key is not configured.
    ImportError
        If the google-generativeai SDK is not installed.
    """
    user_prompt = build_user_prompt(request)
    raw_response = _call_llm(user_prompt)
    return parse_diagnosis_response(raw_response, case_id=request.case_id)


def generate_diagnosis_batch(
    requests: List[DiagnosisRequest],
) -> List[DiagnosisResponse]:
    """Run diagnosis on multiple cases sequentially.

    Returns a list of DiagnosisResponse objects.  If a single case
    fails, the error is captured and a placeholder response is
    returned for that case.
    """
    results: List[DiagnosisResponse] = []
    for req in requests:
        try:
            resp = generate_diagnosis(req)
            results.append(resp)
        except Exception as exc:
            results.append(DiagnosisResponse(
                case_id=req.case_id,
                root_cause=f"ERROR: {exc}",
                confidence=0.0,
                evidence=[f"Diagnosis failed: {exc}"],
                next_command="Retry diagnosis",
                fix_steps=["Investigate the error and retry"],
                severity="Unknown",
            ))
    return results
