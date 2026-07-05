Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Target: src/dbt_osmosis/core/node_yaml.py
Verdict: pass

# Node YAML Complexipy Refactor Review

## Target

Review of the refactor that reduced Complexipy failures in `src/dbt_osmosis/core/node_yaml.py`.

## Assumptions Tested

- Source nodes still read `original_file_path`, match source name, then table name.
- Model and seed nodes still require `patch_path` and select by resource section plus node name.
- Model nodes still prefer a versioned model YAML view when one applies.
- Returned YAML views remain read-only `MappingProxyType` instances.
- The change did not add a metric baseline, threshold increase, ratchet, ignore marker, or other tool bypass.

## Findings

No blocking findings.

## Verdict

Pass. Evidence in `.10x/evidence/2026-07-05-node-yaml-complexipy.md` supports the ticket acceptance criteria.

## Residual Risk

Repository-wide Complexipy still has unrelated hotspots. Those remain outside this completed node-yaml ticket and need their own direct fixes.
