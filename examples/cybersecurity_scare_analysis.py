"""
Test the Cybersecurity Scare article to see what Nuance catches
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.schemas import Claim
from nuance.statistical_checks import StatisticalAnalyzer


def test_cybersecurity_article():
    """Test the cybersecurity fear-mongering article."""

    # The article text
    cyber_text = """
    Headline: Cybersecurity Wave: Attacks Have Tripled in 2025

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

    print("\n" + "=" * 80)
    print("🔒 TESTING: Cybersecurity Scare Article")
    print("=" * 80)

    # Create analyzer
    analyzer = StatisticalAnalyzer(cyber_text)

    # Calculate text metrics
    print("\n📊 TEXT-LEVEL METRICS:")
    print("-" * 80)
    metrics = analyzer.calculate_text_metrics()
    print(f"Data Density Score:       {metrics.data_density_score:.1%}")
    print(f"Vagueness Score:          {metrics.vagueness_score:.1%}")
    print(f"Extreme Language Count:   {metrics.extreme_language_count}")
    print(f"Sample Size Mentioned:    {metrics.sample_size_mentioned}")
    print(f"Causation Language Count: {metrics.causation_language_count}")

    # Test some example claims that would be extracted
    print("\n\n🔍 TESTING SAMPLE CLAIMS:")
    print("=" * 80)

    test_claims = [
        {
            "id": "c1",
            "quote": "Ransomware attacks on small businesses have increased by 300% in the last month alone",
            "type": "statistical"
        },
        {
            "id": "c2",
            "quote": "This tripling of risk means that your business is almost certain to be hit next",
            "type": "statistical"
        },
        {
            "id": "c3",
            "quote": "companies without enterprise-grade protection are more vulnerable to these attacks",
            "type": "comparative"
        },
        {
            "id": "c4",
            "quote": "Most cybersecurity experts agree that the threat will continue to increase",
            "type": "statistical"
        },
        {
            "id": "c5",
            "quote": "Three out of four businesses that ignored this warning were compromised within weeks",
            "type": "statistical"
        }
    ]

    total_issues_found = 0

    for claim_data in test_claims:
        print(f"\n{'─' * 80}")
        print(f"CLAIM {claim_data['id'].upper()}: \"{claim_data['quote']}\"")
        print(f"Type: {claim_data['type']}")
        print(f"{'─' * 80}")

        # Create claim object
        claim = Claim(
            claim_id=claim_data['id'],
            quote=claim_data['quote'],
            claim_type=claim_data['type'],
            confidence=0.9,
            variables=[],
            numerical_values=[]
        )

        # Run all checks
        checks = analyzer.check_claim(claim)
        failed_checks = [c for c in checks if not c.passed]

        if failed_checks:
            print(f"\n❌ ISSUES FOUND: {len(failed_checks)}")
            total_issues_found += len(failed_checks)

            for check in failed_checks:
                severity_emoji = {
                    'high': '🔴',
                    'medium': '⚠️',
                    'low': '🟡'
                }
                print(f"\n  {severity_emoji.get(check.severity, '❓')} {check.check_name} [{check.severity.upper()}]")
                print(f"     Problem: {check.explanation[:200]}...")
                if check.suggestion:
                    print(f"     Fix: {check.suggestion[:150]}...")
        else:
            print("\n✅ No issues found (clean claim)")

    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print(f"Total sample claims tested: {len(test_claims)}")
    print(f"Total issues found: {total_issues_found}")
    print(f"Average issues per claim: {total_issues_found / len(test_claims):.1f}")

    print("\n🎯 EXPECTED CHECKS TO TRIGGER:")
    print("-" * 80)
    print("✅ Relative Risk Without Context (300%, tripling of risk)")
    print("✅ Extreme Language (terrifying, almost certain, completely exposed)")
    print("✅ Missing Sample Size (latest security report - no n=)")
    print("✅ Base Rate Neglect (percentages without absolute context)")
    print("✅ Data Support (Most experts agree)")
    print("✅ Missing Comparator (more vulnerable - vs what?)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_cybersecurity_article()
        print("\n✅ Test complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
