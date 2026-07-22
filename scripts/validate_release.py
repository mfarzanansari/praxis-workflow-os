#!/usr/bin/env python3
"""Validate Praxis repository readiness for a public release."""
from __future__ import annotations

import argparse
import json
import re
# subprocess invokes this repository's manifest validator with fixed arguments.
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ACTION_USE_RE = re.compile(r"(?m)^\s*uses:\s+[^@\s]+@([^\s#]+)")
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SKILL_VERSION_RE = re.compile(r"(?m)^[ \t]{2}version:\s*[\"']?([^\"'\s]+)")
SKILL_AUTHOR_RE = re.compile(r"(?m)^[ \t]{2}author:\s*(.+?)\s*$")
REQUIRED_FILES = [
    ".gitattributes",
    "README.md",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "GOVERNANCE.md",
    "ROADMAP.md",
    "RELEASING.md",
    "ARCHITECTURE.md",
    "RESEARCH_REPORT.md",
    "RELEASE_RESEARCH.md",
    "SOURCE_PROVENANCE.md",
    "MANIFEST.sha256",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/ISSUE_TEMPLATE/skill-proposal.yml",
]
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def add(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate_marketplace(root: Path, version: str, errors: list[str]) -> dict[str, Any] | None:
    path = root / ".claude-plugin/marketplace.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid marketplace manifest: {exc}")
        return None
    add(errors, data.get("name") == "praxis-workflow-os", "marketplace name must be praxis-workflow-os")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    add(errors, metadata.get("version") == version, "marketplace metadata.version must match VERSION")
    plugins = data.get("plugins")
    add(errors, isinstance(plugins, list) and len(plugins) == 1, "marketplace must define one Praxis plugin")
    if isinstance(plugins, list) and plugins:
        plugin = plugins[0] if isinstance(plugins[0], dict) else {}
        add(errors, plugin.get("name") == "praxis", "marketplace plugin name must be praxis")
        add(errors, plugin.get("version") == version, "marketplace plugin version must match VERSION")
        add(errors, plugin.get("strict") is False, "marketplace skill bundle must use strict: false")
        skills = plugin.get("skills")
        add(errors, isinstance(skills, list) and bool(skills), "marketplace plugin needs a non-empty skills list")
        if isinstance(skills, list):
            for item in skills:
                add(errors, isinstance(item, str), f"marketplace skill path is not a string: {item!r}")
                if isinstance(item, str):
                    target = root / item.removeprefix("./") / "SKILL.md"
                    add(errors, target.is_file(), f"marketplace skill path missing SKILL.md: {item}")
    return data


def load_json_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid {label}: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"invalid {label}: root must be an object")
        return None
    return data


def validate_codex_distribution(root: Path, version: str, errors: list[str]) -> None:
    plugin = load_json_object(root / ".codex-plugin/plugin.json", "Codex plugin manifest", errors)
    if plugin is not None:
        add(errors, plugin.get("name") == "praxis-workflow-os", "Codex plugin name must be praxis-workflow-os")
        add(errors, plugin.get("version") == version, "Codex plugin version must match VERSION")
        add(errors, plugin.get("license") == "MIT", "Codex plugin license must be MIT")
        add(errors, plugin.get("skills") == "./skills/", "Codex plugin must expose ./skills/")
        author = plugin.get("author") if isinstance(plugin.get("author"), dict) else {}
        add(errors, author.get("name") == "Farzan Ansari", "Codex plugin author must identify Farzan Ansari")
        interface = plugin.get("interface") if isinstance(plugin.get("interface"), dict) else {}
        for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            add(errors, isinstance(interface.get(field), str) and bool(interface[field].strip()), f"Codex plugin interface.{field} is required")

    marketplace = load_json_object(
        root / ".agents/plugins/marketplace.json", "Codex marketplace manifest", errors
    )
    if marketplace is not None:
        add(errors, marketplace.get("name") == "praxis-workflow-os", "Codex marketplace name must be praxis-workflow-os")
        entries = marketplace.get("plugins")
        add(errors, isinstance(entries, list) and len(entries) == 1, "Codex marketplace must contain one plugin")
        if isinstance(entries, list) and entries:
            entry = entries[0] if isinstance(entries[0], dict) else {}
            add(errors, entry.get("name") == "praxis-workflow-os", "Codex marketplace plugin name mismatch")
            source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
            add(errors, source.get("source") == "local", "Codex marketplace source must be local")
            add(errors, source.get("path") == "./", "Codex marketplace must point to the repository plugin root")
            policy = entry.get("policy") if isinstance(entry.get("policy"), dict) else {}
            add(errors, policy.get("installation") == "AVAILABLE", "Codex plugin must be available for installation")
            add(errors, policy.get("authentication") == "ON_INSTALL", "Codex plugin authentication policy mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-manifest", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        add(errors, (root / rel).is_file(), f"required release file missing: {rel}")

    attributes_path = root / ".gitattributes"
    attributes = attributes_path.read_text(encoding="utf-8") if attributes_path.is_file() else ""
    add(
        errors,
        re.search(r"(?m)^\*\s+text=auto\s+eol=lf\s*$", attributes) is not None,
        ".gitattributes must enforce LF text checkouts for cross-platform manifest stability",
    )

    version_path = root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    add(errors, bool(SEMVER_RE.fullmatch(version)), f"VERSION is not stable semantic version MAJOR.MINOR.PATCH: {version!r}")

    skills_root = root / "skills"
    skills = sorted(path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()) if skills_root.is_dir() else []
    add(errors, len(skills) == 7, f"expected 7 bundled skills, found {len(skills)}")
    for skill in skills:
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        version_match = SKILL_VERSION_RE.search(text)
        add(errors, version_match is not None, f"{skill.name}: metadata.version missing")
        if version_match:
            add(errors, version_match.group(1) == version, f"{skill.name}: metadata.version {version_match.group(1)!r} != {version!r}")
        author_match = SKILL_AUTHOR_RE.search(text)
        add(errors, author_match is not None and "Farzan Ansari" in author_match.group(1), f"{skill.name}: metadata.author must identify Farzan Ansari")

    validate_marketplace(root, version, errors)
    validate_codex_distribution(root, version, errors)

    for workflow_rel in (".github/workflows/ci.yml", ".github/workflows/release.yml"):
        workflow_path = root / workflow_rel
        if not workflow_path.is_file():
            continue
        workflow = workflow_path.read_text(encoding="utf-8")
        for action_ref in ACTION_USE_RE.findall(workflow):
            add(
                errors,
                FULL_SHA_RE.fullmatch(action_ref) is not None,
                f"{workflow_rel}: action ref must be a full commit SHA: {action_ref}",
            )

    release_workflow_path = root / ".github/workflows/release.yml"
    if release_workflow_path.is_file():
        release_workflow = release_workflow_path.read_text(encoding="utf-8")
        safety_markers = {
            "permissions: {}": "deny-all workflow permissions",
            "persist-credentials: false": "read-only build checkout",
            "git cat-file -t": "annotated-tag verification",
            "gh run list": "successful-CI verification",
            "needs.build.outputs.commit": "validated commit binding",
            "actions/upload-artifact@": "build/publish privilege split",
            "concurrency:": "per-tag release serialization",
            "--draft": "draft-first immutable release publication",
            "gh release download": "release asset reconciliation",
        }
        for marker, purpose in safety_markers.items():
            add(errors, marker in release_workflow, f"release workflow missing {purpose}")
        add(
            errors,
            'TAG="${{ inputs.tag }}"' not in release_workflow,
            "release workflow must not interpolate user input directly into shell source",
        )

    release_notes = root / f"docs/releases/v{version}.md"
    add(errors, release_notes.is_file(), f"release notes missing: docs/releases/v{version}.md")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8") if (root / "CHANGELOG.md").is_file() else ""
    add(errors, re.search(rf"(?m)^##\s+v?{re.escape(version)}\b", changelog) is not None, "CHANGELOG does not contain current version heading")

    # Transient caches may be created by local test execution. They are excluded by
    # build_manifest.py and build_release.py, so release readiness should verify that
    # they are absent from the distributable manifest rather than fail on an untracked
    # working-tree cache. This keeps validation deterministic in CI and after tests.
    manifest_path = root / "MANIFEST.sha256"
    if manifest_path.is_file():
        manifest_entries = []
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            if "  " in line:
                manifest_entries.append(line.split("  ", 1)[1])
        forbidden = [
            rel for rel in manifest_entries
            if any(part in FORBIDDEN_PARTS for part in Path(rel).parts)
            or Path(rel).suffix in FORBIDDEN_SUFFIXES
        ]
        add(errors, not forbidden, "generated/cache files included in manifest: " + ", ".join(forbidden[:10]))

    if not args.skip_manifest and (root / "scripts/build_manifest.py").is_file():
        # sys.executable and the checked-in script path are controlled by this process.
        result = subprocess.run(  # nosec B603
            # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args
            [sys.executable, str(root / "scripts/build_manifest.py"), "--root", str(root), "--check"],
            text=True,
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            errors.append("repository manifest is stale; run python scripts/build_manifest.py")

    report = {
        "valid": not errors,
        "version": version,
        "skill_count": len(skills),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
