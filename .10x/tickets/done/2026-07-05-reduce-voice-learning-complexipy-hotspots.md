Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce voice learning Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/voice_learning.py` so Complexipy no longer reports `_extract_common_phrases`, `_detect_tone_markers`, `analyze_project_documentation_style`, or `extract_style_examples` while preserving style analysis behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/voice_learning.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/voice_learning.py` pass.
- Direct voice learning tests pass.
- Existing phrase extraction, tone marker counting, style sample collection, and example formatting remain unchanged.

## Explicit Exclusions

- Do not change prompt wording.
- Do not change similarity scoring.
- Do not add new tone or terminology rules.
- Do not change LLM integration behavior.

## Evidence Expectations

- Record Complexipy, static check, and direct pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/voice_learning.py`
- `tests/core/test_voice_learning.py`
- `AGENTS.md`
- `src/dbt_osmosis/core/AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Complexipy reports four voice-learning hotspots: `extract_style_examples` 20, `_detect_tone_markers` 19, `analyze_project_documentation_style` 19, and `_extract_common_phrases` 16.
- 2026-07-05: Extracted phrase candidate, tone marker, documentation sample, style profile, and example formatting helpers.
- 2026-07-05: Focused Complexipy, Ruff, ty, mypy, and direct voice-learning pytest checks pass. Evidence recorded in `.10x/evidence/2026-07-05-voice-learning-complexipy.md`; closure review recorded in `.10x/reviews/2026-07-05-voice-learning-complexipy.md`.
