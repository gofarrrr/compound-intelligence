#!/usr/bin/env python3
"""Create an explicitly requested learning home without overwriting files.

Standard library only. No network, telemetry, hooks, or automatic invocation.
Designed for ordinary local use, not concurrent adversarial filesystem mutation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "home-templates"


def _reject_symlinks(path: Path) -> None:
    """Inspect components before resolving, including links followed by '..'."""
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current = current / component
        if current.is_symlink():
            raise ValueError(f"Refusing symlink in destination path: {current}")


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _package_roots() -> list[Path]:
    roots = [SKILL_ROOT]
    candidate = SKILL_ROOT.parent.parent
    if SKILL_ROOT.parent.name == "skills" and (
        (candidate / ".claude-plugin" / "plugin.json").is_file()
        or (candidate / ".codex-plugin" / "plugin.json").is_file()
        or (candidate / "plugin.json").is_file()
    ):
        roots.append(candidate.resolve())
    return roots


def create_home(
    target: str | Path, *, add_missing: bool = False, dry_run: bool = False
) -> dict[str, Any]:
    """Preflight all paths, then exclusively create only missing template files."""
    requested = Path(target).expanduser()
    _reject_symlinks(requested)
    destination = requested.resolve(strict=False)
    if destination == Path(destination.anchor):
        raise ValueError("The filesystem root is not a learning-home destination.")
    if any(_inside(destination, root) for root in _package_roots()):
        raise ValueError("Choose a user-owned location outside the installed package.")
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"Destination is not a directory: {destination}")
    if destination.exists() and any(destination.iterdir()) and not add_missing:
        raise ValueError(
            "Destination is nonempty. Inspect it first; use --add-missing only "
            "when adding the missing templates is explicitly authorized."
        )
    if not TEMPLATES.is_dir() or TEMPLATES.is_symlink():
        raise ValueError("Canonical learning-home templates are unavailable.")

    planned: list[tuple[Path, bytes]] = []
    preserved: list[Path] = []
    for source in sorted(TEMPLATES.rglob("*")):
        if source.is_symlink():
            raise ValueError(f"Unexpected symlink in package templates: {source}")
        if not source.is_file():
            continue
        relative = source.relative_to(TEMPLATES)
        output = destination / relative
        _reject_symlinks(output)
        parent = output.parent
        while parent != destination.parent:
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"A required directory is an existing file: {parent}")
            if parent == destination:
                break
            parent = parent.parent
        if output.exists():
            if not output.is_file():
                raise ValueError(f"A template file path is an existing directory: {output}")
            preserved.append(output)
            continue
        # Validate the shipped text before making any changes.
        payload = source.read_text(encoding="utf-8").encode("utf-8")
        planned.append((output, payload))

    result: dict[str, Any] = {
        "destination": str(destination),
        "dry_run": dry_run,
        "would_create": [str(path) for path, _ in planned] if dry_run else [],
        "created": [],
        "preserved": [str(path) for path in preserved],
    }
    if dry_run:
        return result

    for output, payload in planned:
        # Repeat ordinary checks immediately before creation. Exclusive open is
        # the no-overwrite guarantee even if a file appears after preflight.
        _reject_symlinks(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(output, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
        except BaseException:
            # Do not delete or overwrite a file on failure: report the error.
            raise
        result["created"].append(str(output))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Explicit user-owned learning-home path")
    parser.add_argument("--add-missing", action="store_true", help="Preserve all existing files and create only missing templates")
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without creating directories or files")
    args = parser.parse_args()
    try:
        result = create_home(args.target, add_missing=args.add_missing, dry_run=args.dry_run)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Learning home not created or not completed: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
