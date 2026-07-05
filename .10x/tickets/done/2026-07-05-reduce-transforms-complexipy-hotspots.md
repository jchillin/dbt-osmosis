Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce transforms Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/transforms.py` so Complexipy no longer reports `inherit_upstream_column_knowledge`, `inject_missing_columns`, `synchronize_data_types`, `_collect_upstream_documents`, `apply_semantic_analysis`, or `suggest_improved_documentation` while preserving transform behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/transforms.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/transforms.py` pass.
- Direct transform and inheritance behavior tests pass.
- Existing skip settings, output-case behavior, inheritance semantics, semantic-analysis error handling, upstream doc bounds, and AI suggestion threshold behavior remain unchanged.

## Explicit Exclusions

- Do not change transform pipeline semantics.
- Do not change sync/write behavior.
- Do not change LLM prompt behavior.
- Do not alter inheritance graph construction.

## Evidence Expectations

- Record Complexipy, static check, and focused pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/transforms.py`
- `tests/core/test_transforms.py`
- `tests/core/test_inheritance_behavior.py`
- `tests/test_yaml_inheritance.py`
- `AGENTS.md`
- `src/dbt_osmosis/core/AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports six transform hotspots: `inherit_upstream_column_knowledge` 35, `apply_semantic_analysis` 34, `inject_missing_columns` 32, `synchronize_data_types` 27, `suggest_improved_documentation` 26, and `_collect_upstream_documents` 19.
- 2026-07-05: Extracted behavior-preserving helpers for inheritance metadata selection, missing-column generation, data-type synchronization, upstream-document collection, semantic analysis, and AI documentation suggestions.
- 2026-07-05: Verified Complexipy exits zero for `src/dbt_osmosis/core/transforms.py`; focused static checks and transform/inheritance tests pass. Evidence: `.10x/evidence/2026-07-05-transforms-complexipy.md`. Review: `.10x/reviews/2026-07-05-transforms-complexipy.md`.
