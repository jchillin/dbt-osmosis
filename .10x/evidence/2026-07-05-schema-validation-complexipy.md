Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-schema-validation-complexipy-hotspots.md

# Schema Validation Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/schema/validation.py` was refactored to split column entry validation, test entry validation, model version entry/latest validation, and source table validation into focused helpers. The focused Complexipy command now exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/schema/validation.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/schema/validation.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/schema/validation.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/schema/validation.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/schema/validation.py
uv run pytest tests/core/test_validation.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/schema/validation.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `50 passed, 2 warnings in 0.23s`.

## What This Supports Or Challenges

Supports that the validation hotspots were reduced without failing direct validator coverage or focused static checks.

## Limits

The evidence does not exhaustively assert every warning/error message by snapshot; closure review inspected the extraction against the original branch behavior.
