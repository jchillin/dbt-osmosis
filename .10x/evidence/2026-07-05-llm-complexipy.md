Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-llm-complexipy-hotspots.md

# LLM Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/llm.py` was refactored to split retry wait-time handling, provider-specific client builders, Azure AD token acquisition, provider env validation, and documentation suggestion orchestration into focused helpers. The focused Complexipy command exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/llm.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/llm.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/llm.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/llm.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/llm.py
uv run pytest tests/core/test_llm.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/llm.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `30 passed, 9 skipped, 2 warnings in 0.13s`.

## What This Supports Or Challenges

Supports that LLM provider setup, retry, and documentation suggestion complexity was reduced without failing direct mocked-provider coverage or focused static checks.

## Limits

Azure Identity and OpenAI SDK-dependent retry tests were skipped where optional packages were unavailable; non-skipped tests cover mocked provider setup and configuration behavior.
