#!/usr/bin/env python3
"""Build deterministic Praxis release archives and SHA-256 checksums."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import stat
import tarfile
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
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def archive_prefix(version: str) -> str:
    return f"praxis-workflow-os-v{version}"


def build_zip(root: Path, output: Path, version: str) -> None:
    prefix = archive_prefix(version)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in source_files(root):
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=ZIP_DATE)
            info.create_system = 3
            mode = path.stat().st_mode
            permissions = 0o755 if mode & stat.S_IXUSR else 0o644
            info.external_attr = permissions << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_tar_gz(root: Path, output: Path, version: str) -> None:
    prefix = archive_prefix(version)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in source_files(root):
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
    parser.add_argument("--clean", action="store_true", help="Remove the output directory before building")
    args = parser.parse_args()

    root = args.root.resolve()
    dist = (args.dist or root / "dist").resolve()
    version = version_from(root)
    validate_dist_path(root, dist)
    stem = archive_prefix(version)
    if args.clean and dist.exists():
        clean_known_outputs(dist, stem)
    dist.mkdir(parents=True, exist_ok=True)

    zip_path = dist / f"{stem}.zip"
    tar_path = dist / f"{stem}.tar.gz"
    build_zip(root, zip_path, version)
    build_tar_gz(root, tar_path, version)

    checksums = dist / "SHA256SUMS"
    checksums.write_text(
        f"{sha256(zip_path)}  {zip_path.name}\n"
        f"{sha256(tar_path)}  {tar_path.name}\n",
        encoding="utf-8",
    )
    print(zip_path)
    print(tar_path)
    print(checksums)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
