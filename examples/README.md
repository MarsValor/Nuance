# Example Analyses

This directory contains real-world examples demonstrating Nuance's capabilities on viral articles and common misinformation patterns.

## Running Examples

```bash
# Run wine article analysis
python examples/wine_article_analysis.py

# Run cybersecurity scare analysis
python examples/cybersecurity_scare_analysis.py
```

## Example Files

### `wine_article_analysis.py`

Analyzes the viral "Wine = Exercise" health claim article that spread widely online.

**Article claim:** "Drinking a glass of red wine a day is THE SAME AS A ONE-HOUR GYM SESH"

**What Nuance catches:**
- ✅ Missing Comparator (regulates, fights, improve)
- ✅ Correlation vs Causation (equals, causes)
- ✅ Extreme Language (THE SAME AS)
- ✅ Base Rate Neglect (less likely... cancer)
- ✅ Sample Size Missing (Alberta study - no n=)

**Why this example matters:**
- Real viral content that millions saw
- Demonstrates multiple check types triggering
- Perfect for demos and onboarding

### `cybersecurity_scare_analysis.py`

Analyzes technical fear-mongering about cybersecurity threats.

**Article claim:** "Ransomware attacks have increased by 300%... your business is almost certain to be hit next"

**What Nuance catches:**
- 🔴 Relative Risk Without Context (300%, tripling)
- ⚠️ Extreme Language (terrifying, almost certain, completely exposed)
- ⚠️ Missing Sample Size (no n= mentioned)
- ⚠️ Base Rate Neglect (percentages without context)
- ⚠️ Data Support (Most experts agree)

**Why this example matters:**
- Shows technical/B2B fear-mongering detection
- Demonstrates relative risk check on security claims
- Different domain from health (proves generalizability)

## Use Cases

These examples are useful for:
1. **Onboarding new developers** - See what Nuance is designed to catch
2. **Demo presentations** - Real-world examples resonate better than synthetic ones
3. **Documentation** - Show expected output format
4. **Regression testing** - Ensure we still catch known viral BS

## Adding New Examples

When adding new examples
1. Document what checks SHOULD trigger
2. Add a summary of why the example is valuable
3. Keep the article text authentic (with personality/jokes intact)
