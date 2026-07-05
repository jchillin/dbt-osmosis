Status: done
Created: 2026-07-05
Updated: 2026-07-05
Parent: None
Depends-On: None

# Reduce model version Complexipy hotspot

## Scope

Reduce `complexipy` cognitive complexity in `src/dbt_osmosis/core/model_versions.py` without changing exact string version matching, numeric fallback rules, or parent model metadata fallback behavior.

In scope:

- Extract exact-version lookup.
- Extract numeric-fallback lookup.
- Extract parent model fallback field overlay.
- Verify with Complexipy, Ruff, ty, mypy, and focused versioned-model tests.

Out of scope:

- Changing dbt version identity semantics.
- Changing versioned YAML selection behavior.
- Adding Complexipy baselines, snapshots, ratchets, ignored functions, or higher thresholds.

## Acceptance Criteria

- ACC-001: `complexipy src/dbt_osmosis/core/model_versions.py --failed --plain --sort desc` exits zero.
- ACC-002: Focused versioned-model tests pass.
- ACC-003: Ruff, ty, and mypy remain clean for the changed file.

## Evidence Expectations

- Record before/after Complexipy score for `_versioned_model_yaml_view`.
- Record exact verification commands and exit codes.

## Progress and Notes

- 2026-07-05: Complexipy reported `_versioned_model_yaml_view` at 17.
- 2026-07-05: Split version entry extraction, exact-version lookup, equivalent-version lookup, selected-version lookup, and parent fallback overlay into focused helpers.
- 2026-07-05: Direct file-level Complexipy check now exits zero for `src/dbt_osmosis/core/model_versions.py`.
- 2026-07-05: Focused versioned-model tests pass.

## Blockers

None.

## References

- Current tool output from `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core src/dbt_osmosis/cli --failed --plain --sort desc`.
- `.10x/evidence/2026-07-05-model-version-complexipy.md`
- `.10x/reviews/2026-07-05-model-version-complexipy.md`
