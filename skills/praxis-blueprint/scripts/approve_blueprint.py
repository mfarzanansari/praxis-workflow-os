#!/usr/bin/env python3
"""Create a content-hashed approval record for a reviewed Praxis blueprint."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

BLUEPRINT_FILES = (
    "workflow-constitution.md",
    "work-streams.md",
    "skill-map.md",
    "knowledge-architecture.md",
    "automation-boundaries.md",
    "rollout-plan.md",
    "acceptance-tests.md",
)
READY_PROFILE_STATUSES = {"complete", "mature"}


def absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def reject_symlink_components(path: Path, label: str) -> None:
    path = absolute(path)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise SystemExit(f"Error: {label} contains a symlink component: {current}")
        if not current.exists():
            break


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_profile(path: Path) -> Dict[str, Any]:
    reject_symlink_components(path, "profile path")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Error: profile not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid profile JSON: {exc}")
    if not isinstance(value, dict) or not value.get("profile_id"):
        raise SystemExit("Error: profile must be an object with profile_id.")
    if value.get("status") not in READY_PROFILE_STATUSES:
        raise SystemExit("Error: profile status must be complete or mature before blueprint approval.")
    return value


def atomic_write(path: Path, text: str) -> None:
    reject_symlink_components(path, "approval output")
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--blueprint-dir", type=Path, default=Path("praxis"))
    parser.add_argument("--approver", required=True, help="Person explicitly approving this blueprint")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--confirm-approved",
        action="store_true",
        help="Confirm the named approver reviewed and approved the exact files",
    )
    args = parser.parse_args()

    if not args.confirm_approved:
        raise SystemExit("Error: explicit --confirm-approved is required.")
    if not args.approver.strip():
        raise SystemExit("Error: --approver must be non-empty.")
    profile_path = absolute(args.profile)
    blueprint_dir = absolute(args.blueprint_dir)
    output = absolute(args.output) if args.output else blueprint_dir / "blueprint-approval.json"
    reject_symlink_components(blueprint_dir, "blueprint directory")
    reject_symlink_components(output, "approval output")
    if output.parent != blueprint_dir:
        raise SystemExit("Error: approval record must be stored inside --blueprint-dir.")
    if output.exists() or output.is_symlink():
        raise SystemExit(f"Error: approval record already exists: {output}")

    profile = load_profile(profile_path)
    hashes: Dict[str, str] = {}
    for name in BLUEPRINT_FILES:
        path = blueprint_dir / name
        reject_symlink_components(path, "blueprint file")
        if not path.is_file():
            raise SystemExit(f"Error: required blueprint file missing: {path}")
        text = path.read_text(encoding="utf-8")
        if "TODO" in text or "requires explicit approval" in text.lower():
            raise SystemExit(f"Error: blueprint file is still draft or contains TODO: {path}")
        hashes[name] = sha256(path)

    record = {
        "schema_version": "1.0",
        "status": "approved",
        "profile_id": profile["profile_id"],
        "profile_sha256": sha256(profile_path),
        "blueprint_files": hashes,
        "approved_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "approver": args.approver.strip(),
    }
    atomic_write(output, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "status": "approved",
        "record": str(output),
        "profile_id": profile["profile_id"],
        "files": len(hashes),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
