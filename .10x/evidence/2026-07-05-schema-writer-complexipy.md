Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-schema-writer-complexipy-hotspots.md

# Schema Writer Complexipy Refactor Evidence

## What Was Observed

`src/dbt_osmosis/core/schema/writer.py` no longer has any functions over the Complexipy failure threshold when checked directly.

Before refactor, the file-level failed-function report showed:

- `commit_yamls`: 45
- `_write_yaml`: 40

After refactor, the same direct file check exited zero with an empty failed-function list.

## Procedure

Commands run from `/Users/alexanderbut/code_projects/personal/dbt-osmosis`:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/schema/writer.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/schema/writer.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/schema/writer.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/schema/writer.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/schema/writer.py
uv run pytest tests/core/test_schema.py tests/core/test_sync_operations.py::test_write_yaml_uses_unique_temp_path_and_preserves_existing_tmp tests/core/test_sync_operations.py::test_write_yaml_preserves_existing_file_mode tests/core/test_sync_operations.py::test_commit_yamls_no_write tests/core/test_restructuring.py::test_apply_restructure_plan_counts_deleted_files_as_disk_mutations tests/core/test_restructuring.py::test_apply_restructure_plan_dry_run_skips_reload
```

## Results

- Complexipy file check: exit 0, no failed functions reported.
- Ruff check: exit 0, `All checks passed!`.
- Ruff format check: exit 0, `1 file already formatted`.
- ty check: exit 0, `All checks passed!`.
- mypy check: exit 0, `Success: no issues found in 1 source file`.
- Focused pytest: exit 0, `35 passed, 2 warnings in 8.12s`.

## What This Supports Or Challenges

This supports that schema writer hotspots were reduced directly, without baselines, threshold changes, ratchets, ignored functions, or tool-output gaming. It also supports that direct writes, buffered commits, dry-run cache discard, no-clobber behavior, temp-file safety, file mode preservation, written-file tracking, and restructure write integration still pass their focused tests.

## Limits

This evidence is scoped to `src/dbt_osmosis/core/schema/writer.py` and focused writer tests. It does not claim repository-wide Complexipy is clean.
