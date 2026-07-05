Status: active
Created: 2026-07-05
Updated: 2026-07-05

# Repair Release Publishing Workflow

## Scope

Fix the GitHub Actions release workflow failure observed while publishing `v1.5.0`.

The live release workflow validated the candidate successfully, then failed in `Tag and publish release` for two release-system reasons:

- The workflow's tag-detection action tried to create `v1.5.0` even when the release tag had already been deliberately created before push.
- The PyPI publishing action was pinned to an annotated tag object SHA, causing the action to request a non-existent container image tag.

## Acceptance Criteria

- Release publishing accepts an existing version tag when it points at the tested commit.
- Release publishing still creates a version tag when the version changed and no tag exists.
- Release publishing refuses to continue when the existing tag points at a different commit.
- PyPI publishing uses an action reference that resolves to a usable published action/container.
- `v1.5.0` is retagged to the repaired release commit before push.
- GitHub release and release workflow are verified after the repair.

## Explicit Exclusions

- Do not redesign the release workflow beyond the observed failures.
- Do not change package runtime behavior.

## Evidence Expectations

- Record the failed workflow symptom, repair commands, and final GitHub release/workflow status.

## References

- `.github/workflows/release.yml`
- `https://github.com/z3z1ma/dbt-osmosis/actions/runs/28737697129`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Release attempt `28737697129` validated the candidate successfully, failed once because the workflow tried to create an already-pushed `v1.5.0` tag, and failed again because `pypa/gh-action-pypi-publish` was referenced by annotated tag object SHA and could not pull `ghcr.io/pypa/gh-action-pypi-publish:<sha>`.
