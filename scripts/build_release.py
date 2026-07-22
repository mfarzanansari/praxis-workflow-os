#!/usr/bin/env python3
"""Build deterministic Praxis release archives and SHA-256 checksums."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import shutil
import stat
# subprocess is limited to a resolved Git executable with a fixed argument list.
import subprocess  # nosec B404
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
}
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def version_from(root: Path) -> str:
    version_file = root / "VERSION"
    if not version_file.is_file():
        raise ValueError(f"VERSION not found: {version_file}")
    version = version_file.read_text(encoding="utf-8").strip()
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"VERSION is not MAJOR.MINOR.PATCH: {version!r}")
    return version


def source_files(root: Path) -> Iterable[Path]:
    if (root / ".git").exists():
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
            if (
                any(part in EXCLUDED_PARTS for part in rel.parts)
                or rel.name in EXCLUDED_NAMES
                or rel.suffix in EXCLUDED_SUFFIXES
            ):
                continue
            unexpected.append(rel.as_posix())
        if unexpected:
            raise ValueError(
                "untracked release file(s) found; add, ignore, or remove them first: "
                + ", ".join(sorted(unexpected))
            )
        tracked = subprocess.run(  # nosec B603
            [git, "-C", str(root), "ls-files", "-z"],
            check=True,
            capture_output=True,
        )
        candidates = []
        for raw in tracked.stdout.split(b"\0"):
            if not raw:
                continue
            rel = Path(raw.decode("utf-8", errors="strict"))
            path = root / rel
            if not path.exists() and not path.is_symlink():
                raise ValueError(f"tracked release file is missing: {rel.as_posix()}")
            candidates.append(path)
    else:
        candidates = root.rglob("*")
    for path in sorted(candidates):
        rel = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.is_symlink():
            raise ValueError(f"refusing symlink in release source: {rel.as_posix()}")
        if not path.is_file():
            continue
        yield path


def archive_prefix(version: str) -> str:
    return f"praxis-workflow-os-v{version}"


def build_zip(root: Path, output: Path, version: str, files: Iterable[Path]) -> None:
    prefix = archive_prefix(version)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=ZIP_DATE)
            info.create_system = 3
            mode = path.stat().st_mode
            permissions = 0o755 if mode & stat.S_IXUSR else 0o644
            info.external_attr = permissions << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_tar_gz(root: Path, output: Path, version: str, files: Iterable[Path]) -> None:
    prefix = archive_prefix(version)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in files:
                    rel = path.relative_to(root).as_posix()
                    info = archive.gettarinfo(str(path), arcname=f"{prefix}/{rel}")
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    with path.open("rb") as handle:
                        archive.addfile(info, handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_dist_path(root: Path, dist: Path) -> None:
    """Reject output paths that overlap source in surprising or unsafe ways."""
    canonical = root / "dist"
    if dist == root or dist in root.parents:
        raise ValueError(f"release output must not be the source root or its ancestor: {dist}")
    if root in dist.parents and dist != canonical:
        raise ValueError(
            f"release output inside the source root must be the canonical directory: {canonical}"
        )


def clean_known_outputs(dist: Path, stem: str) -> None:
    """Remove only files this builder owns, never the output directory itself."""
    for path in (
        dist / f"{stem}.zip",
        dist / f"{stem}.tar.gz",
        dist / "SHA256SUMS",
    ):
        if path.is_dir():
            raise ValueError(f"refusing to replace release output directory: {path}")
        if path.exists() or path.is_symlink():
            path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dist", type=Path)
    parser.add_argument("--clean", action="store_true", help="Replace only release-owned output files")
    args = parser.parse_args()

    root = args.root.resolve()
    dist = (args.dist or root / "dist").resolve()
    version = version_from(root)
    validate_dist_path(root, dist)
    stem = archive_prefix(version)
    files = list(source_files(root))
    dist.mkdir(parents=True, exist_ok=True)
    final_paths = [dist / f"{stem}.zip", dist / f"{stem}.tar.gz", dist / "SHA256SUMS"]
    for path in final_paths:
        if path.is_symlink() or path.is_dir():
            raise ValueError(f"refusing unsafe release output path: {path}")

    staging = Path(tempfile.mkdtemp(prefix=".praxis-release-", dir=dist))
    try:
        staged_zip = staging / f"{stem}.zip"
        staged_tar = staging / f"{stem}.tar.gz"
        staged_checksums = staging / "SHA256SUMS"
        build_zip(root, staged_zip, version, files)
        build_tar_gz(root, staged_tar, version, files)
        with staged_checksums.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(
                f"{sha256(staged_zip)}  {staged_zip.name}\n"
                f"{sha256(staged_tar)}  {staged_tar.name}\n"
            )
        if args.clean:
            clean_known_outputs(dist, stem)
        for staged, final in zip(
            (staged_zip, staged_tar, staged_checksums), final_paths
        ):
            os.replace(staged, final)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    zip_path, tar_path, checksums = final_paths
    print(zip_path)
    print(tar_path)
    print(checksums)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
