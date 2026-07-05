Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-repair-release-publishing-workflow.md

# Release Publishing Workflow Repair Evidence

## What Was Observed

Publishing `v1.5.0` exposed two release workflow defects after the release candidate had already validated:

- The workflow attempted to create `v1.5.0` even when the tag had already been intentionally created before push.
- `pypa/gh-action-pypi-publish` was referenced by the annotated tag object SHA for `v1.13.0`, which made the action try to pull a non-existent container tag.

The workflow now detects release tags in shell:

- If the current version tag already points at the tested commit, it publishes with that tag.
- If the tag exists elsewhere and the package version changed, it fails before publishing.
- If the tag exists elsewhere and the package version did not change, it treats the push as a development build.
- If the version changed and no tag exists, it creates the annotated tag.

The PyPI publish action now uses `pypa/gh-action-pypi-publish@v1.13.0`, with attestations disabled because the workflow publishes with a PyPI token rather than Trusted Publishing.

## Procedure

Commands and remote checks used:

```text
pre-commit run --all-files
git tag -d v1.5.0
git tag -a v1.5.0 -m "Release v1.5.0"
git push origin main +refs/tags/v1.5.0:refs/tags/v1.5.0
gh run list --commit af36c6fba4bba7f5774df5004003663773b09ab5 --limit 10 --json ...
gh run list --workflow Release --limit 5 --json ...
gh release view v1.5.0 --json tagName,name,isDraft,isPrerelease,publishedAt,targetCommitish,url,body
git ls-remote --tags origin v1.5.0 'v1.5.0^{}'
uvx --from dbt-osmosis==1.5.0 dbt-osmosis --version
```

## Results

- Pre-commit exited 0, including actionlint.
- `main` and the peeled `v1.5.0` tag both point at `af36c6fba4bba7f5774df5004003663773b09ab5`.
- Branch push checks for `af36c6fb` passed:
  - `lint`: success.
  - `Tests` on `main`: success.
  - `Tests` on `v1.5.0`: success.
  - `Labeler`: success.
- Release workflow run `28739505387` passed:
  - `Validate release candidate`: success.
  - `Tag and publish release`: success.
- GitHub release `v1.5.0` is non-draft, non-prerelease, and published at `2026-07-05T11:53:52Z`.
- GitHub release URL: `https://github.com/z3z1ma/dbt-osmosis/releases/tag/v1.5.0`.
- PyPI install smoke exited 0: `uvx --from dbt-osmosis==1.5.0 dbt-osmosis --version` printed `dbt-osmosis, version 1.5.0`.

## What This Supports Or Challenges

This supports closing the release-publishing workflow repair ticket: the workflow now accepts the user-required tag-before-push release path, publishes successfully, and leaves the final GitHub release and PyPI package visible.

## Limits

The GitHub release body is owned by Release Drafter and intentionally points to `CHANGELOG.md` for the full change list. Historical failed release workflow attempts remain visible in GitHub Actions, but the final run for `af36c6fb` is green.
