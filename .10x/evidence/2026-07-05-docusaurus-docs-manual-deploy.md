Status: recorded
Created: 2026-07-05
Updated: 2026-07-05
Relates-To: .10x/tickets/done/2026-07-05-deploy-docusaurus-docs.md

# Docusaurus Docs Manual Deploy Evidence

## What Was Observed

The docs site is a Docusaurus 3 app under `docs/`. `docs/package.json` defines `deploy` as `docusaurus deploy`, and `docs/README.md` documents GitHub Pages deployment through `USE_SSH=true npm run deploy` or `GIT_USER=<username> npm run deploy`.

The local deploy was performed with Bun and Docusaurus CLI:

- Bun version: `1.3.14`.
- Node version: `v22.23.1`.
- Docusaurus version: `3.10.1`.
- GitHub Pages source: `gh-pages` branch at `/`.

## Procedure

Commands run from the repository root or `docs/` as indicated:

```text
bun install --frozen-lockfile
bun run build
USE_SSH=true CURRENT_BRANCH=main bun run deploy -- --skip-build
GIT_USER=z3z1ma GIT_PASS="$(gh auth token)" GIT_USER_NAME=z3z1ma GIT_USER_EMAIL=butler.alex2010@gmail.com CURRENT_BRANCH=main bun run deploy -- --skip-build
git fetch --no-tags origin gh-pages:refs/remotes/origin/gh-pages
curl -I -L --max-time 30 https://z3z1ma.github.io/dbt-osmosis/
curl -L --max-time 30 https://z3z1ma.github.io/dbt-osmosis/docs/reference/cli/ | rg -n "migration|validate models|analyze docs|analyze style|analyze discover"
gh api repos/z3z1ma/dbt-osmosis/pages --jq '{status:.status, html_url:.html_url, source:.source}'
```

The SSH deploy attempt cloned `gh-pages` but failed to push because the local SSH key authenticates as `alexanderbut_floqast`, which does not have push access to `z3z1ma/dbt-osmosis`. The successful deployment used the active `gh` HTTPS token for `z3z1ma`; Docusaurus obfuscated `GIT_PASS` in command logs.

## Results

- `bun install --frozen-lockfile` exited 0 and installed docs dependencies from the npm lockfile. The generated untracked `docs/bun.lock` was removed after deployment because the repo tracks `docs/package-lock.json`.
- `bun run build` exited 0 and generated static files in `docs/build`.
- HTTPS Docusaurus deploy exited 0.
- `origin/gh-pages` advanced from `ba89ebf024f629e05b9cc45b980867bec409801d` to `1a20d0d19b2456b364e1a5521b6a9c4b3221c354`.
- The deployed commit is `Deploy website - based on dec58e84689789661efd5bf06373599605373f48`.
- `curl -I -L https://z3z1ma.github.io/dbt-osmosis/` returned HTTP 200 with `last-modified: Sun, 05 Jul 2026 19:48:15 GMT`.
- The live CLI reference page contains the newly added `migration`, `validate models`, `analyze docs`, `analyze style`, and `analyze discover` docs.
- GitHub Pages API reports `{"status":"built","html_url":"https://z3z1ma.github.io/dbt-osmosis/","source":{"branch":"gh-pages","path":"/"}}`.

## What This Supports Or Challenges

This supports closing the docs deployment ticket: the latest Docusaurus site built locally with Bun, deployed to `gh-pages`, and is live at the public GitHub Pages URL with the new CLI docs.

## Limits

Docusaurus emitted the pre-existing warning that `trailingSlash` is not explicitly configured. This warning did not block build or deployment. No docs content or Docusaurus configuration was changed in this deployment ticket.
