Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-expose-stable-core-cli-features.md, .10x/tickets/done/2026-07-05-remediate-workbench-pyarrow-osv.md

# Core CLI Exposure And Release Evidence

## What Was Observed

Stable core capabilities that previously had no direct CLI entrypoint are now reachable through first-class command groups:

- `dbt-osmosis migration plan` renders schema-diff-backed migration plans as SQL, JSON, or Markdown.
- `dbt-osmosis validate models` dry-runs selected models through core model validation and exits non-zero when validations fail.
- `dbt-osmosis analyze docs` checks documentation completeness and exits non-zero when configured coverage/gap requirements fail.
- `dbt-osmosis analyze style` summarizes project documentation style and can emit reusable prompt context.
- `dbt-osmosis analyze discover` reports prioritized model and column documentation gaps, with `--check` for CI-style failure.

The release was prepared as version `1.5.0`, with Changie continuity restored for the existing `1.4.0` changelog state before batching and merging the `1.5.0` changelog entry.

## Procedure

Commands run from repository root unless noted:

```text
uvx ruff==0.15.17 format --check . && uvx ruff==0.15.17 check .
uv run --no-sync --with ty ty check --output-format concise
uv run --no-sync --with mypy mypy .
uv run --no-sync basedpyright --level error
uv run --no-sync --with pydoclint pydoclint src tests
uv run --no-sync --with complexipy complexipy . --failed --plain --sort desc
uv run --no-sync --with vulture vulture src tests --min-confidence 80
uv run --no-sync --with deptry deptry .
uv run pytest tests/core/test_cli.py -q
uv run pytest tests/core/test_cli.py tests/core/test_migration.py tests/core/test_model_validation.py tests/core/test_voice_learning.py tests/core/test_generators.py -q
uv run pytest -q
npm --prefix docs run build
uv audit --frozen
npm --prefix docs audit --json
osv-scanner scan source -r . --no-resolve --format json --output-file /tmp/dbt-osmosis-osv-final-2026-07-05.json
gitleaks dir --no-banner --redact .
git diff --check
uv run --no-sync dbt-osmosis --version
uv run --no-sync dbt-osmosis --help
uv build --out-dir /tmp/dbt-osmosis-release-build-2026-07-05-final
```

Changie sequence:

```text
changie new --kind Added --body "Expose migration planning, model validation, documentation coverage, style analysis, and documentation gap discovery through first-class CLI commands."
changie batch 1.5.0
changie merge
changie latest
changie merge --dry-run
```

The Changie sequence also required restoring `.changes/1.4.0.md` from the already-published `CHANGELOG.md` section because the project had a `v1.4.0` changelog entry but no matching version file. Three stale unreleased fragments already represented in the `1.4.0` changelog were removed before batching `1.5.0`.

Security remediation procedure for the OSV `pyarrow` finding is recorded separately in `.10x/evidence/2026-07-05-workbench-pyarrow-osv-remediation.md`.

## Results

- Ruff format and lint exited 0: `356 files already formatted`; all checks passed.
- `ty` exited 0: all checks passed.
- `mypy` exited 0: no issues in 46 source files.
- `basedpyright --level error` exited 0: 0 errors, 0 warnings, 0 notes.
- `pydoclint src tests` exited 0.
- `complexipy --failed` exited 0.
- `vulture` exited 0.
- `deptry` exited 0.
- Focused CLI tests exited 0: `47 passed, 2 warnings`.
- Related core tests exited 0: `151 passed, 2 warnings`.
- Full pytest exited 0: `971 passed, 15 skipped, 2 warnings in 235.36s`.
- Docusaurus docs build exited 0.
- `uv audit --frozen` exited 0 with no known vulnerabilities.
- `npm audit` reported zero vulnerabilities.
- OSV no-resolve repository scan exited 0 with parsed counts `results=0`, `vulnerabilities=0`.
- Gitleaks exited 0 with no leaks detected.
- `git diff --check` exited 0.
- CLI version output is `dbt-osmosis, version 1.5.0`.
- CLI help includes the new `analyze`, `migration`, and `validate` groups.
- Final package build produced:
  - `/tmp/dbt-osmosis-release-build-2026-07-05-final/dbt_osmosis-1.5.0.tar.gz`
  - `/tmp/dbt-osmosis-release-build-2026-07-05-final/dbt_osmosis-1.5.0-py3-none-any.whl`
- Changie `latest` reports `1.5.0`, and `CHANGELOG.md` matches the `changie merge --dry-run` output.

## Acceptance Mapping

- Migration planning reachable from CLI: supported by `dbt-osmosis migration plan` tests and main help discovery.
- Model validation reachable from CLI with non-zero failure: supported by CLI tests covering failed validation reports.
- Documentation completeness reachable from CLI with non-zero threshold/gap behavior: supported by CLI tests covering low coverage.
- Documentation style analysis reachable from CLI with prompt-context output: supported by CLI tests covering prompt rendering and `max_nodes` plumbing.
- Documentation gap discovery reachable from CLI with CI failure mode: supported by CLI tests covering `--check`.
- Docs and release notes updated: supported by docs build, `README.md`, `docs/docs/intro.md`, `docs/docs/reference/cli.md`, and Changie `1.5.0`.

## What This Supports Or Challenges

This supports closing the CLI exposure ticket and preparing the `v1.5.0` release commit: the implementation, docs, changelog, tests, static checks, package build, and vulnerability scans agree on the final release state.

## Limits

Migration SQL generation was verified at the CLI orchestration boundary and through existing core migration tests; generated migration SQL was not executed against a live warehouse. The workbench was not launched interactively. OSV was run with `--no-resolve` for the full repository because pre-publication resolution of `dbt-osmosis==1.5.0` from PyPI is not possible before the release is published; the direct workbench `pyarrow` source finding is separately resolved and verified.
