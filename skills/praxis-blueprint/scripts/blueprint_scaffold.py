#!/usr/bin/env python3
"""Create non-overwriting Praxis blueprint document shells from a profile."""
from __future__ import annotations

import argparse
import json
import sys
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
    args = parser.parse_args()

    profile = load_profile(args.profile)
    docs = documents(profile)
    plan = []
    for filename in FILES:
        path = args.output / filename
        action = "replace" if path.exists() and args.force else "skip" if path.exists() else "create"
        plan.append({"path": str(path), "action": action})
    if args.dry_run:
        print(json.dumps({"dry_run": True, "plan": plan}, indent=2))
        return 0
    args.output.mkdir(parents=True, exist_ok=True)
    for item in plan:
        if item["action"] == "skip":
            continue
        path = Path(item["path"])
        path.write_text(docs[path.name], encoding="utf-8")
    print(json.dumps({"dry_run": False, "plan": plan}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
