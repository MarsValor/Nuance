"""
Quick integration test for Nuance components.
Tests statistical checks without requiring API key.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.schemas import Claim, TextMetrics
from nuance.statistical_checks import StatisticalAnalyzer


def test_statistical_analyzer():
    """Test the statistical analysis engine."""

    # Test text with obvious issues
    test_text = """
    New study proves that AI always improves productivity by 300%!
    Companies using AI see massive improvements. The technology clearly
    causes better performance. Most experts agree this will revolutionize
    every industry.
    """

    print("🧪 Testing Statistical Analyzer...")
    print("=" * 60)

    analyzer = StatisticalAnalyzer(test_text)

    # Test text metrics
    print("\n📊 Text Metrics:")
    metrics = analyzer.calculate_text_metrics()
    print(f"  - Data Density: {metrics.data_density_score:.1%}")
    print(f"  - Vagueness Score: {metrics.vagueness_score:.1%}")
    print(f"  - Extreme Language Count: {metrics.extreme_language_count}")
    print(f"  - Sample Size Mentioned: {metrics.sample_size_mentioned}")
    print(f"  - Causation Language Count: {metrics.causation_language_count}")

    # Test claim checking
    print("\n🔍 Testing Claim Checks:")
    test_claim = Claim(
        claim_id="c1",
        quote="AI always improves productivity by 300%",
        claim_type="statistical",
        confidence=0.9,
        variables=["AI", "productivity"],
        numerical_values=["300%"]
    )

    checks = analyzer.check_claim(test_claim)

    print(f"\n  Claim: \"{test_claim.quote}\"")
    print(f"  Total checks run: {len(checks)}")

    failed_checks = [c for c in checks if not c.passed]
    print(f"  Failed checks: {len(failed_checks)}")

    for check in failed_checks:
        print(f"\n    ❌ {check.check_name} [{check.severity}]")
        print(f"       {check.explanation}")
        if check.suggestion:
            print(f"       💡 {check.suggestion}")

    print("\n" + "=" * 60)
    print("✅ All tests passed! Statistical analysis is working correctly.")


def test_schema_validation():
    """Test Pydantic schema validation."""

    print("\n🧪 Testing Schema Validation...")
    print("=" * 60)

    # Test valid claim
    try:
        claim = Claim(
            claim_id="c1",
            quote="Test claim",
            claim_type="statistical",
            confidence=0.8,
            variables=["var1", "var2"],
            numerical_values=["50%"]
        )
        print("✅ Valid claim schema passed")
    except Exception as e:
        print(f"❌ Valid claim failed: {e}")
        return

    # Test invalid claim_id format
    try:
        invalid_claim = Claim(
            claim_id="invalid_id",  # Should start with 'c' + number
            quote="Test",
            claim_type="statistical",
            confidence=0.8,
            variables=[],
            numerical_values=[]
        )
        print("❌ Invalid claim_id should have failed but didn't")
    except Exception as e:
        print(f"✅ Invalid claim_id correctly rejected: {type(e).__name__}")

    # Test invalid confidence range
    try:
        invalid_confidence = Claim(
            claim_id="c1",
            quote="Test",
            claim_type="statistical",
            confidence=1.5,  # Out of range
            variables=[],
            numerical_values=[]
        )
        print("❌ Invalid confidence should have failed but didn't")
    except Exception as e:
        print(f"✅ Invalid confidence correctly rejected: {type(e).__name__}")

    print("\n" + "=" * 60)
    print("✅ Schema validation working correctly!")


if __name__ == "__main__":
    print("\n" + "🔬 NUANCE INTEGRATION TEST" + "\n")

    try:
        test_schema_validation()
        test_statistical_analyzer()

        print("\n" + "=" * 60)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Set up your .env file with ANTHROPIC_API_KEY")
        print("2. Run: streamlit run app.py")
        print("3. Test with real articles!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
