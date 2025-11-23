# 🔍 Nuance

**AI-Powered Statistical Reasoning Auditor**

Nuance is a reasoning engine that combines LLM-based semantic extraction with deterministic statistical rules to audit media narratives for cognitive biases and logical fallacies.

Built for the Anthropic AI Toronto Hackathon 2025 - Track 1: Reasoning Systems

---

## 🎯 The Problem

In the age of information abundance, statistical illiteracy is a critical vulnerability. News articles and social media posts often weaponize data—confusing correlation with causation, ignoring base rates, or using vague language to hide weak evidence. **Nuance** is not about writing essays for you—it's about training your bullshit detector.

## 🚀 What Makes Nuance Different

Unlike typical "LLM wrapper" applications, Nuance implements a **neuro-symbolic pipeline**:

### Two-Stage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: Raw Text                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Structured Extraction (Neuro)                     │
│  ------------------------------------------------            │
│  • Claude extracts claims into strict JSON schema            │
│  • Pydantic validates structure                             │
│  • Auto-retry on validation failure                         │
│  • Result: ClaimsExtraction object                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Deterministic Analysis (Symbolic)                 │
│  ------------------------------------------------            │
│  • Python calculates text metrics (no LLM)                  │
│  • Run logical checks on each claim:                        │
│    - Correlation vs causation                               │
│    - Sample size disclosure                                 │
│    - Base rate neglect                                      │
│    - Extreme language without data                          │
│    - Data support for quantitative claims                   │
│  • Result: StatisticalCheck[] per claim                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: Educational Synthesis                             │
│  ------------------------------------------------            │
│  • Claude receives flagged issues                           │
│  • Generates human-friendly educational summary             │
│  • Explains WHY issues matter                               │
│  • Result: Audit report                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technical Highlights

### 1. Guardrails Pattern (Pydantic + Retry)

**Problem:** LLMs sometimes produce malformed JSON or hallucinate fields.

**Solution:** Strict schema validation with automatic retry:

```python
# If Claude outputs invalid JSON:
try:
    validated = ClaimsExtraction.model_validate(json_data)
except ValidationError as e:
    # Feed error back to Claude
    retry_prompt = f"Your JSON failed validation: {e}. Please fix and retry."
    # Claude gets another chance to correct
```

**Impact:** Significantly reduces parsing errors compared to naive JSON parsing.

### 2. Stats Layer (Python > LLM for Math)

**Problem:** LLMs are bad at math and statistical reasoning.

**Solution:** All quantitative analysis done in Python:

- **Data Density:** `sentences_with_numbers / total_sentences`
- **Vagueness Score:** `hedge_words / total_words`
- **Extreme Language:** Regex count of "prove", "always", "never"
- **Sample Size Check:** Pattern matching for "n=", "participants"
- **Causation Scan:** Detect causal language without evidence

**Impact:** Deterministic, explainable, and reproducible results.

### 3. Pipeline Visualization

**Problem:** Black-box AI feels untrustworthy.

**Solution:** Streamlit UI shows step-by-step progress:

```
⏳ Step 1: Extracting claims...
✅ Step 1 Complete: Extracted 5 claims

⏳ Step 2: Running statistical checks...
✅ Step 2 Complete: Found 3 potential issues

⏳ Step 3: Generating audit report...
✅ Step 3 Complete: Audit report ready
```

**Impact:** Users see the reasoning process, building trust.

## 📦 Installation

### Prerequisites

- Python 3.8+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

```bash
# Clone the repository
git clone https://github.com/MarsValor/Nuance.git
cd Nuance

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## 🎮 Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

Then:
1. Open the URL shown in your terminal (usually `http://localhost:8501`)
2. Paste a news article, blog post, or any text
3. Click "🔍 Audit This Text"
4. Watch the pipeline process your text
5. Review the audit results

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific tests (no API key required for statistical checks)
python tests/test_new_checks.py
python tests/test_health_claims.py
python tests/test_implicit_comparator.py

# Run integration tests (may require API key)
python tests/test_integration.py
python tests/test_counterfactuals.py
```

### Example Use Cases

- **Fact-checking news articles** for statistical manipulation
- **Reviewing research summaries** for proper methodology disclosure
- **Analyzing social media posts** for misleading data claims
- **Teaching critical thinking** with real-world examples

### Troubleshooting

**Issue: "API Error" or "Invalid API key"**
- Solution: Check that your `ANTHROPIC_API_KEY` is correctly set in the `.env` file
- Get a valid key from: https://console.anthropic.com/

**Issue: "Rate Limit Exceeded"**
- Solution: You've hit the API rate limit. Wait 60 seconds and try again
- For high usage, consider upgrading your Anthropic plan

**Issue: "No Claims Found"**
- Solution: The text doesn't contain statistical or causal claims
- Try adding text with numbers, percentages, or causal language (e.g., "causes", "increases", "proves")

**Issue: App takes too long / times out**
- Solution: Your text might be too long (>2000 words)
- Try analyzing a shorter excerpt first

**Issue: "Could not generate alternatives"**
- Solution: This optional feature requires API access
- Check your API key and network connection
- The main analysis will still work without this feature

## 🎓 Educational Value

Nuance is designed as a **teaching tool** that explains *why* claims are problematic:

**Bad Claim:**
> "Coffee causes longevity - study shows correlation between coffee drinking and lifespan"

**Nuance Audit:**
- ❌ **Correlation vs Causation:** Uses causal language ("causes") for correlational evidence
- ❌ **Sample Size Disclosure:** No sample size mentioned
- ⚠️ **Base Rate Neglect:** No absolute numbers provided
- 💡 **Suggestion:** Rephrase as "associated with" and include study details

### 🧠 Think-Before-Reveal Mode

**Interactive learning mode** that turns auditing into a game:

1. **Extract Claims** - Nuance identifies statistical claims in the text
2. **Make Your Predictions** - You predict which checks will fail for each claim
3. **Compare Results** - See how accurate your critical thinking was
4. **Get Scored** - Receive accuracy metrics (precision, recall, F1 score)

**Why this matters:** Active prediction strengthens critical thinking better than passive reading. You learn to spot BS *before* the tool tells you.

## 🏗️ Project Structure

```
Nuance/
├── app.py                          # Streamlit UI (main entry point)
├── src/nuance/                     # Core library code
│   ├── __init__.py
│   ├── schemas.py                  # Pydantic models (strict validation)
│   ├── retry.py                    # Auto-retry mechanism
│   ├── claude_client.py            # Anthropic API wrapper
│   └── statistical_checks.py       # 7 deterministic checks
├── tests/                          # Test suite (run before commit)
│   ├── README.md
│   ├── test_new_checks.py          # ⭐ Main statistical checks
│   ├── test_health_claims.py       # Health marketing detection
│   ├── test_implicit_comparator.py # False positive prevention
│   ├── test_integration.py         # End-to-end tests
│   └── test_counterfactuals.py     # Counterfactual reasoning
├── examples/                       # demo analyses
│   ├── README.md
│   ├── wine_article_analysis.py          # Viral health claim
│   └── cybersecurity_scare_analysis.py   # Technical fear-mongering
├── requirements.txt
├── .env.example
├── .gitignore
├── STRUCTURE.md                    # Project organization guide
└── README.md
```

### Directory Guide

- `src/nuance/` – core library code (schemas, Claude client, retry logic, statistical checks)
- `tests/` – must-pass suite covering deterministic checks, integration flows, regression cases
- `examples/` – runnable notebooks/scripts that analyze articles for demos and onboarding
- `app.py` – Streamlit front-end tying everything together
- `requirements.txt` / `.env.example` – environment setup

### Running Tests

```bash
# Run everything
python -m pytest tests/

# Focus on statistical heuristics (fast, no API needed)
python tests/test_new_checks.py

# Include coverage info
pytest --cov=src/nuance tests/
```

### Example Analyses

```bash
python examples/wine_article_analysis.py          # Viral "wine = exercise" article
python examples/cybersecurity_scare_analysis.py   # Technical fear-mongering breakdown
```

### Workflow Tips

1. Make code changes
2. Run at least `python tests/test_new_checks.py`
3. Optionally rerun examples for demo sanity
4. Commit/push once tests pass

### New Contributor Checklist

1. Read `README.md` for the system overview
2. Run `python examples/wine_article_analysis.py` to see Nuance end-to-end
3. Review `tests/README.md` plus `tests/test_new_checks.py` for coding patterns
4. Follow the setup instructions in `setup.sh` / `.env.example` before working on the app

## 🧪 Key Components

### Schemas ([schemas.py](src/nuance/schemas.py))

Pydantic models that enforce structure:
- `Claim`: Individual statistical/causal claim
- `ClaimsExtraction`: Collection of claims from text
- `StatisticalCheck`: Result of a deterministic check
- `ClaimAudit`: Complete audit for one claim
- `TextMetrics`: Quantitative text analysis
- `AuditReport`: Final report structure

### Statistical Checks ([statistical_checks.py](src/nuance/statistical_checks.py))

Seven core checks run on each claim:
1. **Correlation vs Causation** - Flags causal language without causal evidence
2. **Sample Size Disclosure** - Checks if sample size mentioned
3. **Extreme Language** - Detects absolute terms without data
4. **Base Rate Neglect** - Ensures percentages include absolute context
5. **Data Support** - Verifies quantitative claims have numbers
6. **Relative Risk Without Context** (HIGH) - Catches "doubles your risk" without absolute numbers
7. **Missing Comparator** - Flags improvement claims without comparison point (e.g., "improved" vs. what?)

### Retry Mechanism ([retry.py](src/nuance/retry.py))

Auto-correction loop:
1. Call Claude with prompt
2. Try to parse JSON with Pydantic
3. If validation fails → feed error back to Claude
4. Retry up to 3 times
5. Success or raise `RetryExhaustedError`

## 🔬 Technical Differentiators

1. **Implemented robust retry mechanism with Pydantic validators** to enforce strict output schemas
2. **Designed hybrid evaluation metrics** combining LLM semantic analysis with deterministic statistical heuristics
3. **Built neuro-symbolic reasoning pipeline** separating extraction (LLM) from validation (Python)
4. **Created educational reasoning system** that teaches statistical thinking, not just detects errors

## 🍷 Example Analyses

Nuance includes examples to demonstrate its capabilities:

### Wine = Exercise (Viral Health Claim)
```bash
python examples/wine_article_analysis.py
```

Analyzes the viral article claiming "drinking red wine is THE SAME AS A ONE-HOUR GYM SESH"

**Catches:**
- Missing Comparator ("regulates blood sugar" - vs. what?)
- Correlation vs Causation ("equals gym time")
- Extreme Language ("THE SAME AS")
- Base Rate Neglect ("less likely to develop cancer" - from what baseline?)
- Sample Size Missing ("Alberta study" - no n=)

### Cybersecurity Scare (Technical Fear-Mongering)
```bash
python examples/cybersecurity_scare_analysis.py
```

Analyzes fear-based marketing: "Ransomware attacks increased by 300%... your business is almost certain to be hit next"

**Catches:**
- 🔴 Relative Risk Without Context ("tripling of risk" without absolute numbers)
- Extreme Language ("almost certain", "completely exposed")
- Data Support ("Most experts agree")
- Base Rate Neglect (percentages without context)

## 🤝 Contributing

This project was built for Anthropic AI Toronto Hackathon 2025. Contributions, issues, and feature requests are welcome!

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

**MarsValor**
- GitHub: [@MarsValor](https://github.com/MarsValor)
- Project: Built for Anthropic AI Toronto Hackathon 2025

---

**Remember:** Nuance is not about censoring language. It's about building better critical thinking skills. Use it to audit your own writing, too!
