Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce LLM Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/llm.py` so Complexipy no longer reports `_call_with_retry`, `get_llm_client`, or `suggest_documentation_improvements` while preserving provider setup, retry, and documentation suggestion behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/llm.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/llm.py` pass.
- Direct LLM tests pass.
- Existing provider names, environment variable names, default URLs/models, error messages, Azure AD token behavior, retry-after handling, and suggestion confidence/reasoning remain unchanged.

## Explicit Exclusions

- Do not add or remove LLM providers.
- Do not change prompt text.
- Do not change OpenAI-compatible client behavior.
- Do not change optional dependency semantics.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/llm.py`
- `tests/core/test_llm.py`
- `.10x/tickets/done/2026-07-05-tighten-llm-optional-import-handling.md`
- `.10x/tickets/done/2026-07-05-stabilize-llm-optional-sdk-test-imports.md`
- `AGENTS.md`
- `src/dbt_osmosis/core/AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `get_llm_client` 36, `suggest_documentation_improvements` 23, and `_call_with_retry` 21.
- 2026-07-05: Extracted retry wait-time helpers, provider-specific client builders, Azure AD token helpers, env validation, and documentation suggestion dispatch/confidence helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and direct LLM pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-llm-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-llm-complexipy.md`.
