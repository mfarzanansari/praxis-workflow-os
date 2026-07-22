#!/usr/bin/env python3
"""Create a non-overwriting Obsidian note shell with Praxis metadata."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Dict, List

FOLDERS = {
    "research": "Research",
    "decision": "Decision Records",
    "memory": "Memory",
    "prompt": "Prompts",
    "project-state": None,
    "workflow-review": "Reviews",
}

SECTIONS: Dict[str, List[str]] = {
    "research": ["Question", "Sources and freshness", "Evidence", "Synthesis", "Implications", "Disagreements and limits", "Open questions"],
    "decision": ["Context", "Decision", "Alternatives considered", "Rationale", "Consequences", "Reversal or review conditions", "Evidence"],
    "memory": ["Reusable lesson", "Applies when", "Does not apply when", "Evidence", "Failure modes", "Retrieval cues"],
    "prompt": ["Trigger", "Inputs", "Procedure", "Output contract", "Quality gates", "Human approvals", "Tests and known limits"],
    "project-state": ["Objective", "Current truth", "Decisions in force", "Risks and blockers", "Next actions", "Relevant links"],
    "workflow-review": ["Evidence reviewed", "What worked", "Friction and failures", "Keep / change / remove", "Experiment", "Success and rollback criteria"],
}


def absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def reject_symlink_components(path: Path) -> None:
    path = absolute(path)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise SystemExit(f"Error: note path contains a symlink component: {current}")
        if not current.exists():
            break


def atomic_write(path: Path, text: str) -> None:
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


def safe_filename(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title).strip()
    normalized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip(" .-")
    return (normalized[:140] or "Untitled") + ".md"


def yaml_list(values: List[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in values) + "]"


def render(args: argparse.Namespace) -> str:
    today = args.date or dt.date.today().isoformat()
    review = args.review_on or ""
    front = [
        "---",
        f"type: {args.type}",
        "status: draft",
        f"created: {today}",
        f"updated: {today}",
        f"sources: {yaml_list(args.source)}",
        f"confidence: {args.confidence}",
        f"review_on: {review}",
        f"tags: {yaml_list(args.tag)}",
        "---",
        "",
        f"# {args.title}",
        "",
    ]
    for section in SECTIONS[args.type]:
        front.extend([f"## {section}", "", ""])
    return "\n".join(front).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--type", choices=sorted(FOLDERS), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--project-folder", help="Required for project-state; path relative to vault")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--confidence", choices=("verified", "high", "medium", "low", "unknown"), default="unknown")
    parser.add_argument("--review-on")
    parser.add_argument("--date")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.type == "project-state":
        if not args.project_folder:
            raise SystemExit("Error: --project-folder is required for project-state notes.")
        folder = Path(args.project_folder)
        if folder.is_absolute() or ".." in folder.parts:
            raise SystemExit("Error: --project-folder must be a safe path relative to the vault.")
    else:
        folder = Path(FOLDERS[args.type])
    target = absolute(args.vault) / folder / safe_filename(args.title)
    reject_symlink_components(target)
    result = {"path": str(target), "action": "conflict" if target.exists() else "create", "dry_run": args.dry_run}
    if target.exists():
        print(json.dumps(result, indent=2))
        return 3
    if args.dry_run:
        print(json.dumps(result, indent=2))
        return 0
    atomic_write(target, render(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
