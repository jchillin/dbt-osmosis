Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce sync operations Complexipy hotspots

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/sync_operations.py` without changing YAML sync behavior, duplicate-entry fail-closed behavior, source/table matching, version identity semantics, grouped writes, or schema writer usage.

In scope:

- Extract focused helpers from `_get_or_create_source`.
- Extract focused helpers from `_deduplicate_versions`.
- Extract focused helpers from `_validate_no_duplicate_sync_entries`.
- Verify with Complexipy, Ruff, ty, mypy, and sync-operation tests.

Out of scope:

- Changing source matching semantics or ambiguity behavior.
- Changing duplicate model/source/version safety errors.
- Changing YAML read/write/cache behavior.
- Adding Complexipy baselines, snapshots, ratchets, ignored functions, or higher thresholds.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/sync_operations.py --failed --plain --sort desc` exits zero.
- ACC-002: Focused sync-operation tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy scores for `src/dbt_osmosis/core/sync_operations.py`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `_get_or_create_source` at 50, `_validate_no_duplicate_sync_entries` at 17, and `_deduplicate_versions` at 16.
- 2026-07-05: Split source table scanning/matching/disambiguation, version duplicate indexing, and sync-entry duplicate validation into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/sync_operations.py`.
- 2026-07-05: Focused sync-operation and inheritance sync tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-sync-operations-complexipy.md`
- `.10x/reviews/2026-07-05-sync-operations-complexipy.md`
