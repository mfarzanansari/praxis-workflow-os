#!/usr/bin/env python3
"""Scaffold a valid, non-overwriting Agent Skill folder."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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
    target = args.root / args.name
    if target.exists():
        raise SystemExit(f"Error: target already exists: {target}")

    paths = [target / "SKILL.md", target / "evals/evals.json"]
    for flag, folder in [(args.with_scripts, "scripts"), (args.with_references, "references"), (args.with_assets, "assets")]:
        if flag:
            paths.append(target / folder / ".gitkeep")
    if args.dry_run:
        print(json.dumps({"dry_run": True, "paths": [str(p) for p in paths]}, indent=2))
        return 0

    target.mkdir(parents=True)
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
    (target / "SKILL.md").write_text(body, encoding="utf-8")
    evals = {
        "skill_name": args.name,
        "evals": [
            {
                "id": 1,
                "prompt": "TODO: realistic task prompt",
                "expected_output": "TODO: observable expected behavior",
                "files": [],
                "assertions": [],
            }
        ],
    }
    (target / "evals").mkdir()
    (target / "evals/evals.json").write_text(json.dumps(evals, indent=2) + "\n", encoding="utf-8")
    for flag, folder in [(args.with_scripts, "scripts"), (args.with_references, "references"), (args.with_assets, "assets")]:
        if flag:
            (target / folder).mkdir()
            (target / folder / ".gitkeep").write_text("", encoding="utf-8")
    print(json.dumps({"status": "created", "target": str(target), "paths": [str(p) for p in paths]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
