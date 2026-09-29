#!/bin/bash
# Checks the hybrid workflow on a copy of this project: dbt v2 builds the
# project, dbt-osmosis runs from a separate dbt-core environment, and dbt v2
# still accepts the YAML dbt-osmosis writes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dbt-osmosis-v2-hybrid.XXXXXX")"
DBT_OSMOSIS_BIN="${DBT_OSMOSIS_BIN:-dbt-osmosis}"
DBT_CORE_BIN="${DBT_CORE_BIN:-dbt}"
DBT_AUTOFIX_BIN="${DBT_AUTOFIX_BIN:-dbt-autofix}"
# dbt v2 must be installed apart from dbt-osmosis: both ship a `dbt` package.
DBT_V2_BIN="${DBT_V2_BIN:?Set DBT_V2_BIN to a dbt v2 executable from its own environment}"
PYTHON_BIN="${PYTHON:-python}"

cleanup() {
  rm -rf "${TEMP_DIR}"
}
trap cleanup EXIT

PROJECT_DIR="$(${PYTHON_BIN} - "${REPO_ROOT}" "${SCRIPT_DIR}" "${TEMP_DIR}" <<'PY'
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
source_dir = Path(sys.argv[2])
temp_dir = Path(sys.argv[3])
support_path = repo_root / "tests" / "support.py"

spec = importlib.util.spec_from_file_location("dbt_osmosis_test_support", support_path)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load fixture support from {support_path}")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)

print(support.create_temp_project_copy(source_dir, temp_dir))
PY
)"

common_options=(
  --project-dir "${PROJECT_DIR}"
  --profiles-dir "${PROJECT_DIR}"
  --target test
)
MANIFEST_PATH="${PROJECT_DIR}/target/manifest.json"

file_digest() {
  "${PYTHON_BIN}" -c 'import hashlib, pathlib, sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$1"
}

assert_manifest_unchanged() {
  if [[ "$(file_digest "${MANIFEST_PATH}")" != "$1" ]]; then
    echo "dbt-osmosis replaced the dbt v2 target/manifest.json" >&2
    exit 1
  fi
}

"${DBT_V2_BIN}" --version
"${DBT_CORE_BIN}" --version
"${DBT_OSMOSIS_BIN}" --version

# The fixture keeps legacy forms that dbt-core 1.8 needs and dbt v2 rejects.
"${DBT_AUTOFIX_BIN}" deprecations --all --path "${PROJECT_DIR}"

# Load the warehouse so dbt-osmosis documents real columns, then let dbt v2
# write target/manifest.json last, as it would in a hybrid project.
"${DBT_CORE_BIN}" seed "${common_options[@]}"
"${DBT_CORE_BIN}" run "${common_options[@]}"
"${DBT_V2_BIN}" parse "${common_options[@]}"
v2_manifest_digest="$(file_digest "${MANIFEST_PATH}")"

"${DBT_OSMOSIS_BIN}" yaml refactor --auto-apply "${common_options[@]}"
assert_manifest_unchanged "${v2_manifest_digest}"

"${DBT_CORE_BIN}" parse --use-v2-parser "${common_options[@]}"
"${DBT_V2_BIN}" parse "${common_options[@]}"
v2_manifest_digest="$(file_digest "${MANIFEST_PATH}")"

"${DBT_OSMOSIS_BIN}" yaml refactor --auto-apply --dry-run --check "${common_options[@]}"
assert_manifest_unchanged "${v2_manifest_digest}"

echo "dbt v2 accepted dbt-osmosis output against ${PROJECT_DIR}"
