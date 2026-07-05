Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/2026-07-05-remediate-workbench-pyarrow-osv.md

# Workbench PyArrow OSV Remediation Evidence

## What Was Observed

Release verification found OSV records sourced from `src/dbt_osmosis/workbench/requirements.txt` for `pyarrow 17.0.0`. The reported advisory affects Apache Arrow through `23.0.0` and is fixed in `23.0.1`.

The workbench requirements lower bound was tightened from `pyarrow>=17.0.0` to `pyarrow>=23.0.1`.

## Procedure

Commands run from repository root:

```text
osv-scanner scan source src/dbt_osmosis/workbench --no-resolve --format json --output-file /tmp/dbt-osmosis-osv-workbench-after-pyarrow-2026-07-05.json
uv pip compile src/dbt_osmosis/workbench/requirements.txt --python-version 3.10 --find-links /tmp/dbt-osmosis-release-build-2026-07-05 -o /tmp/dbt-osmosis-workbench-requirements-py310-2026-07-05.txt
uv run pytest tests/test_package_metadata.py -q
uvx ruff==0.15.17 check tests/test_package_metadata.py
uvx ruff==0.15.17 format --check tests/test_package_metadata.py
```

The compile command uses the locally built `dbt_osmosis-1.5.0` wheel because the release version is not available on PyPI until after publication.

## Results

- OSV workbench scan exited 0. Parsed result: `{"results":0,"vulnerabilities":0}`.
- Python 3.10 workbench requirements resolution exited 0 and selected `pyarrow==24.0.0`.
- Package metadata tests exited 0: `9 passed, 2 warnings`.
- Ruff check exited 0: `All checks passed!`
- Ruff format check exited 0: `1 file already formatted`.

## What This Supports Or Challenges

This supports closing the PyArrow remediation ticket and keeping the release gate clear: the direct workbench deployment requirements no longer permit the vulnerable Arrow range.

## Limits

The Streamlit workbench was not launched. Verification covered dependency resolution, OSV source scanning, and the package metadata guard.
