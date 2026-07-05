Status: done
Created: 2026-07-05
Updated: 2026-07-05

# Reduce introspection Complexipy hotspots

## Scope

Refactor `src/dbt_osmosis/core/introspection.py` so Complexipy no longer reports:

- `SettingsResolver.resolve`
- `PropertyAccessor._get_from_yaml`
- `get_columns`
- `SettingsResolver.get_precedence_chain`
- `SettingsResolver.get_yaml_path_template`
- `ProjectVarsSource.get`
- `PropertyAccessor._get_from_manifest`

Preserve existing configuration precedence, YAML/property source behavior, catalog-first column discovery, warehouse cache locking, and public API names.

## Acceptance Criteria

- `uv run --no-sync --with complexipy complexipy src/dbt_osmosis/core/introspection.py --failed --plain --sort desc` exits zero.
- Focused static checks for `src/dbt_osmosis/core/introspection.py` pass.
- Direct settings/config/property/introspection tests pass.
- Existing context setting behavior, project vars lookup variants, YAML path template precedence, manifest vs YAML property semantics, catalog fallback, disabled introspection behavior, and column cache locking remain unchanged.

## Explicit Exclusions

- Do not change the documented configuration precedence.
- Do not replace ruamel-backed YAML access or schema reader/cache behavior.
- Do not remove public compatibility exports or aliases.
- Do not alter warehouse introspection side effects beyond preserving existing cache behavior.

## Evidence Expectations

- Record Complexipy, static check, and focused pytest results in `.10x/evidence/`.
- Record closure review in `.10x/reviews/`.

## References

- `src/dbt_osmosis/core/introspection.py`
- `src/dbt_osmosis/core/AGENTS.md`
- `specs/001-unified-config-resolution/spec.md`
- `specs/001-unified-config-resolution/tasks.md`
- `tests/core/test_settings_resolver.py`
- `tests/core/test_config_resolution.py`
- `tests/core/test_introspection.py`
- `tests/core/test_property_accessor.py`
- `tests/core/test_real_config_shapes.py`
- `tests/test_yaml_context.py`

## Blockers

None.

## Progress and Notes

- 2026-07-05: Repo-wide Complexipy reports seven `introspection.py` hotspots: `SettingsResolver.resolve` 53, `PropertyAccessor._get_from_yaml` 36, `get_columns` 36, `SettingsResolver.get_precedence_chain` 35, `SettingsResolver.get_yaml_path_template` 29, `ProjectVarsSource.get` 24, and `PropertyAccessor._get_from_manifest` 17.
- 2026-07-05: Extracted shared setting lookup helpers, project vars source ordering, resolver node/context source helpers, YAML path-template helpers, column collection helpers, and manifest/YAML property helpers.
- 2026-07-05: Verified Complexipy exits zero for `src/dbt_osmosis/core/introspection.py`; focused static checks and settings/config/property/introspection tests pass. Evidence: `.10x/evidence/2026-07-05-introspection-complexipy.md`. Review: `.10x/reviews/2026-07-05-introspection-complexipy.md`.
