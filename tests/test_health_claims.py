"""
Test health/supplement marketing claims with new medical verbs
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.schemas import Claim
from nuance.statistical_checks import StatisticalAnalyzer


def test_health_marketing_claims():
    """Test that we catch vague health supplement marketing."""
    print("\n🧪 Testing Health Marketing Claims")
    print("=" * 70)

    analyzer = StatisticalAnalyzer("Test text")

    test_cases = [
        {
            "quote": "This supplement regulates blood sugar",
            "should_fail": True,
            "check": "Missing Comparator",
            "desc": "regulates without comparator"
        },
        {
            "quote": "Our formula fights aging and boosts energy",
            "should_fail": True,
            "check": "Missing Comparator",
            "desc": "fights/boosts without comparator"
        },
        {
            "quote": "Blocks inflammation naturally",
            "should_fail": True,
            "check": "Missing Comparator",
            "desc": "blocks without comparator"
        },
        {
            "quote": "Stops hair loss in 30 days",
            "should_fail": True,
            "check": "Missing Comparator",
            "desc": "stops without comparator"
        },
        {
            "quote": "Regulates blood sugar better than placebo",
            "should_fail": False,
            "check": "Missing Comparator",
            "desc": "has comparator (should pass)"
        },
    ]

    for i, test in enumerate(test_cases, 1):
        claim = Claim(
            claim_id=f"c{i}",
            quote=test["quote"],
            claim_type="causal",
            confidence=0.9,
            variables=[],
            numerical_values=[]
        )

        checks = analyzer.check_claim(claim)
        comparator_check = [c for c in checks if c.check_name == test["check"]][0]

        expected = "FAIL" if test["should_fail"] else "PASS"
        actual = "FAIL" if not comparator_check.passed else "PASS"
        status = "✅" if (expected == actual) else "❌"

        print(f"\n{status} Test {i}: {test['desc']}")
        print(f"   Quote: \"{test['quote']}\"")
        print(f"   Expected: {expected}, Got: {actual}")

        if test["should_fail"] and not comparator_check.passed:
            print(f"   Severity: {comparator_check.severity}")

        assert (expected == actual), f"Test {i} failed: expected {expected}, got {actual}"

    print("\n" + "=" * 70)
    print("✅ All health marketing claim tests passed!")
    print("\nNow catches:")
    print("  • 'regulates blood sugar' ❌")
    print("  • 'fights aging' ❌")
    print("  • 'blocks inflammation' ❌")
    print("  • 'stops hair loss' ❌")
    print("  • 'regulates blood sugar vs. placebo' ✅")


if __name__ == "__main__":
    print("\n🔬 TESTING HEALTH SUPPLEMENT MARKETING DETECTION\n")

    try:
        test_health_marketing_claims()
        print("\n" + "=" * 70)
        print("🎉 Perfect for catching BS supplement claims!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
