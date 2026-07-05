Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Target: src/dbt_osmosis/core/node_filters.py
Verdict: pass

# Node Filters Complexipy Refactor Review

## Target

Review of the refactor that reduced Complexipy failures in `src/dbt_osmosis/core/node_filters.py`.

## Assumptions Tested

- File matching still accepts node-name stem matches, directory ancestry matches, and SQL/YAML file matches.
- Topological sorting still builds parent-to-child edges from `depends_on_nodes` and raises on cycles.
- Candidate selection still keeps only models, sources, and seeds; excludes external packages by default; excludes ephemeral models; and applies model path plus FQN filters.
- SQL lint still receives the expected filtered node set.
- The change did not add a metric baseline, threshold increase, ratchet, ignore marker, or other tool bypass.

## Findings

No blocking findings.

## Verdict

Pass. Evidence in `.10x/evidence/2026-07-05-node-filters-complexipy.md` supports the ticket acceptance criteria.

## Residual Risk

Repository-wide Complexipy still has unrelated hotspots. Those remain outside this completed node-filter ticket and need their own direct fixes.
