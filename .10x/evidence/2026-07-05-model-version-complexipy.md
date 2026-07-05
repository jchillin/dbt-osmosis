Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-model-version-complexipy-hotspot.md

# Model Version Complexipy Refactor Evidence

## What Was Observed

`src/dbt_osmosis/core/model_versions.py` no longer has any functions over the Complexipy failure threshold when checked directly.

Before refactor, the file-level failed-function report showed:

- `_versioned_model_yaml_view`: 17

After refactor, the same direct file check exited zero with an empty failed-function list.

## Procedure

Commands run from `/Users/alexanderbut/code_projects/personal/dbt-osmosis`:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/model_versions.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/model_versions.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/model_versions.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/model_versions.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/model_versions.py
uv run pytest tests/core/test_inheritance_behavior.py::test_versioned_model_yaml_view_prefers_exact_string_version_match tests/core/test_inheritance_behavior.py::test_versioned_ancestor_unrendered_description_reads_version_columns tests/core/test_property_accessor.py tests/core/test_sync_operations.py::test_sync_node_to_yaml_versioned_preserves_column_selector
```

## Results

- Complexipy file check: exit 0, no failed functions reported.
- Ruff check: exit 0, `All checks passed!`.
- Ruff format check: exit 0, `1 file already formatted`.
- ty check: exit 0, `All checks passed!`.
- mypy check: exit 0, `Success: no issues found in 1 source file`.
- Focused pytest: exit 0, `26 passed, 3 skipped, 2 warnings in 6.31s`.

The skipped tests were existing `demo_project` fixture skips in `tests/core/test_property_accessor.py`.

## What This Supports Or Challenges

This supports that the model-version hotspot was reduced directly, without baselines, threshold changes, ratchets, ignored functions, or tool-output gaming. It also supports exact string version matching, versioned column YAML reads, parent fallback metadata, and versioned sync selector preservation.

## Limits

This evidence is scoped to `src/dbt_osmosis/core/model_versions.py` and focused versioned-model tests. It does not claim repository-wide Complexipy is clean.
