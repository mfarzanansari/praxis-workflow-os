#!/usr/bin/env python3
"""Scaffold a valid, non-overwriting Agent Skill folder."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def reject_symlink_components(path: Path) -> None:
    path = absolute(path)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise SystemExit(f"Error: skill path contains a symlink component: {current}")
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("skills"))
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--type", choices=("discipline", "technique", "pattern", "reference", "router", "output"), default="technique")
    parser.add_argument("--with-scripts", action="store_true")
    parser.add_argument("--with-references", action="store_true")
    parser.add_argument("--with-assets", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not NAME_RE.fullmatch(args.name) or len(args.name) > 64:
        raise SystemExit("Error: --name must be lowercase kebab-case and at most 64 characters.")
    if not 1 <= len(args.description) <= 1024:
        raise SystemExit("Error: --description must be 1–1024 characters.")
    target = absolute(args.root) / args.name
    reject_symlink_components(target)
    if target.exists():
        raise SystemExit(f"Error: target already exists: {target}")

    paths = [
        target / "SKILL.md",
        target / "agents/openai.yaml",
        target / "evals/evals.json",
        target / "evals/trigger_queries.json",
    ]
    for flag, folder in [(args.with_scripts, "scripts"), (args.with_references, "references"), (args.with_assets, "assets")]:
        if flag:
            paths.append(target / folder / ".gitkeep")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "paths": [str(p) for p in paths]}, indent=2))
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_components(target)
    if target.exists():
        raise SystemExit(f"Error: target appeared during planning: {target}")
    staging_root = Path(tempfile.mkdtemp(prefix=f".{args.name}.praxis-", dir=target.parent))
    staged_target = staging_root / args.name
    staged_target.mkdir()
    body = f"""---
name: {args.name}
description: {json.dumps(args.description, ensure_ascii=False)}
license: MIT
metadata:
  version: "0.1.0-draft"
  skill-type: {args.type}
---

# {args.name.replace('-', ' ').title()}

## Core principle

TODO: state the single reusable idea this skill teaches.

## Preconditions and inputs

TODO

## Procedure

1. TODO

## Output or behavior contract

TODO

## Decision points and human gates

TODO

## Failure modes

| Failure | Correction |
|---|---|
| TODO | TODO |

## Completion criteria

- TODO
"""
    try:
        atomic_write(staged_target / "SKILL.md", body)
        atomic_write(
            staged_target / "agents/openai.yaml",
            "interface:\n"
            f"  display_name: {json.dumps(args.name.replace('-', ' ').title())}\n"
            '  short_description: "Build and test an evidence-grounded skill"\n'
            f'  default_prompt: "Use ${args.name} to complete this task with its documented workflow."\n',
        )
        evals = {
            "skill_name": args.name,
            "evals": [
                {
                    "id": 1,
                    "prompt": "TODO: realistic task prompt",
                    "expected_output": "TODO: observable expected behavior",
                    "files": [],
                    "assertions": ["TODO: define one objective, observable success condition"],
                }
            ],
        }
        atomic_write(staged_target / "evals/evals.json", json.dumps(evals, indent=2) + "\n")
        trigger_queries = [
            {"query": f"TODO: realistic should-trigger query {index}", "should_trigger": True}
            for index in range(1, 9)
        ] + [
            {"query": f"TODO: realistic near-miss query {index}", "should_trigger": False}
            for index in range(1, 9)
        ]
        atomic_write(
            staged_target / "evals/trigger_queries.json",
            json.dumps(trigger_queries, indent=2) + "\n",
        )
        for flag, folder in [
            (args.with_scripts, "scripts"),
            (args.with_references, "references"),
            (args.with_assets, "assets"),
        ]:
            if flag:
                (staged_target / folder).mkdir()
                atomic_write(staged_target / folder / ".gitkeep", "")
        staged_target.rename(target)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    print(json.dumps({"status": "created", "target": str(target), "paths": [str(p) for p in paths]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
