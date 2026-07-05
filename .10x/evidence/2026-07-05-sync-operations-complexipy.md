Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-sync-operations-complexipy-hotspots.md

# Sync Operations Complexipy Refactor Evidence

## What Was Observed

`src/dbt_osmosis/core/sync_operations.py` no longer has any functions over the Complexipy failure threshold when checked directly.

Before refactor, the file-level failed-function report showed:

- `_get_or_create_source`: 50
- `_validate_no_duplicate_sync_entries`: 17
- `_deduplicate_versions`: 16

After refactor, the same direct file check exited zero with an empty failed-function list.

## Procedure

Commands run from `/Users/alexanderbut/code_projects/personal/dbt-osmosis`:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/sync_operations.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/sync_operations.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/sync_operations.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/sync_operations.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/sync_operations.py
uv run pytest tests/core/test_sync_operations.py tests/core/test_transforms.py::test_inherit_upstream_column_knowledge tests/test_yaml_inheritance.py
```

## Results

- Complexipy file check: exit 0, no failed functions reported.
- Ruff check: exit 0, `All checks passed!`.
- Ruff format check: exit 0, `1 file already formatted`.
- ty check: exit 0, `All checks passed!`.
- mypy check: exit 0, `Success: no issues found in 1 source file`.
- Focused pytest: exit 0, `46 passed, 2 warnings in 27.57s`.

## What This Supports Or Challenges

This supports that the sync-operation hotspots were reduced directly, without baselines, threshold changes, ratchets, ignored functions, or tool-output gaming. It also supports that duplicate protection, source/table matching, versioned sync, grouped sync, and inheritance sync integration still pass their focused tests.

## Limits

This evidence is scoped to `src/dbt_osmosis/core/sync_operations.py` and focused sync tests. It does not claim repository-wide Complexipy is clean.
