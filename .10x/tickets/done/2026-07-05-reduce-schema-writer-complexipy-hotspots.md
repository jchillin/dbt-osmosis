Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce schema writer Complexipy hotspots

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/schema/writer.py` without changing atomic write behavior, no-clobber behavior, dry-run mutation tracking, preserved-section merging, cache discard, file mode preservation, or written-file tracking.

In scope:

- Extract shared rendering, comparison, temp-write validation, cache discard, and mutation tracking helpers from `_write_yaml`.
- Reuse the same safe write helpers from `commit_yamls`.
- Verify with Complexipy, Ruff, ty, mypy, schema writer tests, and sync writer tests.

Out of scope:

- Changing YAML formatting semantics.
- Changing schema reader cache internals.
- Changing atomic write/no-clobber safety guarantees.
- Adding Complexipy baselines, snapshots, ratchets, ignored functions, or higher thresholds.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/schema/writer.py --failed --plain --sort desc` exits zero.
- ACC-002: Focused schema writer tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy scores for `src/dbt_osmosis/core/schema/writer.py`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `commit_yamls` at 45 and `_write_yaml` at 40.
- 2026-07-05: Split preserved-section merging, cached path/data reads, YAML rendering, temp-write validation, temp install, mutation tracking, cache discard, and single-path commit behavior into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/schema/writer.py`.
- 2026-07-05: Focused schema writer, sync writer, and restructure writer tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-schema-writer-complexipy.md`
- `.10x/reviews/2026-07-05-schema-writer-complexipy.md`
