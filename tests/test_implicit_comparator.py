"""
Test that implicit comparators are recognized (e.g., "increased by 300%")
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.schemas import Claim
from nuance.statistical_checks import StatisticalAnalyzer


def test_implicit_comparators():
    """Test that implicit comparators are properly recognized."""
    print("\n🧪 Testing Implicit Comparator Recognition")
    print("=" * 70)

    analyzer = StatisticalAnalyzer("Test text")

    test_cases = [
        {
            "quote": "Sales increased by 300%",
            "should_fail": False,
            "reason": "increased by X% - implicit comparator to previous period"
        },
        {
            "quote": "Attacks decreased by 50%",
            "should_fail": False,
            "reason": "decreased by X% - implicit comparator"
        },
        {
            "quote": "Performance improved from 20% to 40%",
            "should_fail": False,
            "reason": "from X to Y - explicit numeric comparison"
        },
        {
            "quote": "Revenue rose by $2 million",
            "should_fail": False,
            "reason": "rose by X - implicit comparator"
        },
        {
            "quote": "Symptoms improved significantly",
            "should_fail": True,
            "reason": "improved without comparator - genuinely vague"
        },
        {
            "quote": "The product works better",
            "should_fail": True,
            "reason": "better without comparator - better than what?"
        },
        {
            "quote": "The trend will continue to increase",
            "should_fail": True,
            "reason": "increase without by/from/to - vague directional claim"
        },
    ]

    for i, test in enumerate(test_cases, 1):
        claim = Claim(
            claim_id=f"c{i}",
            quote=test["quote"],
            claim_type="comparative",
            confidence=0.9,
            variables=[],
            numerical_values=[]
        )

        checks = analyzer.check_claim(claim)
        comparator_check = [c for c in checks if c.check_name == "Missing Comparator"][0]

        expected = "FAIL" if test["should_fail"] else "PASS"
        actual = "FAIL" if not comparator_check.passed else "PASS"
        status = "✅" if (expected == actual) else "❌"

        print(f"\n{status} Test {i}: {test['reason']}")
        print(f"   Quote: \"{test['quote']}\"")
        print(f"   Expected: {expected}, Got: {actual}")

        assert (expected == actual), f"Test {i} failed: {test['reason']}"

    print("\n" + "=" * 70)
    print("✅ All implicit comparator tests passed!")
    print("\n📝 Summary:")
    print("   • 'increased/decreased by X%' → PASS (implicit comparator)")
    print("   • 'from X to Y' → PASS (explicit numbers)")
    print("   • 'improved significantly' → FAIL (genuinely vague)")
    print("   • 'works better' → FAIL (better than what?)")


if __name__ == "__main__":
    print("\n🔬 TESTING IMPLICIT COMPARATOR LOGIC\n")

    try:
        test_implicit_comparators()
        print("\n" + "=" * 70)
        print("🎉 Implicit comparators correctly recognized!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
