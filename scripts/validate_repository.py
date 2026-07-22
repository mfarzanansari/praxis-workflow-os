#!/usr/bin/env python3
"""Validate all Agent Skills in a Praxis repository or target skills directory."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_validator(repo_root: Path):
    module_path = repo_root / "skills/praxis-skill-forge/scripts/validate_skill.py"
    if not module_path.exists():
        raise SystemExit(f"Error: validator not found: {module_path}")
    spec = importlib.util.spec_from_file_location("praxis_validate_skill", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit("Error: unable to load skill validator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skills-root", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    skills_root = args.skills_root or args.repo_root / "skills"
    if not skills_root.is_dir():
        raise SystemExit(f"Error: skills root not found: {skills_root}")
    validate = load_validator(args.repo_root)
    skills = sorted(p for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
    if not skills:
        raise SystemExit(f"Error: no skills found in {skills_root}")
    results: List[Dict[str, Any]] = [validate(skill) for skill in skills]
    errors = sum(len(r.get("errors", [])) for r in results)
    warnings = sum(len(r.get("warnings", [])) for r in results)
    report = {
        "valid": errors == 0 and (not args.strict or warnings == 0),
        "skills_root": str(skills_root),
        "skill_count": len(results),
        "error_count": errors,
        "warning_count": warnings,
        "results": results,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
