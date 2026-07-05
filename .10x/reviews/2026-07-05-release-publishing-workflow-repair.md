Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Target: .github/workflows/release.yml
Verdict: pass

# Release Publishing Workflow Repair Review

## Target

The release workflow changes that replaced the tag-detection action with explicit shell logic and changed PyPI publishing to use `pypa/gh-action-pypi-publish@v1.13.0`.

## Findings

- No significant issue found in tag safety. Existing tags are accepted only when they already point at the tested commit, and mismatched tags remain blocking when a package version changes.
- No significant issue found in non-release pushes. When the version is unchanged and the existing version tag belongs to an older release commit, the workflow skips publishing and builds a development artifact instead of failing.
- No significant issue found in action resolution. The final release workflow run reached and completed PyPI publishing successfully.
- No significant issue found in release state. `v1.5.0` is non-draft, the remote tag peels to the final release commit, and installing `dbt-osmosis==1.5.0` from PyPI prints version `1.5.0`.

## Residual Risk

The workflow still performs a full release-candidate validation after every successful main-branch Tests workflow, even for non-version pushes. That is pre-existing behavior and was not changed beyond avoiding false tag failures.

## Verdict

Pass.
