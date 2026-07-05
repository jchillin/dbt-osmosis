Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce workbench main Complexipy hotspot

## Scope

Refactor `src/dbt_osmosis/workbench/app.py` so Complexipy no longer reports `main` while preserving Streamlit workbench initialization, `st.session_state.app` ownership, dashboard composition, feed opt-in behavior, and hotkey registration.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/workbench/app.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/workbench/app.py` pass.
- `tests/core/test_workbench_app.py`, `tests/workbench/test_ai_assistant.py`, and relevant CLI workbench tests pass.
- Workbench state remains under `st.session_state.app`; dashboard items keep their initial-state transfer; existing hotkeys and feed opt-in behavior remain unchanged.

## Explicit Exclusions

- Do not redesign Streamlit UI or dashboard layout.
- Do not wire the AI assistant into real writeback behavior.
- Do not change external feed security behavior.
- Do not change CLI workbench launch behavior.

## Evidence Expectations

- Record Complexipy, static check, and focused pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/workbench/app.py`
- `src/dbt_osmosis/workbench/components/dashboard.py`
- `tests/core/test_workbench_app.py`
- `tests/workbench/test_ai_assistant.py`
- `tests/core/test_cli.py`
- `AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Repo-wide Complexipy reports `src/dbt_osmosis/workbench/app.py main` at 18.
- 2026-07-05: Extracted helpers for dashboard app construction, component initial state transfer, workbench path/query initialization, app retrieval, hotkeys, and dashboard rendering.
- 2026-07-05: Verified Complexipy exits zero for `src/dbt_osmosis/workbench/app.py`; focused static checks, workbench tests, AI assistant tests, and CLI workbench tests pass. Evidence: `.10x/evidence/2026-07-05-workbench-main-complexipy.md`. Review: `.10x/reviews/2026-07-05-workbench-main-complexipy.md`.
