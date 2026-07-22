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
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


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


def load_events(path: Path, strict: bool) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    events: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"Error: event log not found: {path}")
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError("event must be a JSON object")
            events.append(item)
        except (json.JSONDecodeError, ValueError) as exc:
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
    args = parser.parse_args()

    events, parse_errors = load_events(args.input, args.strict)
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
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
