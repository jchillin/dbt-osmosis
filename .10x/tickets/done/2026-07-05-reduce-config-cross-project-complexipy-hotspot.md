Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce config cross-project Complexipy hotspot

## Scope

Refactor `src/dbt_osmosis/core/config.py::_add_cross_project_references` so Complexipy no longer reports it while preserving dbt-loom exposed-model import behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/config.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/config.py` pass.
- Direct config tests pass, including dbt-loom exposed model import coverage.
- Existing eligibility behavior remains: import nodes with `access` set, `access != "protected"`, and `resource_type == "model"`.

## Explicit Exclusions

- Do not change dbt project context creation behavior.
- Do not change adapter binding or manifest reload behavior.
- Do not add new dbt-loom semantics.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/config.py`
- `tests/core/test_config.py`
- `AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `_add_cross_project_references` at score 27.
- 2026-07-05: Extracted dbt-loom manifest loading, exposed-model filtering, parsing, and merge helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and direct pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-config-cross-project-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-config-cross-project-complexipy.md`.
