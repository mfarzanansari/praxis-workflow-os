#!/usr/bin/env python3
"""Create non-overwriting Praxis blueprint document shells from a profile."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

FILES = [
    "workflow-constitution.md",
    "work-streams.md",
    "skill-map.md",
    "knowledge-architecture.md",
    "automation-boundaries.md",
    "rollout-plan.md",
    "acceptance-tests.md",
]


def absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def reject_symlink_components(path: Path, label: str) -> None:
    """Reject existing symlinks in a path without resolving through them."""
    path = absolute(path)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise SystemExit(f"Error: {label} contains a symlink component: {current}")
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


def load_profile(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Error: profile not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        raise SystemExit("Error: profile root must be an object.")
    return value


def stream_sections(profile: Dict[str, Any]) -> str:
    blocks: List[str] = []
    for stream in profile.get("work_streams", []):
        if not isinstance(stream, dict):
            continue
        name = stream.get("name") or stream.get("id") or "Unnamed stream"
        blocks.extend([
            f"## {name}",
            "",
            f"- **ID:** `{stream.get('id', '')}`",
            f"- **Trigger:** {stream.get('trigger', 'TODO')}",
            "- **Inputs and sources:** TODO",
            "- **Decisions and trade-offs:** TODO",
            "- **Actions:** TODO",
            f"- **Deliverables:** {', '.join(map(str, stream.get('deliverables', []))) or 'TODO'}",
            f"- **Quality gates:** {', '.join(map(str, stream.get('quality_gates', []))) or 'TODO'}",
            "- **Human approval:** TODO",
            "- **Handoff:** TODO",
            "- **Durable residue:** TODO",
            "- **Failure and escalation:** TODO",
            "",
        ])
    return "\n".join(blocks) or "## Initial work stream\n\nTODO\n"


def documents(profile: Dict[str, Any]) -> Dict[str, str]:
    primary = profile.get("outcomes", {}).get("primary") or "TODO: confirm primary outcome"
    cadence = profile.get("governance", {}).get("review_cadence") or "TODO"
    preserved = profile.get("knowledge_policy", {}).get("existing_structure_to_preserve", [])
    preserve_text = "\n".join(f"- {item}" for item in preserved) or "- TODO"
    return {
        "workflow-constitution.md": f"""# Workflow Constitution

**Version:** 0.1.0-draft

**Status:** Draft — requires explicit approval

## Purpose

{primary}

## Operating principles

1. TODO: write 5–9 observable principles grounded in the profile.

## Privacy and safety

TODO

## Sources of truth

TODO

## Quality doctrine

TODO

## Knowledge doctrine

TODO

## Governance

- Review cadence: {cadence}
- Amendment process: TODO
- Versioning: semantic versioning
- Rollback: TODO
""",
        "work-streams.md": "# Work Streams\n\n" + stream_sections(profile),
        "skill-map.md": """# Skill Map

## Initial graph

```text
personal-start-work
personal-finish-work
personal-weekly-review
work-<highest-value-stream>
```

## Skill contracts

TODO: trigger, inputs, output, dependencies, terminal state, scripts, references, tests.
""",
        "knowledge-architecture.md": f"""# Knowledge Architecture

## Existing structure to preserve

{preserve_text}

## Durable note types

| Type | Write threshold | Provenance | Review/expiry | Retrieval |
|---|---|---|---|---|
| Research | TODO | TODO | TODO | TODO |
| Decision | TODO | TODO | TODO | TODO |
| Memory | TODO | TODO | TODO | TODO |
| Prompt | TODO | TODO | TODO | TODO |
| Project state | TODO | TODO | TODO | TODO |
| Review | TODO | TODO | TODO | TODO |

## Runtime memory boundary

TODO
""",
        "automation-boundaries.md": """# Automation Boundaries

| Action | Risk | Permission class | Validation | Rollback | Required human |
|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO |
""",
        "rollout-plan.md": """# Rollout Plan

## First proof workflow

TODO

## Minimum installed skills

TODO

## First week

TODO

## Expansion criteria

TODO

## Rollback criteria

TODO
""",
        "acceptance-tests.md": """# Acceptance Tests

## Outcomes

- [ ] TODO: observable improvement

## Non-regressions

- [ ] Existing files are not overwritten without approval.
- [ ] Consequential external actions require the configured human gate.
- [ ] Durable knowledge excludes raw transcript dumps by default.

## Evaluation evidence

TODO
""",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("praxis"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Replace existing files; use only after review")
    parser.add_argument("--backup-dir", type=Path, help="Required with --force; existing files are copied here")
    args = parser.parse_args()

    if args.force and args.backup_dir is None:
        raise SystemExit("Error: --force requires --backup-dir so every replacement is recoverable.")
    output = absolute(args.output)
    backup_root = absolute(args.backup_dir) if args.backup_dir else None
    reject_symlink_components(output, "output path")
    if backup_root is not None:
        reject_symlink_components(backup_root, "backup path")
        if paths_overlap(output, backup_root):
            raise SystemExit("Error: output and backup directories must not overlap.")
    profile = load_profile(args.profile)
    docs = documents(profile)
    plan = []
    for filename in FILES:
        path = output / filename
        reject_symlink_components(path, "blueprint target")
        if path.exists() and not path.is_file():
            raise SystemExit(f"Error: blueprint target is not a regular file: {path}")
        action = "replace" if path.exists() and args.force else "skip" if path.exists() else "create"
        item = {"path": str(path), "action": action}
        if action == "replace":
            if backup_root is None:
                raise RuntimeError("replacement plan is missing its required backup directory")
            backup = backup_root / filename
            reject_symlink_components(backup, "backup target")
            if backup.exists() or backup.is_symlink():
                raise SystemExit(f"Error: backup destination already exists: {backup}")
            item["backup"] = str(backup)
        plan.append(item)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "plan": plan}, indent=2))
        return 0
    output.mkdir(parents=True, exist_ok=True)
    written: List[Dict[str, str]] = []
    try:
        for item in plan:
            if item["action"] == "replace":
                backup = Path(item["backup"])
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(Path(item["path"]), backup)
        for item in plan:
            if item["action"] == "skip":
                continue
            path = Path(item["path"])
            atomic_write(path, docs[path.name])
            written.append(item)
    except Exception:
        for item in reversed(written):
            path = Path(item["path"])
            if item["action"] == "create":
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            else:
                shutil.copy2(Path(item["backup"]), path)
        raise
    print(json.dumps({"dry_run": False, "plan": plan}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
