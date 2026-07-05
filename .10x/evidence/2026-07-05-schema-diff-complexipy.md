Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-schema-diff-complexipy-hotspots.md

# Schema Diff Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/diff.py::SchemaDiff.compare_node` was refactored into comparison setup, additions, removals, rename replacement, and type-change helpers. `_is_type_narrowing` now delegates precision and integer narrowing checks to focused helpers. The focused Complexipy command exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/diff.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/diff.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/diff.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/diff.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/diff.py
uv run pytest tests/core/test_diff.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/diff.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `23 passed, 2 warnings in 18.64s`.

## What This Supports Or Challenges

Supports that schema diff complexity was reduced without failing direct diff coverage or focused static checks.

## Limits

The direct tests exercise the core diff paths with fixtures and mocks; they do not exhaust every adapter-specific database metadata shape.
