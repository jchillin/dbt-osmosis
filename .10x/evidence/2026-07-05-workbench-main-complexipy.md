Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-workbench-main-complexipy-hotspot.md

# Workbench main Complexipy refactor evidence

## What was observed

`src/dbt_osmosis/workbench/app.py` no longer reports failed Complexipy functions after extracting workbench state initialization, path/query setup, hotkey registration, and dashboard rendering helpers from `main()`.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/workbench/app.py --failed --plain --sort desc
```

Observed exit code: 0. Observed output: none.

```bash
uvx ruff==0.15.17 check src/dbt_osmosis/workbench/app.py
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uvx ruff==0.15.17 format --check src/dbt_osmosis/workbench/app.py
```

Observed exit code: 0. Output: `1 file already formatted`

```bash
uv run --no-sync --with basedpyright basedpyright src/dbt_osmosis/workbench/app.py --level error
```

Observed exit code: 0. Output: `0 errors, 0 warnings, 0 notes`

```bash
uv run pytest tests/core/test_workbench_app.py tests/workbench/test_ai_assistant.py
```

Observed exit code: 0. Output summary: `17 passed, 2 warnings in 7.23s`

```bash
uv run pytest tests/core/test_cli.py -k workbench
```

Observed exit code: 0. Output summary: `10 passed, 29 deselected, 2 warnings in 0.25s`

```bash
git diff --check
```

Observed exit code: 0. Observed output: none.

## What this supports or challenges

This supports the ticket acceptance criteria that the workbench `main()` hotspot was eliminated while preserving focused workbench helper behavior, AI assistant smoke coverage, and CLI workbench launch behavior.

## Limits

This is focused verification. It does not launch an interactive Streamlit browser session.
