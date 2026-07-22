#!/usr/bin/env python3
"""Install Praxis skills into an Agent Skills directory safely.

Copies each folder from ./skills to the target. Existing skill folders are
skipped by default. --force requires --backup-dir and backs up each replaced
folder before copying.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List


def paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def reject_symlink_components(path: Path, label: str) -> None:
    path = absolute(path)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink() and current.parent != Path(path.anchor):
            raise SystemExit(f"Error: {label} contains a symlink component: {current}")
        if not current.exists():
            break


def atomic_write(path: Path, text: str) -> None:
    reject_symlink_components(path, "install report path")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.praxis-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            Path(temporary).unlink()
        except FileNotFoundError:
            pass
        raise


def reject_symlinks(root: Path, label: str) -> None:
    """Reject a symlink root or any symlink below it before reading/copying."""
    if root.is_symlink():
        raise SystemExit(f"Error: {label} must not be a symlink: {root}")
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"Error: refusing symlink in {label}: {path}")


def stage_skill(source: Path, target: Path) -> tuple[Path, Path]:
    """Copy a skill completely before changing its destination."""
    reject_symlinks(source, "source skill")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{target.name}.praxis-", dir=target.parent))
    staged = staging_root / target.name
    try:
        shutil.copytree(source, staged)
    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)
        raise
    return staging_root, staged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True, help="Agent skills directory")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "skills")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--include", action="append", default=[], help="Install only named skill; repeatable")
    args = parser.parse_args()

    if args.force and args.backup_dir is None:
        raise SystemExit("Error: --force requires --backup-dir.")
    reject_symlink_components(args.source, "source skills path")
    reject_symlink_components(args.target, "target skills path")
    if args.backup_dir is not None:
        reject_symlink_components(args.backup_dir, "backup path")
    source_root = args.source.resolve()
    target_root = args.target.resolve()
    backup_root = args.backup_dir.resolve() if args.backup_dir else None
    if not source_root.is_dir():
        raise SystemExit(f"Error: source skills directory not found: {source_root}")
    reject_symlinks(source_root, "source skills directory")
    if paths_overlap(source_root, target_root):
        raise SystemExit("Error: source and target directories must not overlap.")
    if backup_root is not None:
        if paths_overlap(target_root, backup_root):
            raise SystemExit("Error: target and backup directories must not overlap.")
        if paths_overlap(source_root, backup_root):
            raise SystemExit("Error: source and backup directories must not overlap.")
    source_skills = sorted(
        p for p in source_root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()
    )
    if args.include:
        requested = set(args.include)
        source_skills = [p for p in source_skills if p.name in requested]
        found = {p.name for p in source_skills}
        missing = sorted(requested - found)
        if missing:
            raise SystemExit(f"Error: requested skill(s) not found: {', '.join(missing)}")
    if not source_skills:
        raise SystemExit("Error: no skills found to install.")

    plan: List[Dict[str, str]] = []
    for source in source_skills:
        target = target_root / source.name
        if target.is_symlink():
            raise SystemExit(f"Error: refusing to replace symlink target: {target}")
        if target.exists():
            reject_symlinks(target, "existing target skill")
        action = "replace" if target.exists() and args.force else "skip" if target.exists() else "create"
        plan.append({"skill": source.name, "source": str(source), "target": str(target), "action": action})

    if backup_root is not None:
        for item in plan:
            if item["action"] != "replace":
                continue
            backup = backup_root / item["skill"]
            if backup.exists() or backup.is_symlink():
                raise SystemExit(f"Error: backup destination already exists: {backup}")

    report = {
        "timestamp": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "dry_run": args.dry_run,
        "target": str(target_root),
        "backup_dir": str(backup_root) if backup_root else None,
        "actions": plan,
    }
    if args.dry_run:
        print(json.dumps(report, indent=2))
        return 0

    target_root.mkdir(parents=True, exist_ok=True)
    completed: List[Dict[str, str]] = []
    try:
        for item in plan:
            source = Path(item["source"])
            target = Path(item["target"])
            if item["action"] == "skip":
                item["result"] = "unchanged"
                continue
            staging_root, staged = stage_skill(source, target)
            backup = backup_root / source.name if backup_root is not None else None
            try:
                if item["action"] == "replace":
                    if backup is None:
                        raise RuntimeError("replacement plan is missing its required backup path")
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(target, backup)
                    item["backup"] = str(backup)
                    shutil.rmtree(target)
                staged.rename(target)
                item["result"] = "installed"
                completed.append(item)
            except Exception:
                if (
                    item["action"] == "replace"
                    and backup is not None
                    and backup.exists()
                    and not target.exists()
                ):
                    shutil.copytree(backup, target)
                raise
            finally:
                shutil.rmtree(staging_root, ignore_errors=True)
    except Exception:
        for item in reversed(completed):
            target = Path(item["target"])
            if target.exists():
                shutil.rmtree(target)
            if item["action"] == "replace":
                backup = Path(item["backup"])
                if backup.exists():
                    shutil.copytree(backup, target)
        raise

    report_path = target_root / "praxis-install-report.json"
    atomic_write(report_path, json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": "complete",
        "report": str(report_path),
        "installed": sum(1 for item in plan if item["action"] in {"create", "replace"}),
        "skipped": sum(1 for item in plan if item["action"] == "skip"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
