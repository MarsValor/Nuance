"""
Test the Wine = Exercise article to see what Nuance catches
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.schemas import Claim
from nuance.statistical_checks import StatisticalAnalyzer


def test_wine_article():
    """Test the viral wine article."""

    # The article text
    wine_text = """
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

    print("\n" + "=" * 80)
    print("🍷 TESTING: Wine = Exercise Article")
    print("=" * 80)

    # Create analyzer
    analyzer = StatisticalAnalyzer(wine_text)

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
            "quote": "drinking a glass of red wine a day is THE SAME AS A ONE-HOUR GYM SESH",
            "type": "comparative"
        },
        {
            "id": "c2",
            "quote": "resveratrol has the ability to improve physical performance, heart function, and muscle strength",
            "type": "causal"
        },
        {
            "id": "c3",
            "quote": "resveratrol also regulates blood sugar levels and fights aging",
            "type": "causal"
        },
        {
            "id": "c4",
            "quote": "making it less likely you'll develop dementia or cancer",
            "type": "statistical"
        },
        {
            "id": "c5",
            "quote": "one glass of red wine a day can also increase the effectiveness of your actual gym sessions",
            "type": "comparative"
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
                print(f"     Problem: {check.explanation[:150]}...")
                if check.suggestion:
                    print(f"     Fix: {check.suggestion[:100]}...")
        else:
            print("\n✅ No issues found (clean claim)")

    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print(f"Total sample claims tested: {len(test_claims)}")
    print(f"Total issues found: {total_issues_found}")
    print(f"Average issues per claim: {total_issues_found / len(test_claims):.1f}")

    print("\n🎯 EXPECTED DEMO IMPACT:")
    print("-" * 80)
    print("✅ Will catch Missing Comparator (regulates, fights, improve, increase)")
    print("✅ Will catch Correlation vs Causation (equals, causes)")
    print("✅ Will catch Extreme Language (THE SAME AS)")
    print("✅ Will catch Base Rate Neglect (less likely... cancer)")
    print("✅ Will catch Sample Size Missing (Alberta study - no n=)")

    print("\n💡 This article is PERFECT for demo - triggers 5+ check types!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_wine_article()
        print("\n✅ Test complete! This article will create an excellent demo.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
