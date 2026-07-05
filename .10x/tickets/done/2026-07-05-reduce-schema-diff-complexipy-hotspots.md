Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce schema diff Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/diff.py` so Complexipy no longer reports `SchemaDiff.compare_node` or `SchemaDiff._is_type_narrowing` while preserving schema diff behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/diff.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/diff.py` pass.
- Direct schema diff tests pass.
- Existing column comparison, rename replacement, type-change, and type-narrowing semantics remain unchanged.

## Explicit Exclusions

- Do not change fuzzy rename threshold behavior.
- Do not change output case setting behavior.
- Do not change type-family classification policy.
- Do not change migration behavior.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/diff.py`
- `tests/core/test_diff.py`
- `AGENTS.md`
- `src/dbt_osmosis/core/AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `SchemaDiff.compare_node` at score 31 and `SchemaDiff._is_type_narrowing` at score 17.
- 2026-07-05: Extracted comparison setup, add/remove, rename replacement, type-change, and type-narrowing helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and direct diff pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-schema-diff-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-schema-diff-complexipy.md`.
