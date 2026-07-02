# AAOS Tests

This directory contains tests for governance contracts, schemas, and runtime evaluators.

Tests should verify that external sources remain evidence candidates and do not become governance authorities.

## Deterministic Test Command

Run the public deterministic evaluator suite with:

```bash
python -m unittest discover -s tests -t . -p "test_*.py"
```

These tests use only the Python standard library and require no external secrets or vendor credentials.
