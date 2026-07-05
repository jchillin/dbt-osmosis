Status: active
Created: 2026-07-05
Updated: 2026-07-05

# Gitleaks History Scans Include Local Refs

`gitleaks git` scans reachable local git refs, not just the checked-out branch. After a history rewrite, stale remote-tracking refs such as `refs/remotes/origin/main` can keep pre-rewrite commits visible to Gitleaks even when local `main` is clean.

When removing historical secret-scan findings with `git-filter-repo`, record the current remote tip before deleting stale refs. Then delete the stale local tracking ref or scan after the force-with-lease push and prune:

```text
git rev-parse origin/main
git update-ref -d refs/remotes/origin/main
gitleaks git --no-banner --redact --report-format json --report-path /tmp/gitleaks-git.json .
git push --force-with-lease=main:<recorded-old-remote-hash> origin main
```

Never print unredacted findings. Preserve only rule IDs, paths, line numbers, and commit prefixes in records.
