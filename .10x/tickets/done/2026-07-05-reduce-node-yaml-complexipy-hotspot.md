Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce node YAML Complexipy hotspot

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/node_yaml.py` without changing source YAML lookup, model/seed YAML lookup, versioned model view selection, or read-only return behavior.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/node_yaml.py --failed --plain --sort desc` exits zero.
- ACC-002: Focused node YAML and inheritance/sync tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy score for `_get_node_yaml`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `_get_node_yaml` at 18.
- 2026-07-05: Split source node lookup, model/seed node lookup, and read-only wrapping into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/node_yaml.py`.
- 2026-07-05: Focused node YAML, inheritance, and sync tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-node-yaml-complexipy.md`
- `.10x/reviews/2026-07-05-node-yaml-complexipy.md`
