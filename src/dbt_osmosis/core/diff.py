"""Schema diff and change detection module for dbt-osmosis.

This module provides functionality to detect and categorize schema changes
between YAML definitions and the actual database schema. It supports:

- Column additions and removals
- Column renames (detected via fuzzy matching)
- Data type changes
- Breaking vs non-breaking change classification
- Change impact assessment
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from dbt.contracts.graph.nodes import (  # pyright: ignore[reportPrivateImportUsage]
    ColumnInfo,
    ResultNode,
)
from dbt_common.contracts.metadata import (
    ColumnMetadata,  # pyright: ignore[reportPrivateImportUsage]
)
from rapidfuzz import fuzz, process

if t.TYPE_CHECKING:
    from dbt_osmosis.core.dbt_protocols import YamlRefactorContextProtocol

_INTEGER_NARROWING_ORDER = ["bigint", "int", "integer", "smallint", "tinyint"]

__all__ = [
    "ChangeCategory",
    "ChangeSeverity",
    "ColumnAdded",
    "ColumnRemoved",
    "ColumnRenamed",
    "ColumnTypeChanged",
    "SchemaChange",
    "SchemaDiff",
    "SchemaDiffResult",
]


def _replace_added_removed_changes_with_renames(
    changes: list[SchemaChange],
    renames: list[ColumnRenamed],
) -> list[SchemaChange]:
    renamed_added = {rename.new_name for rename in renames}
    renamed_removed = {rename.old_name for rename in renames}
    kept_changes = [
        change
        for change in changes
        if not _is_renamed_add_or_remove(change, renamed_added, renamed_removed)
    ]
    return [*kept_changes, *renames]


def _is_renamed_add_or_remove(
    change: SchemaChange,
    renamed_added: set[str],
    renamed_removed: set[str],
) -> bool:
    return (
        isinstance(change, ColumnAdded)
        and change.column_name in renamed_added
        or isinstance(change, ColumnRemoved)
        and change.column_name in renamed_removed
    )


def _extract_type_precision(type_str: str) -> tuple[str, int | None, int | None]:
    """Extract base type, precision, and scale from a type string."""
    import re

    match = re.match(r"(\w+)(?:\((\d+)(?:,(\d+))?\))?", type_str.lower())
    if match:
        base = match.group(1)
        precision = int(match.group(2)) if match.group(2) else None
        scale = int(match.group(3)) if match.group(3) else None
        return base, precision, scale
    return type_str.lower(), None, None


def _has_precision_narrowed(
    old_base: str,
    old_prec: int | None,
    old_scale: int | None,
    new_base: str,
    new_prec: int | None,
    new_scale: int | None,
) -> bool:
    return old_base == new_base and (
        bool(old_prec and new_prec and new_prec < old_prec)
        or bool(old_scale and new_scale and new_scale < old_scale)
    )


def _has_integer_narrowed(old_base: str, new_base: str) -> bool:
    if old_base not in _INTEGER_NARROWING_ORDER or new_base not in _INTEGER_NARROWING_ORDER:
        return False
    return _INTEGER_NARROWING_ORDER.index(old_base) < _INTEGER_NARROWING_ORDER.index(new_base)


class ChangeCategory(Enum):
    """Category of schema change for grouping and reporting."""

    COLUMN_ADDED = "column_added"
    COLUMN_REMOVED = "column_removed"
    COLUMN_RENAMED = "column_renamed"
    TYPE_CHANGED = "type_changed"
    METADATA_CHANGED = "metadata_changed"


class ChangeSeverity(Enum):
    """Severity level of a schema change for impact assessment."""

    SAFE = "safe"  # Non-breaking, can be applied automatically
    MODERATE = "moderate"  # May require review, generally safe
    BREAKING = "breaking"  # Requires manual review and planning


@dataclass(frozen=True)
class SchemaChange:
    """Base class for schema changes.

    Attributes:
        category: The type of change
        severity: Impact severity of the change
        node: The dbt node this change affects
        description: Human-readable description of the change
    """

    category: ChangeCategory
    severity: ChangeSeverity
    node: ResultNode
    description: str

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.description}"


@dataclass(frozen=True)
class ColumnAdded(SchemaChange):
    """A column that exists in the database but not in YAML.

    This is generally a safe change - adding columns to YAML is non-breaking.
    """

    column_name: str
    data_type: str | None = None
    comment: str | None = None

    def __post_init__(self) -> None:
        if self.description == "":
            object.__setattr__(
                self,
                "description",
                f"Column '{self.column_name}' added to {self.node.name}",
            )


@dataclass(frozen=True)
class ColumnRemoved(SchemaChange):
    """A column that exists in YAML but not in the database.

    This is a potentially breaking change - the column may have been dropped
    from the database, or it may be a YAML-only discrepancy.
    """

    column_name: str
    data_type: str | None = None

    def __post_init__(self) -> None:
        if self.description == "":
            object.__setattr__(
                self,
                "description",
                f"Column '{self.column_name}' removed from database in {self.node.name}",
            )


@dataclass(frozen=True)
class ColumnRenamed(SchemaChange):
    """A column that was renamed (detected via fuzzy matching).

    This is detected when a column in YAML closely matches a column in the
    database, but the names don't match exactly.
    """

    old_name: str
    new_name: str
    similarity_score: float
    data_type: str | None = None

    def __post_init__(self) -> None:
        if self.description == "":
            object.__setattr__(
                self,
                "description",
                f"Column '{self.old_name}' renamed to '{self.new_name}' in {self.node.name} "
                f"(similarity: {self.similarity_score:.1%})",
            )


@dataclass(frozen=True)
class ColumnTypeChanged(SchemaChange):
    """A column whose data type changed between YAML and database.

    The severity depends on the type change:
    - SAFE: precision/width changes (e.g., varchar(50) -> varchar(100))
    - MODERATE: compatible type changes (e.g., int -> bigint)
    - BREAKING: incompatible type changes (e.g., int -> text)
    """

    column_name: str
    old_type: str
    new_type: str

    def __post_init__(self) -> None:
        if self.description == "":
            object.__setattr__(
                self,
                "description",
                f"Column '{self.column_name}' type changed from {self.old_type} to {self.new_type} in {self.node.name}",
            )


@dataclass(frozen=True)
class SchemaDiffResult:
    """Result of a schema diff operation.

    Attributes:
        node: The dbt node that was compared
        yaml_columns: Columns defined in YAML
        database_columns: Columns from database introspection
        changes: List of detected changes
        summary: Summary statistics
    """

    node: ResultNode
    yaml_columns: dict[str, ColumnInfo]
    database_columns: dict[str, ColumnMetadata]
    changes: list[SchemaChange] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def summary(self) -> dict[str, int]:
        """Summary of changes by category."""
        summary: dict[str, int] = {}
        for change in self.changes:
            key = change.category.value
            summary[key] = summary.get(key, 0) + 1
        return summary

    @property
    def has_changes(self) -> bool:
        """Whether any changes were detected."""
        return len(self.changes) > 0

    @property
    def breaking_changes(self) -> list[SchemaChange]:
        """Filter changes to only breaking ones."""
        return [c for c in self.changes if c.severity == ChangeSeverity.BREAKING]

    @property
    def safe_changes(self) -> list[SchemaChange]:
        """Filter changes to only safe ones."""
        return [c for c in self.changes if c.severity == ChangeSeverity.SAFE]


class SchemaDiff:
    """Schema change detection and comparison engine.

    This class compares YAML schema definitions with database introspection
    results to detect and categorize schema changes.

    Example:
        >>> from dbt_osmosis.core.diff import SchemaDiff
        >>> diff = SchemaDiff(context)
        >>> result = diff.compare_node(node)
        >>> for change in result.changes:
        ...     print(change)
    """

    def __init__(
        self,
        context: YamlRefactorContextProtocol,
        *,
        fuzzy_match_threshold: float = 85.0,
        detect_column_renames: bool = True,
    ) -> None:
        self._context = context
        self._fuzzy_match_threshold = fuzzy_match_threshold
        self._rename_detection_enabled = detect_column_renames

    def compare_node(self, node: ResultNode) -> SchemaDiffResult:
        """Compare a single node's YAML schema with database schema.

        Args:
            node: The dbt node to compare

        Returns:
            SchemaDiffResult with detected changes
        """
        from dbt_osmosis.core.introspection import get_columns

        # Get YAML columns
        yaml_columns: dict[str, ColumnInfo] = node.columns

        # Get database columns
        database_columns = get_columns(self._context, node)

        yaml_columns_by_name, database_columns_by_name = self._comparison_columns_by_name(
            node, yaml_columns, database_columns
        )
        yaml_col_names = set(yaml_columns_by_name)
        db_col_names = set(database_columns_by_name)

        # Detect changes
        changes: list[SchemaChange] = []

        # Find added columns (in DB but not in YAML)
        added_columns = db_col_names - yaml_col_names
        changes.extend(self._column_additions(node, added_columns, database_columns_by_name))

        # Find removed columns (in YAML but not in DB)
        removed_columns = yaml_col_names - db_col_names
        removed_column_names, removals = self._column_removals(
            node, removed_columns, yaml_columns_by_name
        )
        changes.extend(removals)

        # Detect column renames via fuzzy matching
        changes = self._replace_renamed_columns(
            node,
            changes,
            added_columns,
            removed_columns,
            removed_column_names,
            database_columns,
            database_columns_by_name,
        )

        # Detect type changes for common columns
        common_columns = yaml_col_names & db_col_names
        changes.extend(
            self._column_type_changes(
                node, common_columns, yaml_columns_by_name, database_columns_by_name
            )
        )

        return SchemaDiffResult(
            node=node,
            yaml_columns=yaml_columns,
            database_columns=database_columns,  # pyright: ignore[reportArgumentType]
            changes=changes,
        )

    def _comparison_columns_by_name(
        self,
        node: ResultNode,
        yaml_columns: dict[str, ColumnInfo],
        database_columns: dict[str, ColumnMetadata],
    ) -> tuple[dict[str, ColumnInfo], dict[str, tuple[str, ColumnMetadata]]]:
        from dbt_osmosis.core.introspection import normalize_column_name

        credentials_type = self._context.project.runtime_cfg.credentials.type
        case_insensitive = self._case_insensitive_output_enabled(node)

        def _yaml_compare_name(column_name: str) -> str:
            normalized = normalize_column_name(column_name, credentials_type)
            return normalized.lower() if case_insensitive else normalized

        def _db_compare_name(column_name: str) -> str:
            if case_insensitive:
                return normalize_column_name(column_name, credentials_type).lower()
            return column_name

        return (
            {_yaml_compare_name(c.name): c for c in yaml_columns.values()},
            {_db_compare_name(name): (name, column) for name, column in database_columns.items()},
        )

    def _case_insensitive_output_enabled(self, node: ResultNode) -> bool:
        from dbt_osmosis.core.introspection import resolve_setting

        output_to_upper = bool(
            resolve_setting(
                self._context,
                "output-to-upper",
                node,
                fallback=bool(self._context.settings.output_to_upper),
            )
        )
        output_to_lower = bool(
            resolve_setting(
                self._context,
                "output-to-lower",
                node,
                fallback=bool(self._context.settings.output_to_lower),
            )
        )
        return output_to_upper or output_to_lower

    def _column_additions(
        self,
        node: ResultNode,
        added_columns: set[str],
        database_columns_by_name: dict[str, tuple[str, ColumnMetadata]],
    ) -> list[ColumnAdded]:
        changes: list[ColumnAdded] = []
        for col_name in added_columns:
            original_col_name, col_meta = database_columns_by_name[col_name]
            changes.append(
                ColumnAdded(
                    category=ChangeCategory.COLUMN_ADDED,
                    severity=ChangeSeverity.SAFE,
                    node=node,
                    description="",
                    column_name=original_col_name,
                    data_type=col_meta.type,
                    comment=col_meta.comment,
                )
            )
        return changes

    def _column_removals(
        self,
        node: ResultNode,
        removed_columns: set[str],
        yaml_columns_by_name: dict[str, ColumnInfo],
    ) -> tuple[list[str], list[ColumnRemoved]]:
        from dbt_osmosis.core.introspection import normalize_column_name

        credentials_type = self._context.project.runtime_cfg.credentials.type
        removed_column_names: list[str] = []
        changes: list[ColumnRemoved] = []
        for col_name in removed_columns:
            original_col = yaml_columns_by_name.get(col_name)
            original_col_name = (
                normalize_column_name(original_col.name, credentials_type)
                if original_col
                else col_name
            )
            removed_column_names.append(original_col_name)
            changes.append(
                ColumnRemoved(
                    category=ChangeCategory.COLUMN_REMOVED,
                    severity=ChangeSeverity.MODERATE,
                    node=node,
                    description="",
                    column_name=original_col_name,
                    data_type=original_col.data_type if original_col else None,
                )
            )
        return removed_column_names, changes

    def _replace_renamed_columns(
        self,
        node: ResultNode,
        changes: list[SchemaChange],
        added_columns: set[str],
        removed_columns: set[str],
        removed_column_names: list[str],
        database_columns: dict[str, ColumnMetadata],
        database_columns_by_name: dict[str, tuple[str, ColumnMetadata]],
    ) -> list[SchemaChange]:
        if not self._rename_detection_enabled or not added_columns or not removed_columns:
            return changes

        renames = self._detect_column_renames(
            removed_column_names,
            [database_columns_by_name[col_name][0] for col_name in added_columns],
            database_columns,
            node,
        )
        return _replace_added_removed_changes_with_renames(changes, renames)

    def _column_type_changes(
        self,
        node: ResultNode,
        common_columns: set[str],
        yaml_columns_by_name: dict[str, ColumnInfo],
        database_columns_by_name: dict[str, tuple[str, ColumnMetadata]],
    ) -> list[ColumnTypeChanged]:
        changes: list[ColumnTypeChanged] = []
        for col_name in common_columns:
            change = self._column_type_change(
                node,
                yaml_columns_by_name.get(col_name),
                database_columns_by_name[col_name],
            )
            if change is not None:
                changes.append(change)
        return changes

    def _column_type_change(
        self,
        node: ResultNode,
        yaml_col: ColumnInfo | None,
        db_column: tuple[str, ColumnMetadata],
    ) -> ColumnTypeChanged | None:
        original_db_col_name, db_col = db_column
        if not yaml_col or not db_col:
            return None

        old_type = yaml_col.data_type or "unknown"
        new_type = db_col.type
        if self._normalize_comparable_type(old_type) == self._normalize_comparable_type(new_type):
            return None

        return ColumnTypeChanged(
            category=ChangeCategory.TYPE_CHANGED,
            severity=self._classify_type_change(old_type, new_type),
            node=node,
            description="",
            column_name=original_db_col_name,
            old_type=old_type,
            new_type=new_type,
        )

    def compare_all(
        self,
        nodes: t.Iterable[ResultNode] | None = None,
    ) -> dict[str, SchemaDiffResult]:
        """Compare multiple nodes.

        Args:
            nodes: Iterable of nodes to compare. If None, uses context nodes.

        Returns:
            Dict mapping node unique_id to SchemaDiffResult
        """
        if nodes is None:
            from dbt_osmosis.core.node_filters import _iter_candidate_nodes

            nodes = [n for _, n in _iter_candidate_nodes(self._context)]

        results = {}
        for node in nodes:
            result = self.compare_node(node)
            if result.has_changes:
                results[node.unique_id] = result

        return results

    def _detect_column_renames(
        self,
        removed: list[str],
        added: list[str],
        database_columns: dict[str, ColumnMetadata],
        node: ResultNode,
    ) -> list[ColumnRenamed]:
        """Detect column renames using fuzzy string matching.

        Args:
            removed: Column names in YAML but not in database
            added: Column names in database but not in YAML
            database_columns: Database column metadata for type info
            node: The dbt node being compared

        Returns:
            List of ColumnRenamed changes
        """
        renames: list[ColumnRenamed] = []
        available_added = sorted(added)

        for old_name in sorted(removed):
            # Use fuzzy matching to find potential rename
            match = process.extractOne(
                old_name,
                available_added,
                scorer=fuzz.WRatio,
                score_cutoff=int(self._fuzzy_match_threshold),
            )

            if match and match[1] >= self._fuzzy_match_threshold:
                new_name = match[0]
                similarity = match[1]

                renames.append(
                    ColumnRenamed(
                        category=ChangeCategory.COLUMN_RENAMED,
                        severity=ChangeSeverity.SAFE,
                        # compare_node already knows the affected node; relying on
                        # mutable context state here can misattribute or crash renames.
                        node=node,
                        description="",
                        old_name=old_name,
                        new_name=new_name,
                        similarity_score=similarity,
                        data_type=database_columns[new_name].type,
                    )
                )
                available_added.remove(new_name)

        return renames

    @staticmethod
    def _normalize_comparable_type(data_type: str) -> str:
        """Normalize a data type string only for conservative equality checks."""
        return "".join(data_type.lower().split())

    def _classify_type_change(self, old_type: str, new_type: str) -> ChangeSeverity:
        """Classify the severity of a data type change.

        Args:
            old_type: Original data type
            new_type: New data type

        Returns:
            ChangeSeverity classification
        """
        # Normalize types for comparison
        old_norm = self._normalize_comparable_type(old_type)
        new_norm = self._normalize_comparable_type(new_type)

        # Same type = safe
        if old_norm == new_norm:
            return ChangeSeverity.SAFE

        # Type family changes (breaking)
        type_families = {
            "integer": {"int", "integer", "smallint", "bigint", "tinyint"},
            "float": {"float", "double", "real", "doubleprecision"},
            "text": {"text", "varchar", "char", "character", "string", "clob"},
            "boolean": {"bool", "boolean", "bit"},
            "timestamp": {"timestamp", "datetime", "timestamptz"},
            "date": {"date"},
            "numeric": {"numeric", "decimal", "number", "dec"},
        }

        # Check if types are in the same family
        for types in type_families.values():
            if any(t in old_norm for t in types) and any(t in new_norm for t in types):
                # Same family - generally safe (e.g., int -> bigint, varchar(50) -> varchar(100))
                # But narrowing is potentially breaking
                if self._is_type_narrowing(old_norm, new_norm):
                    return ChangeSeverity.MODERATE
                return ChangeSeverity.SAFE

        # Different families = breaking
        return ChangeSeverity.BREAKING

    def _is_type_narrowing(self, old_type: str, new_type: str) -> bool:
        """Check if a type change narrows precision (potentially breaking).

        Args:
            old_type: Original data type
            new_type: New data type

        Returns:
            True if the new type is narrower than the old type
        """
        old_base, old_prec, old_scale = _extract_type_precision(old_type)
        new_base, new_prec, new_scale = _extract_type_precision(new_type)

        # Check for precision narrowing (e.g., varchar(100) -> varchar(50))
        if _has_precision_narrowed(
            old_base,
            old_prec,
            old_scale,
            new_base,
            new_prec,
            new_scale,
        ):
            return True

        # Check for integer narrowing (e.g., bigint -> int -> smallint)
        return _has_integer_narrowed(old_base, new_base)
