#!/usr/bin/env python3
"""Validate an Agent Skill folder using the core Agent Skills constraints.

This validator intentionally uses only the Python standard library and parses
simple YAML frontmatter fields used by this repository. It reports warnings for
quality and maintenance signals beyond syntax.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import stat
import sys
from pathlib import Path
from typing import Dict, List, Tuple

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(r"(?:\[[^\]]+\]\(([^)]+)\)|`((?:scripts|references|assets)/[^`]+)`)")


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str, List[str]]:
    errors: List[str] = []
    if not text.startswith("---\n"):
        return {}, text, ["SKILL.md must start with YAML frontmatter delimiter ---"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text, ["SKILL.md is missing the closing frontmatter delimiter ---"]
    raw = text[4:end]
    body = text[end + 4:].lstrip("\n")
    fields: Dict[str, str] = {}
    for line_no, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            continue
        if ":" not in line:
            errors.append(f"frontmatter line {line_no} is not key: value")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(('"', "'")):
            try:
                parsed = shlex.split(value)
                value = parsed[0] if parsed else ""
            except ValueError:
                errors.append(f"frontmatter field {key} has invalid quoting")
        elif ": " in value:
            errors.append(
                f"frontmatter field {key} contains an unquoted colon; quote the YAML scalar"
            )
        fields[key] = value
    return fields, body, errors


def validate(skill_dir: Path) -> Dict[str, object]:
    errors: List[str] = []
    warnings: List[str] = []
    path = skill_dir / "SKILL.md"
    if not path.exists():
        return {"valid": False, "errors": [f"missing {path}"], "warnings": []}
    text = path.read_text(encoding="utf-8")
    fields, body, parse_errors = parse_frontmatter(text)
    errors.extend(parse_errors)
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        errors.append("frontmatter.name is required")
    elif not NAME_RE.fullmatch(name):
        errors.append("name must be lowercase kebab-case without consecutive or edge hyphens")
    elif len(name) > 64:
        errors.append("name must be at most 64 characters")
    if name and name != skill_dir.name:
        errors.append(f"name '{name}' does not match parent folder '{skill_dir.name}'")
    if not description:
        errors.append("frontmatter.description is required")
    elif len(description) > 1024:
        errors.append("description must be at most 1024 characters")
    elif len(description) < 40:
        warnings.append("description is very short; include realistic trigger contexts")
    if description and "use when" not in description.lower():
        warnings.append("description does not contain 'Use when'; verify triggering intent is explicit")
    lines = text.splitlines()
    if len(lines) > 500:
        warnings.append(f"SKILL.md has {len(lines)} lines; move heavy material to references")
    words = len(re.findall(r"\b\w+\b", body))
    if words > 3500:
        warnings.append(f"SKILL.md body has approximately {words} words; progressive disclosure may be weak")
    if "TODO" in text:
        warnings.append("SKILL.md contains TODO markers")
    if not re.search(r"^#\s+", body, flags=re.MULTILINE):
        errors.append("SKILL.md body needs a level-1 heading")
    if "http://" in text:
        warnings.append("unencrypted http:// URL found")
    if re.search(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*[^\s{[]", text):
        warnings.append("possible credential-like literal found; inspect manually")

    for match in REF_RE.finditer(text):
        rel = match.group(1) or match.group(2)
        if not rel or rel.startswith(("http://", "https://", "#")):
            continue
        rel = rel.split("#", 1)[0]
        target = skill_dir / rel
        if not target.exists():
            errors.append(f"referenced file does not exist: {rel}")

    scripts = list((skill_dir / "scripts").glob("*")) if (skill_dir / "scripts").exists() else []
    for script in scripts:
        if not script.is_file() or script.name.startswith("."):
            continue
        if script.suffix == ".py":
            content = script.read_text(encoding="utf-8", errors="replace")
            if "argparse" not in content and "--help" not in content:
                warnings.append(f"Python script may not expose --help: {script.relative_to(skill_dir)}")
            if script.name != "validate_skill.py":
                if "requests" in content or "urllib.request" in content or "http.client" in content:
                    warnings.append(f"network-capable script requires explicit review: {script.relative_to(skill_dir)}")
                if "subprocess" in content or "os.system" in content:
                    warnings.append(f"process execution requires explicit review: {script.relative_to(skill_dir)}")
        mode = script.stat().st_mode
        if script.suffix in {".sh", ".py"} and not (mode & stat.S_IXUSR):
            warnings.append(f"script is not executable for owner: {script.relative_to(skill_dir)}")

    agent_metadata = skill_dir / "agents/openai.yaml"
    if not agent_metadata.exists():
        warnings.append("missing agents/openai.yaml for Codex skill presentation")
    else:
        metadata_text = agent_metadata.read_text(encoding="utf-8")
        for field in ("display_name", "short_description", "default_prompt"):
            if not re.search(rf"(?m)^\s{{2}}{field}:\s*\S", metadata_text):
                errors.append(f"agents/openai.yaml missing interface.{field}")
        if name and f"${name}" not in metadata_text:
            errors.append("agents/openai.yaml default_prompt must explicitly mention the skill")

    eval_path = skill_dir / "evals/evals.json"
    if not eval_path.exists():
        warnings.append("missing evals/evals.json")
    else:
        try:
            data = json.loads(eval_path.read_text(encoding="utf-8"))
            evals = data.get("evals", []) if isinstance(data, dict) else []
            if not isinstance(evals, list) or not evals:
                errors.append("evals/evals.json must contain a non-empty evals list")
            if isinstance(data, dict) and data.get("skill_name") not in (None, name):
                errors.append("evals skill_name does not match frontmatter name")
            ids = set()
            for index, item in enumerate(evals):
                if not isinstance(item, dict) or not item.get("prompt") or not item.get("expected_output"):
                    errors.append(f"evals[{index}] needs prompt and expected_output")
                    continue
                if item.get("id") in ids:
                    errors.append(f"evals[{index}] has a duplicate id: {item.get('id')!r}")
                ids.add(item.get("id"))
                assertions = item.get("assertions")
                if (
                    not isinstance(assertions, list)
                    or not assertions
                    or not all(isinstance(value, str) and value.strip() for value in assertions)
                ):
                    errors.append(f"evals[{index}] needs a non-empty list of assertion strings")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid evals/evals.json: {exc}")

    trigger_path = skill_dir / "evals/trigger_queries.json"
    if not trigger_path.exists():
        warnings.append("missing evals/trigger_queries.json")
    else:
        try:
            queries = json.loads(trigger_path.read_text(encoding="utf-8"))
            if not isinstance(queries, list) or not 16 <= len(queries) <= 24:
                errors.append("trigger_queries.json must contain 16-24 labeled queries")
            else:
                seen_queries = set()
                positives = 0
                negatives = 0
                for index, item in enumerate(queries):
                    if not isinstance(item, dict) or not isinstance(item.get("query"), str) or not item["query"].strip():
                        errors.append(f"trigger_queries[{index}] needs a non-empty query string")
                        continue
                    if not isinstance(item.get("should_trigger"), bool):
                        errors.append(f"trigger_queries[{index}].should_trigger must be boolean")
                    elif item["should_trigger"]:
                        positives += 1
                    else:
                        negatives += 1
                    normalized = item["query"].strip().casefold()
                    if normalized in seen_queries:
                        errors.append(f"trigger_queries[{index}] duplicates another query")
                    seen_queries.add(normalized)
                if positives != negatives:
                    errors.append("trigger queries must contain equal positive and near-miss-negative cases")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid evals/trigger_queries.json: {exc}")

    return {
        "valid": not errors,
        "skill": name or skill_dir.name,
        "path": str(skill_dir),
        "line_count": len(lines),
        "word_count": words,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()
    result = validate(args.skill)
    print(json.dumps(result, indent=2))
    failed = not result["valid"] or (args.strict and bool(result["warnings"]))
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
