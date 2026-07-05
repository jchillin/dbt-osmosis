Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce discovery Complexipy hotspot

## Scope

Refactor `src/dbt_osmosis/core/discovery.py::discover_undocumented_models` so Complexipy no longer reports it while preserving existing documentation discovery behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/discovery.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/discovery.py` pass.
- Focused tests that exercise discovery-adjacent dbt context behavior pass.
- No user-visible discovery scoring, filtering, output shape, or counter semantics are intentionally changed.

## Explicit Exclusions

- Do not redesign documentation coverage semantics.
- Do not change priority scoring.
- Do not add new CLI behavior.
- Do not normalize or reinterpret the existing column counter behavior.

## Evidence Expectations

- Record Complexipy, static check, and focused test results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/discovery.py`
- `AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `discover_undocumented_models` at score 16.
- 2026-07-05: Extracted scan eligibility, model gap construction, and documented-column counting helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-discovery-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-discovery-complexipy.md`.
