#!/usr/bin/env python3
"""Persist Praxis interview state without making model calls.

Commands:
  start     Initialize workspace and profile.
  record    Set a value at a dotted path.
  append    Append a value to a list at a dotted path.
  status    Print a compact JSON status report.
  complete  Mark complete after structural validation.
  export    Write Markdown summaries from the profile.

All structured data is written to stdout; diagnostics go to stderr.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List

SCHEMA_VERSION = "1.0"
VALID_DEPTHS = {"quick", "standard", "deep"}
VALID_STATES = {"confirmed", "inferred", "deferred", "disputed"}


def absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def reject_symlink_components(path: Path, label: str) -> None:
    path = absolute(path)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink() and current.parent != Path(path.anchor):
            raise SystemExit(f"Error: {label} contains a symlink component: {current}")
        if not current.exists():
            break


def workspace_path(value: str) -> Path:
    workspace = absolute(Path(value))
    reject_symlink_components(workspace, "workspace path")
    return workspace


def atomic_write(path: Path, text: str) -> None:
    reject_symlink_components(path, "output path")
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


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    reject_symlink_components(path, "profile path")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Error: profile not found: {path}. Run 'start' first.")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid JSON in {path}: {exc}")


def save_json(path: Path, data: Dict[str, Any]) -> None:
    atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "Error: --value must be valid JSON. "
            f"Strings require quotes, for example --value '\"weekly\"'. Details: {exc}"
        )


def split_path(path: str) -> List[str]:
    parts = [p for p in path.split(".") if p]
    if not parts or any(not re.fullmatch(r"[A-Za-z0-9_-]+", p) for p in parts):
        raise SystemExit("Error: --path must be a dotted path using letters, numbers, _ or -.")
    return parts


def get_parent(root: Dict[str, Any], parts: List[str]) -> tuple[Dict[str, Any], str]:
    node: Dict[str, Any] = root
    for part in parts[:-1]:
        current = node.get(part)
        if current is None:
            current = {}
            node[part] = current
        if not isinstance(current, dict):
            raise SystemExit(f"Error: cannot descend through non-object field '{part}'.")
        node = current
    return node, parts[-1]


def add_evidence(profile: Dict[str, Any], args: argparse.Namespace, value: Any) -> None:
    entry = {
        "timestamp": now_iso(),
        "question_id": args.question_id or args.path,
        "question": args.question or "",
        "path": args.path,
        "state": args.state,
        "source": args.source,
        "confidence": args.confidence,
        "value": value,
    }
    profile.setdefault("evidence", []).append(entry)


def base_profile(depth: str, person_name: str | None) -> Dict[str, Any]:
    timestamp = now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "profile_id": str(uuid.uuid4()),
        "status": "interviewing",
        "created_at": timestamp,
        "updated_at": timestamp,
        "interview": {"depth": depth, "resolved_decisions": 0},
        "person": {"display_name": person_name or ""},
        "consent": {
            "inspect_allowed": [],
            "restricted_data": [],
            "change_permission": "create-only-until-approved",
        },
        "outcomes": {"primary": "", "success_measures": [], "failure_costs": []},
        "work_streams": [],
        "tools_and_sources": {"tools": [], "sources_of_truth": []},
        "human_constraints": {
            "accessibility": [],
            "environment": [],
            "attention_energy": [],
            "communication": [],
        },
        "knowledge_policy": {
            "durable_note_types": ["research", "decision", "memory", "prompt", "project-state", "review"],
            "provenance_required": True,
            "raw_transcripts_as_memory": False,
            "existing_structure_to_preserve": [],
        },
        "automation_boundaries": {
            "autonomous": [],
            "review_before_action": [],
            "explicit_per_action": [],
            "forbidden": [],
        },
        "governance": {"review_cadence": "", "change_budget": "", "owner": ""},
        "evidence": [],
        "open_questions": [],
    }


def cmd_start(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    profile_path = workspace / "profile.json"
    events_path = workspace / "events.jsonl"
    existing = [path for path in (profile_path, events_path) if path.exists() or path.is_symlink()]
    if existing and not args.force:
        raise SystemExit(
            f"Error: {existing[0]} already exists. Use a different workspace or --force with --backup-dir."
        )
    if args.force and args.backup_dir is None:
        raise SystemExit("Error: --force requires --backup-dir so prior interview state is recoverable.")
    if args.depth not in VALID_DEPTHS:
        raise SystemExit(f"Error: --depth must be one of: {', '.join(sorted(VALID_DEPTHS))}.")
    for path in existing:
        reject_symlink_components(path, "interview state")
        if not path.is_file():
            raise SystemExit(f"Error: interview state path is not a regular file: {path}")
    backup_root = absolute(args.backup_dir) if args.backup_dir else None
    backups: Dict[Path, Path] = {}
    if backup_root is not None:
        reject_symlink_components(backup_root, "backup path")
        if paths_overlap(workspace, backup_root):
            raise SystemExit("Error: workspace and backup directories must not overlap.")
        for path in existing:
            backup = backup_root / path.name
            reject_symlink_components(backup, "backup target")
            if backup.exists() or backup.is_symlink():
                raise SystemExit(f"Error: backup destination already exists: {backup}")
            backups[path] = backup
    workspace.mkdir(parents=True, exist_ok=True)
    profile = base_profile(args.depth, args.person_name)
    for original, backup in backups.items():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, backup)
    try:
        save_json(profile_path, profile)
        atomic_write(events_path, "")
    except Exception:
        for path in (profile_path, events_path):
            if path in backups:
                shutil.copy2(backups[path], path)
            elif path not in existing:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
        raise
    print(json.dumps({"status": "started", "profile": str(profile_path), "depth": args.depth}))
    return 0


def cmd_record(args: argparse.Namespace, append: bool = False) -> int:
    if args.state not in VALID_STATES:
        raise SystemExit(f"Error: --state must be one of: {', '.join(sorted(VALID_STATES))}.")
    workspace = workspace_path(args.workspace)
    path = workspace / "profile.json"
    profile = load_json(path)
    value = parse_value(args.value)
    parts = split_path(args.path)
    parent, key = get_parent(profile, parts)
    if append:
        current = parent.get(key)
        if current is None:
            current = []
            parent[key] = current
        if not isinstance(current, list):
            raise SystemExit(f"Error: target '{args.path}' is not a list.")
        current.append(value)
    else:
        parent[key] = value
    add_evidence(profile, args, value)
    if args.state == "confirmed":
        profile.setdefault("interview", {}).setdefault("resolved_decisions", 0)
        profile["interview"]["resolved_decisions"] += 1
    profile["updated_at"] = now_iso()
    event = {
        "event": "append" if append else "record",
        "timestamp": profile["updated_at"],
        "path": args.path,
        "state": args.state,
        "value": value,
    }
    events_path = workspace / "events.jsonl"
    reject_symlink_components(events_path, "event log")
    try:
        previous_events = events_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        previous_events = ""
    if events_path.exists() and not events_path.is_file():
        raise SystemExit(f"Error: event log is not a regular file: {events_path}")
    next_events = previous_events + json.dumps(event, ensure_ascii=False) + "\n"
    atomic_write(events_path, next_events)
    try:
        save_json(path, profile)
    except Exception:
        # Keep profile and event log logically consistent if the second replace fails.
        atomic_write(events_path, previous_events)
        raise
    print(json.dumps({"status": "recorded", "path": args.path, "state": args.state}))
    return 0


def validation_errors(profile: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not profile.get("outcomes", {}).get("primary"):
        errors.append("outcomes.primary is required")
    work_streams = profile.get("work_streams")
    if not isinstance(work_streams, list) or not work_streams:
        errors.append("at least one work_stream is required")
    else:
        required = {"id", "name", "trigger", "deliverables", "quality_gates"}
        for index, stream in enumerate(work_streams):
            if not isinstance(stream, dict):
                errors.append(f"work_streams[{index}] must be an object")
                continue
            missing = [key for key in required if not stream.get(key)]
            if missing:
                errors.append(f"work_streams[{index}] missing: {', '.join(missing)}")
    boundaries = profile.get("automation_boundaries", {})
    if not any(boundaries.get(key) for key in (
        "autonomous", "review_before_action", "explicit_per_action", "forbidden"
    )):
        errors.append("automation_boundaries must contain at least one classified action")
    if not profile.get("governance", {}).get("review_cadence"):
        errors.append("governance.review_cadence is required")
    if "knowledge_policy" not in profile:
        errors.append("knowledge_policy is required")
    return errors


def cmd_status(args: argparse.Namespace) -> int:
    profile = load_json(workspace_path(args.workspace) / "profile.json")
    states: Dict[str, int] = {state: 0 for state in VALID_STATES}
    for item in profile.get("evidence", []):
        state = item.get("state")
        if state in states:
            states[state] += 1
    output = {
        "status": profile.get("status"),
        "depth": profile.get("interview", {}).get("depth"),
        "resolved_decisions": profile.get("interview", {}).get("resolved_decisions", 0),
        "work_streams": len(profile.get("work_streams", [])),
        "evidence_states": states,
        "validation_errors": validation_errors(profile),
        "open_questions": len(profile.get("open_questions", [])),
    }
    print(json.dumps(output, indent=2))
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    path = workspace_path(args.workspace) / "profile.json"
    profile = load_json(path)
    errors = validation_errors(profile)
    if errors and not args.allow_incomplete:
        print(json.dumps({"status": "incomplete", "errors": errors}, indent=2))
        return 2
    profile["status"] = "complete" if not errors else "complete-with-open-items"
    profile["completed_at"] = now_iso()
    profile["updated_at"] = profile["completed_at"]
    save_json(path, profile)
    print(json.dumps({"status": profile["status"], "errors": errors}, indent=2))
    return 0


def md_list(items: Any) -> List[str]:
    if not items:
        return ["- None recorded."]
    result = []
    for item in items:
        if isinstance(item, dict):
            label = item.get("name") or item.get("id") or json.dumps(item, ensure_ascii=False)
        else:
            label = str(item)
        result.append(f"- {label}")
    return result


def cmd_export(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    profile = load_json(workspace / "profile.json")
    summary = [
        "# Praxis Interview Summary",
        "",
        f"- Profile: `{profile.get('profile_id', '')}`",
        f"- Status: `{profile.get('status', '')}`",
        f"- Interview depth: `{profile.get('interview', {}).get('depth', '')}`",
        f"- Updated: `{profile.get('updated_at', '')}`",
        "",
        "## Primary outcome",
        "",
        profile.get("outcomes", {}).get("primary") or "Not confirmed.",
        "",
        "## Initial work streams",
        "",
        *md_list(profile.get("work_streams")),
        "",
        "## Existing structure to preserve",
        "",
        *md_list(profile.get("knowledge_policy", {}).get("existing_structure_to_preserve")),
        "",
        "## Review-before-action boundaries",
        "",
        *md_list(profile.get("automation_boundaries", {}).get("review_before_action")),
        "",
        "## Forbidden boundaries",
        "",
        *md_list(profile.get("automation_boundaries", {}).get("forbidden")),
        "",
        "## Next stage",
        "",
        "Use `praxis-blueprint` after the person confirms this summary.",
        "",
    ]
    atomic_write(workspace / "interview-summary.md", "\n".join(summary))
    open_questions = ["# Open Questions", ""]
    if profile.get("open_questions"):
        for item in profile["open_questions"]:
            open_questions.append(f"- {item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)}")
    else:
        open_questions.append("- None recorded.")
    open_questions.append("")
    atomic_write(workspace / "open-questions.md", "\n".join(open_questions))
    print(json.dumps({
        "status": "exported",
        "files": [str(workspace / "interview-summary.md"), str(workspace / "open-questions.md")]
    }))
    return 0


def add_record_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", default="praxis")
    parser.add_argument("--path", required=True)
    parser.add_argument("--value", required=True, help="JSON value; quote JSON strings")
    parser.add_argument("--question-id", default="")
    parser.add_argument("--question", default="")
    parser.add_argument("--state", choices=sorted(VALID_STATES), default="confirmed")
    parser.add_argument("--source", default="user")
    parser.add_argument("--confidence", type=float, default=1.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Initialize an interview workspace")
    start.add_argument("--workspace", default="praxis")
    start.add_argument("--depth", choices=sorted(VALID_DEPTHS), default="standard")
    start.add_argument("--person-name")
    start.add_argument("--force", action="store_true")
    start.add_argument("--backup-dir", type=Path)
    start.set_defaults(func=cmd_start)

    record = sub.add_parser("record", help="Set a value at a dotted path")
    add_record_args(record)
    record.set_defaults(func=lambda a: cmd_record(a, append=False))

    append = sub.add_parser("append", help="Append a value to a list at a dotted path")
    add_record_args(append)
    append.set_defaults(func=lambda a: cmd_record(a, append=True))

    status = sub.add_parser("status", help="Print interview status as JSON")
    status.add_argument("--workspace", default="praxis")
    status.set_defaults(func=cmd_status)

    complete = sub.add_parser("complete", help="Validate and mark the profile complete")
    complete.add_argument("--workspace", default="praxis")
    complete.add_argument("--allow-incomplete", action="store_true")
    complete.set_defaults(func=cmd_complete)

    export = sub.add_parser("export", help="Generate Markdown summaries")
    export.add_argument("--workspace", default="praxis")
    export.set_defaults(func=cmd_export)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if hasattr(args, "confidence") and not 0 <= args.confidence <= 1:
        raise SystemExit("Error: --confidence must be between 0 and 1.")
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
