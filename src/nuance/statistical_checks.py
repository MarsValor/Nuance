"""
Statistical analysis engine - the "deterministic layer."

This module contains Python-based heuristics that analyze text WITHOUT relying on LLMs.
This is where your stats expertise shines - code handles the math, not Claude.
"""

import re
from typing import List, Dict, Tuple
from .schemas import Claim, StatisticalCheck, TextMetrics


# Pattern definitions
HEDGE_WORDS = [
    r'\bmight\b', r'\bmay\b', r'\bcould\b', r'\bpossibly\b', r'\bperhaps\b',
    r'\bprobably\b', r'\blikely\b', r'\bseems?\b', r'\bappears?\b', r'\bsuggests?\b',
    r'\btends?\b', r'\boften\b', r'\bsometimes\b', r'\bgenerally\b'
]

EXTREME_WORDS = [
    r'\bprove[sd]?\b', r'\balways\b', r'\bnever\b', r'\bimpossible\b',
    r'\bcertainly\b', r'\bdefinitely\b', r'\bclearly\b', r'\bobviously\b',
    r'\bundoubtedly\b', r'\ball\b', r'\bnone\b', r'\bevery\b', r'\bno\b',
    r'\bcure[sd]?\b', r'\bwill\b', r'\bguarantee[sd]?\b', r'\bcertain\b',
    r'\bzero risk\b', r'\bmust\b', r'\bcan\'?t\b', r'\bwon\'?t\b',
    r'\beliminates?\b', r'\bensures?\b', r'\b100%\b', r'\bcompletely\b',
    r'\bentirely\b', r'\babsolutely\b', r'\btotally\b'
]

CAUSATION_WORDS = [
    r'\bcauses?\b', r'\bcaused by\b', r'\bleads? to\b', r'\bresults? in\b',
    r'\bmakes?\b', r'\bforces?\b', r'\bproduces?\b', r'\bcreates?\b',
    r'\bdue to\b', r'\bbecause of\b', r'\btherefore\b', r'\bthus\b',
    r'\bincreases?\b', r'\bdecreases?\b', r'\bimproves?\b', r'\bworsens?\b',
    r'\bcures?\b', r'\bboosts?\b', r'\breduces?\b', r'\braises?\b',
    r'\blowers?\b', r'\benhances?\b', r'\bprevents?\b', r'\btriggers?\b',
    r'\benables?\b', r'\bdisables?\b'
]

SAMPLE_SIZE_PATTERNS = [
    r'\bn\s*=\s*\d+', r'\bsample size[:\s]+\d+', r'\b\d+\s+participants?\b',
    r'\b\d+\s+subjects?\b', r'\b\d+\s+respondents?\b', r'\b\d+\s+people\b',
    r'\bN\s*=\s*\d+'
]

NUMBER_PATTERNS = [
    r'\b\d+\.?\d*%', r'\b\d+\.?\d*x\b', r'\b\d+\.?\d*\s*times\b',
    r'\b\d+\s*percent', r'\$\d+', r'\b\d+\.?\d*\s*(million|billion|thousand)\b'
]

RISK_MULTIPLIER_PATTERNS = [
    r'\bdoubl(e|es|ed|ing)\b', r'\btripl(e|es|ed|ing)\b',
    r'\b\d+x\s+(higher|more|greater|increased)',
    r'\b\d+\s+times\s+(higher|more|greater|as likely)',
    r'\b\d+%\s+increase', r'\b\d+00%\b'  # e.g., 200%, 300%
]

RISK_WORDS = [
    r'\brisk\b', r'\bchance\b', r'\blikely\b', r'\blikelihood\b',
    r'\bprobability\b', r'\bodds\b', r'\bmore likely\b', r'\bhazard\b'
]

EFFECT_WORDS = [
    r'\bimproved?\b', r'\breduced?\b', r'\bincreased?\b', r'\bdecreased?\b',
    r'\bbetter\b', r'\bworse\b', r'\bmore effective\b', r'\bless effective\b',
    r'\bsuperior\b', r'\binferior\b', r'\benhanced?\b', r'\bworked\b',
    r'\bhelped\b', r'\bbenefited\b', r'\bboosted\b',
    # Medical/health claim verbs (common in supplement marketing)
    r'\bregulates?\b', r'\bfights?\b', r'\bblocks?\b', r'\bstops?\b',
    r'\bprevents?\b', r'\bcures?\b'  # Also in other checks, but good to catch here too
]

COMPARATOR_WORDS = [
    r'\bthan\b', r'\bvs\.?\b', r'\bversus\b', r'\bcompared to\b',
    r'\bcompared with\b', r'\brelative to\b', r'\bagainst\b',
    r'\bcontrol group\b', r'\bplacebo\b', r'\bbaseline\b',
    r'\bcontrol\b', r'\bcomparison group\b'
]


class StatisticalAnalyzer:
    """
    Performs deterministic statistical analysis on text and claims.
    """

    def __init__(self, text: str):
        """
        Initialize analyzer with text to analyze.

        Args:
            text: The full text to analyze
        """
        self.text = text
        self.sentences = self._split_sentences(text)

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        Simple implementation - can be improved with NLP library if needed.
        """
        # Basic sentence splitting on period, exclamation, question mark
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def calculate_text_metrics(self) -> TextMetrics:
        """
        Calculate all text-level metrics using Python (not LLM).

        Returns:
            TextMetrics with all calculated scores
        """
        return TextMetrics(
            data_density_score=self._calculate_data_density(),
            vagueness_score=self._calculate_vagueness_score(),
            extreme_language_count=self._count_extreme_language(),
            sample_size_mentioned=self._check_sample_size_mentioned(),
            causation_language_count=self._count_causation_language()
        )

    def _calculate_data_density(self) -> float:
        """
        Calculate what % of sentences contain numbers/statistics.

        Returns:
            Float between 0.0 and 1.0
        """
        if not self.sentences:
            return 0.0

        sentences_with_numbers = 0
        for sentence in self.sentences:
            # Check if sentence contains any numerical patterns
            if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in NUMBER_PATTERNS):
                sentences_with_numbers += 1

        return sentences_with_numbers / len(self.sentences)

    def _calculate_vagueness_score(self) -> float:
        """
        Calculate ratio of hedge words to total words.
        Higher score = more vague language.

        Returns:
            Float between 0.0 and 1.0
        """
        text_lower = self.text.lower()
        total_words = len(self.text.split())

        if total_words == 0:
            return 0.0

        hedge_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in HEDGE_WORDS
        )

        # Normalize to 0-1 scale (cap at 10% hedge words = score of 1.0)
        return min(1.0, (hedge_count / total_words) * 10)

    def _count_extreme_language(self) -> int:
        """
        Count instances of absolute/extreme language (always, never, prove, etc.).

        Returns:
            Count of extreme words found
        """
        text_lower = self.text.lower()
        return sum(
            len(re.findall(pattern, text_lower))
            for pattern in EXTREME_WORDS
        )

    def _check_sample_size_mentioned(self) -> bool:
        """
        Check if sample size is mentioned anywhere in the text.

        Returns:
            True if sample size found, False otherwise
        """
        return any(
            re.search(pattern, self.text, re.IGNORECASE)
            for pattern in SAMPLE_SIZE_PATTERNS
        )

    def _count_causation_language(self) -> int:
        """
        Count instances of causal language (causes, leads to, results in, etc.).

        Returns:
            Count of causation words found
        """
        text_lower = self.text.lower()
        return sum(
            len(re.findall(pattern, text_lower))
            for pattern in CAUSATION_WORDS
        )

    def check_claim(self, claim: Claim) -> List[StatisticalCheck]:
        """
        Run all statistical checks on a single claim.

        Args:
            claim: The claim to check

        Returns:
            List of StatisticalCheck results
        """
        checks = []

        # Check 1: Correlation vs Causation
        checks.append(self._check_correlation_vs_causation(claim))

        # Check 2: Sample Size
        checks.append(self._check_sample_size(claim))

        # Check 3: Extreme Language
        checks.append(self._check_extreme_language_in_claim(claim))

        # Check 4: Base Rate
        checks.append(self._check_base_rate(claim))

        # Check 5: Data Support
        checks.append(self._check_data_support(claim))

        # Check 6: Relative Risk Without Context (HIGH severity)
        checks.append(self._check_relative_risk_without_context(claim))

        # Check 7: Missing Comparator
        checks.append(self._check_missing_comparator(claim))

        return checks

    def _check_correlation_vs_causation(self, claim: Claim) -> StatisticalCheck:
        """
        Check if claim uses causal language (content-based, not type-based).
        """
        quote_lower = claim.quote.lower()
        has_causation_words = any(
            re.search(pattern, quote_lower)
            for pattern in CAUSATION_WORDS
        )

        # Check for experimental evidence markers
        has_experimental_evidence = bool(re.search(
            r'\brandomized\b|\bcontrolled trial\b|\bRCT\b|\bexperiment\b|\bintervention\b',
            claim.quote,
            re.IGNORECASE
        ))

        if has_causation_words and not has_experimental_evidence:
            return StatisticalCheck(
                check_name="Correlation vs Causation",
                passed=False,
                severity="high",
                explanation=f"Claim uses causal language ('{claim.quote}') but doesn't mention experimental evidence. "
                           "Causal claims require randomized controlled trials or careful causal inference, not just correlation.",
                suggestion="Either provide experimental evidence or rephrase using correlational language: 'associated with', 'correlated with', 'linked to'"
            )

        return StatisticalCheck(
            check_name="Correlation vs Causation",
            passed=True,
            severity="low",
            explanation="No inappropriate causal language detected."
        )

    def _check_sample_size(self, claim: Claim) -> StatisticalCheck:
        """
        Check if statistical claims mention sample size.
        """
        # Check if claim contains numbers/percentages (content-based, not type-based)
        quote_lower = claim.quote.lower()
        has_numbers = bool(re.search(r'\d+%|\d+\s*percent|\d+\.?\d*\s*times', quote_lower))

        if has_numbers or claim.numerical_values:
            # Check if sample size is mentioned in the claim or nearby context
            has_sample_size = any(
                re.search(pattern, claim.quote, re.IGNORECASE)
                for pattern in SAMPLE_SIZE_PATTERNS
            )

            if not has_sample_size:
                return StatisticalCheck(
                    check_name="Sample Size Disclosure",
                    passed=False,
                    severity="medium",
                    explanation=f"Statistical claim '{claim.quote}' provides numbers but doesn't mention sample size. "
                               "Small samples can produce misleading statistics.",
                    suggestion="Include sample size: 'n=X' or 'based on X participants'"
                )

        return StatisticalCheck(
            check_name="Sample Size Disclosure",
            passed=True,
            severity="low",
            explanation="Sample size mentioned or not required for this claim type."
        )

    def _check_extreme_language_in_claim(self, claim: Claim) -> StatisticalCheck:
        """
        Check for absolute terms without appropriate qualification.
        """
        quote_lower = claim.quote.lower()
        extreme_matches = [
            pattern for pattern in EXTREME_WORDS
            if re.search(pattern, quote_lower)
        ]

        if extreme_matches:
            # Find which extreme words were matched for better explanation
            matched_words = []
            for pattern in extreme_matches:
                match = re.search(pattern, quote_lower)
                if match:
                    matched_words.append(match.group())

            return StatisticalCheck(
                check_name="Extreme Language",
                passed=False,
                severity="high" if any(word in quote_lower for word in ['will', 'cure', 'guarantee', 'must']) else "medium",
                explanation=f"Claim uses absolute language: '{', '.join(matched_words[:3])}'. "
                           f"Words like 'always', 'never', 'will', 'cure', 'guarantee' are rarely justified in science.",
                suggestion="Use qualified language: 'often', 'may', 'suggests', 'can help', 'associated with'"
            )

        return StatisticalCheck(
            check_name="Extreme Language",
            passed=True,
            severity="low",
            explanation="No problematic absolute language detected."
        )

    def _check_base_rate(self, claim: Claim) -> StatisticalCheck:
        """
        Check if percentages or rates mention the base/denominator.
        """
        quote_lower = claim.quote.lower()

        # Check for percentages or relative terms (content-based, not type-based)
        has_percentage = bool(re.search(r'\d+%|\d+\s*percent', quote_lower))
        has_relative = bool(re.search(r'increase[sd]?|decrease[sd]?|more|less|higher|lower|times', quote_lower))
        has_multiplier = bool(re.search(r'\d+x\b', quote_lower))

        if has_percentage or has_relative or has_multiplier:
            # Check if absolute numbers or base rates are mentioned
            has_absolute = bool(re.search(r'\bof\s+\d+|\bout of\s+\d+|from\s+\d+\s+to\s+\d+|n\s*=\s*\d+', quote_lower))

            if not has_absolute:
                return StatisticalCheck(
                    check_name="Base Rate Neglect",
                    passed=False,
                    severity="medium",
                    explanation=f"Claim provides relative statistics without absolute context. "
                               f"'50% increase' or '200%' means different things if starting from 2 vs 2000.",
                    suggestion="Include absolute numbers: '50% increase (from 100 to 150)' or baseline context"
                )

        return StatisticalCheck(
            check_name="Base Rate Neglect",
            passed=True,
            severity="low",
            explanation="Base rates provided or not applicable."
        )

    def _check_data_support(self, claim: Claim) -> StatisticalCheck:
        """
        Check if claim has numerical support when making quantitative assertions.
        """
        quote_lower = claim.quote.lower()

        # Quantitative keywords that should have numbers
        quant_keywords = [
            'significant', 'substantial', 'large', 'small', 'majority',
            'minority', 'most', 'few', 'many', 'rare', 'common'
        ]

        has_quant_keyword = any(keyword in quote_lower for keyword in quant_keywords)

        if has_quant_keyword and not claim.numerical_values:
            return StatisticalCheck(
                check_name="Data Support",
                passed=False,
                severity="medium",
                explanation=f"Claim uses quantitative language ('{claim.quote}') but provides no actual numbers. "
                           f"Terms like 'significant' or 'most' should be backed by data.",
                suggestion="Replace vague terms with specific percentages or counts"
            )

        return StatisticalCheck(
            check_name="Data Support",
            passed=True,
            severity="low",
            explanation="Claims are appropriately supported with data or don't require it."
        )

    def _check_relative_risk_without_context(self, claim: Claim) -> StatisticalCheck:
        """
        Check for relative risk claims (doubles, triples, X times) without absolute context.
        This is a HIGH severity specialized version of base rate check for risk language.
        """
        quote_lower = claim.quote.lower()

        # Check for risk multiplier language
        has_risk_multiplier = any(
            re.search(pattern, quote_lower)
            for pattern in RISK_MULTIPLIER_PATTERNS
        )

        # Check for risk-related words
        has_risk_word = any(
            re.search(pattern, quote_lower)
            for pattern in RISK_WORDS
        )

        # If claim uses both risk language AND multipliers
        if has_risk_multiplier and has_risk_word:
            # Check if absolute context is provided
            has_absolute = bool(re.search(
                r'\bfrom\s+\d+\.?\d*%?\s+to\s+\d+\.?\d*%?|\bout of\s+\d+|'
                r'\bof\s+\d+|\bin\s+\d+|\b\d+\.?\d*%\s+to\s+\d+\.?\d*%|'
                r'\babsolute risk',
                quote_lower
            ))

            if not has_absolute:
                return StatisticalCheck(
                    check_name="Relative Risk Without Context",
                    passed=False,
                    severity="high",
                    explanation=f"Claim uses alarming relative risk language ('{claim.quote}') without providing absolute numbers. "
                               f"'Doubles your risk' sounds scary, but doubling from 0.001% to 0.002% is very different from 10% to 20%.",
                    suggestion="Include absolute risk: 'increased from 0.5% to 1%' or 'affecting 2 in 10,000 people instead of 1 in 10,000'"
                )

        return StatisticalCheck(
            check_name="Relative Risk Without Context",
            passed=True,
            severity="low",
            explanation="Relative risk properly contextualized or not applicable."
        )

    def _check_missing_comparator(self, claim: Claim) -> StatisticalCheck:
        """
        Check for improvement/effect claims without stating what they're compared to.
        Catches both missing control groups in studies and vague marketing claims.
        """
        quote_lower = claim.quote.lower()

        # Check for effect/improvement language
        has_effect_claim = any(
            re.search(pattern, quote_lower)
            for pattern in EFFECT_WORDS
        )

        if has_effect_claim:
            # Check if comparator is mentioned
            has_comparator = any(
                re.search(pattern, quote_lower)
                for pattern in COMPARATOR_WORDS
            )

            # Check for implicit comparators: "increased by X%", "from X to Y" implies comparison to previous state
            has_implicit_comparator = bool(re.search(
                r'\b(increase[ds]?|decrease[ds]?|reduced?|improved?|rose|fell|dropped|grew|enhanced?)\s+(by|from|to)\s+\d+|'
                r'\bfrom\s+\d+.*?\bto\s+\d+',  # "from X to Y" pattern
                quote_lower
            ))

            if not has_comparator and not has_implicit_comparator:
                # Determine severity based on context
                is_research_claim = bool(re.search(
                    r'\bstudy\b|\bresearch\b|\btrial\b|\btest\b|\bparticipants?\b|\bsubjects?\b',
                    quote_lower
                ))

                severity = "high" if is_research_claim else "medium"

                return StatisticalCheck(
                    check_name="Missing Comparator",
                    passed=False,
                    severity=severity,
                    explanation=f"Claim states that something '{claim.quote}' but doesn't specify compared to what. "
                               f"Improved vs. placebo? Control group? Previous version? Doing nothing? Without a comparison point, the claim is meaningless.",
                    suggestion="Specify the comparison: 'improved compared to placebo', 'better than standard treatment', 'reduced vs. baseline'"
                )

        return StatisticalCheck(
            check_name="Missing Comparator",
            passed=True,
            severity="low",
            explanation="Comparisons are properly specified or not required."
        )


def analyze_text(text: str) -> TextMetrics:
    """
    Convenience function to analyze text and get metrics.

    Args:
        text: Text to analyze

    Returns:
        TextMetrics with calculated scores
    """
    analyzer = StatisticalAnalyzer(text)
    return analyzer.calculate_text_metrics()


def check_claims(text: str, claims: List[Claim]) -> Dict[str, List[StatisticalCheck]]:
    """
    Convenience function to run checks on all claims.

    Args:
        text: Original text
        claims: List of extracted claims

    Returns:
        Dictionary mapping claim_id to list of check results
    """
    analyzer = StatisticalAnalyzer(text)
    return {
        claim.claim_id: analyzer.check_claim(claim)
        for claim in claims
    }
