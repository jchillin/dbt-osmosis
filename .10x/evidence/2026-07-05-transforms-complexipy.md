Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-transforms-complexipy-hotspots.md

# transforms.py Complexipy refactor evidence

## What was observed

`src/dbt_osmosis/core/transforms.py` no longer reports failed Complexipy functions after decomposing the transform hotspots. Focused static checks and transform/inheritance tests pass.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/transforms.py --failed --plain --sort desc
```

Observed exit code: 0. Observed output: none.

```bash
uvx ruff==0.15.17 check src/dbt_osmosis/core/transforms.py
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/transforms.py
```

Observed exit code: 0. Output: `1 file already formatted`

```bash
uv run --no-sync --with ty ty check src/dbt_osmosis/core/transforms.py --output-format concise
```

Observed exit code: 0. Output: `All checks passed!`

```bash
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/transforms.py
```

Observed exit code: 0. Output: `Success: no issues found in 1 source file`

```bash
uv run pytest tests/core/test_transforms.py tests/core/test_inheritance_behavior.py tests/test_yaml_inheritance.py
```

Observed exit code: 0. Output summary: `63 passed, 2 warnings in 31.18s`

## What this supports or challenges

This supports the ticket acceptance criteria that the transform Complexipy hotspots were eliminated without breaking direct transform and inheritance behavior tests or focused static checks.

## Limits

This is focused verification for `transforms.py` and directly related transform/inheritance tests. It is not a full repository verification run.
