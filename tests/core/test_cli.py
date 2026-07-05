# pyright: reportPrivateImportUsage=false, reportPrivateUsage=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportAny=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportFunctionMemberAccess=false, reportUnknownVariableType=false, reportUnusedParameter=false

import subprocess
import typing as t
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest
from click.testing import CliRunner

from dbt_osmosis.cli.main import cli
from dbt_osmosis.core.diff import ChangeCategory, ChangeSeverity, ColumnAdded, SchemaDiffResult
from dbt_osmosis.core.discovery import DiscoveryResult, DocumentationGap
from dbt_osmosis.core.exceptions import LLMConfigurationError
from dbt_osmosis.core.generators import DocumentationCheckResult
from dbt_osmosis.core.settings import YamlRefactorContext
from dbt_osmosis.core.sql_lint import LintLevel, LintResult, LintViolation
from dbt_osmosis.core.validation import (
    ModelValidationResult,
    ModelValidationStatus,
    ValidationReport,
)
from dbt_osmosis.core.voice_learning import ProjectStyleProfile


@pytest.fixture(scope="module")
def runner() -> CliRunner:
    """Create a Click CliRunner for testing CLI commands."""
    return CliRunner()


def test_cli_group(runner: CliRunner) -> None:
    """Test that the main CLI group is accessible and shows help."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "dbt-osmosis" in result.output
    assert "yaml" in result.output
    assert "sql" in result.output
    assert "test" in result.output
    assert "workbench" in result.output
    assert "migration" in result.output
    assert "validate" in result.output
    assert "analyze" in result.output


def test_yaml_group(runner: CliRunner) -> None:
    """Test that the yaml command group is accessible."""
    result = runner.invoke(cli, ["yaml", "--help"])
    assert result.exit_code == 0
    assert "Manage, document, and organize dbt YAML files" in result.output
    assert "refactor" in result.output
    assert "organize" in result.output
    assert "document" in result.output


def test_sql_group(runner: CliRunner) -> None:
    """Test that the sql command group is accessible."""
    result = runner.invoke(cli, ["sql", "--help"])
    assert result.exit_code == 0
    assert "Execute and compile dbt SQL statements" in result.output
    assert "run" in result.output
    assert "compile" in result.output


def test_migration_group(runner: CliRunner) -> None:
    """Test that the migration command group exposes plan generation."""
    result = runner.invoke(cli, ["migration", "--help"])
    assert result.exit_code == 0
    assert "Plan database migrations" in result.output
    assert "plan" in result.output


def test_validate_group(runner: CliRunner) -> None:
    """Test that the validate command group exposes model validation."""
    result = runner.invoke(cli, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate dbt models" in result.output
    assert "models" in result.output


def test_analyze_group(runner: CliRunner) -> None:
    """Test that the analyze command group exposes documentation analysis."""
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "Analyze documentation" in result.output
    assert "docs" in result.output
    assert "style" in result.output
    assert "discover" in result.output


def test_yaml_refactor_help(runner: CliRunner) -> None:
    """Test that the yaml refactor command shows help with all options."""
    result = runner.invoke(cli, ["yaml", "refactor", "--help"])
    assert result.exit_code == 0
    assert "--project-dir" in result.output
    assert "--profiles-dir" in result.output
    assert "--dry-run" in result.output
    assert "--check" in result.output
    assert "--synthesize" in result.output
    assert "--fusion-compat" in result.output
    assert "discovered project root" in result.output


def test_fusion_compat_flag_in_yaml_commands(runner: CliRunner) -> None:
    """Test that --fusion-compat and --no-fusion-compat flags appear in yaml commands."""
    for cmd in ["refactor", "organize", "document"]:
        result = runner.invoke(cli, ["yaml", cmd, "--help"])
        assert result.exit_code == 0
        assert "--fusion-compat" in result.output, (
            f"--fusion-compat flag missing from yaml {cmd} command"
        )


def test_yaml_organize_help(runner: CliRunner) -> None:
    """Test that the yaml organize command shows help."""
    result = runner.invoke(cli, ["yaml", "organize", "--help"])
    assert result.exit_code == 0
    assert "--project-dir" in result.output
    assert "--auto-apply" in result.output


def test_yaml_document_help(runner: CliRunner) -> None:
    """Test that the yaml document command shows help."""
    result = runner.invoke(cli, ["yaml", "document", "--help"])
    assert result.exit_code == 0
    assert "--project-dir" in result.output
    assert "--synthesize" in result.output
    assert "--use-unrendered-descriptions" in result.output


def test_sql_run_help(runner: CliRunner) -> None:
    """Test that the sql run command shows help."""
    result = runner.invoke(cli, ["sql", "run", "--help"])
    assert result.exit_code == 0
    assert "SQL" in result.output


def test_test_group(runner: CliRunner) -> None:
    """Test that the test command group is accessible."""
    result = runner.invoke(cli, ["test", "--help"])
    assert result.exit_code == 0
    assert "Suggest and generate dbt tests" in result.output
    assert "suggest" in result.output


def test_test_suggest_help(runner: CliRunner) -> None:
    """Test that the test suggest command shows help."""
    result = runner.invoke(cli, ["test", "suggest", "--help"])
    assert result.exit_code == 0
    assert "--project-dir" in result.output
    assert "--use-ai" in result.output
    assert "--pattern-only" in result.output
    assert "--format" in result.output


def test_sql_compile_help(runner: CliRunner) -> None:
    """Test that the sql compile command shows help."""
    result = runner.invoke(cli, ["sql", "compile", "--help"])
    assert result.exit_code == 0
    assert "SQL" in result.output


def test_sql_compile_plain_sql_outputs_sql(
    runner: CliRunner, yaml_context: YamlRefactorContext
) -> None:
    """Plain SQL compile should print executable SQL, not None."""
    project_dir = str(yaml_context.project.runtime_cfg.project_root)

    with mock.patch(
        "dbt_osmosis.cli.main.create_dbt_project_context",
        return_value=yaml_context.project,
    ):
        result = runner.invoke(
            cli,
            [
                "sql",
                "compile",
                "--project-dir",
                project_dir,
                "--profiles-dir",
                project_dir,
                "select 1",
            ],
        )

    assert result.exit_code == 0
    assert result.output.strip().splitlines()[-1] == "select 1"


def test_sql_compile_uses_project_local_profiles_dir_when_omitted(
    runner: CliRunner,
) -> None:
    """dbt_opts should resolve omitted profiles-dir from the effective project-dir."""
    project_dir = Path("demo_duckdb").resolve()
    project = mock.Mock()

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=project,
        ) as create_context,
        mock.patch(
            "dbt_osmosis.cli.main.compile_sql_code",
            return_value=SimpleNamespace(compiled_code="select 1"),
        ),
    ):
        result = runner.invoke(
            cli,
            [
                "sql",
                "compile",
                "--project-dir",
                str(project_dir),
                "select 1",
            ],
        )

    assert result.exit_code == 0
    settings = create_context.call_args.args[0]
    assert settings.project_dir == str(project_dir)
    assert settings.profiles_dir == str(project_dir)


def test_sql_compile_preserves_explicit_profiles_dir(
    runner: CliRunner,
) -> None:
    """Explicit profiles-dir values should pass through without rediscovery."""
    project_dir = Path("demo_duckdb").resolve()
    explicit_profiles_dir = "demo_duckdb"
    project = mock.Mock()

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=project,
        ) as create_context,
        mock.patch(
            "dbt_osmosis.cli.main.compile_sql_code",
            return_value=SimpleNamespace(compiled_code="select 1"),
        ),
    ):
        result = runner.invoke(
            cli,
            [
                "sql",
                "compile",
                "--project-dir",
                str(project_dir),
                "--profiles-dir",
                explicit_profiles_dir,
                "select 1",
            ],
        )

    assert result.exit_code == 0
    settings = create_context.call_args.args[0]
    assert settings.project_dir == str(project_dir)
    assert settings.profiles_dir == explicit_profiles_dir


def test_diff_schema_passes_positional_selectors_to_refactor_settings(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """diff schema positional selectors should scope the compared node set."""
    compared_nodes = []

    def compare_node(_self, node):
        compared_nodes.append(node.name)
        return SchemaDiffResult(
            node=node,
            yaml_columns={},
            database_columns={},
            changes=[],
        )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.core.diff.SchemaDiff.compare_node", compare_node),
    ):
        result = runner.invoke(
            cli,
            [
                "diff",
                "schema",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "customers",
            ],
        )

    assert result.exit_code == 0
    assert compared_nodes == ["customers"]


def test_diff_schema_preserves_unknown_positional_selector_for_empty_selection(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """Unknown positional selectors should not be broadened to all nodes."""
    compared_nodes = []

    def compare_node(_self, node):
        compared_nodes.append(node.name)
        return SchemaDiffResult(
            node=node,
            yaml_columns={},
            database_columns={},
            changes=[],
        )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.core.diff.SchemaDiff.compare_node", compare_node),
    ):
        result = runner.invoke(
            cli,
            [
                "diff",
                "schema",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "missing_model",
            ],
        )

    assert result.exit_code == 0
    assert compared_nodes == []


def test_migration_plan_generates_sql_from_schema_diff(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """migration plan should expose MigrationPlanner through the CLI."""
    node = yaml_context.project.manifest.nodes["model.jaffle_shop_duckdb.customers"]
    diff_result = SchemaDiffResult(
        node=node,
        yaml_columns={},
        database_columns={},
        changes=[
            ColumnAdded(
                category=ChangeCategory.COLUMN_ADDED,
                severity=ChangeSeverity.SAFE,
                node=node,
                description="",
                column_name="new_metric",
                data_type="INTEGER",
            )
        ],
    )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch(
            "dbt_osmosis.cli.main.SchemaDiff.compare_all",
            return_value={node.unique_id: diff_result},
        ),
    ):
        result = runner.invoke(
            cli,
            [
                "migration",
                "plan",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "customers",
            ],
        )

    assert result.exit_code == 0
    assert "dbt-osmosis migration plans" in result.output
    assert "ALTER TABLE" in result.output
    assert "ADD COLUMN" in result.output
    assert "new_metric" in result.output


def test_validate_models_command_exits_nonzero_on_failed_validation(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """validate models should expose core validation and fail on failed results."""
    report = ValidationReport()
    report.add_result(
        ModelValidationResult(
            model_name="customers",
            unique_id="model.jaffle_shop_duckdb.customers",
            status=ModelValidationStatus.EXECUTION_ERROR,
            error_message="relation missing",
            execution_time_seconds=0.1,
        )
    )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.cli.main.validate_models", return_value=report) as validate_call,
    ):
        result = runner.invoke(
            cli,
            [
                "validate",
                "models",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "customers",
            ],
        )

    assert result.exit_code == 1
    assert "Model validation summary" in result.output
    assert "Failed: 1" in result.output
    selected_models = validate_call.call_args.args[1]
    assert [node.name for _, node in selected_models] == ["customers"]


def test_analyze_docs_exits_nonzero_when_coverage_threshold_fails(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """analyze docs should expose documentation checking with CI-friendly exits."""
    doc_result = DocumentationCheckResult(
        total_models=1,
        models_with_descriptions=1,
        models_without_descriptions=0,
        total_columns=2,
        documented_columns=1,
        undocumented_columns=1,
        gaps=[SimpleNamespace(description="Column customer_id is too short")],
    )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.cli.main.check_documentation", return_value=doc_result) as check,
    ):
        result = runner.invoke(
            cli,
            [
                "analyze",
                "docs",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--model-filter",
                "customers",
                "--min-column-coverage",
                "100",
            ],
        )

    assert result.exit_code == 1
    assert "Documentation check summary" in result.output
    assert "Columns documented: 1/2 (50.0%)" in result.output
    assert check.call_args.kwargs["model_filter"] == "customers"


def test_analyze_style_can_render_prompt_context(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """analyze style should expose the voice-learning profile as prompt context."""
    profile = ProjectStyleProfile(
        description_length_stats={"avg_length": 8.0, "min_length": 4.0, "max_length": 12.0},
        common_phrases=[("customer identifier", 3)],
        model_description_samples=["Customer dimension model"],
        column_description_samples=["Unique customer identifier"],
    )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch(
            "dbt_osmosis.cli.main.analyze_project_documentation_style",
            return_value=profile,
        ) as analyze_call,
    ):
        result = runner.invoke(
            cli,
            [
                "analyze",
                "style",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--format",
                "prompt",
                "--max-examples",
                "1",
            ],
        )

    assert result.exit_code == 0
    assert "Target description length: ~8 words" in result.output
    assert "Customer dimension model" in result.output
    assert analyze_call.call_args.kwargs["max_nodes"] == 50


def test_analyze_discover_check_exits_nonzero_when_gaps_exist(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """analyze discover should expose prioritized documentation discovery."""
    node = yaml_context.project.manifest.nodes["model.jaffle_shop_duckdb.customers"]
    discovery_result = DiscoveryResult(
        gaps=[
            DocumentationGap(
                node=node,
                gap_type="missing",
                description="Model has no description",
                current_doc=None,
                priority=75.0,
                reason="Gap type: missing",
            )
        ],
        total_models=1,
        total_columns=3,
        coverage_percent=0.0,
        scan_time=mock.Mock(),
        duration_seconds=0.01,
    )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch(
            "dbt_osmosis.cli.main.discover_undocumented_models",
            return_value=discovery_result,
        ) as discover_models,
    ):
        result = runner.invoke(
            cli,
            [
                "analyze",
                "discover",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--scope",
                "models",
                "--check",
            ],
        )

    assert result.exit_code == 1
    assert "Models discovery summary" in result.output
    assert "Model has no description" in result.output
    discover_models.assert_called_once()


def test_lint_file_passes_disabled_rules_and_does_not_duplicate_warning_output(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """lint file should honor disabled rules and avoid repeating warnings under Other."""
    lint_result = LintResult(
        violations=[
            LintViolation("warn-rule", "warning", LintLevel.WARNING),
            LintViolation("info-rule", "info", LintLevel.INFO),
        ]
    )

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.cli.main.lint_sql_code", return_value=lint_result) as lint_sql,
    ):
        result = runner.invoke(
            cli,
            [
                "lint",
                "file",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--disable-rules",
                "select-star",
                "select * from users",
            ],
        )

    assert result.exit_code == 1
    assert lint_sql.call_args.kwargs["disabled_rules"] == ["select-star"]
    assert result.output.count("warn-rule") == 1
    assert result.output.count("info-rule") == 1
    assert ":information_source: Other:" in result.output


def test_lint_model_does_not_duplicate_warning_output(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """lint model should not repeat error/warning violations under Other."""
    lint_result = LintResult(
        violations=[
            LintViolation("warn-rule", "warning", LintLevel.WARNING),
            LintViolation("info-rule", "info", LintLevel.INFO),
        ]
    )
    linter = mock.Mock()
    linter.lint_model.return_value = lint_result

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.cli.main.SQLLinter", return_value=linter),
    ):
        result = runner.invoke(
            cli,
            [
                "lint",
                "model",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "customers",
            ],
        )

    assert result.exit_code == 1
    assert result.output.count("warn-rule") == 1
    assert result.output.count("info-rule") == 1


def test_lint_project_does_not_duplicate_warning_output(
    runner: CliRunner,
    yaml_context: YamlRefactorContext,
) -> None:
    """lint project should not repeat error/warning violations as information."""
    lint_result = LintResult(
        violations=[
            LintViolation("warn-rule", "warning", LintLevel.WARNING),
            LintViolation("info-rule", "info", LintLevel.INFO),
        ]
    )
    linter = mock.Mock()
    linter.lint_project.return_value = {"customers": lint_result}

    with (
        mock.patch(
            "dbt_osmosis.cli.main.create_dbt_project_context",
            return_value=yaml_context.project,
        ),
        mock.patch("dbt_osmosis.cli.main.SQLLinter", return_value=linter),
    ):
        result = runner.invoke(
            cli,
            [
                "lint",
                "project",
                "--project-dir",
                str(yaml_context.project.runtime_cfg.project_root),
                "--profiles-dir",
                str(yaml_context.project.runtime_cfg.project_root),
            ],
        )

    assert result.exit_code == 1
    assert result.output.count("warn-rule") == 1
    assert result.output.count("info-rule") == 1


def test_workbench_help(runner: CliRunner) -> None:
    """Test that the workbench command shows help."""
    result = runner.invoke(cli, ["workbench", "--help"])
    assert result.exit_code == 0
    assert "discovered project root" in result.output
    assert "--host" in result.output
    assert "--port" in result.output
    assert "--enable-external-feed" in result.output


def test_workbench_uses_streamlit_server_bind_flags_and_preserves_passthrough(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workbench host/port should bind Streamlit's server, not browser defaults."""
    completed: subprocess.CompletedProcess[t.Any] = subprocess.CompletedProcess(
        args=[], returncode=0
    )
    monkeypatch.setattr("shutil.which", lambda name: "streamlit")
    monkeypatch.setattr("importlib.import_module", lambda name: object())
    with mock.patch.object(subprocess, "run", return_value=completed) as run:
        result = runner.invoke(
            cli,
            [
                "workbench",
                "--host",
                "0.0.0.0",
                "--port",
                "8502",
                "--server.headless=true",
                "--theme.base=dark",
            ],
        )

    assert result.exit_code == 0
    command = run.call_args.args[0]
    assert "--server.address=0.0.0.0" in command
    assert "--server.port=8502" in command
    assert "--browser.serverAddress=0.0.0.0" not in command
    assert "--browser.serverPort=8502" not in command
    script_path_index = next(i for i, value in enumerate(command) if str(value).endswith("app.py"))
    assert command[script_path_index - 2 : script_path_index] == [
        "--server.headless=true",
        "--theme.base=dark",
    ]


def test_workbench_enable_external_feed_passes_app_opt_in(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """External RSS feed should require an explicit app-level opt-in."""
    completed: subprocess.CompletedProcess[t.Any] = subprocess.CompletedProcess(
        args=[], returncode=0
    )
    monkeypatch.setattr("shutil.which", lambda name: "streamlit")
    monkeypatch.setattr("importlib.import_module", lambda name: object())
    with mock.patch.object(subprocess, "run", return_value=completed) as run:
        result = runner.invoke(cli, ["workbench", "--enable-external-feed"])

    assert result.exit_code == 0
    command = run.call_args.args[0]
    script_path_index = next(i for i, value in enumerate(command) if str(value).endswith("app.py"))
    assert "--enable-external-feed" not in command[:script_path_index]
    script_args = command[script_path_index + 1 :]
    assert script_args[0] == "--"
    assert "--enable-external-feed" in script_args


def test_workbench_uses_project_local_profiles_dir_when_omitted(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workbench should pass the project-local profiles dir to the app when omitted."""
    project_dir = Path("demo_duckdb").resolve()
    completed: subprocess.CompletedProcess[t.Any] = subprocess.CompletedProcess(
        args=[], returncode=0
    )
    monkeypatch.setattr("shutil.which", lambda name: "streamlit")
    monkeypatch.setattr("importlib.import_module", lambda name: object())

    with mock.patch.object(subprocess, "run", return_value=completed) as run:
        result = runner.invoke(
            cli,
            [
                "workbench",
                "--project-dir",
                str(project_dir),
            ],
        )

    assert result.exit_code == 0
    command = run.call_args.args[0]
    script_path_index = next(i for i, value in enumerate(command) if str(value).endswith("app.py"))
    script_args = command[script_path_index + 1 :]
    assert script_args[0] == "--"
    profiles_dir_index = script_args.index("--profiles-dir")
    assert script_args[profiles_dir_index + 1] == str(project_dir)


def test_workbench_preserves_literal_double_dash_passthrough(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Click's literal -- pass-through should still become Streamlit args."""
    completed: subprocess.CompletedProcess[t.Any] = subprocess.CompletedProcess(
        args=[], returncode=0
    )
    monkeypatch.setattr("shutil.which", lambda name: "streamlit")
    monkeypatch.setattr("importlib.import_module", lambda name: object())
    with mock.patch.object(subprocess, "run", return_value=completed) as run:
        result = runner.invoke(
            cli,
            ["workbench", "--", "--server.headless=true"],
        )

    assert result.exit_code == 0
    command = run.call_args.args[0]
    script_path_index = next(i for i, value in enumerate(command) if str(value).endswith("app.py"))
    assert command[script_path_index - 1] == "--server.headless=true"


@pytest.mark.parametrize(
    "args",
    [
        ["workbench"],
        ["workbench", "--options"],
        ["workbench", "--config"],
    ],
)
def test_workbench_missing_streamlit_has_workbench_extra_hint(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
) -> None:
    """All workbench launch paths should fail clearly when Streamlit is absent."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    with mock.patch("subprocess.run", side_effect=FileNotFoundError("streamlit")):
        result = runner.invoke(cli, args)

    assert result.exit_code != 0
    assert "Streamlit is required" in result.output
    assert "pip install dbt-osmosis[workbench]" in result.output


def test_workbench_missing_extra_dependency_has_workbench_extra_hint(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Normal launch should preflight app imports, not defer raw app tracebacks."""
    monkeypatch.setattr("shutil.which", lambda name: "streamlit")

    def import_module(name: str) -> object:
        if name == "feedparser":
            raise ModuleNotFoundError("No module named 'feedparser'", name=name)
        return object()

    monkeypatch.setattr("importlib.import_module", import_module)
    with mock.patch.object(subprocess, "run") as run:
        result = runner.invoke(cli, ["workbench"])

    assert result.exit_code != 0
    assert "Workbench optional dependencies are missing: feedparser" in result.output
    assert "pip install dbt-osmosis[workbench]" in result.output
    run.assert_not_called()


def test_workbench_transitive_import_failure_has_workbench_extra_hint(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workbench preflight should catch transitive import failures before Streamlit."""
    monkeypatch.setattr("shutil.which", lambda name: "streamlit")

    def import_module(name: str) -> object:
        if name == "ydata_profiling":
            raise ImportError("No module named 'IPython'")
        return object()

    monkeypatch.setattr("importlib.import_module", import_module)
    with mock.patch.object(subprocess, "run") as run:
        result = runner.invoke(cli, ["workbench"])

    assert result.exit_code != 0
    assert "Workbench optional dependencies are missing" in result.output
    assert "ydata_profiling" in result.output
    assert "IPython" in result.output
    assert "pip install dbt-osmosis[workbench]" in result.output
    run.assert_not_called()


def test_test_llm_command(runner: CliRunner) -> None:
    """Test the test_llm command exists and is callable."""
    result = runner.invoke(cli, ["test-llm"])
    # Should not crash, should provide helpful output about missing env vars
    assert (
        result.exit_code in [0, 1]
        or "LLM_PROVIDER" in result.output
        or "openai" in result.output.lower()
    )


def test_test_llm_defaults_to_openai_and_resolves_once(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """test-llm should use the default OpenAI provider without requiring LLM_PROVIDER."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    mock_client = mock.Mock()

    with mock.patch(
        "dbt_osmosis.core.llm.get_llm_client",
        return_value=(mock_client, "gpt-4o"),
    ) as get_client:
        result = runner.invoke(cli, ["test-llm"])

    assert result.exit_code == 0
    assert "Provider: openai" in result.output
    assert "Model Engine: gpt-4o" in result.output
    get_client.assert_called_once_with()


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (LLMConfigurationError("OPENAI_API_KEY not set for OpenAI provider"), "OPENAI_API_KEY"),
        (LLMConfigurationError("Invalid LLM provider 'bogus'"), "Invalid LLM provider"),
        (
            ImportError("OpenAI is not installed. Please install dbt-osmosis[openai]"),
            "dbt-osmosis[openai]",
        ),
    ],
)
def test_test_llm_reports_friendly_click_errors(
    runner: CliRunner,
    error: Exception,
    expected: str,
) -> None:
    """LLM config failures should be nonzero Click errors instead of tracebacks."""
    with mock.patch("dbt_osmosis.core.llm.get_llm_client", side_effect=error):
        result = runner.invoke(cli, ["test-llm"])

    assert result.exit_code != 0
    assert "Error:" in result.output
    assert expected in result.output


def test_test_suggest_pattern_only_reports_ai_disabled(
    runner: CliRunner,
) -> None:
    """Pattern-only mode should be explicit and not invoke AI suggestions."""
    mock_project = mock.Mock()

    with (
        mock.patch("dbt_osmosis.cli.main.create_dbt_project_context", return_value=mock_project),
        mock.patch("dbt_osmosis.cli.main.YamlRefactorContext", return_value=mock.Mock()),
        mock.patch(
            "dbt_osmosis.cli.main.suggest_tests_for_project", return_value={}
        ) as suggest_project,
    ):
        result = runner.invoke(cli, ["test", "suggest", "--pattern-only"])

    assert result.exit_code == 0
    assert "Pattern-only test suggestions enabled" in result.output
    suggest_project.assert_called_once()
    assert suggest_project.call_args.kwargs["use_ai"] is False


def test_test_suggest_default_reports_ai_enabled(
    runner: CliRunner,
) -> None:
    """Default suggestion mode should visibly tell users AI is on with fallback."""
    mock_project = mock.Mock()

    with (
        mock.patch("dbt_osmosis.cli.main.create_dbt_project_context", return_value=mock_project),
        mock.patch("dbt_osmosis.cli.main.YamlRefactorContext", return_value=mock.Mock()),
        mock.patch(
            "dbt_osmosis.cli.main.suggest_tests_for_project", return_value={}
        ) as suggest_project,
    ):
        result = runner.invoke(cli, ["test", "suggest"])

    assert result.exit_code == 0
    assert "AI test suggestions are enabled by default" in result.output
    assert "falls back to pattern-based suggestions" in result.output
    suggest_project.assert_called_once()
    assert suggest_project.call_args.kwargs["use_ai"] is True


def test_version_option(runner: CliRunner) -> None:
    """Test that --version works."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0


def test_formatter_flag_in_yaml_commands(runner: CliRunner) -> None:
    """Test that --formatter flag appears in help for all yaml subcommands."""
    for cmd in ["refactor", "organize", "document"]:
        result = runner.invoke(cli, ["yaml", cmd, "--help"])
        assert result.exit_code == 0
        assert "--formatter" in result.output, f"--formatter flag missing from yaml {cmd} command"


def test_invalid_command(runner: CliRunner) -> None:
    """Test that invalid commands produce a helpful error."""
    result = runner.invoke(cli, ["invalid-command"])
    assert result.exit_code != 0
    assert "No such command" in result.output
