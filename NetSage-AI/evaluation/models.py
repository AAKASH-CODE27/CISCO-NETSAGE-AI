"""
Evaluation models for NetSage AI (Phase 6).

Defines Pydantic models for per-case evaluation results, per-category metrics,
confidence analysis items, and aggregate summary metrics.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Evaluation result for a single troubleshooting case.

    Compares AI DiagnosisResponse outputs against TroubleshootingCase ground truth.
    """
    case_id: str = Field(..., description="Unique case identifier (e.g. NET-001)")
    issue_type: str = Field(..., description="Networking category (VLAN, Gateway, etc.)")
    ai_success: bool = Field(..., description="True if AI diagnosis succeeded without exception")
    
    # Root Cause Evaluation
    ai_root_cause: str = Field(default="", description="Root cause diagnosed by AI")
    expected_root_cause: str = Field(..., description="Ground-truth expected fault")
    root_cause_match: bool = Field(default=False, description="True if AI root cause matches ground truth")
    
    # Confidence
    ai_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="AI confidence score")
    
    # Severity Evaluation
    ai_severity: Optional[str] = Field(default=None, description="Severity returned by AI")
    expected_severity: str = Field(..., description="Ground-truth expected severity")
    severity_match: bool = Field(default=False, description="True if AI severity matches expected severity")
    
    # OSI Layer Evaluation
    ai_osi_layer: Optional[str] = Field(default=None, description="OSI layer diagnosed by AI (if supported)")
    expected_osi_layer: str = Field(..., description="Ground-truth expected OSI layer")
    osi_layer_match: Optional[bool] = Field(default=None, description="True if OSI layer matches (None if unsupported)")
    
    # Evidence Grounding
    ai_evidence: List[str] = Field(default_factory=list, description="Evidence items cited by AI")
    evidence_grounded: bool = Field(default=False, description="True if AI evidence cites legitimate case data")
    
    # Next Command & Fix Steps (Captured for review, non-autonomous)
    ai_next_command: str = Field(default="", description="Next diagnostic command proposed by AI")
    ai_fix_steps: List[str] = Field(default_factory=list, description="Remediation steps proposed by AI")
    
    # Context & Diagnostics
    rule_checker_findings: List[str] = Field(default_factory=list, description="Deterministic rule checker finding messages")
    error: Optional[str] = Field(default=None, description="Error message if diagnosis failed")
    latency_ms: Optional[float] = Field(default=None, description="Diagnosis execution latency in milliseconds")


class CategoryMetric(BaseModel):
    """Aggregated performance metrics for a specific networking issue category."""
    category: str = Field(..., description="Category name (VLAN, Gateway, etc.)")
    total_cases: int = Field(..., description="Total cases in this category")
    successful: int = Field(..., description="Number of successful AI diagnoses")
    root_cause_accuracy: float = Field(..., description="Ratio of root cause matches (0.0 - 1.0)")
    severity_accuracy: float = Field(..., description="Ratio of severity matches (0.0 - 1.0)")
    evidence_grounding_rate: float = Field(..., description="Ratio of grounded AI diagnoses (0.0 - 1.0)")


class ConfidenceAnalysisItem(BaseModel):
    """Counts for a specific confidence bucket vs actual correctness."""
    confidence_bucket: str = Field(..., description="Bucket name ('high' >= 0.8, 'medium' 0.5-0.79, 'low' < 0.5)")
    total: int = Field(default=0, description="Total cases in this bucket")
    correct: int = Field(default=0, description="Cases that were correct (root cause match)")
    wrong: int = Field(default=0, description="Cases that were incorrect (root cause mismatch)")


class SummaryMetrics(BaseModel):
    """Overall evaluation summary metrics across the entire dataset."""
    total_cases: int = Field(..., description="Total troubleshooting cases evaluated")
    successful_diagnoses: int = Field(..., description="Count of successful AI diagnoses")
    failed_diagnoses: int = Field(..., description="Count of failed AI diagnoses")
    
    # Accuracies & Rates
    root_cause_accuracy: float = Field(..., description="Overall root cause accuracy (0.0 - 1.0)")
    severity_accuracy: float = Field(..., description="Overall severity accuracy (0.0 - 1.0)")
    osi_accuracy: Optional[float] = Field(default=None, description="Overall OSI layer accuracy if supported, else None")
    evidence_grounding_rate: float = Field(..., description="Overall evidence grounding rate (0.0 - 1.0)")
    
    # Confidence metrics
    avg_confidence: float = Field(..., description="Average AI confidence across all cases")
    confidence_distribution: Dict[str, int] = Field(..., description="Distribution of cases by confidence level")
    confidence_accuracy_breakdown: Dict[str, Dict[str, int]] = Field(..., description="High/Medium/Low confidence vs correctness")
    
    # Per-category metrics
    category_metrics: Dict[str, CategoryMetric] = Field(..., description="Breakdown of metrics by category tag")
