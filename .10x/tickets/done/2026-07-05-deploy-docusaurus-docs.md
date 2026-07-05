Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Deploy Docusaurus Docs To GitHub Pages

## Scope

Manually deploy the latest `docs/` Docusaurus site to GitHub Pages using the repository's Docusaurus CLI deployment path, preferring Bun when practical.

## Acceptance Criteria

- Confirm the docs deployment command and required environment from repository files and CLI help.
- Build the docs site from the current `main` content.
- Deploy the generated site to the `gh-pages` branch.
- Verify `origin/gh-pages` advances and the public docs URL is reachable.
- Record deployment evidence and close this ticket.

## Explicit Exclusions

- Do not change docs content unless deployment verification exposes a docs build blocker.
- Do not redesign docs hosting or add a GitHub Actions deployment workflow in this ticket.

## Evidence Expectations

- Record the exact commands, relevant commit SHAs, deployment branch update, and URL check in `.10x/evidence/`.

## References

- `docs/package.json`
- `docs/README.md`
- `docs/docusaurus.config.js`
- `docs/package-lock.json`
- `https://z3z1ma.github.io/dbt-osmosis/`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Inspected docs tooling. `docs/package.json` defines `deploy` as `docusaurus deploy`; `docs/README.md` documents `USE_SSH=true npm run deploy` or `GIT_USER=<username> npm run deploy`. Bun is available locally as `1.3.14`, Node is `v22.23.1`, and `docs/node_modules` is present.
- 2026-07-05: Built the docs with `bun run build`. SSH deployment failed at push because the available SSH identity does not have push rights to `z3z1ma/dbt-osmosis`. Re-ran deployment over HTTPS using the active `z3z1ma` GitHub token, with Docusaurus obfuscating `GIT_PASS` in logs.
- 2026-07-05: `origin/gh-pages` advanced to `1a20d0d19b2456b364e1a5521b6a9c4b3221c354`, GitHub Pages reports `status: built`, and the public CLI reference includes the newly added command docs. Evidence: `.10x/evidence/2026-07-05-docusaurus-docs-manual-deploy.md`. Review: `.10x/reviews/2026-07-05-docusaurus-docs-manual-deploy.md`.
