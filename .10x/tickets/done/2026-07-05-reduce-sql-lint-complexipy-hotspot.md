Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce SQL lint Complexipy hotspot

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/sql_lint.py` for `KeywordCapitalizationRule.__call__` without changing keyword detection, expected-case selection, violation position reporting, or fixes.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/sql_lint.py --failed --plain --sort desc` exits zero.
- ACC-002: SQL lint tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy score for `KeywordCapitalizationRule.__call__`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `KeywordCapitalizationRule.__call__` at 17.
- 2026-07-05: Split keyword regex construction, case counting, expected-case selection, fix calculation, and violation construction into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/sql_lint.py`.
- 2026-07-05: SQL lint tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-sql-lint-complexipy.md`
- `.10x/reviews/2026-07-05-sql-lint-complexipy.md`
