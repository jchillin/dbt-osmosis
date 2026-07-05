Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce migration quote Complexipy hotspot

## Scope

Refactor `src/dbt_osmosis/core/migration.py::MigrationPlanner._quote_identifier` so Complexipy no longer reports it while preserving existing dialect quoting behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/migration.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/migration.py` pass.
- Direct migration tests pass.
- Existing delimiter behavior is preserved for double-quote, backtick, SQL Server bracket, and default dialect paths.

## Explicit Exclusions

- Do not change migration SQL generation semantics.
- Do not add dialects.
- Do not alter identifier splitting behavior.
- Do not introduce escaping or normalization beyond the existing behavior.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/migration.py`
- `tests/core/test_migration.py`
- `AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `MigrationPlanner._quote_identifier` at score 34.
- 2026-07-05: Extracted shared quoted-identifier part helpers and collapsed duplicate dialect branches.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and direct pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-migration-quote-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-migration-quote-complexipy.md`.
