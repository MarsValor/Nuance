"""
Nuance - AI-Powered Statistical Reasoning Auditor
Streamlit UI with pipeline visualization
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nuance.claude_client import ClaudeClient
from nuance.statistical_checks import StatisticalAnalyzer, analyze_text, check_claims
from nuance.schemas import ClaimAudit, TextMetrics


# Page configuration
st.set_page_config(
    page_title="Nuance - Statistical Reasoning Auditor",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .severity-critical {
        color: #d32f2f;
        font-weight: bold;
    }
    .severity-high {
        color: #f57c00;
        font-weight: bold;
    }
    .severity-medium {
        color: #fbc02d;
        font-weight: bold;
    }
    .severity-low {
        color: #388e3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application logic"""

    # Header
    st.markdown('<div class="main-header">🔍 Nuance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Statistical Reasoning Auditor</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **Nuance** audits text for statistical bullshit and sloppy logic. Paste a news article, blog post,
    or report below, and we'll analyze it for logical fallacies, missing context, and hand-wavy claims.
    """)

    # Sidebar
    with st.sidebar:
        st.header("About Nuance")
        st.markdown("""
        ### How it works

        **1. Extraction (Neuro)**
        - Claude extracts statistical claims
        - Strict schema validation with retry

        **2. Analysis (Symbolic)**
        - Python runs deterministic checks
        - No guessing - real statistical analysis

        **3. Synthesis**
        - Educational feedback on findings
        - Train your bullshit detector

        ---

        ### Example Articles
        """)

        if st.button("Load Example: Cybersecurity Scare (Technical)"):
            st.session_state['example_text'] = """
            Headline: Cybercrime Wave: Attacks Have Tripled in 2025

            Our latest security report shows a terrifying trend: Ransomware attacks on
            small businesses have increased by 300% in the last month alone. This tripling
            of risk means that your business is almost certain to be hit next.

            The data clearly proves that companies without enterprise-grade protection are
            more vulnerable to these attacks. Most cybersecurity experts agree that the
            threat will continue to increase.

            Unless you buy our 'Total-Shield' protection package today, you are leaving
            your data completely exposed to this surging threat. Three out of four
            businesses that ignored this warning were compromised within weeks.
            """

        if st.button("Load Example: Wine = Exercise (Viral Health Claim)"):
            st.session_state['example_text'] = """
            Drop and give me twenty… ounces of merlot, that is!

            Red wine equals gym time! Thanks to Jason Dyck and some research
            completed at the University of Alberta, we now know that drinking
            a glass of red wine a day is THE SAME AS A ONE-HOUR GYM SESH.
            You heard me, folks. So go ahead and kick off those trainers and
            pour yourself a glass of exercise 'cause it's about to get sweaty
            lazy up in here.

            That would be Resveratrol, the compound found in red wine responsible
            for its health benefits. According to the Alberta study, the resveratrol
            found in the skin of grapes, and thus red wine, has the ability to
            improve physical performance, heart function, and muscle strength.
            The physiological results of drinking one glass a day mimic having
            spent one hour working out.

            In addition to allowing you to skip the Stairmaster, resveratrol also
            regulates blood sugar levels and fights aging, all while making it
            less likely you'll develop dementia or cancer.

            This is good news for those who are physically unable to exercise
            but still need the physical benefits. This is great news for those
            of you who are just plain exhausted after work and are too lazy to
            even walk upstairs to change your clothes. But, to rain on my own
            parade here, this only works for ONE glass of red wine. Three glasses
            does not equal three hours of exercise. Nice try though.

            So you still want to work out? First of all, GOOD FOR YOU! Second,
            one glass of red wine a day can also increase the effectiveness of
            your actual gym sessions for all the same reasons listed above.
            """

    # Text input
    default_text = st.session_state.get('example_text', '')
    text_input = st.text_area(
        "Paste text to analyze:",
        height=200,
        placeholder="Paste a news article, blog post, or any text you want to audit...",
        value=default_text
    )

    # Think-Before-Reveal Mode
    st.markdown("---")
    thinking_mode = st.checkbox(
        "🧠 **Think-Before-Reveal Mode:** Test your critical thinking first!",
        help="Predict which claims have issues before seeing the AI's analysis. Get scored on your predictions!"
    )

    # Initialize session state for thinking mode
    if 'user_predictions' not in st.session_state:
        st.session_state['user_predictions'] = {}
    if 'show_predictions' not in st.session_state:
        st.session_state['show_predictions'] = False

    # If thinking mode enabled and text provided, extract claims for prediction
    if thinking_mode and text_input.strip() and not st.session_state.get('show_predictions', False):
        if st.button("📝 Start Prediction Phase", type="secondary"):
            with st.spinner("Extracting claims for you to evaluate..."):
                try:
                    client = ClaudeClient()
                    claims_extraction = client.extract_claims(text_input)
                    st.session_state['extracted_claims'] = claims_extraction.claims
                    st.session_state['show_predictions'] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error extracting claims: {e}")

    # Show prediction interface if in thinking mode and claims extracted
    if thinking_mode and st.session_state.get('show_predictions', False):
        st.markdown("### 🎯 Make Your Predictions")
        st.info("For each claim below, select which issues you think it has. Then click 'Run Analysis' to see how you did!\n\n**Note:** Some claims may have no issues. If you think a claim is fine, leave all checkboxes unchecked.")

        extracted_claims = st.session_state.get('extracted_claims', [])

        if not extracted_claims:
            st.warning("⚠️ No claims were extracted. Try different text or disable Think-Before-Reveal mode.")
        elif extracted_claims:
            max_to_show = st.slider(
                "How many claims to review now?",
                min_value=1,
                max_value=len(extracted_claims),
                value=min(5, len(extracted_claims)),
                help="Adjust to avoid a wall of questions; you can review more by moving the slider."
            )

            claims_to_review = extracted_claims[:max_to_show]
            if len(extracted_claims) > max_to_show:
                st.caption(f"Showing first {max_to_show} of {len(extracted_claims)} claims. Move the slider to see more.")

            # Clean up predictions for claims beyond current slider value
            claims_to_review_ids = {claim.claim_id for claim in claims_to_review}
            predictions_to_remove = [
                claim_id for claim_id in st.session_state['user_predictions'].keys()
                if claim_id not in claims_to_review_ids
            ]
            for claim_id in predictions_to_remove:
                del st.session_state['user_predictions'][claim_id]

            for claim in claims_to_review:
                with st.expander(f"{claim.claim_id.upper()}: {claim.quote[:120]}..."):
                    st.markdown(f"**Full Claim:** {claim.quote}")

                    # Prediction options
                    col1, col2 = st.columns(2)

                    with col1:
                        corr = st.checkbox(
                            "Correlation/Causation issue",
                            key=f"pred_{claim.claim_id}_corr"
                        )
                        sample = st.checkbox(
                            "Missing sample size",
                            key=f"pred_{claim.claim_id}_sample"
                        )
                        extreme = st.checkbox(
                            "Extreme language",
                            key=f"pred_{claim.claim_id}_extreme"
                        )
                        relative_risk = st.checkbox(
                            "Relative risk without context",
                            key=f"pred_{claim.claim_id}_relative_risk"
                        )

                    with col2:
                        base_rate = st.checkbox(
                            "Base rate neglect",
                            key=f"pred_{claim.claim_id}_base"
                        )
                        data_support = st.checkbox(
                            "Inadequate data support",
                            key=f"pred_{claim.claim_id}_data"
                        )
                        missing_comparator = st.checkbox(
                            "Missing comparator",
                            key=f"pred_{claim.claim_id}_comparator"
                        )

                    # Store predictions
                    st.session_state['user_predictions'][claim.claim_id] = {
                        'correlation': corr,
                        'sample_size': sample,
                        'extreme_language': extreme,
                        'base_rate': base_rate,
                        'data_support': data_support,
                        'relative_risk': relative_risk,
                        'missing_comparator': missing_comparator
                    }

        st.markdown("### ✅ Ready to See How You Did?")

        # Add restart button in prediction mode
        if st.button("🔄 Start Over (New Text)", key="restart_predictions", type="secondary"):
            st.session_state['show_predictions'] = False
            st.session_state['user_predictions'] = {}
            st.session_state['extracted_claims'] = []
            st.rerun()

    # Analyze button (modified label for thinking mode)
    button_label = "🔍 Run Analysis & Compare" if (thinking_mode and st.session_state.get('show_predictions')) else "🔍 Audit This Text"
    if st.button(button_label, type="primary"):
        if not text_input.strip():
            st.error("Please paste some text to analyze.")
            return

        # Validate text length
        word_count = len(text_input.split())
        if word_count > 2000:
            st.warning(f"⚠️ **Large Text Detected:** {word_count:,} words. Processing may take 30-60 seconds.")
        elif word_count < 20:
            st.warning("⚠️ **Short Text:** Text may not contain enough claims for meaningful analysis.")

        # Pipeline visualization
        st.markdown("---")
        st.subheader("📊 Analysis Pipeline")

        # Create placeholders for pipeline steps
        step1_placeholder = st.empty()
        step2_placeholder = st.empty()
        step3_placeholder = st.empty()

        try:
            # STEP 1: Extract claims
            step1_placeholder.info("⏳ **Step 1:** Extracting statistical claims...")

            client = ClaudeClient()
            claims_extraction = client.extract_claims(text_input)

            step1_placeholder.success(
                f"✅ **Step 1 Complete:** Extracted {claims_extraction.total_claims} claims"
            )

            # STEP 2: Run statistical checks
            step2_placeholder.info("⏳ **Step 2:** Running deterministic statistical checks...")

            analyzer = StatisticalAnalyzer(text_input)
            text_metrics = analyzer.calculate_text_metrics()

            # Run checks on each claim
            claim_check_results = {}
            for claim in claims_extraction.claims:
                claim_check_results[claim.claim_id] = analyzer.check_claim(claim)

            # Create ClaimAudit objects
            claim_audits = []
            for claim in claims_extraction.claims:
                checks = claim_check_results[claim.claim_id]
                failed_checks = [c for c in checks if not c.passed]

                # Determine overall status
                if any(c.severity == "critical" for c in failed_checks):
                    status = "critical"
                elif any(c.severity == "high" for c in failed_checks):
                    status = "major_issues"
                elif failed_checks:
                    status = "minor_issues"
                else:
                    status = "clean"

                claim_audits.append(ClaimAudit(
                    claim_id=claim.claim_id,
                    claim_quote=claim.quote,
                    checks_performed=checks,
                    overall_status=status
                ))

            total_issues = sum(len([c for c in audit.checks_performed if not c.passed])
                             for audit in claim_audits)

            step2_placeholder.success(
                f"✅ **Step 2 Complete:** Found {total_issues} potential issues"
            )

            # STEP 3: Generate summary
            step3_placeholder.info("⏳ **Step 3:** Generating audit report...")

            summary = client.generate_audit_summary(
                original_text=text_input,
                claim_audits=claim_audits,
                text_metrics=text_metrics.model_dump()
            )

            # Calculate overall reliability score (0-100)
            reliability_score = calculate_reliability_score(text_metrics, claim_audits)

            step3_placeholder.success("✅ **Step 3 Complete:** Audit report ready")

            # Display results
            st.markdown("---")
            st.subheader("📋 Audit Results")

            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Reliability Score",
                    f"{reliability_score:.0f}/100"
                )

            with col2:
                st.metric(
                    "Data Density",
                    f"{text_metrics.data_density_score:.0%}",
                    help="% of sentences with numbers/statistics"
                )

            with col3:
                st.metric(
                    "Issues Found",
                    total_issues
                )

            with col4:
                st.metric(
                    "Claims Analyzed",
                    claims_extraction.total_claims
                )

            # Text metrics details
            with st.expander("📊 Detailed Text Metrics", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Quantitative Analysis:**")
                    st.write(f"- **Data Density:** {text_metrics.data_density_score:.1%}")
                    st.write(f"- **Vagueness Score:** {text_metrics.vagueness_score:.1%}")
                    st.write(f"- **Sample Size Mentioned:** {'Yes' if text_metrics.sample_size_mentioned else 'No'}")

                with col2:
                    st.markdown("**Language Analysis:**")
                    st.write(f"- **Extreme Language:** {text_metrics.extreme_language_count} instances")
                    st.write(f"- **Causation Claims:** {text_metrics.causation_language_count} instances")

            # Summary
            st.markdown("### 🎯 Summary")
            st.markdown(summary)

            # Group issues by error type
            st.markdown("### 📊 Issues Grouped by Type")

            # Collect all errors and group by check name
            errors_by_type = {}
            clean_claims = []

            for audit in claim_audits:
                failed_checks = [c for c in audit.checks_performed if not c.passed]

                if not failed_checks:
                    clean_claims.append({
                        'id': audit.claim_id,
                        'quote': audit.claim_quote
                    })
                else:
                    for check in failed_checks:
                        if check.check_name not in errors_by_type:
                            errors_by_type[check.check_name] = {
                                'check': check,
                                'claims': []
                            }
                        # Avoid duplicates
                        claim_exists = any(
                            c['id'] == audit.claim_id for c in errors_by_type[check.check_name]['claims']
                        )
                        if not claim_exists:
                            errors_by_type[check.check_name]['claims'].append({
                                'id': audit.claim_id,
                                'quote': audit.claim_quote
                            })

            # Show errors grouped by type
            if errors_by_type:
                # Sort by severity (high -> medium -> low)
                severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

                for error_type, error_data in sorted(
                    errors_by_type.items(),
                    key=lambda x: (severity_order.get(x[1]['check'].severity, 4), -len(x[1]['claims']))
                ):
                    check = error_data['check']
                    affected_claims = error_data['claims']
                    count = len(affected_claims)

                    # Severity styling
                    severity_emoji = {
                        'critical': '🚨',
                        'high': '🔴',
                        'medium': '⚠️',
                        'low': '🟡'
                    }

                    with st.expander(
                        f"{severity_emoji.get(check.severity, '❓')} **{check.check_name}** — {count} claim{'s' if count != 1 else ''}",
                        expanded=(check.severity in ['critical', 'high'])
                    ):
                        severity_class = f"severity-{check.severity}"
                        st.markdown(
                            f"<span class='{severity_class}'>**Severity:** {check.severity.upper()}</span>",
                            unsafe_allow_html=True
                        )

                        st.markdown(f"**Problem:** {check.explanation}")

                        if check.suggestion:
                            st.info(f"💡 **How to fix it:** {check.suggestion}")

                        st.markdown(f"**Claims with this issue ({count}):**")
                        for claim_info in affected_claims:
                            st.markdown(
                                f"• **{claim_info['id'].upper()}:** {claim_info['quote']}"
                            )

                        # Counterfactuals for high/medium severity
                        if check.severity in ["high", "medium"]:
                            st.markdown("---")
                            st.markdown("**🧠 Think Deeper: Alternative Explanations**")

                            with st.spinner("Generating alternative perspectives..."):
                                try:
                                    # Use first claim as example
                                    example_claim = affected_claims[0]['quote']

                                    counterfactuals = client.generate_counterfactuals(
                                        claim_quote=example_claim,
                                        fallacy_type=check.check_name,
                                        check_explanation=check.explanation
                                    )

                                    st.markdown("*What else could explain this?*")
                                    for i, alternative in enumerate(counterfactuals, 1):
                                        if alternative:
                                            st.markdown(f"{i}. {alternative}")

                                    st.info("💡 Tip: Always consider alternative explanations before accepting claims at face value.")

                                except Exception as e:
                                    st.warning(f"Could not generate alternatives: {type(e).__name__}. This feature requires API access.")

            # Show clean claims
            if clean_claims:
                with st.expander(f"✅ **Clean Claims** — {len(clean_claims)} claim{'s' if len(clean_claims) != 1 else ''}"):
                    st.success("These claims have no detected issues!")
                    for claim_info in clean_claims:
                        st.markdown(f"• **{claim_info['id'].upper()}:** {claim_info['quote']}")

            # Think-Before-Reveal Mode: Show comparison if predictions were made
            if thinking_mode and st.session_state.get('user_predictions'):
                st.markdown("---")
                st.markdown("## 🎯 You vs AI Analysis")
                st.info("See how your predictions compared to the AI's analysis!")

                # Calculate accuracy
                user_predictions = st.session_state['user_predictions']
                accuracy_metrics = calculate_prediction_accuracy(user_predictions, claim_audits)

                # Overall score
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Your Accuracy",
                        f"{accuracy_metrics['overall_accuracy']:.0%}",
                        help="Percentage of issues you correctly identified"
                    )
                with col2:
                    st.metric(
                        "Issues Caught",
                        f"{accuracy_metrics['true_positives']}/{accuracy_metrics['total_issues']}",
                        help="Number of real issues you correctly flagged"
                    )

                # Detailed breakdown
                st.markdown("### 📊 Detailed Breakdown")

                for claim_id, metrics in accuracy_metrics['per_claim'].items():
                    with st.expander(f"**{claim_id.upper()}:** {metrics['quote'][:100]}..."):
                        col_pred, col_actual = st.columns(2)

                        with col_pred:
                            st.markdown("**Your Predictions:**")
                            predicted_issues = metrics['predicted']
                            if predicted_issues:
                                for issue in predicted_issues:
                                    status = "✅" if issue in metrics['caught'] else "❌"
                                    st.markdown(f"{status} {issue.replace('_', ' ').title()}")
                            else:
                                st.markdown("_No issues predicted_")

                        with col_actual:
                            st.markdown("**AI Found:**")
                            actual_issues = metrics['actual']
                            if actual_issues:
                                for issue in actual_issues:
                                    st.markdown(f"• {issue.replace('_', ' ').title()}")
                            else:
                                st.markdown("_No issues found_")

                        # Summary
                        if metrics['caught']:
                            st.success(f"✅ You caught: {', '.join(metrics['caught'])}")
                        if metrics['missed']:
                            st.warning(f"❌ You missed: {', '.join(metrics['missed'])}")
                        if metrics['false_positives']:
                            st.info(f"💭 Wrong guess: {', '.join(metrics['false_positives'])}")

                # Learning feedback
                st.markdown("### 💡 Learning Insights")
                feedback_messages = []

                # Check accuracy by issue type
                for issue_type, type_metrics in accuracy_metrics['by_type'].items():
                    if type_metrics['total'] > 0:
                        accuracy = type_metrics['caught'] / type_metrics['total']
                        if accuracy >= 0.8:
                            feedback_messages.append(
                                f"✅ **{issue_type.replace('_', ' ').title()}**: Excellent! You're catching these consistently."
                            )
                        elif accuracy < 0.5 and type_metrics['total'] >= 2:
                            feedback_messages.append(
                                f"📚 **{issue_type.replace('_', ' ').title()}**: Room for improvement. Pay closer attention to this pattern."
                            )

                if feedback_messages:
                    for msg in feedback_messages:
                        st.markdown(msg)
                else:
                    st.markdown("Keep practicing to build your critical thinking skills!")

                # Reset button
                if st.button("🔄 Try Another Text"):
                    st.session_state['show_predictions'] = False
                    st.session_state['user_predictions'] = {}
                    st.rerun()

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            # Provide specific guidance for common errors
            if "API" in error_msg or "api" in error_msg.lower():
                st.error("❌ **API Error:** Check that your ANTHROPIC_API_KEY is valid in the .env file.")
                st.info("Get your API key from: https://console.anthropic.com/")
            elif "rate" in error_msg.lower() or "429" in error_msg:
                st.error("❌ **Rate Limit:** API rate limit exceeded. Please wait a moment and try again.")
            elif "No claims" in error_msg or "RetryExhausted" in error_type:
                st.error("❌ **No Claims Found:** The text doesn't contain statistical or causal claims to analyze.")
                st.info("Try adding text with numbers, percentages, or causal statements (e.g., 'causes', 'increases').")
            else:
                st.error(f"❌ **Error ({error_type}):** {error_msg}")
                st.info("If this persists, check your API key and network connection.")


def calculate_prediction_accuracy(user_predictions: dict, claim_audits: list) -> dict:
    """
    Compare user predictions to actual analysis results.

    Args:
        user_predictions: Dict of {claim_id: {issue_type: bool}}
        claim_audits: List of ClaimAudit results

    Returns:
        Dict with accuracy metrics
    """
    # Mapping between prediction keys and check names
    PRED_TO_CHECK = {
        'correlation': 'Correlation vs Causation',
        'sample_size': 'Sample Size Disclosure',
        'extreme_language': 'Extreme Language',
        'base_rate': 'Base Rate Neglect',
        'data_support': 'Data Support',
        'relative_risk': 'Relative Risk Without Context',
        'missing_comparator': 'Missing Comparator'
    }

    total_issues = 0
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    per_claim_metrics = {}
    by_type_metrics = {issue: {'caught': 0, 'total': 0} for issue in PRED_TO_CHECK.keys()}

    for audit in claim_audits:
        claim_id = audit.claim_id

        # Skip claims user didn't review (not in predictions)
        if claim_id not in user_predictions:
            continue

        # Get user's predictions for this claim
        user_pred = user_predictions.get(claim_id, {})
        predicted_issues = {
            issue for issue, flagged in user_pred.items() if flagged
        }

        # Get actual issues from checks
        actual_checks = {
            check.check_name for check in audit.checks_performed if not check.passed
        }

        # Map check names to prediction keys
        actual_issues = set()
        for check_name in actual_checks:
            for pred_key, check_full_name in PRED_TO_CHECK.items():
                if check_full_name in check_name:
                    actual_issues.add(pred_key)
                    break

        # Calculate matches
        caught = predicted_issues & actual_issues
        missed = actual_issues - predicted_issues
        false_pos = predicted_issues - actual_issues

        # Update totals
        total_issues += len(actual_issues)
        true_positives += len(caught)
        false_positives += len(false_pos)
        false_negatives += len(missed)

        # Track by type
        for issue in actual_issues:
            by_type_metrics[issue]['total'] += 1
            if issue in caught:
                by_type_metrics[issue]['caught'] += 1

        # Store per-claim metrics
        per_claim_metrics[claim_id] = {
            'quote': audit.claim_quote,
            'predicted': list(predicted_issues),
            'actual': list(actual_issues),
            'caught': list(caught),
            'missed': list(missed),
            'false_positives': list(false_pos)
        }

    # Calculate overall accuracy (as decimal 0-1, will be formatted as % in UI)
    overall_accuracy = (true_positives / total_issues) if total_issues > 0 else 0

    return {
        'overall_accuracy': overall_accuracy,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'total_issues': total_issues,
        'per_claim': per_claim_metrics,
        'by_type': by_type_metrics
    }


def calculate_reliability_score(text_metrics: TextMetrics, claim_audits: list) -> float:
    """
    Calculate overall reliability score (0-100).

    Args:
        text_metrics: Quantitative text metrics
        claim_audits: List of claim audit results

    Returns:
        Score from 0-100
    """
    score = 50.0  # Start at neutral

    # Boost for data density
    score += text_metrics.data_density_score * 20

    # Penalize for vagueness
    score -= text_metrics.vagueness_score * 15

    # Boost if sample size mentioned
    if text_metrics.sample_size_mentioned:
        score += 10

    # Penalize for extreme language
    score -= min(text_metrics.extreme_language_count * 2, 15)

    # Penalize for failed checks
    total_checks = sum(len(audit.checks_performed) for audit in claim_audits)
    failed_checks = sum(
        len([c for c in audit.checks_performed if not c.passed])
        for audit in claim_audits
    )

    if total_checks > 0:
        failure_rate = failed_checks / total_checks
        score -= failure_rate * 30

    # Clamp to 0-100
    return max(0.0, min(100.0, score))


if __name__ == "__main__":
    main()
