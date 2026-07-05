Status: done
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
- 2026-07-05: Replaced release tag detection with shell logic that accepts a pre-created tag only when it points at the tested commit, preserves development-build behavior for non-version pushes, and errors on mismatched release tags when a version changed.
- 2026-07-05: Changed PyPI publishing to use `pypa/gh-action-pypi-publish@v1.13.0` and disabled attestations for token-based publishing.
- 2026-07-05: Retagged `v1.5.0` to the repaired release commit `af36c6fba4bba7f5774df5004003663773b09ab5`, pushed `main` and the tag, and verified branch/tag Tests, lint, final Release workflow, GitHub release, and PyPI install smoke. Evidence: `.10x/evidence/2026-07-05-release-publishing-workflow-repair.md`. Review: `.10x/reviews/2026-07-05-release-publishing-workflow-repair.md`.
