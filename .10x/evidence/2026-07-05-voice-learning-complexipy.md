Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-reduce-voice-learning-complexipy-hotspots.md

# Voice Learning Complexipy Evidence

## What Was Observed

`src/dbt_osmosis/core/voice_learning.py` was refactored to split phrase candidate extraction, tone marker counting, documentation sample collection, style profile assembly, and style example formatting into focused helpers. The focused Complexipy command exits zero for the file.

## Procedure

From repository root:

```bash
uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/voice_learning.py --failed --plain --sort desc
uvx ruff==0.15.17 check src/dbt_osmosis/core/voice_learning.py
uvx ruff==0.15.17 format --check src/dbt_osmosis/core/voice_learning.py
uv run --no-sync --with ty ty check src/dbt_osmosis/core/voice_learning.py --output-format concise
uv run --no-sync --with mypy mypy src/dbt_osmosis/core/voice_learning.py
uv run pytest tests/core/test_voice_learning.py
```

## Results

- Complexipy: exit 0, no failed functions reported for `src/dbt_osmosis/core/voice_learning.py`.
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- ty: `All checks passed!`
- mypy: `Success: no issues found in 1 source file`.
- Pytest: `47 passed, 2 warnings in 10.53s`.

## What This Supports Or Challenges

Supports that voice-learning complexity was reduced without failing direct style-analysis coverage or focused static checks.

## Limits

The evidence covers deterministic style analysis helpers, not downstream LLM prompt-response behavior.
