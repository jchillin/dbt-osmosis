Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce schema reader Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/schema/reader.py` so Complexipy no longer reports `_normalize_managed_quote_styles` or `_read_yaml` while preserving YAML read/cache and managed quote normalization behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/schema/reader.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/schema/reader.py` pass.
- Direct schema reader/write tests that cover unmanaged preservation, managed quote normalization, cache behavior, and YAML error handling pass.
- No change to YAML section partitioning, quote preservation, cache keying, cache locking, or YAML error behavior is intentional.

## Explicit Exclusions

- Do not change writer behavior.
- Do not change schema parser partitioning behavior.
- Do not alter YAML formatting policy beyond preserving the current behavior.
- Do not replace ruamel.yaml or bypass schema helpers.

## Evidence Expectations

- Record Complexipy, static check, and focused pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/schema/reader.py`
- `tests/core/test_schema.py`
- `tests/core/test_error_handling.py`
- `AGENTS.md`
- `src/dbt_osmosis/core/AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `_normalize_managed_quote_styles` at score 30 and `_read_yaml` at score 17.
- 2026-07-05: Extracted recursive mapping/sequence normalization and YAML load/filter/cache helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and schema/error pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-schema-reader-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-schema-reader-complexipy.md`.
