Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce test suggestions Complexipy hotspot

## Scope

Refactor `src/dbt_osmosis/core/test_suggestions.py::_get_existing_tests_for_node` so Complexipy no longer reports it while preserving manifest generic-test discovery behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/test_suggestions.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/test_suggestions.py` pass.
- Direct test suggestion tests pass, including manifest generic-test extraction coverage.
- No change to public `TestSuggestion`, `TestPatternExtractor`, or `AITestSuggester` behavior is intentional.

## Explicit Exclusions

- Do not change AI test suggestion prompting or parsing.
- Do not redesign pattern extraction.
- Do not add new test types or infer additional metadata.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/test_suggestions.py`
- `tests/core/test_test_suggestions.py`
- `AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports `_get_existing_tests_for_node` at score 18.
- 2026-07-05: Extracted manifest-test attachment detection and suggestion construction helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and direct pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-test-suggestions-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-test-suggestions-complexipy.md`.
