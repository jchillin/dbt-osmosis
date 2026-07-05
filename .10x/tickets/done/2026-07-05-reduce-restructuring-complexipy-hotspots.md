Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce restructuring Complexipy hotspots

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/restructuring.py` without changing restructure planning, confirmation, YAML merge, superseded-file cleanup, cache discard, dry-run, mutation tracking, or manifest reload behavior.

In scope:

- Extract cohesive helpers from `_create_operations_for_node`.
- Extract operation collection and deduplication helpers from `draft_restructure_delta_plan`.
- Extract confirmation, output write, superseded cleanup, and commit/reload helpers from `apply_restructure_plan`.
- Verify with Complexipy, Ruff, ty, mypy, and restructuring tests.

Out of scope:

- Changing YAML routing behavior.
- Changing schema reader/writer behavior.
- Changing confirmation prompts or dry-run semantics.
- Adding Complexipy baselines, snapshots, ratchets, ignored functions, or higher thresholds.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/restructuring.py --failed --plain --sort desc` exits zero.
- ACC-002: Focused restructuring tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy scores for `src/dbt_osmosis/core/restructuring.py`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `apply_restructure_plan` at 62, `draft_restructure_delta_plan` at 52, and `_create_operations_for_node` at 32.
- 2026-07-05: Split node lookup, new/existing operation creation, plan worker collection, operation deduplication, confirmation, operation writes, superseded-file cleanup, deletion/cache invalidation, and final commit/reload into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/restructuring.py`.
- 2026-07-05: Focused restructuring and YAML-context tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-restructuring-complexipy.md`
- `.10x/reviews/2026-07-05-restructuring-complexipy.md`
