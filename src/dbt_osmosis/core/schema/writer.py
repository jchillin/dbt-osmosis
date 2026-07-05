"""YAML file writing for dbt-osmosis.

Thread-safety:
    - _write_yaml() acquires yaml_handler_lock for the entire write operation
    - Cache invalidation is performed under _YAML_BUFFER_CACHE_LOCK
    - Multiple threads can safely write to different files concurrently
"""

import io
import os
import secrets
import stat
import threading
import typing as t
from pathlib import Path

import ruamel.yaml

from dbt_osmosis.core import logger
from dbt_osmosis.core.schema.parser import _partition_yaml_top_level_sections
from dbt_osmosis.core.schema.reader import (
    _YAML_BUFFER_CACHE,
    _YAML_BUFFER_CACHE_LOCK,
    _YAML_ORIGINAL_CACHE,
    _discard_yaml_caches,
)

__all__ = [
    "_merge_preserved_sections",
    "_write_yaml",
    "commit_yamls",
]


def _merge_preserved_sections(
    filtered_data: dict[str, t.Any], original_data: dict[str, t.Any]
) -> dict[str, t.Any]:
    """Merge preserved top-level sections from original YAML.

    When dbt-osmosis processes a YAML file, it filters out top-level sections that it
    does not manage directly. This function restores every preserved section from the
    original file so mixed schema files do not lose snapshots, exposures, anchors,
    semantic models, or any future dbt keys that dbt-osmosis still ignores.

    Args:
        filtered_data: The processed YAML data (may have models, sources, etc.)
        original_data: The original unfiltered YAML data with unmanaged top-level keys

    Returns:
        A merged dictionary containing both processed and preserved sections.

    """
    # Preserve the original top-level order so anchors defined in unmanaged
    # sections can still precede managed aliases after dbt-osmosis writes.
    merged: dict[str, t.Any] = {}
    _, preserved_sections = _partition_yaml_top_level_sections(original_data)

    for key, value in original_data.items():
        if key in filtered_data:
            merged[key] = filtered_data[key]
        elif key in preserved_sections:
            merged[key] = value
            logger.debug(f":recycle: Restoring preserved section '{key}' from original YAML")

    for key, value in filtered_data.items():
        if key not in merged:
            merged[key] = value

    return merged


def _strip_eof_blank_lines(content: bytes) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    newline = "\r\n" if "\r\n" in text else "\n"
    endswith_newline = text.endswith("\n")
    lines = text.splitlines()
    while lines and lines[-1].strip() == "":
        lines.pop()
    if not lines:
        return b""
    result = newline.join(lines)
    if endswith_newline:
        result += newline
    return result.encode("utf-8")


def _write_unique_temp_file(path: Path, content: bytes) -> tuple[Path, int]:
    """Write content to a unique temp file in the target directory."""
    for _ in range(100):
        temp_path = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
        try:
            with temp_path.open("xb") as f:
                bytes_written = f.write(content)
            if path.exists():
                temp_path.chmod(stat.S_IMODE(path.stat().st_mode))
            return temp_path, bytes_written
        except FileExistsError:
            continue
        except Exception:
            _cleanup_temp_path(temp_path)
            raise

    raise FileExistsError(f"Unable to create unique temporary file for {path}")


def _cleanup_temp_path(temp_path: Path | None) -> None:
    """Remove a temp file if this write still owns one."""
    if temp_path and temp_path.exists():
        try:
            temp_path.unlink()
        except Exception:  # noqa: BLE001, S110
            pass


def _discard_yaml_cache(path: Path) -> None:
    with _YAML_BUFFER_CACHE_LOCK:
        _discard_yaml_caches(path)


def _merge_cached_original_sections(path: Path, data: dict[str, t.Any]) -> dict[str, t.Any]:
    with _YAML_BUFFER_CACHE_LOCK:
        if path in _YAML_ORIGINAL_CACHE:
            return _merge_preserved_sections(data, _YAML_ORIGINAL_CACHE[path])
    return data


def _cached_yaml_paths() -> list[Path]:
    with _YAML_BUFFER_CACHE_LOCK:
        return list(_YAML_BUFFER_CACHE.keys())


def _cached_yaml_data(path: Path) -> dict[str, t.Any]:
    with _YAML_BUFFER_CACHE_LOCK:
        data = _YAML_BUFFER_CACHE[path]
        if path in _YAML_ORIGINAL_CACHE:
            return _merge_preserved_sections(data, _YAML_ORIGINAL_CACHE[path])
        return data


def _render_yaml_bytes(
    yaml_handler: ruamel.yaml.YAML,
    data: dict[str, t.Any],
    *,
    strip_eof_blank_lines: bool,
) -> bytes:
    with io.BytesIO() as staging:
        yaml_handler.dump(data, staging)
        modified = staging.getvalue()
    return _strip_eof_blank_lines(modified) if strip_eof_blank_lines else modified


def _validate_temp_write(temp_path: Path, bytes_written: int, expected: bytes) -> None:
    if not temp_path.exists():
        raise OSError(f"Temporary file not created: {temp_path}")
    if temp_path.stat().st_size == 0 and len(expected) > 0:
        raise OSError(f"Temporary file is empty: {temp_path}")
    if bytes_written != len(expected):
        raise OSError(
            f"Write incomplete: expected {len(expected)} bytes, wrote {bytes_written}",
        )


def _install_temp_file(temp_path: Path, path: Path, *, allow_overwrite: bool) -> None:
    if allow_overwrite:
        _replace_atomically(temp_path, path)
        return

    try:
        os.link(temp_path, path)
    except FileExistsError:
        raise FileExistsError(f"Refusing to overwrite existing YAML file: {path}") from None
    finally:
        _cleanup_temp_path(temp_path)


def _write_modified_bytes(
    path: Path,
    modified: bytes,
    *,
    allow_overwrite: bool,
    written_file_tracker: t.Callable[[Path], None] | None,
    error_action: str,
) -> None:
    temp_path: Path | None = None
    try:
        temp_path, bytes_written = _write_unique_temp_file(path, modified)
        _validate_temp_write(temp_path, bytes_written, modified)
        _install_temp_file(temp_path, path, allow_overwrite=allow_overwrite)
        _discard_yaml_cache(path)
        if written_file_tracker:
            written_file_tracker(path)
    except Exception as e:
        _cleanup_temp_path(temp_path)
        logger.error(":boom: Failed to %s YAML to => %s: %s", error_action, path, e)
        raise


def _record_mutation(mutation_tracker: t.Callable[[int], None] | None) -> None:
    if mutation_tracker:
        mutation_tracker(1)


def _handle_yaml_change(
    path: Path,
    modified: bytes,
    *,
    dry_run: bool,
    mutation_tracker: t.Callable[[int], None] | None,
    written_file_tracker: t.Callable[[Path], None] | None,
    allow_overwrite: bool,
    write_message: str,
    error_action: str,
) -> None:
    if dry_run:
        logger.info(":eyes: Would write changes to => %s (dry-run)", path)
    else:
        logger.info(write_message, path)
        _write_modified_bytes(
            path,
            modified,
            allow_overwrite=allow_overwrite,
            written_file_tracker=written_file_tracker,
            error_action=error_action,
        )
    _record_mutation(mutation_tracker)


def _discard_processed_cache(path: Path, *, dry_run: bool, changed: bool) -> None:
    if dry_run or not changed:
        _discard_yaml_cache(path)


def _commit_one_yaml(
    yaml_handler: ruamel.yaml.YAML,
    path: Path,
    *,
    dry_run: bool,
    mutation_tracker: t.Callable[[int], None] | None,
    strip_eof_blank_lines: bool,
    written_file_tracker: t.Callable[[Path], None] | None,
) -> None:
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)

    original = path.read_bytes() if path.is_file() else b""
    modified = _render_yaml_bytes(
        yaml_handler,
        _cached_yaml_data(path),
        strip_eof_blank_lines=strip_eof_blank_lines,
    )
    changed = modified != original
    if changed:
        _handle_yaml_change(
            path,
            modified,
            dry_run=dry_run,
            mutation_tracker=mutation_tracker,
            written_file_tracker=written_file_tracker,
            allow_overwrite=True,
            write_message=":writing_hand: Writing => %s",
            error_action="commit",
        )
    else:
        logger.debug(":white_check_mark: Skipping => %s (no changes)", path)
    _discard_processed_cache(path, dry_run=dry_run, changed=changed)


def _write_yaml(
    yaml_handler: ruamel.yaml.YAML,
    yaml_handler_lock: threading.Lock,
    path: Path,
    data: dict[str, t.Any],
    dry_run: bool = False,
    mutation_tracker: t.Callable[[int], None] | None = None,
    strip_eof_blank_lines: bool = False,
    written_file_tracker: t.Callable[[Path], None] | None = None,
    allow_overwrite: bool = True,
) -> None:
    """Write a yaml file to disk and register a mutation with the context. Clears the path from the buffer cache.

    Thread-safety: This function is thread-safe. It acquires yaml_handler_lock
    to ensure exclusive access to the yaml handler, and _YAML_BUFFER_CACHE_LOCK
    for cache invalidation. Multiple threads can safely write to different files.

    Uses a write-validate-replace pattern to prevent data loss:
    1. Write to a unique temporary file in the target directory
    2. Validate write succeeded (file exists and non-empty)
    3. Replace original file via atomic rename
    4. If any step fails, clean up temp file and preserve original

    Note: When dry_run=True, changes are detected and mutation_tracker is called,
    but no files are written to disk. This enables --check to work with --dry-run.
    """
    logger.debug(":page_with_curl: Attempting to write YAML to => %s", path)
    with yaml_handler_lock:
        data = _merge_cached_original_sections(path, data)

        if not dry_run:
            if not allow_overwrite and path.exists():
                raise FileExistsError(f"Refusing to overwrite existing YAML file: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)

        original = path.read_bytes() if path.is_file() else b""
        modified = _render_yaml_bytes(
            yaml_handler,
            data,
            strip_eof_blank_lines=strip_eof_blank_lines,
        )
        changed = modified != original
        if changed:
            _handle_yaml_change(
                path,
                modified,
                dry_run=dry_run,
                mutation_tracker=mutation_tracker,
                written_file_tracker=written_file_tracker,
                allow_overwrite=allow_overwrite,
                write_message=":writing_hand: Writing changes to => %s",
                error_action="write",
            )
        else:
            logger.debug(":white_check_mark: Skipping write => %s (no changes)", path)

        _discard_processed_cache(path, dry_run=dry_run, changed=changed)


def _replace_atomically(temp_path: Path, target_path: Path) -> None:
    """Atomically replace target_path with temp_path.

    This ensures that the target file is never in a partially-written state.
    Works across platforms using the safest available method.
    """
    try:
        # Try atomic rename (works on Unix and Windows with Python 3.3+)
        temp_path.replace(target_path)
    except OSError:
        # Fallback for older systems or special filesystems
        if target_path.exists():
            target_path.unlink()
        temp_path.rename(target_path)


def commit_yamls(
    yaml_handler: ruamel.yaml.YAML,
    yaml_handler_lock: threading.Lock,
    dry_run: bool = False,
    mutation_tracker: t.Callable[[int], None] | None = None,
    strip_eof_blank_lines: bool = False,
    written_file_tracker: t.Callable[[Path], None] | None = None,
) -> None:
    """Commit all files in the yaml buffer cache to disk. Clears the buffer cache and registers mutations.

    Uses the same write-validate-replace pattern as _write_yaml for safety.

    Note: When dry_run=True, changes are detected and mutation_tracker is called,
    but no files are written to disk. This enables --check to work with --dry-run.
    """
    logger.info(":inbox_tray: Committing all YAMLs from buffer cache to disk.")
    with yaml_handler_lock:
        for path in _cached_yaml_paths():
            _commit_one_yaml(
                yaml_handler,
                path,
                dry_run=dry_run,
                mutation_tracker=mutation_tracker,
                strip_eof_blank_lines=strip_eof_blank_lines,
                written_file_tracker=written_file_tracker,
            )
