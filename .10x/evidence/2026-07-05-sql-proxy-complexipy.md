Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-sql-proxy-complexipy-hotspot.md

# SQL proxy Complexipy refactor evidence

## What was observed

`src/dbt_osmosis/sql/proxy.py` no longer reports failed Complexipy functions after decomposing ALTER TABLE comment middleware parsing and in-memory manifest mutation. Direct mypy checking of the optional proxy module also passes after adding local `mysql_mimic` stubs under `typings/`.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/sql/proxy.py --failed --plain --sort desc
```

Observed exit code: 0. Observed output: none.

```bash
uvx ruff==0.15.17 check src/dbt_osmosis/sql/proxy.py typings/mysql_mimic
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uvx ruff==0.15.17 format --check src/dbt_osmosis/sql/proxy.py typings/mysql_mimic
```

Observed exit code: 0. Output: `6 files already formatted`

```bash
uv run --no-sync --with ty ty check src/dbt_osmosis/sql/proxy.py --output-format concise
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uv run --no-sync --with mypy mypy src/dbt_osmosis/sql/proxy.py
```

Observed exit code: 0. Output summary: `Success: no issues found in 1 source file`

```bash
uv run --no-sync --with basedpyright basedpyright src/dbt_osmosis/sql/proxy.py --level error
```

Observed exit code: 0. Output: `0 errors, 0 warnings, 0 notes`

```bash
uv run pytest tests/core/test_sql_proxy.py tests/test_package_metadata.py
```

Observed exit code: 0. Output summary: `11 passed, 2 warnings in 0.22s`

```bash
git diff --check
```

Observed exit code: 0. Observed output: none.

## What this supports or challenges

This supports the ticket acceptance criteria that the SQL proxy Complexipy hotspot was eliminated while preserving tested proxy query behavior, in-memory comment middleware behavior, and package metadata expectations.

## Limits

This is focused verification for the SQL proxy slice. It does not exercise a live MySQL proxy server or a real `mysql_mimic` installation.
