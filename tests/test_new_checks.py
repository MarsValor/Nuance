"""
Test the new statistical checks: Relative Risk and Missing Comparator
"""

import sys
from pathlib import Path

# Add src to path (go up from tests/ to project root, then into src/)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.schemas import Claim
from nuance.statistical_checks import StatisticalAnalyzer


def test_relative_risk_check():
    """Test the Relative Risk Without Context check."""
    print("\n🧪 Testing Relative Risk Without Context Check")
    print("=" * 70)

    analyzer = StatisticalAnalyzer("Test text")

    # Test case 1: Should FAIL - relative risk without context
    test_claim_1 = Claim(
        claim_id="c1",
        quote="Coffee drinking doubles your risk of heart disease",
        claim_type="statistical",
        confidence=0.9,
        variables=["coffee", "heart disease"],
        numerical_values=[]
    )

    checks_1 = analyzer.check_claim(test_claim_1)
    relative_risk_check_1 = [c for c in checks_1 if c.check_name == "Relative Risk Without Context"][0]

    print(f"\n✅ Test 1: '{test_claim_1.quote}'")
    print(f"   Expected: FAIL (high severity)")
    print(f"   Result: {'FAIL' if not relative_risk_check_1.passed else 'PASS'} ({relative_risk_check_1.severity})")
    print(f"   Explanation: {relative_risk_check_1.explanation}")

    assert not relative_risk_check_1.passed, "Should catch relative risk without context"
    assert relative_risk_check_1.severity == "high", "Should be high severity"

    # Test case 2: Should PASS - has absolute context
    test_claim_2 = Claim(
        claim_id="c2",
        quote="Risk increased from 0.5% to 1% in the treatment group",
        claim_type="statistical",
        confidence=0.9,
        variables=["risk"],
        numerical_values=["0.5%", "1%"]
    )

    checks_2 = analyzer.check_claim(test_claim_2)
    relative_risk_check_2 = [c for c in checks_2 if c.check_name == "Relative Risk Without Context"][0]

    print(f"\n✅ Test 2: '{test_claim_2.quote}'")
    print(f"   Expected: PASS")
    print(f"   Result: {'FAIL' if not relative_risk_check_2.passed else 'PASS'}")

    assert relative_risk_check_2.passed, "Should pass when absolute context is provided"

    # Test case 3: Should FAIL - "3x more likely" without context
    test_claim_3 = Claim(
        claim_id="c3",
        quote="Smokers are 3x more likely to develop cancer",
        claim_type="statistical",
        confidence=0.9,
        variables=["smoking", "cancer"],
        numerical_values=["3x"]
    )

    checks_3 = analyzer.check_claim(test_claim_3)
    relative_risk_check_3 = [c for c in checks_3 if c.check_name == "Relative Risk Without Context"][0]

    print(f"\n✅ Test 3: '{test_claim_3.quote}'")
    print(f"   Expected: FAIL (high severity)")
    print(f"   Result: {'FAIL' if not relative_risk_check_3.passed else 'PASS'} ({relative_risk_check_3.severity})")

    assert not relative_risk_check_3.passed, "Should catch '3x more likely' without absolute numbers"

    print("\n" + "=" * 70)
    print("✅ All Relative Risk tests passed!")


def test_missing_comparator_check():
    """Test the Missing Comparator check."""
    print("\n\n🧪 Testing Missing Comparator Check")
    print("=" * 70)

    analyzer = StatisticalAnalyzer("Test text")

    # Test case 1: Should FAIL - improvement without comparator (research context)
    test_claim_1 = Claim(
        claim_id="c1",
        quote="The study found that participants improved significantly",
        claim_type="causal",
        confidence=0.9,
        variables=["participants"],
        numerical_values=[]
    )

    checks_1 = analyzer.check_claim(test_claim_1)
    comparator_check_1 = [c for c in checks_1 if c.check_name == "Missing Comparator"][0]

    print(f"\n✅ Test 1: '{test_claim_1.quote}'")
    print(f"   Expected: FAIL (high severity - research context)")
    print(f"   Result: {'FAIL' if not comparator_check_1.passed else 'PASS'} ({comparator_check_1.severity})")
    print(f"   Explanation: {comparator_check_1.explanation}")

    assert not comparator_check_1.passed, "Should catch missing comparator in research"
    assert comparator_check_1.severity == "high", "Should be high severity for research claims"

    # Test case 2: Should PASS - has comparator
    test_claim_2 = Claim(
        claim_id="c2",
        quote="Treatment improved symptoms compared to placebo",
        claim_type="causal",
        confidence=0.9,
        variables=["treatment", "symptoms"],
        numerical_values=[]
    )

    checks_2 = analyzer.check_claim(test_claim_2)
    comparator_check_2 = [c for c in checks_2 if c.check_name == "Missing Comparator"][0]

    print(f"\n✅ Test 2: '{test_claim_2.quote}'")
    print(f"   Expected: PASS")
    print(f"   Result: {'FAIL' if not comparator_check_2.passed else 'PASS'}")

    assert comparator_check_2.passed, "Should pass when comparator is mentioned"

    # Test case 3: Should FAIL - "works better" without comparator (medium severity)
    test_claim_3 = Claim(
        claim_id="c3",
        quote="Our product works better for busy professionals",
        claim_type="comparative",
        confidence=0.9,
        variables=["product", "professionals"],
        numerical_values=[]
    )

    checks_3 = analyzer.check_claim(test_claim_3)
    comparator_check_3 = [c for c in checks_3 if c.check_name == "Missing Comparator"][0]

    print(f"\n✅ Test 3: '{test_claim_3.quote}'")
    print(f"   Expected: FAIL (medium severity - marketing claim)")
    print(f"   Result: {'FAIL' if not comparator_check_3.passed else 'PASS'} ({comparator_check_3.severity})")

    assert not comparator_check_3.passed, "Should catch vague 'better' claims"
    assert comparator_check_3.severity == "medium", "Should be medium severity for non-research"

    print("\n" + "=" * 70)
    print("✅ All Missing Comparator tests passed!")


if __name__ == "__main__":
    print("\n🔬 TESTING NEW STATISTICAL CHECKS\n")

    try:
        test_relative_risk_check()
        test_missing_comparator_check()

        print("\n" + "=" * 70)
        print("🎉 ALL NEW CHECKS WORKING CORRECTLY!")
        print("=" * 70)
        print("\nNew checks added:")
        print("  1. Relative Risk Without Context (HIGH severity)")
        print("  2. Missing Comparator (HIGH/MEDIUM severity)")
        print("\nReady for demo! 🚀")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
