Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-restructuring-complexipy-hotspots.md

# Restructuring Complexipy Refactor Evidence

## What Was Observed

`src/dbt_osmosis/core/restructuring.py` no longer has any functions over the Complexipy failure threshold when checked directly.

Before refactor, the file-level failed-function report showed:

- `apply_restructure_plan`: 62
- `draft_restructure_delta_plan`: 52
- `_create_operations_for_node`: 32

After refactor, the same direct file check exited zero with an empty failed-function list.

## Procedure

Commands run from `/Users/alexanderbut/code_projects/personal/dbt-osmosis`:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/restructuring.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/restructuring.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/restructuring.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/restructuring.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/restructuring.py
uv run pytest tests/core/test_restructuring.py tests/test_yaml_context.py
```

## Results

- Complexipy file check: exit 0, no failed functions reported.
- Ruff check: exit 0, `All checks passed!`.
- Ruff format check: exit 0, `1 file already formatted`.
- ty check: exit 0, `All checks passed!`.
- mypy check: exit 0, `Success: no issues found in 1 source file`.
- Focused pytest: exit 0, `38 passed, 1 skipped, 2 warnings in 30.97s`.

The skipped test was `tests/core/test_restructuring.py::test_target_path_source_node_handling`, skipped because the local manifest fixture did not contain source nodes.

## What This Supports Or Challenges

This supports that the restructuring hotspots were reduced directly, without baselines, threshold changes, ratchets, ignored functions, or tool-output gaming. It also supports that restructure planning, applying, confirmation, dry-run, deletion tracking, and YAML context smoke paths continue to pass their focused tests.

## Limits

This evidence is scoped to `src/dbt_osmosis/core/restructuring.py` and focused restructuring tests. It does not claim repository-wide Complexipy is clean.
