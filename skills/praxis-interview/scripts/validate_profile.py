#!/usr/bin/env python3
"""Validate a Praxis profile and emit structured JSON results."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def load(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Error: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        raise SystemExit("Error: profile root must be a JSON object.")
    return value


def validate(profile: Dict[str, Any]) -> tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    required = [
        "schema_version", "profile_id", "status", "interview", "person", "consent",
        "outcomes", "work_streams", "tools_and_sources", "human_constraints",
        "knowledge_policy", "automation_boundaries", "governance", "evidence", "open_questions",
    ]
    for key in required:
        if key not in profile:
            errors.append(f"missing top-level field: {key}")
    if not profile.get("outcomes", {}).get("primary"):
        errors.append("outcomes.primary must be non-empty")
    streams = profile.get("work_streams", [])
    if not isinstance(streams, list) or not streams:
        errors.append("work_streams must contain at least one item")
    else:
        ids = set()
        required_stream = ["id", "name", "trigger", "deliverables", "quality_gates"]
        for index, stream in enumerate(streams):
            if not isinstance(stream, dict):
                errors.append(f"work_streams[{index}] must be an object")
                continue
            for key in required_stream:
                if not stream.get(key):
                    errors.append(f"work_streams[{index}].{key} must be non-empty")
            stream_id = stream.get("id", "")
            if stream_id and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", stream_id):
                errors.append(f"work_streams[{index}].id must use lowercase kebab-case")
            if stream_id in ids:
                errors.append(f"duplicate work stream id: {stream_id}")
            ids.add(stream_id)
            if len(stream.get("quality_gates", [])) > 8:
                warnings.append(f"work_streams[{index}] has more than 8 quality gates; consider prioritizing")
    boundaries = profile.get("automation_boundaries", {})
    expected = ["autonomous", "review_before_action", "explicit_per_action", "forbidden"]
    for key in expected:
        if key not in boundaries:
            errors.append(f"automation_boundaries.{key} is missing")
    if not profile.get("governance", {}).get("review_cadence"):
        errors.append("governance.review_cadence must be non-empty")
    policy = profile.get("knowledge_policy", {})
    if policy.get("raw_transcripts_as_memory") is True:
        warnings.append("raw_transcripts_as_memory is true; Praxis recommends curated durable residue instead")
    if len(streams) > 3 and profile.get("status") != "mature":
        warnings.append("initial profile has more than 3 work streams; staged rollout is recommended")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    profile = load(args.profile)
    errors, warnings = validate(profile)
    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
