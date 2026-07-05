Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-final-deep-quality-sweep.md

# Final deep quality sweep evidence

## What Was Observed

The final deep quality sweep on rewritten `main` produced this metric vector:

```text
branch: main
head_before_final_record_commit: cb062945a8a2873a98e16584e1f814b9058b2dea
ruff_format_drift: 0
ruff_lint_errors: 0
ty_errors: 0
mypy_errors: 0
basedpyright_errors: 0
tach_violations: not configured
pytest_xdist_randomized: 963 passed, 15 skipped, 38 warnings
pytest_coverage: 963 passed, 15 skipped, 2 warnings
coverage_total: 73.65%
radon_max_cc: 21, rank D, tests/core/test_settings.py::TestYamlRefactorSettings.test_default_settings
radon_average_cc: 3.414
radon_rank_counts: A=1857, B=271, C=44, D=1
radon_halstead_effort_total: 494246.690
complexipy_over_threshold_count: 0
vulture_full_high_confidence_count: 0
vulture_source_high_confidence_count: 0
deptry_issues: 0
pydoclint_violations: 0
semgrep_default_findings: 0
semgrep_security_audit_findings: 0
codeql_python_security_and_quality_findings: 0
uv_audit_vulnerabilities: 0
osv_vulnerabilities: 0
npm_audit_docs_vulnerabilities: 0
gitleaks_dir_findings: 0
gitleaks_git_findings: 0
jscpd_source_clones: 50
jscpd_source_duplicated_lines: 669
jscpd_source_duplicated_percent: 2.89%
jscpd_full_clones: 280
jscpd_full_duplicated_lines: 4441
jscpd_full_duplicated_percent: 5.45%
pytest_benchmark: no benchmark tests discovered
scalene_memray: not run; no benchmark regression, leak, or performance investigation target remained
```

## Procedure

- Confirmed `main` was the working branch and aligned with `origin/main` before starting the sweep.
- Ran project-wide static gates:

```text
uvx ruff==0.15.17 format --check .
uvx ruff==0.15.17 check .
uv run --no-sync --with ty ty check
uv run --no-sync --with mypy mypy .
uv run --no-sync basedpyright --level error
```

All exited 0.

- Ran randomized/timeout/xdist pytest:

```text
uv run --no-sync --with pytest-randomly --with pytest-timeout --with pytest-xdist pytest -q -n auto --timeout=300
```

Final result: 963 passed, 15 skipped, 38 warnings.

- Ran serial coverage:

```text
COVERAGE_FILE=/tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/.coverage-final \
  uv run --no-sync --with pytest-timeout coverage run --branch -m pytest -q --timeout=300
COVERAGE_FILE=/tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/.coverage-final \
  uv run --no-sync coverage report --show-missing
COVERAGE_FILE=/tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/.coverage-final \
  uv run --no-sync coverage json -o /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/coverage-final.json
```

Final result: 963 passed, 15 skipped, 2 warnings; total coverage 73.65%.

- Ran complexity and dead-code tools:

```text
uv run --no-sync --with radon radon cc src tests -s -a -j
uv run --no-sync --with radon radon mi src tests -s -j
uv run --no-sync --with radon radon raw src tests -s -j
uv run --no-sync --with radon radon hal src tests -j
uv run --no-sync --with complexipy complexipy . --failed --plain --sort desc
uv run --no-sync --with vulture vulture src tests --min-confidence 80
uv run --no-sync --with vulture vulture src --min-confidence 80
```

Radon metrics are in the metric vector. Complexipy and both Vulture passes exited 0.

- Ran dependency hygiene and documentation consistency:

```text
uv run --no-sync --with deptry deptry .
uv run --no-sync --with pydoclint pydoclint src tests
```

Both exited 0.

- Ran Semgrep:

```text
uv run --no-sync --with semgrep semgrep scan --config p/default --error --json --output /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/semgrep-default-final.json .
uv run --no-sync --with semgrep semgrep scan --config p/security-audit --error --json --output /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/semgrep-security-final.json .
```

Both exited 0 with 0 findings.

- Ran supply-chain and secret scans:

```text
uv audit --frozen
osv-scanner scan source -r . --format json --output /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/osv-final.json
npm --prefix docs audit --json > /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/npm-audit-final.json
gitleaks dir --no-banner --redact --report-format json --report-path /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/gitleaks-dir-final.json .
gitleaks git --no-banner --redact --report-format json --report-path /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/gitleaks-git-final-cleanrefs.json .
```

All final scans exited 0 with 0 vulnerabilities or findings.

- Ran CodeQL:

```text
codeql database create /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/codeql-db-after-catalog-fix --language=python --source-root . --overwrite
codeql database analyze /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/codeql-db-after-catalog-fix codeql/python-queries:codeql-suites/python-security-and-quality.qls --format=sarif-latest --output=/tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/codeql-after-catalog-fix.sarif
```

Final SARIF result count: 0.

- Ran duplication scans:

```text
jscpd src --reporters json,console --output /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/jscpd-src-final --ignore "**/__pycache__/**"
jscpd . --reporters json,console --output /tmp/dbt-osmosis-ai-quality/final-sweep-2026-07-05/jscpd-full-final --ignore "**/.venv/**,**/.git/**,**/__pycache__/**,**/.mypy_cache/**,**/.ruff_cache/**,**/reports/**,**/target/**,**/docs/build/**"
```

Both exited 0. Source-only duplication improved during the sweep from 55 clones / 3.25% duplicated lines to 50 clones / 2.89% duplicated lines. Full-repo duplication improved from 285 clones / 5.55% duplicated lines to 280 clones / 5.45% duplicated lines.

## Fixes Performed

- Converted side-effect-only pytest fixture parameters to explicit `pytestmark = pytest.mark.usefixtures("fresh_caches")`, removing Vulture false-positive unused parameters without disabling the fixture behavior.
- Replaced unused catch-all lambda names with leading-underscore names where the parameter is intentionally ignored.
- Kept the private `_get_setting_for_node` compatibility export alive through real `__all__` construction instead of a Vulture suppression.
- Extracted helpers in `tests/core/test_demo_fixture_support.py`, `tests/core/test_sync_operations.py`, and `tests/support.py` to reduce full-repo Complexipy findings to zero.
- Collapsed repeated CLI project-context and SQL-linter setup in `src/dbt_osmosis/cli/main.py`, reducing jscpd source duplication.
- Replaced Protocol method `...` bodies in `src/dbt_osmosis/core/catalog_operations.py` with explicit `raise NotImplementedError`, clearing CodeQL `py/ineffectual-statement`.
- Rewrote local git history with `git-filter-repo --path .loom --invert-paths` to remove historical `.loom/*/manifest.json` secret-scan findings. The current tree did not contain those files.

## What This Supports Or Challenges

This supports closing the final deep quality sweep ticket: every hard gate from the attached procedure that is available and applicable exits zero in the final state. The remaining nonzero-looking metrics are metrics, not failing gates: Radon still has one rank-D test method made of explicit default-value assertions, and jscpd still reports duplicated command-option/test/record patterns. The sweep reduced the actionable jscpd source metric without introducing baselines or suppressions.

## Limits

Tach was not run because no Tach configuration exists and the procedure forbids `tach init` as an automatic baseline. `pytest-benchmark` was not run because no benchmark tests were discovered. Scalene and Memray were not run because no benchmark regression, leak, allocation, or hot-path performance question remained after the functional/security sweep.
