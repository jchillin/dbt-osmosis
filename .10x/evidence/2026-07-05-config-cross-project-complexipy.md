Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-config-cross-project-complexipy-hotspot.md

# Config Cross-Project Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/config.py::_add_cross_project_references` was refactored into focused helpers for dbt-loom manifest loading, exposed-model filtering, `ModelNode` parsing, and manifest merging. The focused Complexipy command now exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/config.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/config.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/config.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/config.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/config.py
uv run pytest tests/core/test_config.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/config.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `21 passed, 2 warnings in 6.18s`.

## What This Supports Or Challenges

Supports that dbt-loom cross-project import complexity was reduced without failing config coverage or focused static checks.

## Limits

The direct test uses a mocked dbt-loom object; live dbt-loom installation behavior is not exercised by this evidence.
