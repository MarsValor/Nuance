"""
Claude API client for statistical claim extraction and analysis.

This module handles all interactions with the Anthropic API, using
strict schema validation and retry mechanisms.
"""

import os
from typing import List
import anthropic
from dotenv import load_dotenv

from .schemas import ClaimsExtraction, Claim, ClaimAudit, StatisticalCheck
from .retry import validate_with_retry

# Load environment variables
load_dotenv()


class ClaudeClient:
    """
    Client for interacting with Claude API with built-in validation.
    """

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Model to use for generation
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or arguments")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def extract_claims(self, text: str) -> ClaimsExtraction:
        """
        Extract statistical and causal claims from text.

        Uses retry mechanism to ensure valid structured output.

        Args:
            text: Input text to analyze

        Returns:
            ClaimsExtraction with validated claims
        """
        prompt = self._build_extraction_prompt(text)

        messages = [{"role": "user", "content": prompt}]

        return validate_with_retry(
            client=self.client,
            model=self.model,
            initial_messages=messages,
            schema_class=ClaimsExtraction,
            max_retries=3
        )

    def generate_audit_summary(
        self,
        original_text: str,
        claim_audits: List[ClaimAudit],
        text_metrics: dict
    ) -> str:
        """
        Generate human-friendly summary of audit findings.

        Args:
            original_text: The original text that was analyzed
            claim_audits: List of audit results for each claim
            text_metrics: Dictionary of quantitative metrics

        Returns:
            Plain-language explanation of findings
        """
        prompt = self._build_summary_prompt(original_text, claim_audits, text_metrics)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_counterfactuals(
        self,
        claim_quote: str,
        fallacy_type: str,
        check_explanation: str
    ) -> List[str]:
        """
        Generate alternative explanations for a logical fallacy.

        This is the "deep reasoning" feature that teaches users to think
        about alternative hypotheses and confounding factors.

        Args:
            claim_quote: The problematic claim
            fallacy_type: Type of logical error (e.g., "Correlation vs Causation")
            check_explanation: Why this is problematic

        Returns:
            List of 3-4 alternative explanations
        """
        prompt = self._build_counterfactual_prompt(claim_quote, fallacy_type, check_explanation)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.7,  # Slightly higher for creative alternatives
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response into list of alternatives
        response_text = response.content[0].text.strip()

        # Split by numbered lines (1., 2., 3., etc.) or bullet points
        import re
        alternatives = re.split(r'\n\s*[\d•\-\*]+[\.\)]\s*', response_text)

        # Clean up and filter
        alternatives = [alt.strip() for alt in alternatives if alt.strip()]

        # If parsing failed, try splitting by newlines
        if len(alternatives) < 2:
            alternatives = [line.strip() for line in response_text.split('\n') if line.strip()]

        # Return up to 4 alternatives
        return alternatives[:4]

    def _build_extraction_prompt(self, text: str) -> str:
        """Build prompt for claim extraction."""
        return f"""You are a statistical reasoning auditor. Your job is to extract concrete, testable claims from text.

Analyze this text and extract ALL statistical, causal, comparative, or absolute claims:

<text>
{text}
</text>

For each claim, identify:
1. The exact quote from the text
2. The type of claim (statistical/causal/comparative/absolute)
3. Any variables or factors mentioned
4. Any numerical values, percentages, or statistics

IMPORTANT INSTRUCTIONS:
- Extract ONLY claims that make factual assertions
- Do NOT extract opinions or subjective statements
- Include the exact quote from the original text
- Assign sequential IDs: c1, c2, c3, etc.
- Be thorough but precise

Output your response as JSON matching this exact schema:

{{
    "claims": [
        {{
            "claim_id": "c1",
            "quote": "exact quote from text",
            "claim_type": "statistical" | "causal" | "comparative" | "absolute",
            "confidence": 0.0 to 1.0,
            "variables": ["variable1", "variable2"],
            "numerical_values": ["50%", "1000", "3x"]
        }}
    ],
    "total_claims": number_of_claims
}}

Output ONLY the JSON, with no additional text or explanation."""

    def _build_summary_prompt(
        self,
        original_text: str,
        claim_audits: List[ClaimAudit],
        text_metrics: dict
    ) -> str:
        """Build prompt for generating audit summary."""

        # Format claim audits for context
        audits_text = "\n\n".join([
            f"Claim {audit.claim_id}: \"{audit.claim_quote}\"\n"
            f"Status: {audit.overall_status}\n"
            f"Issues found: {len([c for c in audit.checks_performed if not c.passed])}\n"
            f"Details: {', '.join([c.explanation for c in audit.checks_performed if not c.passed])}"
            for audit in claim_audits
        ])

        return f"""You are a statistical reasoning educator. Your job is to explain audit findings in a clear, educational way.

ORIGINAL TEXT:
{original_text}

QUANTITATIVE ANALYSIS:
- Data density: {text_metrics.get('data_density_score', 0):.1%} of sentences contain numbers/statistics
- Vagueness score: {text_metrics.get('vagueness_score', 0):.1%} (higher = more hedge words)
- Extreme language: {text_metrics.get('extreme_language_count', 0)} instances of absolute terms
- Sample size mentioned: {text_metrics.get('sample_size_mentioned', False)}
- Causation language: {text_metrics.get('causation_language_count', 0)} instances without evidence

CLAIM-BY-CLAIM AUDIT RESULTS:
{audits_text}

Your task: Write a clear, educational summary (200-300 words) that:

1. Starts with an overall assessment (is this text data-driven or hand-wavy?)
2. Highlights the 2-3 most important issues found
3. Explains WHY each issue is problematic (teach statistical reasoning)
4. Keeps a balanced tone (not preachy, but informative)

Focus on being helpful, not judgmental. The goal is to train the reader's "bullshit detector."

Write your summary now:"""

    def _build_counterfactual_prompt(
        self,
        claim_quote: str,
        fallacy_type: str,
        check_explanation: str
    ) -> str:
        """Build prompt for generating counterfactual explanations."""

        # Customize prompts based on fallacy type
        if "correlation" in fallacy_type.lower() or "causation" in fallacy_type.lower():
            focus = """
Think like a skeptical scientist. What are alternative explanations for this correlation?
Consider:
- Confounding variables (what else might cause both?)
- Reverse causation (does B actually cause A instead?)
- Selection bias (who was studied?)
- Spurious correlation (coincidence?)"""

        elif "sample" in fallacy_type.lower():
            focus = """
Think about sample size issues. What could go wrong with small or biased samples?
Consider:
- Statistical noise and random variation
- Non-representative samples
- Cherry-picked data
- Publication bias"""

        elif "extreme" in fallacy_type.lower() or "absolute" in fallacy_type.lower():
            focus = """
Think about exceptions and edge cases. Why is absolute language problematic?
Consider:
- Edge cases and exceptions
- Context-dependent situations
- Individual variation
- Time-dependent factors"""

        elif "base rate" in fallacy_type.lower():
            focus = """
Think about missing context. What information would change the interpretation?
Consider:
- Absolute numbers vs percentages
- Starting baseline
- Comparison groups
- Historical context"""

        else:
            focus = """
Think critically about what might be wrong or missing in this reasoning.
Consider alternative explanations, missing information, and potential biases."""

        return f"""You are teaching critical thinking. A claim has a logical issue.

Claim: "{claim_quote}"

Issue: {fallacy_type}
Why it's problematic: {check_explanation}

{focus}

Generate 3-4 concise alternative explanations (each 1-2 sentences). Format as a numbered list:

1. [First alternative explanation]
2. [Second alternative explanation]
3. [Third alternative explanation]
4. [Fourth alternative explanation]

Be specific and educational. Help the reader think deeper about this claim."""


def get_client() -> ClaudeClient:
    """
    Convenience function to get a configured Claude client.
    """
    return ClaudeClient()
