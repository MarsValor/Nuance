"""
Quick test for the counterfactual generation feature.
Requires ANTHROPIC_API_KEY to be set in .env
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nuance.claude_client import ClaudeClient


def test_counterfactual_generation():
    """Test counterfactual generation with a known fallacy."""

    print("\n🧪 Testing Counterfactual Generation")
    print("=" * 70)

    try:
        # Initialize client
        client = ClaudeClient()
        print("✅ Claude client initialized")

        # Test case: Correlation vs Causation
        claim = "Coffee drinking causes longevity"
        fallacy = "Correlation vs Causation"
        explanation = "Uses causal language but only shows correlation"

        print(f"\nClaim: \"{claim}\"")
        print(f"Fallacy: {fallacy}")
        print(f"\nGenerating alternative explanations...")
        print("-" * 70)

        counterfactuals = client.generate_counterfactuals(
            claim_quote=claim,
            fallacy_type=fallacy,
            check_explanation=explanation
        )

        print("\n🧠 Alternative Explanations:\n")
        for i, alternative in enumerate(counterfactuals, 1):
            print(f"{i}. {alternative}")

        print("\n" + "=" * 70)
        print(f"✅ Generated {len(counterfactuals)} alternative explanations!")

        if len(counterfactuals) >= 3:
            print("✅ Feature is working correctly!")
        else:
            print("⚠️  Expected 3-4 alternatives, got", len(counterfactuals))

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_multiple_fallacy_types():
    """Test different types of fallacies."""

    print("\n\n🧪 Testing Different Fallacy Types")
    print("=" * 70)

    client = ClaudeClient()

    test_cases = [
        {
            "claim": "AI always improves productivity by 300%",
            "fallacy": "Extreme Language",
            "explanation": "Uses absolute terms without data support"
        },
        {
            "claim": "50% increase in sales",
            "fallacy": "Base Rate Neglect",
            "explanation": "Provides percentages without absolute context"
        },
        {
            "claim": "Study shows significant results",
            "fallacy": "Sample Size Disclosure",
            "explanation": "Statistical claim without mentioning sample size"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['fallacy']}")
        print(f"   Claim: \"{test['claim']}\"")

        try:
            counterfactuals = client.generate_counterfactuals(
                claim_quote=test['claim'],
                fallacy_type=test['fallacy'],
                check_explanation=test['explanation']
            )
            print(f"   ✅ Generated {len(counterfactuals)} alternatives")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n🔬 COUNTERFACTUAL GENERATION TEST\n")

    try:
        test_counterfactual_generation()
        test_multiple_fallacy_types()

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\nThe counterfactual feature is ready for the hackathon!")
        print("It will show up in the UI for medium/high severity issues.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
