Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce node filters Complexipy hotspots

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/node_filters.py` without changing resource eligibility, package filtering, ephemeral model exclusion, model path/FQN filtering, or dependency ordering.

In scope:

- Extract file/path match helpers from `_is_file_match`.
- Extract graph-building helpers from `_topological_sort`.
- Extract node eligibility helpers from `_iter_candidate_nodes`.
- Verify with Complexipy, Ruff, ty, mypy, and node-filter tests.

Out of scope:

- Changing node selection semantics.
- Changing topological ordering rules.
- Adding Complexipy baselines, snapshots, ratchets, ignored functions, or higher thresholds.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/node_filters.py --failed --plain --sort desc` exits zero.
- ACC-002: Focused node-filter tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy scores for `src/dbt_osmosis/core/node_filters.py`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `_iter_candidate_nodes` at 18, `_topological_sort` at 18, and `_is_file_match` at 16.
- 2026-07-05: Split file path matching, dependency graph construction/visitation, manifest iteration, and candidate eligibility into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/node_filters.py`.
- 2026-07-05: Focused node-filter and SQL lint tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-node-filters-complexipy.md`
- `.10x/reviews/2026-07-05-node-filters-complexipy.md`
