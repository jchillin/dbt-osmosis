Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce SQL proxy Complexipy hotspot

## Scope

Refactor `src/dbt_osmosis/sql/proxy.py` so Complexipy no longer reports `DbtSession._alter_table_comment_middleware` while preserving the existing in-memory ALTER TABLE comment handling.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/sql/proxy.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/sql/proxy.py` pass.
- `tests/core/test_sql_proxy.py` passes.
- The middleware still only handles `exp.Command` ALTER TABLE comment statements, updates matching model/source descriptions in memory, and delegates non-command queries to `q.next()`.

## Explicit Exclusions

- Do not add durable YAML writes.
- Do not change SQL proxy startup, auth, TLS, or bind behavior.
- Do not broaden regex grammar beyond the existing two comment statement patterns.

## Evidence Expectations

- Record Complexipy, static check, and focused pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/sql/proxy.py`
- `tests/core/test_sql_proxy.py`
- `.10x/evidence/2026-07-05-optional-return-paths.md`
- `.10x/reviews/2026-07-05-optional-return-paths-review.md`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Repo-wide Complexipy reports `DbtSession._alter_table_comment_middleware` at 34.
- 2026-07-05: Extracted comment-statement prefiltering, regex parsing, manifest node lookup, and in-memory apply helpers.
- 2026-07-05: Direct mypy checking exposed missing optional `mysql_mimic` import stubs; added narrow local stubs under `typings/mysql_mimic` and configured `mypy_path`.
- 2026-07-05: Verified Complexipy exits zero for `src/dbt_osmosis/sql/proxy.py`; focused static checks and SQL proxy/package metadata tests pass. Evidence: `.10x/evidence/2026-07-05-sql-proxy-complexipy.md`. Review: `.10x/reviews/2026-07-05-sql-proxy-complexipy.md`.
