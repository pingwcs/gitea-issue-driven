#!/usr/bin/env python3
"""Install the Gitea issue-driven skills and agent into a Codex home."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple, Sequence


SKILL_NAMES = (
    "gitea-branch-bootstrap",
    "gitea-change-publish",
    "gitea-issue-decomposition",
    "gitea-issue-evidence",
    "gitea-issue-execution",
    "gitea-issue-intake",
    "gitea-issue-triage",
    "gitea-pr-delivery",
)
SHARED_RUNTIME = Path("gitea")
AGENT_NAME = "gitea-issue-driven.toml"
LEGACY_DESTINATIONS = (Path("skills") / "gitea-connector-profile.md",)


class InstallError(RuntimeError):
    """Raised when the installation cannot be completed safely."""


class InstallItem(NamedTuple):
    source: Path
    relative_destination: Path


def _path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _move_path(source: Path, destination: Path) -> None:
    source.replace(destination)


def _build_items(source_root: Path) -> tuple[InstallItem, ...]:
    skills_root = source_root / ".agents" / "skills"
    items = tuple(
        InstallItem(skills_root / name, Path("skills") / name)
        for name in SKILL_NAMES
    ) + (
        InstallItem(
            source_root / ".agents" / "shared" / SHARED_RUNTIME,
            Path("shared") / SHARED_RUNTIME,
        ),
        InstallItem(
            source_root / ".codex" / "agents" / AGENT_NAME,
            Path("agents") / AGENT_NAME,
        ),
    )
    missing = [str(item.source) for item in items if not _path_exists(item.source)]
    if missing:
        formatted = "\n  - ".join(missing)
        raise InstallError(f"installation source is incomplete:\n  - {formatted}")
    return items


def _legacy_targets(codex_home: Path) -> tuple[Path, ...]:
    return tuple(
        codex_home / relative
        for relative in LEGACY_DESTINATIONS
        if _path_exists(codex_home / relative)
    )


def _conflicts(
    items: Sequence[InstallItem], codex_home: Path, legacy_targets: Sequence[Path]
) -> list[Path]:
    current = [
        codex_home / item.relative_destination
        for item in items
        if _path_exists(codex_home / item.relative_destination)
    ]
    return current + list(legacy_targets)


def _format_plan(
    items: Sequence[InstallItem],
    codex_home: Path,
    legacy_targets: Sequence[Path],
    *,
    force: bool,
    dry_run: bool,
) -> str:
    heading = "DRY RUN - no files will be changed" if dry_run else "Installation plan"
    lines = [heading]
    for item in items:
        destination = codex_home / item.relative_destination
        action = "OVERWRITE" if _path_exists(destination) and force else "CREATE"
        lines.append(f"  {action}: {destination}")
    for destination in legacy_targets:
        lines.append(f"  REMOVE LEGACY: {destination}")
    return "\n".join(lines)


def _copy_to_payload(items: Sequence[InstallItem], payload_root: Path) -> None:
    for item in items:
        staged = payload_root / item.relative_destination
        staged.parent.mkdir(parents=True, exist_ok=True)
        if item.source.is_dir():
            shutil.copytree(
                item.source,
                staged,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(item.source, staged)


def _ensure_directory(path: Path, created_directories: list[Path]) -> None:
    missing: list[Path] = []
    cursor = path
    while not _path_exists(cursor):
        missing.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    path.mkdir(parents=True, exist_ok=True)
    created_directories.extend(reversed(missing))


def _remove_created_directories(created_directories: Sequence[Path]) -> list[str]:
    errors: list[str] = []
    for path in reversed(created_directories):
        try:
            path.rmdir()
        except FileNotFoundError:
            pass
        except OSError as error:
            errors.append(f"remove directory {path}: {error}")
    return errors


def _rollback(
    installed: Sequence[Path], backups: Sequence[tuple[Path, Path]]
) -> list[str]:
    errors: list[str] = []
    for destination in reversed(installed):
        try:
            _remove_path(destination)
        except OSError as error:
            errors.append(f"remove {destination}: {error}")
    for destination, backup in reversed(backups):
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _move_path(backup, destination)
        except OSError as error:
            errors.append(f"restore {destination}: {error}")
    return errors


def _backup_path(
    destination: Path,
    relative_backup: Path,
    backup_root: Path,
    backups: list[tuple[Path, Path]],
) -> None:
    backup = backup_root / relative_backup
    backup.parent.mkdir(parents=True, exist_ok=True)
    _move_path(destination, backup)
    backups.append((destination, backup))


def install(
    source_root: Path, codex_home: Path, *, force: bool = False, dry_run: bool = False
) -> tuple[Path, ...]:
    """Install all package items and transactionally migrate managed legacy files."""
    source_root = source_root.resolve()
    codex_home = codex_home.expanduser().resolve()
    items = _build_items(source_root)
    legacy_targets = _legacy_targets(codex_home)
    conflicts = _conflicts(items, codex_home, legacy_targets)
    if conflicts and not force:
        formatted = "\n  - ".join(str(path) for path in conflicts)
        raise InstallError(
            "installation conflicts with existing managed targets:\n"
            f"  - {formatted}\n"
            "Review the targets, then retry explicitly with --force to replace or migrate them."
        )

    print(
        _format_plan(
            items,
            codex_home,
            legacy_targets,
            force=force,
            dry_run=dry_run,
        )
    )
    if dry_run:
        return tuple(codex_home / item.relative_destination for item in items)

    installed: list[Path] = []
    backups: list[tuple[Path, Path]] = []
    created_directories: list[Path] = []
    transaction: tempfile.TemporaryDirectory[str] | None = None
    try:
        _ensure_directory(codex_home.parent, created_directories)
        transaction = tempfile.TemporaryDirectory(
            prefix=".gitea-issue-driven-install-", dir=codex_home.parent
        )
        transaction_root = Path(transaction.name)
        payload_root = transaction_root / "payload"
        backup_root = transaction_root / "backup"
        _copy_to_payload(items, payload_root)

        for destination in legacy_targets:
            relative = destination.relative_to(codex_home)
            _backup_path(
                destination,
                Path("legacy") / relative,
                backup_root,
                backups,
            )

        for item in items:
            staged = payload_root / item.relative_destination
            destination = codex_home / item.relative_destination
            _ensure_directory(destination.parent, created_directories)
            if _path_exists(destination):
                if not force:
                    raise InstallError(
                        f"target appeared during installation: {destination}; "
                        "retry explicitly with --force if it may be overwritten"
                    )
                _backup_path(
                    destination,
                    Path("current") / item.relative_destination,
                    backup_root,
                    backups,
                )
            _move_path(staged, destination)
            installed.append(destination)
    except Exception as error:
        rollback_errors = _rollback(installed, backups)
        if transaction is not None:
            transaction.cleanup()
        rollback_errors.extend(_remove_created_directories(created_directories))
        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise InstallError(
                f"installation failed ({error}); rollback was incomplete: {details}"
            ) from error
        raise InstallError(f"installation failed ({error}); changes were rolled back") from error
    else:
        assert transaction is not None
        transaction.cleanup()

    destinations = tuple(codex_home / item.relative_destination for item in items)
    print(f"Installed {len(destinations)} items into {codex_home}")
    return destinations


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install the Gitea issue-driven Codex skills and agent."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Codex home directory (default: ~/.codex)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace managed targets and migrate the legacy connector profile",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show the installation plan without writing"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source_root = Path(__file__).resolve().parents[1]
    try:
        install(
            source_root,
            args.codex_home,
            force=args.force,
            dry_run=args.dry_run,
        )
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
