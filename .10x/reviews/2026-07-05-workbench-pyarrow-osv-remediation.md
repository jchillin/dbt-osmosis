Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Target: src/dbt_osmosis/workbench/requirements.txt
Verdict: pass

# Workbench PyArrow OSV Remediation Review

## Target

The one-line requirements change from `pyarrow>=17.0.0` to `pyarrow>=23.0.1`, plus the package metadata test expectation update.

## Findings

- No significant issue found. The new lower bound matches the first fixed version for the advisory observed during OSV verification.
- No dependency-resolution regression found. The requirements resolve on Python 3.10 when pointed at the locally built `dbt-osmosis==1.5.0` artifact and select `pyarrow==24.0.0`.
- No test guard drift found. `tests/test_package_metadata.py` now asserts the safer lower bound.

## Residual Risk

OSV scanning of the full repository must use a release-aware approach before publication because `dbt-osmosis==1.5.0` is intentionally not yet available from PyPI. This is release timing, not a dependency vulnerability.

## Verdict

Pass.
