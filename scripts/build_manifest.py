#!/usr/bin/env python3
"""Build or verify a SHA-256 manifest for distributable Praxis files."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

EXCLUDED = {"MANIFEST.sha256", "praxis-workflow-os.zip"}
EXCLUDED_PARTS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "dist"}


def entries(root: Path):
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root)
        if path.name in EXCLUDED or path.suffix in {".pyc", ".pyo"} or any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        yield digest, rel.as_posix()


def render(root: Path) -> str:
    return "".join(f"{digest}  {rel}\n" for digest, rel in entries(root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output or args.root / "MANIFEST.sha256"
    current = render(args.root)
    if args.check:
        if not output.exists():
            print(f"Error: manifest not found: {output}", file=sys.stderr)
            return 2
        expected = output.read_text(encoding="utf-8")
        if expected != current:
            print("Error: manifest does not match repository contents.", file=sys.stderr)
            return 3
        print(f"Manifest valid: {output}")
        return 0
    output.write_text(current, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
