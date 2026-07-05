Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-introspection-complexipy-hotspots.md

# introspection.py Complexipy refactor evidence

## What was observed

`src/dbt_osmosis/core/introspection.py` no longer reports failed Complexipy functions after decomposing settings resolution, project vars lookup, YAML path template lookup, column discovery, and property access helpers. Focused static checks and config/property/introspection tests pass.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/introspection.py --failed --plain --sort desc
```

Observed exit code: 0. Observed output: none.

```bash
uvx ruff==0.15.17 check src/dbt_osmosis/core/introspection.py
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/introspection.py
```

Observed exit code: 0. Output: `1 file already formatted`

```bash
uv run --no-sync --with ty ty check src/dbt_osmosis/core/introspection.py --output-format concise
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/introspection.py
```

Observed exit code: 0. Output: `Success: no issues found in 1 source file`

```bash
uv run --no-sync --with basedpyright basedpyright src/dbt_osmosis/core/introspection.py --level error
```

Observed exit code: 0. Output: `0 errors, 0 warnings, 0 notes`

```bash
uv run pytest tests/core/test_settings_resolver.py tests/core/test_config_resolution.py tests/core/test_introspection.py tests/core/test_property_accessor.py tests/core/test_real_config_shapes.py tests/test_yaml_context.py
```

Observed exit code: 0. Output summary: `127 passed, 3 skipped, 2 warnings in 16.97s`

```bash
git diff --check
```

Observed exit code: 0. Observed output: none.

## What this supports or challenges

This supports the ticket acceptance criteria that the `introspection.py` Complexipy hotspots were eliminated while preserving direct settings, configuration precedence, property access, and column discovery behavior covered by the focused tests.

## Limits

This is focused verification for `introspection.py` and directly related tests. It is not a full repository verification run.
