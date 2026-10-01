# pyright: reportPrivateImportUsage=false, reportPrivateUsage=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportAny=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportFunctionMemberAccess=false, reportUnknownVariableType=false, reportUnusedParameter=false

import gc
import json
import os
import threading
import time
import weakref
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest
import ruamel.yaml

from dbt_osmosis.core.config import (
    _MANIFEST_HEAD_CHARS,
    DbtConfiguration,
    _add_cross_project_references,
    _detect_fusion_manifest,
    _guard_dbt_v2_manifest,
    _reload_manifest,
    config_to_namespace,
    create_dbt_project_context,
    discover_profiles_dir,
    discover_project_dir,
)
from dbt_osmosis.core.settings import YamlRefactorContext
from tests.support import create_temp_project_copy

_V12_SCHEMA_URL = "https://schemas.getdbt.com/dbt/manifest/v12.json"
_NODES_PAST_READ_WINDOW = {"model.demo.big": {"description": "x" * (_MANIFEST_HEAD_CHARS + 1)}}
_METADATA_ENV_PAST_READ_WINDOW = {"DBT_ENV_CUSTOM_ENV_NOTES": "x" * (_MANIFEST_HEAD_CHARS + 1)}
_V2_MANIFEST = {"metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "2.0.5"}}
_LARGE_V2_MANIFEST_TEXT = json.dumps({
    "metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "2.0.5"},
    "nodes": _NODES_PAST_READ_WINDOW,
})


def test_discover_project_dir(tmp_path):
    """Ensures discover_project_dir falls back properly if no environment
    variable is set and no dbt_project.yml is found in parents.
    """
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        found = discover_project_dir()
        assert str(tmp_path.resolve()) == found
    finally:
        os.chdir(original_cwd)


def test_discover_profiles_dir(tmp_path):
    """Ensures discover_profiles_dir falls back to ~/.dbt
    if no DBT_PROFILES_DIR is set and no local profiles.yml is found.
    """
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        found = discover_profiles_dir()
        assert str(Path.home() / ".dbt") == found
    finally:
        os.chdir(original_cwd)


def test_discover_profiles_dir_finds_project_root_profiles_from_subdirectory(tmp_path):
    """Subdirectory invocation should still find a project-local profiles.yml."""
    project_root = tmp_path / "demo_project"
    nested_dir = project_root / "models" / "staging"
    nested_dir.mkdir(parents=True)
    (project_root / "dbt_project.yml").write_text("name: demo_project\nversion: '1.0'\n")
    (project_root / "profiles.yml").write_text("demo_project: {}\n")

    original_cwd = os.getcwd()
    os.chdir(nested_dir)
    try:
        found = discover_profiles_dir()
        assert str(project_root.resolve()) == found
    finally:
        os.chdir(original_cwd)


def test_discover_profiles_dir_prefers_current_directory_over_project_root(tmp_path):
    """A local profiles.yml should win before falling back to the project root."""
    project_root = tmp_path / "demo_project"
    nested_dir = project_root / "models" / "staging"
    nested_dir.mkdir(parents=True)
    (project_root / "dbt_project.yml").write_text("name: demo_project\nversion: '1.0'\n")
    (project_root / "profiles.yml").write_text("demo_project: {}\n")
    (nested_dir / "profiles.yml").write_text("nested_profile: {}\n")

    original_cwd = os.getcwd()
    os.chdir(nested_dir)
    try:
        found = discover_profiles_dir()
        assert str(nested_dir.resolve()) == found
    finally:
        os.chdir(original_cwd)


def test_config_to_namespace():
    """Tests that DbtConfiguration is properly converted to argparse.Namespace."""
    cfg = DbtConfiguration(project_dir="demo_duckdb", profiles_dir="demo_duckdb", target="dev")
    ns = config_to_namespace(cfg)
    assert ns.project_dir == "demo_duckdb"
    assert ns.profiles_dir == "demo_duckdb"
    assert ns.target == "dev"


def test_reload_manifest(yaml_context: YamlRefactorContext):
    """Basic check that _reload_manifest doesn't raise, given a real project."""
    _reload_manifest(yaml_context.project)


def test_create_dbt_project_context_accepts_interface_registered_adapter():
    """Bootstrap succeeds when dbt-core-interface owns the factory registration."""
    cfg = DbtConfiguration(project_dir="demo_duckdb", profiles_dir="demo_duckdb")
    adapter = mock.Mock()
    project = SimpleNamespace(
        runtime_config=SimpleNamespace(
            credentials=SimpleNamespace(type="duckdb"),
            adapter=adapter,
        ),
        manifest=mock.Mock(),
        project_name="demo_duckdb",
        target_path=Path("demo_duckdb/target"),
    )
    factory = SimpleNamespace(adapters={"duckdb": adapter})
    context = mock.sentinel.context

    with (
        mock.patch("dbt.adapters.factory.FACTORY", factory),
        mock.patch("dbt_osmosis.core.config._detect_fusion_manifest", return_value=False),
        mock.patch("dbt_osmosis.core.config._load_interface_project", return_value=project),
        mock.patch("dbt_osmosis.core.config.DbtProjectContext.from_project", return_value=context),
        mock.patch("dbt_osmosis.core.config.importlib.import_module", side_effect=ImportError),
    ):
        result = create_dbt_project_context(cfg)

    assert result is context


def test_create_dbt_project_context_registers_project_adapter_when_factory_missing():
    """Bootstrap binds the current project adapter when the factory is empty."""
    cfg = DbtConfiguration(project_dir="demo_duckdb", profiles_dir="demo_duckdb")
    adapter = mock.Mock()
    project = SimpleNamespace(
        runtime_config=SimpleNamespace(
            credentials=SimpleNamespace(type="duckdb"),
            adapter=adapter,
        ),
        manifest=mock.Mock(),
        project_name="demo_duckdb",
        target_path=Path("demo_duckdb/target"),
    )
    factory = SimpleNamespace(adapters={})

    with (
        mock.patch("dbt.adapters.factory.FACTORY", factory),
        mock.patch("dbt_osmosis.core.config._detect_fusion_manifest", return_value=False),
        mock.patch("dbt_osmosis.core.config._load_interface_project", return_value=project),
        mock.patch(
            "dbt_osmosis.core.config.DbtProjectContext.from_project",
            return_value=mock.sentinel.context,
        ),
        mock.patch("dbt_osmosis.core.config.importlib.import_module", side_effect=ImportError),
    ):
        result = create_dbt_project_context(cfg)

    assert result is mock.sentinel.context
    assert factory.adapters["duckdb"] is adapter


def test_create_dbt_project_context_replaces_stale_factory_adapter():
    """Bootstrap replaces stale factory state with the current project adapter."""
    cfg = DbtConfiguration(project_dir="demo_duckdb", profiles_dir="demo_duckdb")
    project_adapter = mock.Mock()
    registered_adapter = mock.Mock()
    project = SimpleNamespace(
        runtime_config=SimpleNamespace(
            credentials=SimpleNamespace(type="duckdb"),
            adapter=project_adapter,
        ),
        manifest=mock.Mock(),
        project_name="demo_duckdb",
        target_path=Path("demo_duckdb/target"),
    )
    factory = SimpleNamespace(adapters={"duckdb": registered_adapter})

    with (
        mock.patch("dbt.adapters.factory.FACTORY", factory),
        mock.patch("dbt_osmosis.core.config._detect_fusion_manifest", return_value=False),
        mock.patch("dbt_osmosis.core.config._load_interface_project", return_value=project),
        mock.patch(
            "dbt_osmosis.core.config.DbtProjectContext.from_project",
            return_value=mock.sentinel.context,
        ),
        mock.patch("dbt_osmosis.core.config.importlib.import_module", side_effect=ImportError),
    ):
        result = create_dbt_project_context(cfg)

    assert result is mock.sentinel.context
    registered_adapter.cleanup_connections.assert_called_once_with()
    assert factory.adapters["duckdb"] is project_adapter


def test_create_dbt_project_context_falls_back_to_close_all_connections():
    """Bootstrap still cleans up stale adapters that only expose legacy cleanup hooks."""
    cfg = DbtConfiguration(project_dir="demo_duckdb", profiles_dir="demo_duckdb")
    project_adapter = mock.Mock()
    registered_adapter = SimpleNamespace(close_all_connections=mock.Mock())
    project = SimpleNamespace(
        runtime_config=SimpleNamespace(
            credentials=SimpleNamespace(type="duckdb"),
            adapter=project_adapter,
        ),
        manifest=mock.Mock(),
        project_name="demo_duckdb",
        target_path=Path("demo_duckdb/target"),
    )
    factory = SimpleNamespace(adapters={"duckdb": registered_adapter})

    with (
        mock.patch("dbt.adapters.factory.FACTORY", factory),
        mock.patch("dbt_osmosis.core.config._detect_fusion_manifest", return_value=False),
        mock.patch("dbt_osmosis.core.config._load_interface_project", return_value=project),
        mock.patch(
            "dbt_osmosis.core.config.DbtProjectContext.from_project",
            return_value=mock.sentinel.context,
        ),
        mock.patch("dbt_osmosis.core.config.importlib.import_module", side_effect=ImportError),
    ):
        result = create_dbt_project_context(cfg)

    assert result is mock.sentinel.context
    registered_adapter.close_all_connections.assert_called_once_with()
    assert factory.adapters["duckdb"] is project_adapter


def test_create_dbt_project_context_rebinds_when_stale_adapter_has_no_cleanup_hook():
    """Bootstrap should not fail if a stale adapter exposes neither known cleanup hook."""
    cfg = DbtConfiguration(project_dir="demo_duckdb", profiles_dir="demo_duckdb")
    project_adapter = mock.Mock()
    registered_adapter = SimpleNamespace()
    project = SimpleNamespace(
        runtime_config=SimpleNamespace(
            credentials=SimpleNamespace(type="duckdb"),
            adapter=project_adapter,
        ),
        manifest=mock.Mock(),
        project_name="demo_duckdb",
        target_path=Path("demo_duckdb/target"),
    )
    factory = SimpleNamespace(adapters={"duckdb": registered_adapter})

    with (
        mock.patch("dbt.adapters.factory.FACTORY", factory),
        mock.patch("dbt_osmosis.core.config._detect_fusion_manifest", return_value=False),
        mock.patch("dbt_osmosis.core.config._load_interface_project", return_value=project),
        mock.patch(
            "dbt_osmosis.core.config.DbtProjectContext.from_project",
            return_value=mock.sentinel.context,
        ),
        mock.patch("dbt_osmosis.core.config.importlib.import_module", side_effect=ImportError),
    ):
        result = create_dbt_project_context(cfg)

    assert result is mock.sentinel.context
    assert factory.adapters["duckdb"] is project_adapter


def test_add_cross_project_references_imports_exposed_models_without_parser_hack(
    yaml_context: YamlRefactorContext,
):
    """dbt-loom exposed model nodes should import without ModelParser internals."""
    base_node = next(
        node
        for node in yaml_context.project.manifest.nodes.values()
        if str(node.resource_type) == "model"
    )
    base_node_dict = base_node.to_dict(omit_none=False)

    def loom_model(unique_id: str, *, access: str, resource_type: str = "model"):
        node_dict = deepcopy(base_node_dict)
        package_name, model_name = unique_id.split(".")[1:]
        node_dict.update({
            "unique_id": unique_id,
            "package_name": package_name,
            "name": model_name,
            "alias": model_name,
            "access": access,
            "resource_type": resource_type,
        })
        return node_dict

    public_model = loom_model("model.upstream.public_orders", access="public")
    private_model = loom_model("model.upstream.private_orders", access="private")
    protected_model = loom_model("model.upstream.protected_orders", access="protected")
    non_model = loom_model("model.upstream.seed_orders", access="public", resource_type="seed")
    manifest = SimpleNamespace(nodes={})
    dbt_loom = SimpleNamespace(
        dbtLoom=lambda project_name: SimpleNamespace(
            manifests={
                "upstream": {
                    "nodes": {
                        public_model["unique_id"]: public_model,
                        private_model["unique_id"]: private_model,
                        protected_model["unique_id"]: protected_model,
                        non_model["unique_id"]: non_model,
                    }
                }
            }
        )
    )

    with mock.patch(
        "dbt.parser.models.ModelParser.parse_from_dict",
        side_effect=AssertionError("ModelParser parser hack should not be called"),
    ) as parse_from_dict:
        result = _add_cross_project_references(manifest, dbt_loom, "downstream")

    assert result is manifest
    assert sorted(manifest.nodes) == [
        "model.upstream.private_orders",
        "model.upstream.public_orders",
    ]
    assert (
        manifest.nodes["model.upstream.public_orders"].unique_id == "model.upstream.public_orders"
    )
    parse_from_dict.assert_not_called()


def test_adapter_ttl_expiration(yaml_context: YamlRefactorContext):
    """Check that if the TTL is expired, we refresh the connection in DbtProjectContext.adapter.
    We patch time.time to simulate a large jump.
    """
    project_ctx = yaml_context.project
    old_adapter = project_ctx.adapter
    # Force we have an entry in _connection_created_at
    thread_id = threading.get_ident()
    project_ctx._connection_created_at[thread_id] = time.time() - 999999  # artificially old

    with (
        mock.patch.object(old_adapter.connections, "release") as mock_release,
        mock.patch.object(old_adapter.connections, "clear_thread_connection") as mock_clear,
    ):
        new_adapter = project_ctx.adapter
        # The underlying object is the same instance, but the connection is re-acquired
        assert new_adapter == old_adapter
        mock_release.assert_called_once()
        mock_clear.assert_called_once()


class TestDetectFusionManifest:
    """Tests for _detect_fusion_manifest() Fusion detection logic."""

    @staticmethod
    def _detect(tmp_path, manifest_text: str) -> bool:
        target = tmp_path / "target"
        target.mkdir()
        (target / "manifest.json").write_text(manifest_text)
        return _detect_fusion_manifest(tmp_path / "target" / "manifest.json")

    def test_no_manifest_returns_false(self, tmp_path):
        """Without a manifest, there is no project-local Fusion evidence."""
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False

    def test_no_manifest_ignores_fusion_binaries_on_path(self, tmp_path):
        """Installed Fusion binaries alone are not evidence about this project."""
        with mock.patch(
            "shutil.which",
            side_effect=lambda cmd: (
                "/usr/bin/dbtf"
                if cmd == "dbtf"
                else "/usr/bin/dbt-fusion"
                if cmd == "dbt-fusion"
                else None
            ),
        ) as mock_which:
            assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False
        mock_which.assert_not_called()

    def test_dbt_core_manifest_v12(self, tmp_path):
        """dbt-core manifest (v12) → returns False."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {
            "metadata": {
                "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json",
                "dbt_version": "1.11.2",
            },
        }
        (target / "manifest.json").write_text(json.dumps(manifest))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False

    def test_fusion_manifest_v20(self, tmp_path):
        """Fusion manifest (v20) → returns True."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {
            "metadata": {
                "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v20.json",
                "dbt_version": "2025.1.0",
            },
        }
        (target / "manifest.json").write_text(json.dumps(manifest))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is True

    def test_dbt_v2_ga_manifest_v12(self, tmp_path):
        """dbt v2 GA manifest (schema v12, dbt_version 2.x, compact JSON) → returns True."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {
            "metadata": {
                "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json",
                "dbt_version": "2.0.5",
                "adapter_type": "duckdb",
            },
            "nodes": {},
        }
        (target / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is True

    @pytest.mark.parametrize("dbt_version", ["2.0.0-rc8", "2.0.0-preview.154"])
    def test_dbt_v2_prerelease_manifest(self, tmp_path, dbt_version):
        """dbt v2 pre-release and Fusion preview version strings → returns True."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {
            "metadata": {
                "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json",
                "dbt_version": dbt_version,
            },
        }
        (target / "manifest.json").write_text(json.dumps(manifest))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is True

    @pytest.mark.parametrize("dbt_version", ["1.10.20", "1.12.0b2"])
    def test_dbt_core_v1_manifest_versions(self, tmp_path, dbt_version):
        """dbt-core 1.x release and pre-release manifests → returns False."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {
            "metadata": {
                "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json",
                "dbt_version": dbt_version,
            },
        }
        (target / "manifest.json").write_text(json.dumps(manifest))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False

    def test_dbt_v2_manifest_larger_than_read_window(self, tmp_path):
        """A valid v2 manifest larger than the metadata read window → returns True."""
        assert self._detect(tmp_path, _LARGE_V2_MANIFEST_TEXT) is True

    def test_dbt_core_manifest_is_not_validated_past_metadata(self, tmp_path):
        """Without v2 evidence in metadata, the rest of the manifest is never read."""
        manifest = {
            "metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "1.11.2"},
            "nodes": _NODES_PAST_READ_WINDOW,
        }
        with mock.patch("dbt_osmosis.core.config.validate_json_file") as validate:
            assert self._detect(tmp_path, json.dumps(manifest)) is False
        validate.assert_not_called()

    def test_dbt_v2_metadata_larger_than_read_window(self, tmp_path):
        """A valid v2 manifest whose metadata alone outgrows the read window → returns True."""
        manifest = {
            "metadata": {
                "dbt_schema_version": _V12_SCHEMA_URL,
                "dbt_version": "2.0.5",
                "env": _METADATA_ENV_PAST_READ_WINDOW,
            },
            "nodes": {},
        }
        assert self._detect(tmp_path, json.dumps(manifest)) is True

    def test_dbt_core_metadata_larger_than_read_window(self, tmp_path):
        """dbt-core metadata that outgrows the read window still isn't v2 evidence."""
        manifest = {
            "metadata": {
                "dbt_schema_version": _V12_SCHEMA_URL,
                "dbt_version": "1.11.2",
                "env": _METADATA_ENV_PAST_READ_WINDOW,
            },
            "nodes": _NODES_PAST_READ_WINDOW,
        }
        with mock.patch("dbt_osmosis.core.config.validate_json_file") as validate:
            assert self._detect(tmp_path, json.dumps(manifest)) is False
        validate.assert_not_called()

    @pytest.mark.parametrize(
        "manifest_text",
        [
            pytest.param(_LARGE_V2_MANIFEST_TEXT[:-5], id="truncated-inside-node-string"),
            pytest.param(_LARGE_V2_MANIFEST_TEXT[:-1], id="truncated-before-final-brace"),
            pytest.param(_LARGE_V2_MANIFEST_TEXT[:-1] + ',"sources":nope}', id="invalid-token"),
            pytest.param(_LARGE_V2_MANIFEST_TEXT + "{}", id="trailing-data"),
        ],
    )
    def test_malformed_v2_manifest_larger_than_read_window(self, tmp_path, manifest_text):
        """Valid v2 metadata followed by malformed JSON past the read window → returns False."""
        assert self._detect(tmp_path, manifest_text) is False

    @pytest.mark.parametrize(
        "manifest_text",
        [
            pytest.param(
                f'{{"metadata":{{"dbt_schema_version":"{_V12_SCHEMA_URL}","dbt_version":"2.0.5"',
                id="inside-metadata",
            ),
            pytest.param(
                f'{{"metadata":{{"dbt_schema_version":"{_V12_SCHEMA_URL}","dbt_version":"2.0.5"}},"nodes":{{',
                id="after-metadata",
            ),
        ],
    )
    def test_truncated_manifest_with_v2_version(self, tmp_path, manifest_text):
        """Truncated JSON containing "dbt_version":"2.0.5" → returns False."""
        assert self._detect(tmp_path, manifest_text) is False

    @pytest.mark.parametrize(
        "manifest",
        [
            pytest.param(
                {
                    "dbt_version": "2.0.5",
                    "metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "1.11.2"},
                },
                id="top-level",
            ),
            pytest.param(
                {
                    "metadata": {
                        "env": {"dbt_version": "2.0.5"},
                        "dbt_schema_version": _V12_SCHEMA_URL,
                        "dbt_version": "1.11.2",
                    },
                },
                id="metadata-env",
            ),
            pytest.param(
                {
                    "metadata": {"dbt_schema_version": _V12_SCHEMA_URL},
                    "nodes": {"model.demo.a": {"dbt_version": "2.0.5"}},
                },
                id="node",
            ),
            pytest.param(
                {
                    "nodes": {"model.demo.a": {"dbt_version": "2.0.5"}, **_NODES_PAST_READ_WINDOW},
                    "metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "1.11.2"},
                },
                id="node-before-metadata-past-read-window",
            ),
        ],
    )
    def test_dbt_version_outside_metadata(self, tmp_path, manifest):
        """A v2 dbt_version anywhere but metadata.dbt_version → returns False."""
        assert self._detect(tmp_path, json.dumps(manifest)) is False

    @pytest.mark.parametrize("dbt_version", ["2.not-a-version", "2.", "2..0", "2.0.5-"])
    def test_invalid_v2_version_strings(self, tmp_path, dbt_version):
        """dbt_version strings that start with 2 but aren't versions → returns False."""
        manifest = {"metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": dbt_version}}
        assert self._detect(tmp_path, json.dumps(manifest)) is False

    def test_future_manifest_v13(self, tmp_path):
        """Synthetic future dbt-core manifest versions do not prove Fusion."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {
            "metadata": {
                "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v13.json",
                "dbt_version": "1.12.0",
            },
        }
        (target / "manifest.json").write_text(json.dumps(manifest))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False

    def test_malformed_manifest(self, tmp_path):
        """Malformed manifest.json → returns False gracefully."""
        target = tmp_path / "target"
        target.mkdir()
        (target / "manifest.json").write_text("not valid json{{{")
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False

    def test_manifest_missing_metadata(self, tmp_path):
        """Manifest with no metadata section → returns False."""
        target = tmp_path / "target"
        target.mkdir()
        (target / "manifest.json").write_text(json.dumps({"nodes": {}}))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False

    def test_manifest_empty_schema_version(self, tmp_path):
        """Manifest with empty dbt_schema_version → returns False."""
        target = tmp_path / "target"
        target.mkdir()
        manifest = {"metadata": {"dbt_schema_version": ""}}
        (target / "manifest.json").write_text(json.dumps(manifest))
        assert _detect_fusion_manifest(tmp_path / "target" / "manifest.json") is False


class _RecordingProject:
    def __init__(self, target_path: Path) -> None:
        self.target_path = target_path
        self.writes: list[object] = []

    def write_manifest(self, path=None) -> None:
        self.writes.append(path)


class TestGuardDbtV2Manifest:
    """_guard_dbt_v2_manifest() only skips writes that would replace a dbt v2 manifest."""

    @staticmethod
    def _guarded_project(tmp_path: Path, manifest: dict[str, object]) -> _RecordingProject:
        target = tmp_path / "target"
        target.mkdir()
        (target / "manifest.json").write_text(json.dumps(manifest))
        project = _RecordingProject(target)
        _guard_dbt_v2_manifest(project)
        return project

    def test_skips_default_write_over_dbt_v2_manifest(self, tmp_path):
        project = self._guarded_project(tmp_path, _V2_MANIFEST)
        project.write_manifest()
        assert project.writes == []

    def test_writes_over_dbt_core_manifest_when_guarded_twice(self, tmp_path):
        project = self._guarded_project(
            tmp_path, {"metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "1.11.2"}}
        )
        guarded_write = vars(project)["write_manifest"]
        _guard_dbt_v2_manifest(project)
        assert vars(project)["write_manifest"] is guarded_write
        project.write_manifest()
        assert project.writes == [None]

    def test_writes_explicit_path(self, tmp_path):
        project = self._guarded_project(tmp_path, _V2_MANIFEST)
        project.write_manifest("elsewhere")
        assert project.writes == ["elsewhere"]


class TestProjectContextManifestWrite:
    """create_dbt_project_context() parses with dbt-core; these cover what it leaves in the target directory."""

    @staticmethod
    def _demo_project_with_manifest(
        tmp_path: Path, manifest: dict[str, object], target_dir: str = "target"
    ) -> Path:
        project_dir = create_temp_project_copy(Path("demo_duckdb"), tmp_path)
        manifest_path = project_dir / target_dir / "manifest.json"
        manifest_path.parent.mkdir()
        manifest_path.write_text(json.dumps(manifest))
        return project_dir

    @staticmethod
    def _create_context(project_dir: Path, **config: object):
        return create_dbt_project_context(
            DbtConfiguration(
                project_dir=str(project_dir),
                profiles_dir=str(project_dir),
                target="test",
                **config,
            )
        )

    def test_keeps_dbt_v2_manifest(self, tmp_path):
        """dbt v2 reads target/manifest.json for state and deferral, so osmosis must not replace it."""
        project_dir = self._demo_project_with_manifest(tmp_path, _V2_MANIFEST)
        manifest_path = project_dir / "target" / "manifest.json"
        v2_manifest = manifest_path.read_bytes()

        with self._create_context(project_dir) as context:
            assert context.is_fusion_manifest is True
            assert "model.jaffle_shop_duckdb.orders" in context.manifest.nodes

        assert manifest_path.read_bytes() == v2_manifest

    def test_keeps_dbt_v2_manifest_when_project_is_reused_with_new_vars(self, tmp_path):
        """dbt-core-interface reuses a live project for the same root and re-parses it when vars change."""
        project_dir = self._demo_project_with_manifest(tmp_path, _V2_MANIFEST)
        manifest_path = project_dir / "target" / "manifest.json"
        v2_manifest = manifest_path.read_bytes()
        model = project_dir / "models" / "orders.sql"

        with self._create_context(project_dir) as first_context:
            model.write_text(model.read_text() + "\n-- edited so the re-parse isn't skipped\n")
            with self._create_context(project_dir, vars={"review_marker": True}) as context:
                assert context.is_fusion_manifest is True
                assert context._project is first_context._project

        assert manifest_path.read_bytes() == v2_manifest

    def test_project_is_freed_with_its_last_context(self, tmp_path):
        """The guard mustn't keep a project alive, or dbt-core-interface would reuse it instead of parsing anew."""
        project_dir = self._demo_project_with_manifest(tmp_path, _V2_MANIFEST)
        gc.disable()
        try:
            context = self._create_context(project_dir)
            project_ref = weakref.ref(context._project)
            context.close()
            del context
            assert project_ref() is None
        finally:
            gc.enable()

    def test_keeps_dbt_v2_manifest_in_configured_target_path(self, tmp_path):
        """Detection and the write both use target-path from dbt_project.yml."""
        project_dir = self._demo_project_with_manifest(tmp_path, _V2_MANIFEST, "artifacts")
        project_yml = project_dir / "dbt_project.yml"
        yaml = ruamel.yaml.YAML()
        project_config = yaml.load(project_yml)
        project_config["target-path"] = "artifacts"
        yaml.dump(project_config, project_yml)
        manifest_path = project_dir / "artifacts" / "manifest.json"
        v2_manifest = manifest_path.read_bytes()

        with self._create_context(project_dir) as context:
            assert context.is_fusion_manifest is True

        assert manifest_path.read_bytes() == v2_manifest

    def test_ignores_dbt_target_path_environment_variable(self, tmp_path, monkeypatch):
        """dbt-core-interface ignores DBT_TARGET_PATH, so a dbt v2 manifest there is out of reach."""
        project_dir = self._demo_project_with_manifest(tmp_path, _V2_MANIFEST, "artifacts")
        monkeypatch.setenv("DBT_TARGET_PATH", str(project_dir / "artifacts"))
        manifest_path = project_dir / "artifacts" / "manifest.json"
        v2_manifest = manifest_path.read_bytes()

        with self._create_context(project_dir) as context:
            assert context.is_fusion_manifest is False

        assert manifest_path.read_bytes() == v2_manifest
        assert (project_dir / "target" / "manifest.json").is_file()

    def test_replaces_dbt_core_manifest(self, tmp_path):
        """Without dbt v2 evidence, osmosis still writes its fresh dbt-core manifest."""
        project_dir = self._demo_project_with_manifest(
            tmp_path,
            {"metadata": {"dbt_schema_version": _V12_SCHEMA_URL, "dbt_version": "1.10.0"}},
        )

        with self._create_context(project_dir) as context:
            assert context.is_fusion_manifest is False
            dbt_core_version = context.dbt_version

        written = json.loads((project_dir / "target" / "manifest.json").read_text())
        assert written["metadata"]["dbt_version"] == dbt_core_version
        assert "model.jaffle_shop_duckdb.orders" in written["nodes"]
