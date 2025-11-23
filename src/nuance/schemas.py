"""
Pydantic schemas for strict validation of LLM outputs.
This is the "Guardrails" layer that prevents hallucinated/malformed data.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class Claim(BaseModel):
    """
    Represents a single statistical or causal claim extracted from text.

    This schema enforces strict structure on LLM outputs, enabling
    deterministic validation and retry mechanisms.
    """
    claim_id: str = Field(..., description="Unique identifier for this claim (e.g., 'c1', 'c2')")
    quote: str = Field(..., min_length=5, description="Exact quote from the original text")
    claim_type: Literal["statistical", "causal", "comparative", "absolute"] = Field(
        ...,
        description="Type of claim being made"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    variables: List[str] = Field(
        default_factory=list,
        description="Key variables mentioned in the claim"
    )
    numerical_values: List[str] = Field(
        default_factory=list,
        description="Any numbers, percentages, or statistics mentioned"
    )

    @field_validator('claim_id')
    @classmethod
    def validate_claim_id(cls, v: str) -> str:
        if not v.startswith('c') or not v[1:].isdigit():
            raise ValueError("claim_id must follow format 'c1', 'c2', etc.")
        return v


class ClaimsExtraction(BaseModel):
    """
    Container for all claims extracted from a text.
    """
    claims: List[Claim] = Field(..., min_length=1, description="List of extracted claims")
    total_claims: int = Field(..., ge=1, description="Total number of claims extracted")

    @field_validator('total_claims')
    @classmethod
    def validate_count_matches(cls, v: int, info) -> int:
        if 'claims' in info.data and len(info.data['claims']) != v:
            raise ValueError(f"total_claims ({v}) must match actual claims count ({len(info.data['claims'])})")
        return v


class StatisticalCheck(BaseModel):
    """
    Result of a deterministic statistical validation check.
    """
    check_name: str = Field(..., description="Name of the check performed")
    passed: bool = Field(..., description="Whether the check passed")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ...,
        description="Severity of the issue if check failed"
    )
    explanation: str = Field(..., min_length=10, description="Human-readable explanation")
    suggestion: Optional[str] = Field(None, description="How to fix the issue")


class ClaimAudit(BaseModel):
    """
    Complete audit report for a single claim.
    """
    claim_id: str = Field(..., description="ID of the claim being audited")
    claim_quote: str = Field(..., description="The original claim text")
    checks_performed: List[StatisticalCheck] = Field(..., description="All checks run on this claim")
    overall_status: Literal["clean", "minor_issues", "major_issues", "critical"] = Field(
        ...,
        description="Overall assessment"
    )

    @field_validator('claim_id')
    @classmethod
    def validate_claim_id_format(cls, v: str) -> str:
        if not v.startswith('c'):
            raise ValueError("claim_id must reference a valid claim (format: 'c1', 'c2', etc.)")
        return v


class TextMetrics(BaseModel):
    """
    Quantitative metrics calculated by Python (not LLM).
    This is the "Stats Layer" - deterministic analysis.
    """
    data_density_score: float = Field(..., ge=0.0, le=1.0, description="% of sentences with numbers/data")
    vagueness_score: float = Field(..., ge=0.0, le=1.0, description="Ratio of hedge words to definitive claims")
    extreme_language_count: int = Field(..., ge=0, description="Count of absolute terms (always/never/prove)")
    sample_size_mentioned: bool = Field(..., description="Whether sample size is mentioned")
    causation_language_count: int = Field(..., ge=0, description="Count of causal language without evidence")


class AuditReport(BaseModel):
    """
    Final audit report combining LLM extraction with Python validation.
    """
    text_metrics: TextMetrics = Field(..., description="Quantitative analysis from Python")
    claim_audits: List[ClaimAudit] = Field(..., description="Per-claim audit results")
    overall_reliability_score: float = Field(..., ge=0.0, le=100.0, description="Aggregated reliability score")
    summary: str = Field(..., min_length=50, description="Human-friendly summary of findings")
    key_issues: List[str] = Field(..., description="Top issues found")
