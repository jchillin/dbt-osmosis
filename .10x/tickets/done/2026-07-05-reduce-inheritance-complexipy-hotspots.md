Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce inheritance Complexipy hotspots

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/inheritance.py` without changing column metadata inheritance, progenitor tracking, override behavior, skipped-meta filtering, placeholder cleanup, tag/meta merge order, or versioned model YAML behavior.

In scope:

- Extract focused helpers from `_filter_skipped_inherited_meta_keys`.
- Extract focused helpers from `_clean_graph_edge`.
- Extract focused helpers from `_merge_graph_node_data`.
- Extract focused helpers from `_build_column_knowledge_graph`.
- Verify with Complexipy, Ruff, ty, mypy, and inheritance-focused tests.

Out of scope:

- Changing inheritance precedence or which ancestor wins.
- Changing progenitor override semantics.
- Changing schema/YAML read/write behavior.
- Adding Complexipy baselines, snapshots, ratchets, ignored functions, or higher thresholds.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/inheritance.py --failed --plain --sort desc` exits zero.
- ACC-002: Knowledge-graph and inheritance behavior tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy scores for `src/dbt_osmosis/core/inheritance.py`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `_build_column_knowledge_graph` at 50, `_merge_graph_node_data` at 23, `_filter_skipped_inherited_meta_keys` at 19, and `_clean_graph_edge` at 16.
- 2026-07-05: Split skipped-meta filtering, graph-edge cleanup, tag/meta/config merge behavior, local-origin processing, ancestor resolution, inherited-column processing, and graph-builder orchestration into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/inheritance.py`.
- 2026-07-05: Focused knowledge-graph and inheritance behavior tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-inheritance-complexipy.md`
- `.10x/reviews/2026-07-05-inheritance-complexipy.md`
