# Test Suite

This directory contains the core test suite for Nuance. All tests should pass before committing to main.

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_new_checks.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Files

### Core Functionality Tests

**`test_new_checks.py`** ⭐ CRITICAL
- Tests the two main statistical checks: Relative Risk Without Context and Missing Comparator
- Ensures these high-value checks work correctly
- Run this before any commit

**`test_health_claims.py`**
- Tests detection of vague health/supplement marketing claims
- Validates that medical verbs (regulates, fights, blocks, etc.) are caught
- Ensures comparator detection works for health claims

**`test_implicit_comparator.py`**
- Tests the fix for implicit comparator false positives
- Ensures "increased by X%" is NOT flagged as missing comparator
- Documents important edge cases

**`test_integration.py`**
- Integration tests for the full pipeline
- Tests claim extraction, analysis, and audit generation

**`test_counterfactuals.py`**
- Tests counterfactual reasoning detection
- (If applicable to your implementation)

## Adding New Tests

When adding new statistical checks:
1. Add unit tests to `test_new_checks.py` or create a new file
2. Test both positive cases (should fail) and negative cases (should pass)
3. Document edge cases with specific test cases
4. Update this README

## Test Coverage

Run coverage reports with:
```bash
pytest --cov=src/nuance tests/
```
