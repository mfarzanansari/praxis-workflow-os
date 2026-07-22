#!/usr/bin/env python3
"""Safely scaffold a Praxis vault overlay and personalized Agent Skills.

The script is standard-library-only, non-interactive, and has no network access.
It never overwrites by default. Replacement requires --force and --backup-dir.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


def load_profile(path: Path) -> Dict[str, Any]:
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Error: profile not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid JSON in {path}: {exc}")
    if not isinstance(profile, dict):
        raise SystemExit("Error: profile root must be a JSON object.")
    if not profile.get("profile_id"):
        raise SystemExit("Error: profile_id is required.")
    return profile


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def md_list(values: Iterable[Any], fallback: str = "None recorded") -> str:
    items = list(values or [])
    if not items:
        return f"- {fallback}"
    lines = []
    for item in items:
        if isinstance(item, dict):
            label = item.get("name") or item.get("id") or json.dumps(item, ensure_ascii=False)
        else:
            label = str(item)
        lines.append(f"- {label}")
    return "\n".join(lines)


def clean_slug(value: str, fallback: str = "work-stream") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug[:50] or fallback


def frontmatter(note_type: str) -> str:
    return (
        "---\n"
        f"type: {note_type}\n"
        "status: draft\n"
        "created: {{date}}\n"
        "updated: {{date}}\n"
        "sources: []\n"
        "confidence: unknown\n"
        "review_on:\n"
        "tags: []\n"
        "---\n"
    )


def vault_files(profile: Dict[str, Any]) -> Dict[Path, str]:
    profile_json = json.dumps(profile, indent=2, ensure_ascii=False) + "\n"
    primary = profile.get("outcomes", {}).get("primary") or "Not confirmed"
    streams = profile.get("work_streams", [])
    boundaries = profile.get("automation_boundaries", {})
    system = f"""# Praxis System

## Purpose

{primary}

## Profile

- Profile ID: `{profile.get('profile_id', '')}`
- Schema: `{profile.get('schema_version', '')}`
- Status: `{profile.get('status', '')}`

## Initial work streams

{md_list(streams)}

## Operating loop

```text
Start work → execute work-stream skill → verify → finish work → distill → review
```

## Governance

- Review cadence: {profile.get('governance', {}).get('review_cadence') or 'TODO'}
- Owner: {profile.get('governance', {}).get('owner') or 'TODO'}

## System maps

- [[Skill Map]]
- [[Automation Boundaries]]
- [[../Research/Research MOC|Research MOC]]
- [[../Decision Records/Decision Records MOC|Decision Records MOC]]
- [[../Memory/Memory MOC|Memory MOC]]
- [[../Prompts/Prompts MOC|Prompts MOC]]
- [[../Reviews/Reviews MOC|Reviews MOC]]
"""
    skill_lines = ["# Skill Map", "", "## Lifecycle", "", "- `personal-start-work`", "- `personal-finish-work`", "- `personal-weekly-review`", "", "## Work streams", ""]
    for stream in streams:
        if isinstance(stream, dict):
            sid = clean_slug(str(stream.get("id") or stream.get("name") or "work-stream"))
            skill_lines.append(f"- `work-{sid}` — {stream.get('name') or sid}")
    skill_lines.extend(["", "## Routing rule", "", "Load the smallest skill that matches the current lifecycle stage and work stream.", ""])
    boundary_doc = ["# Automation Boundaries", ""]
    for heading, key in [
        ("Autonomous", "autonomous"),
        ("Review before action", "review_before_action"),
        ("Explicit per-action approval", "explicit_per_action"),
        ("Forbidden", "forbidden"),
    ]:
        boundary_doc.extend([f"## {heading}", "", md_list(boundaries.get(key, [])), ""])
    files: Dict[Path, str] = {
        Path("_meta/Praxis System.md"): system,
        Path("_meta/Praxis Profile.json"): profile_json,
        Path("_meta/Skill Map.md"): "\n".join(skill_lines),
        Path("_meta/Automation Boundaries.md"): "\n".join(boundary_doc),
        Path("Research/Research MOC.md"): "# Research MOC\n\nSource-backed evidence and synthesis worth retrieving across work.\n\n## Index\n\n- Add links here or use backlinks/search.\n",
        Path("Decision Records/Decision Records MOC.md"): "# Decision Records MOC\n\nConsequential choices, alternatives, rationale, consequences, and reversal conditions.\n\n## Index\n\n- Add links here or use backlinks/search.\n",
        Path("Memory/Memory MOC.md"): "# Memory MOC\n\nReusable lessons, traps, doctrine, and verified setup—not raw transcripts.\n\n## Index\n\n- Add links here or use backlinks/search.\n",
        Path("Prompts/Prompts MOC.md"): "# Prompts MOC\n\nReusable workflow software and kickoff briefs with stable inputs, outputs, and gates.\n\n## Index\n\n- Add links here or use backlinks/search.\n",
        Path("Reviews/Reviews MOC.md"): "# Reviews MOC\n\nEvidence-based workflow retrospectives, experiments, and system changes.\n\n## Index\n\n- Add links here or use backlinks/search.\n",
        Path("_meta/Templates/Research Note.md"): frontmatter("research") + "\n# {{title}}\n\n## Question\n\n## Sources and freshness\n\n## Evidence\n\n## Synthesis\n\n## Implications\n\n## Open questions\n",
        Path("_meta/Templates/Decision Record.md"): frontmatter("decision") + "\n# {{title}}\n\n## Context\n\n## Decision\n\n## Alternatives considered\n\n## Rationale\n\n## Consequences\n\n## Reversal or review conditions\n",
        Path("_meta/Templates/Memory Note.md"): frontmatter("memory") + "\n# {{title}}\n\n## Reusable lesson\n\n## Applies when\n\n## Does not apply when\n\n## Evidence\n\n## Failure modes\n\n## Retrieval cues\n",
        Path("_meta/Templates/Prompt Note.md"): frontmatter("prompt") + "\n# {{title}}\n\n## Trigger\n\n## Inputs\n\n## Procedure\n\n## Output contract\n\n## Quality gates\n\n## Human approvals\n\n## Tests\n",
        Path("_meta/Templates/Project State.md"): frontmatter("project-state") + "\n# {{title}}\n\n## Current objective\n\n## Current truth\n\n## Decisions in force\n\n## Risks and blockers\n\n## Next actions\n\n## Relevant links\n",
        Path("_meta/Templates/Workflow Review.md"): frontmatter("workflow-review") + "\n# {{title}}\n\n## Evidence reviewed\n\n## What worked\n\n## Friction and failures\n\n## Keep / change / remove\n\n## Experiment\n\n## Success and rollback criteria\n",
    }
    return files


def common_metadata(profile: Dict[str, Any]) -> str:
    return (
        "metadata:\n"
        "  author: Praxis generated personal skill\n"
        "  version: \"0.1.0-draft\"\n"
        f"  profile-id: {yaml_scalar(str(profile.get('profile_id', '')))}\n"
        f"  profile-schema: {yaml_scalar(str(profile.get('schema_version', '')))}\n"
    )


def start_skill(profile: Dict[str, Any]) -> str:
    primary = profile.get("outcomes", {}).get("primary") or "the current approved outcome"
    return f"""---
name: personal-start-work
description: Use when beginning a meaningful work session, responding to a new request, resuming an interrupted task, or assembling context for one of this person's approved work streams. Use before execution when the deliverable, evidence, current state, or quality gate is not already explicit.
license: MIT
{common_metadata(profile)}---

# Personal Start Work

## Outcome

Create a compact execution brief that makes the work, evidence, decisions, risks, and finish line explicit without loading the whole knowledge base.

Primary system outcome: {primary}

## Procedure

1. Identify the matching work stream. If none matches, ask whether this is a one-off task or evidence for a new recurring stream; do not create a skill yet.
2. State the requested deliverable, audience, deadline, and completion condition.
3. Load only the relevant project state, decisions, research, prompts, and memory notes.
4. Distinguish current authoritative evidence from stale or contextual notes.
5. Surface the decisions that require human judgment.
6. Name the quality gates and approval boundary.
7. Produce the execution brief below.

## Execution brief

```markdown
# Execution Brief — [task]
- Work stream:
- Deliverable and audience:
- Deadline / urgency:
- Sources of truth:
- Relevant decisions in force:
- Quality gates:
- Human approval required:
- Risks / unknowns:
- Planned actions:
- Durable residue likely:
```

## Constraints

- Inspect before asking the person to restate context.
- Do not load unrelated notes “just in case.”
- Do not begin consequential external action before the configured approval.
- When evidence conflicts, stop and resolve source authority.
"""


def finish_skill(profile: Dict[str, Any]) -> str:
    boundaries = profile.get("automation_boundaries", {})
    return f"""---
name: personal-finish-work
description: Use when a meaningful task, deliverable, meeting, analysis, creative iteration, field job, or project checkpoint is ending and the person needs verification, handoff, unresolved-risk capture, or durable learning without saving a raw transcript.
license: MIT
{common_metadata(profile)}---

# Personal Finish Work

## Outcome

Verify completion, preserve handoff context, and decide whether any residue deserves durable storage.

## Procedure

1. Compare the output with the execution brief and work-stream quality gates.
2. Verify facts, tests, approvals, inspection, rehearsal, or review appropriate to the work.
3. Identify unresolved risks and state who owns them.
4. Confirm the handoff and what the recipient needs.
5. Classify possible durable residue:
   - research;
   - decision record;
   - reusable memory;
   - reusable prompt;
   - project state;
   - workflow review evidence.
6. Invoke `praxis-distill` only for items likely to change future work.
7. Record a compact event for retrospective evidence when logging is configured.

## Finish report

```markdown
# Finish Report — [task]
- Deliverable:
- Verification performed:
- Quality gates passed / failed:
- Human approval status:
- Handoff:
- Unresolved risks and owner:
- Durable notes created:
- Workflow friction observed:
```

## Boundaries

Review-before-action examples configured in the profile:
{md_list(boundaries.get('review_before_action', []))}

Do not call work complete when a required approval or verification is pending.
"""


def weekly_skill(profile: Dict[str, Any]) -> str:
    cadence = profile.get("governance", {}).get("review_cadence") or "weekly"
    return f"""---
name: personal-weekly-review
description: Use at the configured review cadence, after several real workflow runs, or when the person reports repeated friction, missed context, low adoption, unnecessary skill activation, or declining trust in the system.
license: MIT
{common_metadata(profile)}---

# Personal Weekly Review

Configured cadence: {cadence}

Use `praxis-retrospective` to review evidence. Do not redesign from memory or novelty.

## Required review questions

- Which workflows produced meaningful value?
- Where did the person correct the agent?
- Which skill should have triggered but did not?
- Which skill triggered unnecessarily?
- Which repeated mechanics should be scripted?
- Which note was hard to retrieve or never useful?
- Which gate prevented harm, and which gate created needless friction?
- What should be kept, changed, removed, or tested next?

## Output

Produce one prioritized experiment at a time, with success and rollback criteria. Prefer deleting or narrowing weak system elements before adding more.
"""


def stream_skill(profile: Dict[str, Any], stream: Dict[str, Any]) -> Tuple[str, str]:
    sid = clean_slug(str(stream.get("id") or stream.get("name") or "work-stream"))
    name = f"work-{sid}"
    title = stream.get("name") or sid.replace("-", " ").title()
    trigger = stream.get("trigger") or "the stream's approved trigger occurs"
    deliverables = stream.get("deliverables", [])
    quality = stream.get("quality_gates", [])
    decisions = stream.get("decisions", [])
    residue = stream.get("durable_residue", [])
    approvals = stream.get("approvals", [])
    description = (
        f"Use when performing the person's recurring {title} work stream, especially when {trigger}. "
        "Use for producing its approved deliverables, applying its domain judgment and quality gates, "
        "and preparing the configured handoff; do not use for unrelated tasks that merely share keywords."
    )
    content = f"""---
name: {name}
description: {yaml_scalar(description)}
license: MIT
{common_metadata(profile)}---

# {title}

## Trigger

{trigger}

## Inputs and sources of truth

{md_list(stream.get('inputs', []), 'Inspect the profile/blueprint and ask for the missing authoritative input.')}

## Decisions and judgment

{md_list(decisions, 'No decisions were captured; return to the blueprint before autonomous execution.')}

When a consequential choice has real alternatives, present the recommendation, trade-offs, and evidence. Do not hide the decision inside execution prose.

## Procedure

1. Use `personal-start-work` to create the execution brief.
2. Confirm authoritative inputs and freshness.
3. Perform the bounded actions in the approved order.
4. Stop at any human approval gate.
5. Produce the deliverable using the output contract.
6. Apply every quality gate and report failures honestly.
7. Use `personal-finish-work` for handoff and residue classification.

## Deliverable contract

{md_list(deliverables, 'TODO: define the concrete deliverable before release.')}

## Quality gates

{md_list(quality, 'TODO: define observable quality gates before release.')}

## Human approvals

{md_list(approvals, 'Use the global automation boundaries; ask before consequential external action.')}

## Durable residue

{md_list(residue, 'Use praxis-distill only when future work will benefit.')}

## Failure and escalation

- Missing or conflicting source of truth → stop and resolve authority.
- Required input unavailable → state impact and request it; do not invent.
- Quality gate fails → do not label the deliverable complete.
- Risk exceeds the approved boundary → escalate to the person.
- Repeated new failure → log evidence for retrospective; do not rewrite the skill mid-task.
"""
    return name, content


def generated_skills(profile: Dict[str, Any], max_streams: int) -> Dict[Path, str]:
    files = {
        Path("personal-start-work/SKILL.md"): start_skill(profile),
        Path("personal-finish-work/SKILL.md"): finish_skill(profile),
        Path("personal-weekly-review/SKILL.md"): weekly_skill(profile),
    }
    streams = [s for s in profile.get("work_streams", []) if isinstance(s, dict)]
    streams.sort(key=lambda s: s.get("priority", 999))
    for stream in streams[:max_streams]:
        name, content = stream_skill(profile, stream)
        files[Path(name) / "SKILL.md"] = content
    return files


def backup_existing(source: Path, root: Path, relative: Path) -> Path:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def plan_files(base: Path, files: Dict[Path, str], force: bool) -> List[Dict[str, str]]:
    plan = []
    for relative in sorted(files, key=lambda p: str(p).lower()):
        target = base / relative
        action = "replace" if target.exists() and force else "skip" if target.exists() else "create"
        plan.append({"base": str(base), "relative": str(relative), "path": str(target), "action": action})
    return plan


def apply_plan(plan: List[Dict[str, str]], content: Dict[Path, str], backup_root: Path | None) -> List[Dict[str, str]]:
    results = []
    for item in plan:
        target = Path(item["path"])
        relative = Path(item["relative"])
        action = item["action"]
        result = dict(item)
        if action == "skip":
            result["result"] = "unchanged"
        else:
            if action == "replace":
                if backup_root is None:
                    raise RuntimeError("replace planned without backup root")
                backup = backup_existing(target, backup_root, relative)
                result["backup"] = str(backup)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content[relative], encoding="utf-8")
            result["result"] = "written"
        results.append(result)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--vault", type=Path)
    parser.add_argument("--skills-target", type=Path, required=True)
    parser.add_argument("--mode", choices=("augment", "new-vault", "skills-only"), default="augment")
    parser.add_argument("--max-streams", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--report", type=Path, default=Path("praxis-install-report.json"))
    args = parser.parse_args()

    if args.max_streams < 1 or args.max_streams > 20:
        raise SystemExit("Error: --max-streams must be between 1 and 20.")
    if args.mode != "skills-only" and args.vault is None:
        raise SystemExit("Error: --vault is required unless --mode skills-only.")
    if args.force and args.backup_dir is None:
        raise SystemExit("Error: --force requires --backup-dir so every replacement is recoverable.")
    if args.mode == "new-vault" and args.vault and args.vault.exists() and any(args.vault.iterdir()) and not args.force:
        raise SystemExit("Error: new-vault target is not empty. Use augment or explicit --force with --backup-dir.")

    profile = load_profile(args.profile)
    skill_content = generated_skills(profile, args.max_streams)
    plans: List[Dict[str, str]] = []
    vault_content: Dict[Path, str] = {}
    if args.mode != "skills-only":
        assert args.vault is not None
        vault_content = vault_files(profile)
        plans.extend(plan_files(args.vault, vault_content, args.force))
    plans.extend(plan_files(args.skills_target, skill_content, args.force))

    report = {
        "timestamp": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "profile_id": profile.get("profile_id"),
        "mode": args.mode,
        "dry_run": args.dry_run,
        "force": args.force,
        "backup_dir": str(args.backup_dir) if args.backup_dir else None,
        "actions": plans,
    }
    if args.dry_run:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    results: List[Dict[str, str]] = []
    if args.mode != "skills-only":
        assert args.vault is not None
        vault_plan = [p for p in plans if p["base"] == str(args.vault)]
        results.extend(apply_plan(vault_plan, vault_content, args.backup_dir / "vault" if args.backup_dir else None))
    skill_plan = [p for p in plans if p["base"] == str(args.skills_target)]
    results.extend(apply_plan(skill_plan, skill_content, args.backup_dir / "skills" if args.backup_dir else None))
    report["actions"] = results
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "complete",
        "report": str(args.report),
        "created": sum(1 for r in results if r["action"] == "create"),
        "replaced": sum(1 for r in results if r["action"] == "replace"),
        "skipped": sum(1 for r in results if r["action"] == "skip"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
