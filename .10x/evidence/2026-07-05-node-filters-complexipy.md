Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-node-filters-complexipy-hotspots.md

# Node Filters Complexipy Refactor Evidence

## What Was Observed

`src/dbt_osmosis/core/node_filters.py` no longer has any functions over the Complexipy failure threshold when checked directly.

Before refactor, the file-level failed-function report showed:

- `_iter_candidate_nodes`: 18
- `_topological_sort`: 18
- `_is_file_match`: 16

After refactor, the same direct file check exited zero with an empty failed-function list.

## Procedure

Commands run from `/Users/alexanderbut/code_projects/personal/dbt-osmosis`:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/node_filters.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/node_filters.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/node_filters.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/node_filters.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/node_filters.py
uv run pytest tests/core/test_node_filters.py tests/core/test_sql_lint.py
```

## Results

- Complexipy file check: exit 0, no failed functions reported.
- Ruff check: exit 0, `All checks passed!`.
- Ruff format check: exit 0, `1 file already formatted`.
- ty check: exit 0, `All checks passed!`.
- mypy check: exit 0, `Success: no issues found in 1 source file`.
- Focused pytest: exit 0, `68 passed, 2 warnings in 7.84s`.

## What This Supports Or Challenges

This supports that node-filter hotspots were reduced directly, without baselines, threshold changes, ratchets, ignored functions, or tool-output gaming. It also supports that path/FQN filtering, external package inclusion, ephemeral exclusion, topological sorting, and SQL lint model selection still pass their focused tests.

## Limits

This evidence is scoped to `src/dbt_osmosis/core/node_filters.py` and focused node-filter consumers. It does not claim repository-wide Complexipy is clean.
