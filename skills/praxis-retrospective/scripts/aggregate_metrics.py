#!/usr/bin/env python3
"""Aggregate optional Praxis JSONL workflow events into a compact JSON report.

Accepted fields are intentionally flexible. Common fields:
  timestamp, skill, work_stream, outcome, duration_seconds, tokens,
  corrections, quality_failures, approval_events, notes_created, friction_tags.
Malformed lines are reported and skipped unless --strict is used.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

DEFAULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_LINES = 100_000
DEFAULT_MAX_KEYS = 10_000


class LimitExceeded(ValueError):
    pass


def reject_symlink_components(path: Path, label: str) -> None:
    path = path if path.is_absolute() else Path.cwd() / path
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink() and current.parent != Path(path.anchor):
            raise SystemExit(f"Error: {label} contains a symlink component: {current}")
        if not current.exists():
            break


def atomic_write(path: Path, text: str) -> None:
    reject_symlink_components(path, "metrics output path")
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


def numeric(values: Iterable[Any]) -> List[float]:
    result = []
    for value in values:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result.append(float(value))
    return result


def stats(values: List[float]) -> Dict[str, float | int | None]:
    if not values:
        return {"count": 0, "sum": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(values),
        "sum": round(sum(values), 3),
        "mean": round(statistics.fmean(values), 3),
        "median": round(statistics.median(values), 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
    }


def load_events(
    path: Path,
    strict: bool,
    max_bytes: int,
    max_lines: int,
    max_keys: int,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    events: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    if path.is_symlink():
        raise SystemExit(f"Error: event log must not be a symlink: {path}")
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        raise SystemExit(f"Error: event log not found: {path}")
    if size > max_bytes:
        raise LimitExceeded(f"input is {size} bytes; --max-bytes is {max_bytes}")
    observed_keys = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if line_no > max_lines:
                raise LimitExceeded(f"input exceeds --max-lines ({max_lines})")
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError("event must be a JSON object")
                for field in ("skill", "work_stream", "outcome"):
                    observed_keys.add((field, str(item.get(field, "unknown"))))
                tags = item.get("friction_tags", [])
                if isinstance(tags, str):
                    tags = [tags]
                if isinstance(tags, list):
                    observed_keys.update(("friction_tag", str(tag)) for tag in tags)
                if len(observed_keys) > max_keys:
                    raise LimitExceeded(f"input exceeds --max-keys ({max_keys})")
                events.append(item)
            except (json.JSONDecodeError, ValueError) as exc:
                if isinstance(exc, LimitExceeded):
                    raise
                error = {"line": line_no, "error": str(exc)}
                errors.append(error)
                if strict:
                    print(json.dumps({"valid": False, "errors": errors}, indent=2))
                    raise SystemExit(2)
    return events, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("--max-keys", type=int, default=DEFAULT_MAX_KEYS)
    args = parser.parse_args()

    if min(args.max_bytes, args.max_lines, args.max_keys) < 1:
        raise SystemExit("Error: resource limits must be positive integers.")
    try:
        events, parse_errors = load_events(
            args.input, args.strict, args.max_bytes, args.max_lines, args.max_keys
        )
    except LimitExceeded as exc:
        print(json.dumps({
            "valid": False,
            "error": "resource limit exceeded",
            "detail": str(exc),
            "limits": {
                "max_bytes": args.max_bytes,
                "max_lines": args.max_lines,
                "max_keys": args.max_keys,
            },
        }, indent=2))
        return 2
    skills = Counter(str(e.get("skill", "unknown")) for e in events)
    streams = Counter(str(e.get("work_stream", "unknown")) for e in events)
    outcomes = Counter(str(e.get("outcome", "unknown")) for e in events)
    friction = Counter()
    by_skill: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "events": 0, "corrections": 0, "quality_failures": 0, "approval_events": 0, "notes_created": 0,
        "duration_seconds": [], "tokens": []
    })
    for event in events:
        skill = str(event.get("skill", "unknown"))
        bucket = by_skill[skill]
        bucket["events"] += 1
        for field in ("corrections", "quality_failures", "approval_events", "notes_created"):
            value = event.get(field, 0)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                bucket[field] += value
        for field in ("duration_seconds", "tokens"):
            value = event.get(field)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                bucket[field].append(float(value))
        tags = event.get("friction_tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if isinstance(tags, list):
            friction.update(str(t) for t in tags)

    skill_detail = {}
    for skill, bucket in sorted(by_skill.items()):
        skill_detail[skill] = {
            "events": bucket["events"],
            "corrections": bucket["corrections"],
            "quality_failures": bucket["quality_failures"],
            "approval_events": bucket["approval_events"],
            "notes_created": bucket["notes_created"],
            "duration_seconds": stats(numeric(bucket["duration_seconds"])),
            "tokens": stats(numeric(bucket["tokens"])),
        }

    result = {
        "valid_lines": len(events),
        "parse_errors": parse_errors,
        "skills": dict(skills.most_common()),
        "work_streams": dict(streams.most_common()),
        "outcomes": dict(outcomes.most_common()),
        "friction_tags": dict(friction.most_common()),
        "duration_seconds": stats(numeric(e.get("duration_seconds") for e in events)),
        "tokens": stats(numeric(e.get("tokens") for e in events)),
        "corrections": stats(numeric(e.get("corrections") for e in events)),
        "quality_failures": stats(numeric(e.get("quality_failures") for e in events)),
        "by_skill": skill_detail,
    }
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        atomic_write(args.output, text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
