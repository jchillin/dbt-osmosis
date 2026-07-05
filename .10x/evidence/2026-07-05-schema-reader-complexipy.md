Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-schema-reader-complexipy-hotspots.md

# Schema Reader Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/schema/reader.py::_normalize_managed_quote_styles` and `_read_yaml` were refactored into focused helpers for mapping normalization, sequence normalization, unfiltered loading, filtered-content preparation, and cache writes. The focused Complexipy command now exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/schema/reader.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/schema/reader.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/schema/reader.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/schema/reader.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/schema/reader.py
uv run pytest tests/core/test_schema.py tests/core/test_error_handling.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/schema/reader.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `47 passed, 2 warnings in 7.41s`.

## What This Supports Or Challenges

Supports that YAML reader complexity was reduced without failing quote normalization, unmanaged-section preservation, cache, or YAML error handling coverage.

## Limits

This evidence covers direct schema reader/writer and error handling tests, not the full project-wide YAML workflow suite.
