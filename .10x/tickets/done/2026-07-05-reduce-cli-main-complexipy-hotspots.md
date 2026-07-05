Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce CLI main Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/cli/main.py` so Complexipy no longer reports the remaining CLI hotspots:

- `lint_project_command`
- `_output_diff_text`
- `suggest`
- `lint_file`
- `lint_model_command`
- `_output_as_table`
- `model`
- `nl_generate_deprecated`
- `_output_diff_markdown`
- `generate_query`
- `query`
- `staging`

Preserve CLI command names, options, outputs materially covered by tests, generated file safety checks, diff severity filtering, test suggestion AI/pattern behavior, and lint exit-code behavior.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/cli/main.py --failed --plain --sort desc` exits zero.
- Repo-wide `uv run --no-sync --with complexipy complexipy src/dbt_osmosis --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/cli/main.py` pass.
- CLI, generation, SQL lint, test suggestion, and diff-focused tests pass.
- Existing overwrite/path guards for generated SQL/YAML, deprecated `nl generate` behavior, workbench launch behavior, diff output formats, test-suggestion status messages, and lint nonzero exit behavior remain unchanged.

## Explicit Exclusions

- Do not change Click command names, option names, or public command grouping.
- Do not change generation safety policy or schema writer behavior.
- Do not change lint rule semantics.
- Do not add new LLM behavior.

## Evidence Expectations

- Record CLI-file and repo-wide Complexipy, static check, and focused pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/cli/main.py`
- `tests/core/test_cli.py`
- `tests/core/test_cli_generate_group.py`
- `tests/core/test_sql_lint.py`
- `tests/core/test_test_suggestions.py`
- `tests/core/test_diff.py`
- `AGENTS.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Repo-wide Complexipy reports only `src/dbt_osmosis/cli/main.py` failures: `lint_project_command` 38, `_output_diff_text` 30, `suggest` 27, `lint_file` 23, `lint_model_command` 23, `_output_as_table` 22, `model` 22, `nl_generate_deprecated` 22, `_output_diff_markdown` 21, `generate_query` 16, `query` 16, and `staging` 16.
- 2026-07-05: Extracted shared helpers for manifest source discovery, model/query generation output, staging output preparation, diff filtering/rendering, test suggestion selection/output, suggestion table formatting, and lint result rendering/exit handling.
- 2026-07-05: Verified `src/dbt_osmosis/cli/main.py` and repo-wide Complexipy exit zero; focused static checks and CLI/generation/lint/test-suggestion/diff tests pass. Evidence: `.10x/evidence/2026-07-05-cli-main-complexipy.md`. Review: `.10x/reviews/2026-07-05-cli-main-complexipy.md`.
