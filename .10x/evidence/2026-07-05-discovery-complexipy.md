Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-discovery-complexipy-hotspot.md

# Discovery Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/discovery.py::discover_undocumented_models` was refactored into focused helpers for scan eligibility, model gap construction, and documented column counting. The focused Complexipy command now exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/discovery.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/discovery.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/discovery.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/discovery.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/discovery.py
uv run pytest tests/core/test_config.py tests/core/test_cli.py::test_sql_compile_preserves_explicit_profiles_dir tests/core/test_inheritance_behavior.py::test_multi_generation_inheritance_chain
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/discovery.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `23 passed, 2 warnings in 10.15s`.

## What This Supports Or Challenges

Supports that the discovery hotspot was reduced without failing focused lint, format, type, or nearby dbt context/inheritance tests.

## Limits

No direct unit test exists for `discover_undocumented_models`; this evidence relies on static checks and nearby integration-style coverage.
