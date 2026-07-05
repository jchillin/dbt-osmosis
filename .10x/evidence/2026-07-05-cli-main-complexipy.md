Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-cli-main-complexipy-hotspots.md

# CLI main Complexipy refactor evidence

## What was observed

`src/dbt_osmosis/cli/main.py` no longer reports failed Complexipy functions after extracting shared helpers for natural-language generation, staging output preparation, diff rendering, test suggestion selection/output, suggestion table formatting, and SQL lint display.

Repo-wide Complexipy also exits zero with no failed functions.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/cli/main.py --failed --plain --sort desc
```

Observed exit code: 0. Observed output: none.

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis --failed --plain --sort desc
```

Observed exit code: 0. Observed output: none.

```bash
uvx ruff==0.15.17 check src/dbt_osmosis/cli/main.py
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uvx ruff==0.15.17 format --check src/dbt_osmosis/cli/main.py
```

Observed exit code: 0. Output: `1 file already formatted`

```bash
uv run --no-sync --with ty ty check src/dbt_osmosis/cli/main.py --output-format concise
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uv run --no-sync --with mypy mypy src/dbt_osmosis/cli/main.py
```

Observed exit code: 0. Output: `Success: no issues found in 1 source file`

```bash
uv run --no-sync --with basedpyright basedpyright src/dbt_osmosis/cli/main.py --level error
```

Observed exit code: 0. Output: `0 errors, 0 warnings, 0 notes`

```bash
uv run pytest tests/core/test_cli.py tests/core/test_cli_generate_group.py tests/core/test_sql_lint.py tests/core/test_test_suggestions.py tests/core/test_diff.py
```

Observed exit code: 0. Output summary: `181 passed, 2 warnings in 37.50s`

```bash
git diff --check
```

Observed exit code: 0. Observed output: none.

## What this supports or challenges

This supports the ticket acceptance criteria that all remaining CLI Complexipy hotspots were eliminated and the repo-wide Complexipy gate is clean while focused CLI, generation, lint, test-suggestion, and diff behaviors remain covered by tests.

## Limits

This is focused CLI verification plus repo-wide Complexipy. It is not the final full repository verification sweep.
