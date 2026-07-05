Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce schema validation Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/schema/validation.py` so Complexipy no longer reports `ModelValidator._validate_versions`, `SourceValidator._validate`, `TestConfigValidator._validate_tests`, or `TestConfigValidator._validate_columns` while preserving validation behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/schema/validation.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/schema/validation.py` pass.
- Direct validation tests pass.
- Existing validation error codes, warning codes, messages, and contexts for covered paths remain unchanged.

## Explicit Exclusions

- Do not change schema parser or writer behavior.
- Do not add new validation rules.
- Do not remove existing warnings or errors.
- Do not reinterpret dbt model version identity semantics.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/schema/validation.py`
- `tests/core/test_validation.py`
- `AGENTS.md`
- `src/dbt_osmosis/core/AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports four validation hotspots: `_validate_versions` 24, `SourceValidator._validate` 24, `_validate_tests` 19, and `_validate_columns` 18.
- 2026-07-05: Extracted column entry, test entry, model version, and source table validation helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and validation pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-schema-validation-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-schema-validation-complexipy.md`.
