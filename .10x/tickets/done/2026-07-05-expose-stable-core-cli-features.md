Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Expose Stable Core Features Through CLI

## Scope

Audit maintained `src/dbt_osmosis/core/` feature modules and expose stable, tested, user-meaningful capabilities through `dbt-osmosis` CLI commands where no existing command already provides access.

The source-backed feature candidates for this pass are:

- `core.migration`: migration SQL/JSON/Markdown planning from schema diff results.
- `core.validation`: dry-run model compile/execute validation reports.
- `core.generators.check_documentation`: documentation completeness checks.
- `core.voice_learning`: documentation style/profile analysis.

## Acceptance Criteria

- Migration planning is reachable from the CLI and reuses schema diff selection/options.
- Model validation is reachable from the CLI and exits non-zero when validations fail.
- Documentation completeness checking is reachable from the CLI and exits non-zero when gaps fail the configured threshold.
- Documentation style analysis is reachable from the CLI and can print prompt context or structured profile data.
- Main CLI help and docs list the newly exposed surfaces.
- Focused CLI tests cover command discovery, option plumbing, output behavior, and non-zero failure paths.
- Formatting, linting, type checks, focused tests, and release-publish checks pass before closure.
- Changie is used for the release note sequence before tagging: add this change, batch the release, merge the changelog, and verify `CHANGELOG.md`.
- Commit, tag, push, and create a GitHub release after verification.

## Explicit Exclusions

- Do not expose internal helper modules or private functions as public CLI behavior.
- Do not change the semantics of schema diffing, migration SQL generation, model validation, documentation checking, or style analysis beyond thin CLI orchestration.
- Do not expose experimental SQL proxy behavior as a supported CLI surface.
- Do not add new external dependencies.

## Evidence Expectations

- Record final command outputs in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.
- Move this ticket to `.10x/tickets/done/` only after evidence and review support the acceptance criteria.

## References

- `src/dbt_osmosis/cli/main.py`
- `src/dbt_osmosis/core/migration.py`
- `src/dbt_osmosis/core/validation.py`
- `src/dbt_osmosis/core/generators.py`
- `src/dbt_osmosis/core/voice_learning.py`
- `tests/core/test_cli.py`
- `tests/core/test_migration.py`
- `tests/core/test_model_validation.py`
- `tests/core/test_voice_learning.py`
- `docs/docs/reference/cli.md`
- `README.md`
- `.changie.yaml`
- `.changes/`
- `CHANGELOG.md`

## Dependencies

None.

## Blockers

None.

## Progress and Notes

- 2026-07-05: Audited current CLI and core modules. Existing CLI covers YAML refactor/document/organize, SQL compile/run, schema diff, generation, SQL lint, test suggestions, LLM config, and workbench. Maintained core features without direct CLI exposure are migration planning, model validation, documentation completeness checking, and documentation style analysis.
- 2026-07-05: User added a release constraint: use Changie before the release commit/tag. Local Changie is installed. `CHANGELOG.md` contains `1.4.0`, but `.changes/` lacks `1.4.0.md`, so the release path must first restore Changie version-file continuity without moving the existing `v1.4.0` tag.
- 2026-07-05: Implemented `migration plan`, `validate models`, and `analyze docs/style/discover` CLI surfaces, updated README and Docusaurus CLI docs, and added focused CLI tests for discovery, option plumbing, output behavior, and non-zero failure paths.
- 2026-07-05: Restored Changie `1.4.0` version-file continuity, removed stale unreleased fragments already represented in `1.4.0`, batched `1.5.0`, and merged `CHANGELOG.md`.
- 2026-07-05: Release verification found a direct workbench `pyarrow` OSV finding. Opened and closed `.10x/tickets/done/2026-07-05-remediate-workbench-pyarrow-osv.md`; evidence is `.10x/evidence/2026-07-05-workbench-pyarrow-osv-remediation.md`.
- 2026-07-05: Closure evidence is `.10x/evidence/2026-07-05-core-cli-exposure-release.md`; closure review is `.10x/reviews/2026-07-05-core-cli-exposure-release.md`. Acceptance criteria are satisfied, and release commit/tag/push may proceed.
