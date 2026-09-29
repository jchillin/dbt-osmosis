---
sidebar_position: 1
---

# Configuration

This page describes how dbt-osmosis discovers file paths and behavior settings.

## Routing YAML files

### Models and seeds

Provide a `+dbt-osmosis` template under each folder you want managed:

```yaml title="dbt_project.yml"
models:
  <your_project_name>:
    +dbt-osmosis: "_{model}.yml"

    staging:
      +dbt-osmosis: "{parent}.yml"

    intermediate:
      +dbt-osmosis: "{node.config[materialized]}/{model}.yml"

seeds:
  <your_project_name>:
    +dbt-osmosis: "_schema.yml"
```

If a node does not have a `+dbt-osmosis` rule, dbt-osmosis can fall back to `vars.dbt_osmosis_default_path`:

```yaml title="dbt_project.yml"
vars:
  dbt_osmosis_default_path: "_{model}.yml"
```

### Fusion-Compatible Routing via `vars`

If you use **dbt v2** (formerly dbt Fusion), the `+dbt-osmosis` and `+dbt-osmosis-options` keys in `dbt_project.yml` cause parse errors, because the v2 parser rejects config keys it doesn't know. Two forms work on both dbt v2 and dbt-core.

The first is to nest the same values under `+meta`. This is what [`dbt-autofix`](https://github.com/dbt-labs/dbt-autofix) writes when it migrates a project, and dbt-osmosis resolves it exactly like `+dbt-osmosis`:

```yaml title="dbt_project.yml"
models:
  <your_project_name>:
    +meta:
      dbt-osmosis: "_{model}.yml"

    staging:
      +meta:
        dbt-osmosis: "{parent}.yml"
        dbt-osmosis-options:
          skip-add-columns: true
```

Model-level options move the same way, from `config(dbt_osmosis_prefix="o_")` to `config(meta={"dbt_osmosis_prefix": "o_"})`.

The second is to route by folder under `vars.dbt-osmosis.models`:

```yaml title="dbt_project.yml"
vars:
  dbt-osmosis:
    models:
      staging: "_stg_{parent}__models.yml"
      intermediate: "_int_{parent}__models.yml"
      marts: "_marts_{parent}__models.yml"
    seeds: "_seeds__models.yml"
```

This is functionally equivalent to `+dbt-osmosis` config keys but uses `vars:`, which both dbt-core and dbt v2 accept. Routing matches against the node's FQN folder path -- a model in `models/staging/oem_raw/` matches the `staging` key. For nested folders, use dot notation (`staging.oem_raw`) -- the most specific match wins.

Seeds can be a single string (applies to all seeds) or a dict with per-folder keys like models.

**Precedence**: `+dbt-osmosis` and `+meta: {dbt-osmosis: ...}` config keys (if present) take priority over vars routing. This means existing dbt-core projects keep working unchanged -- vars routing is only used when the config key is absent.

### Placing vars in `vars.yml` (dbt-core 1.12+)

dbt-core 1.12 and dbt v2 support an external `vars.yml` file at the project root as an alternative to the `vars:` key in `dbt_project.yml`. dbt-osmosis reads from both locations transparently -- no configuration change is needed in osmosis itself.

To use `vars.yml`, create the file and move the `dbt-osmosis` vars block there:

```yaml title="vars.yml"
vars:
  dbt-osmosis:
    models:
      staging: "_stg_{parent}__models.yml"
      intermediate: "_int_{parent}__models.yml"
      marts: "_marts_{parent}__models.yml"
    seeds: "_seeds__models.yml"
```

Then remove the `vars:` block from `dbt_project.yml`. The two locations are mutually exclusive -- having `vars:` defined in both files raises a `DbtProjectError` at parse time.

Note that `+meta: {dbt-osmosis: ...}` and `+dbt-osmosis:` model config keys are separate from the `vars:` block and are not affected by this rule. Those keys live in `dbt_project.yml` regardless of where vars are declared.

### Sources

Configure managed sources under `vars.dbt-osmosis.sources`:

```yaml title="dbt_project.yml"
vars:
  dbt-osmosis:
    sources:
      salesforce:
        path: "staging/salesforce/source.yml"
        schema: "salesforce_v2"
      marketo: "staging/customer/marketo.yml"

    column_ignore_patterns:
      - "_FIVETRAN_SYNCED"
      - ".*__key__.namespace"
```

## Fusion compatibility

:::caution dbt-osmosis requires dbt-core

dbt-osmosis **does not run on dbt v2** (`dbt` or `dbt-oss`, formerly dbt Fusion). It depends on dbt-core for manifest parsing, database introspection, and SQL compilation, and dbt v2 has no Python API to replace them. If your team uses dbt v2, you need a **hybrid setup** with two virtual environments: one running dbt-core 1.x for dbt-osmosis, and one running dbt v2 for your normal development workflow. Both engines can share the same project directory. See [Hybrid workflow](#hybrid-workflow-for-fusion-projects) below.

:::

dbt-osmosis can produce **Fusion-compatible YAML** where column `meta` and `tags` are nested inside `config` blocks instead of at the top level. dbt-core supports this format from 1.9.6, and dbt v2 requires it.

Fusion-compatible output covers the columns dbt-osmosis writes. dbt-osmosis doesn't write model-, seed-, or source-level `meta` and `tags`, so it leaves those keys where you put them. Move them under `config` yourself or with `dbt-autofix`.

### Auto-detection

By default (`--fusion-compat` not specified), dbt-osmosis auto-detects whether to produce Fusion-compatible output:

1. **dbt v2 manifest** — if `target/manifest.json` was written by the dbt v2 engine, fusion-compat is enabled. dbt-osmosis treats a `metadata.dbt_version` of 2.0 or later as v2 evidence, which covers `dbt` and `dbt OSS` (formerly Fusion and dbt Core v2) and earlier Fusion previews. It also accepts the Fusion preview manifest schema v20. A truncated or otherwise invalid manifest doesn't count, so if a dbt v2 run was interrupted while writing it, rerun `dbt parse` with dbt v2 or pass `--fusion-compat`. When dbt-osmosis finds a dbt v2 manifest, it still parses the project with dbt-core but leaves that manifest in place, so dbt v2 state selection and deferral keep working.
2. **dbt-core version** — if dbt-core >= 1.9.6 is installed, fusion-compat is enabled (these versions natively support the `config` block format).

### Explicit override

```bash
# Force Fusion-compatible output
dbt-osmosis yaml refactor --fusion-compat

# Force legacy output (even on dbt >= 1.9.6)
dbt-osmosis yaml refactor --no-fusion-compat
```

### Hybrid workflow for Fusion projects

If your team runs dbt v2 (formerly dbt Fusion) alongside dbt-core:

1. Maintain **two virtual environments**: one with `dbt-core` and `dbt-osmosis`, another with dbt v2 (`dbt` or `dbt-oss`). Don't install them together. dbt v2 and dbt-core both ship a `dbt` Python package and overwrite each other's files, which can leave both engines broken. dbt-osmosis doesn't depend on `dbt` or `dbt-oss`, so installing it never pulls in dbt v2, but nothing stops you from installing both into one environment.
2. Migrate the project once with `dbt-autofix deprecations --all`. It moves `+dbt-osmosis` routing and SQL `dbt_osmosis_*` options under `meta` (see [routing that dbt v2 accepts](#fusion-compatible-routing-via-vars)), moves model and seed properties such as `meta` under `config`, and nests generic test arguments under `arguments:`.
3. Use dbt-core 1.10.5 or later in the dbt-osmosis environment. Earlier versions can't parse generic test `arguments:`.
4. Run dbt v2 for compilation and execution in your normal workflow.
5. Run dbt-osmosis from the dbt-core environment to manage YAML schema files. It detects the dbt v2 manifest in `target/`, produces compatible output, and leaves that manifest in place. Its dbt-core parse still writes `partial_parse.msgpack` to `target/`, and dbt v2 parses and builds normally with that file present.
6. Check the result with `dbt parse` from the dbt v2 environment.

Both environments share the same `dbt_project.yml` and model files. The dbt-osmosis CI runs these steps on the demo project with `dbt-oss` and dbt-core 1.12.

Switching targets in the workbench re-parses through dbt-core-interface, which always writes `target/manifest.json`. If you use the workbench on a dbt v2 project, rerun `dbt parse` with dbt v2 afterwards.

## Behavior settings

Use CLI flags for global defaults and override them in config when needed.

## YAML writer settings

You can tune the underlying `ruamel.yaml` serializer via `vars.dbt-osmosis.yaml_settings`:

```yaml title="dbt_project.yml"
vars:
  dbt-osmosis:
    yaml_settings:
      width: 120
      preserve_quotes: true
```

### CLI defaults

```bash
dbt-osmosis yaml refactor \
  --skip-add-columns \
  --skip-add-data-types \
  --skip-merge-meta \
  --skip-add-tags \
  --numeric-precision-and-scale \
  --string-length \
  --force-inherit-descriptions \
  --output-to-lower \
  --add-progenitor-to-meta \
  --strip-eof-blank-lines \
  --fusion-compat
```

### Folder-level overrides

```yaml title="dbt_project.yml"
models:
  my_project:
    staging:
      +dbt-osmosis: "{parent}.yml"
      +dbt-osmosis-options:
        skip-add-columns: true
        sort-by: "alphabetical"

    intermediate:
      +dbt-osmosis: "{node.config[materialized]}/{model}.yml"
      +dbt-osmosis-options:
        skip-add-tags: true
        output-to-lower: true
```

### Node-level overrides

```jinja title="models/intermediate/some_model.sql"
{{ config(
    materialized='incremental',
    dbt_osmosis_options={
      "skip-add-data-types": true,
      "sort-by": "alphabetical"
    }
) }}
```

### Column-level overrides

```yaml
tables:
  - name: some_model
    columns:
      - name: tricky_column
        meta:
          dbt-osmosis-skip-add-data-types: true
          dbt_osmosis_options:
            skip-add-tags: true
```

## Setting precedence (most specific wins)

1. Column `meta` and column `dbt-osmosis-options`
2. Node `meta` and `dbt_osmosis_options`
3. Node `config.extra` and `dbt_osmosis_options`
4. CLI defaults / fallback settings

## Common options (excerpt)

See the [settings reference](../reference/settings) for the full list of options and defaults.
