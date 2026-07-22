#!/usr/bin/env python3
"""Build or verify a SHA-256 manifest for distributable Praxis files."""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
# subprocess is limited to a resolved Git executable with a fixed argument list.
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path

EXCLUDED = {"MANIFEST.sha256", "praxis-workflow-os.zip"}
EXCLUDED_PARTS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "dist"}


def excluded(path: Path) -> bool:
    return (
        path.name in EXCLUDED
        or path.suffix in {".pyc", ".pyo"}
        or any(part in EXCLUDED_PARTS for part in path.parts)
    )


def reject_untracked_release_files(root: Path) -> None:
    """Fail closed when a Git checkout has unexpected distributable files."""
    if not (root / ".git").exists():
        return
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required to validate untracked release files")
    # The executable is absolute, the argument list is fixed, and shell remains disabled.
    result = subprocess.run(  # nosec B603
        [git, "-C", str(root), "ls-files", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    unexpected = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", errors="strict"))
        if not excluded(rel):
            unexpected.append(rel.as_posix())
    if unexpected:
        raise ValueError(
            "untracked release file(s) found; add, ignore, or remove them first: "
            + ", ".join(sorted(unexpected))
        )


def git_tracked_files(root: Path) -> list[Path]:
    """Return only files present in Git's index, excluding ignored local residue."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required to enumerate release files")
    result = subprocess.run(  # nosec B603
        [git, "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    paths = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", errors="strict"))
        if excluded(rel):
            continue
        path = root / rel
        if path.is_symlink():
            raise ValueError(f"refusing symlink in release source: {rel.as_posix()}")
        if not path.is_file():
            raise ValueError(f"tracked release file is missing: {rel.as_posix()}")
        paths.append(path)
    return paths


def entries(root: Path):
    reject_untracked_release_files(root)
    candidates = git_tracked_files(root) if (root / ".git").exists() else root.rglob("*")
    for path in sorted(candidates):
        rel = path.relative_to(root)
        if excluded(rel):
            continue
        if path.is_symlink():
            raise ValueError(f"refusing symlink in release source: {rel.as_posix()}")
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        yield digest, rel.as_posix()


def render(root: Path) -> str:
    return "".join(f"{digest}  {rel}\n" for digest, rel in entries(root))


def reject_symlink_components(path: Path) -> None:
    path = path if path.is_absolute() else Path.cwd() / path
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"manifest output contains a symlink component: {current}")
        if not current.exists():
            break


def atomic_write(path: Path, text: str) -> None:
    reject_symlink_components(path)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "MANIFEST.sha256"
    try:
        reject_symlink_components(output)
        current = render(root)
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 4
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
    atomic_write(output, current)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
