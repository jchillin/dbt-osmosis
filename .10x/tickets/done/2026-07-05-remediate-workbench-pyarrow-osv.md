Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Remediate Workbench PyArrow OSV Finding

## Scope

Tighten the Streamlit workbench deployment requirements so OSV no longer reports the 2026 Apache Arrow advisory against the direct `pyarrow` lower bound.

## Acceptance Criteria

- `src/dbt_osmosis/workbench/requirements.txt` requires a `pyarrow` version at or above the first fixed version for the reported advisory.
- Workbench requirements still resolve.
- OSV no longer reports vulnerabilities sourced from `src/dbt_osmosis/workbench/requirements.txt`.
- Package metadata tests still pass.

## Explicit Exclusions

- Do not redesign workbench dependency management.
- Do not change root package dependencies unless required by verification.

## Evidence Expectations

- Record the requirements diff, OSV result, resolution check, and package metadata test result.

## References

- `src/dbt_osmosis/workbench/requirements.txt`
- `.10x/tickets/done/2026-07-05-remediate-workbench-requirements-osv-vulnerabilities.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Release verification found OSV records for `pyarrow 17.0.0` from `src/dbt_osmosis/workbench/requirements.txt`. The advisory is fixed in `23.0.1`.
- 2026-07-05: Tightened the workbench requirement to `pyarrow>=23.0.1`, updated the package metadata guard, and verified OSV, Python 3.10 resolution with the local release wheel, package metadata tests, and Ruff. Evidence: `.10x/evidence/2026-07-05-workbench-pyarrow-osv-remediation.md`. Review: `.10x/reviews/2026-07-05-workbench-pyarrow-osv-remediation.md`.
