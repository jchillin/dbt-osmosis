Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-test-suggestions-complexipy-hotspot.md

# Test Suggestions Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/test_suggestions.py::_get_existing_tests_for_node` was refactored into focused helpers for manifest-test attachment detection and `TestSuggestion` construction. The focused Complexipy command now exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/test_suggestions.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/test_suggestions.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/test_suggestions.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/test_suggestions.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/test_suggestions.py
uv run pytest tests/core/test_test_suggestions.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/test_suggestions.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `42 passed, 2 warnings in 19.13s`.

## What This Supports Or Challenges

Supports that manifest generic-test extraction complexity was reduced without failing direct test-suggestion coverage or focused static checks.

## Limits

The evidence does not cover live OpenAI-backed generation paths; the changed helper is manifest extraction only.
