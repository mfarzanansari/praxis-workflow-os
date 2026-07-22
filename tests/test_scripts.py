from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
BLUEPRINT_FILES = (
    "workflow-constitution.md", "work-streams.md", "skill-map.md",
    "knowledge-architecture.md", "automation-boundaries.md", "rollout-plan.md",
    "acceptance-tests.md",
)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [PYTHON, *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(map(str, args))}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_blueprint_approval(root: Path, profile: Path) -> Path:
    blueprint = root / "blueprint"
    blueprint.mkdir()
    hashes = {}
    for name in BLUEPRINT_FILES:
        path = blueprint / name
        path.write_text(f"# Approved {name}\n\nReviewed content.\n", encoding="utf-8")
        hashes[name] = sha256(path)
    profile_data = json.loads(profile.read_text(encoding="utf-8"))
    record = {
        "schema_version": "1.0",
        "status": "approved",
        "profile_id": profile_data["profile_id"],
        "profile_sha256": sha256(profile),
        "blueprint_files": hashes,
        "approved_at": "2026-07-22T00:00:00+00:00",
        "approver": "Test Owner",
    }
    approval = blueprint / "blueprint-approval.json"
    approval.write_text(json.dumps(record) + "\n", encoding="utf-8")
    return approval


class PraxisScriptTests(unittest.TestCase):
    def test_git_attributes_preserve_cross_platform_manifest_bytes(self) -> None:
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes.splitlines())

    def test_skill_validator_rejects_unquoted_yaml_colon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "invalid-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: invalid-skill\n"
                "description: Use when routing work: this colon must be quoted.\n"
                "---\n\n"
                "# Invalid Skill\n",
                encoding="utf-8",
            )
            result = run(
                "skills/praxis-skill-forge/scripts/validate_skill.py",
                str(skill),
                check=False,
            )
            report = json.loads(result.stdout)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(any("unquoted colon" in error for error in report["errors"]))

    def test_repository_validates(self) -> None:
        result = run("scripts/validate_repository.py")
        report = json.loads(result.stdout)
        self.assertTrue(report["valid"])
        self.assertEqual(report["skill_count"], 7)

    def test_example_profiles_validate(self) -> None:
        module_path = ROOT / "skills/praxis-interview/scripts/validate_profile.py"
        spec = importlib.util.spec_from_file_location("praxis_profile_validator", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        profiles = sorted((ROOT / "examples/profiles").glob("*.json"))
        self.assertGreaterEqual(len(profiles), 6)
        for profile in profiles:
            errors, warnings = module.validate(module.load(profile))
            self.assertFalse(errors, msg=f"{profile}: {errors}; warnings={warnings}")

    def test_interview_state_lifecycle(self) -> None:
        script = "skills/praxis-interview/scripts/interview_state.py"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "praxis"
            run(script, "start", "--workspace", str(workspace), "--depth", "quick")
            run(
                script, "record", "--workspace", str(workspace),
                "--path", "outcomes.primary", "--value", '"Reduce repeated context work"',
                "--state", "confirmed", "--source", "user",
            )
            stream = {
                "id": "weekly-report",
                "name": "Weekly report",
                "trigger": "Friday review starts",
                "deliverables": ["approved report"],
                "quality_gates": ["sources linked"],
            }
            run(
                script, "append", "--workspace", str(workspace),
                "--path", "work_streams", "--value", json.dumps(stream),
                "--state", "confirmed", "--source", "user",
            )
            run(
                script, "append", "--workspace", str(workspace),
                "--path", "automation_boundaries.review_before_action",
                "--value", '"send report"', "--state", "confirmed", "--source", "user",
            )
            run(
                script, "record", "--workspace", str(workspace),
                "--path", "governance.review_cadence", "--value", '"weekly"',
                "--state", "confirmed", "--source", "user",
            )
            completed = run(script, "complete", "--workspace", str(workspace))
            self.assertEqual(json.loads(completed.stdout)["status"], "complete")
            run(script, "export", "--workspace", str(workspace))
            self.assertTrue((workspace / "interview-summary.md").exists())
            self.assertTrue((workspace / "open-questions.md").exists())

    def test_create_note_is_non_overwriting(self) -> None:
        script = "skills/praxis-distill/scripts/create_note.py"
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            dry = run(
                script, "--vault", str(vault), "--type", "memory",
                "--title", "A reusable lesson", "--dry-run",
            )
            self.assertEqual(json.loads(dry.stdout)["action"], "create")
            created = run(
                script, "--vault", str(vault), "--type", "memory",
                "--title", "A reusable lesson",
            )
            target = Path(json.loads(created.stdout)["path"])
            self.assertTrue(target.exists())
            conflict = run(
                script, "--vault", str(vault), "--type", "memory",
                "--title", "A reusable lesson", check=False,
            )
            self.assertEqual(conflict.returncode, 3)
            self.assertEqual(json.loads(conflict.stdout)["action"], "conflict")

    def test_setup_dry_run_and_safe_apply(self) -> None:
        script = "skills/praxis-setup/scripts/scaffold_system.py"
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "profile.json"
            profile_data = json.loads((ROOT / "examples/profiles/marketer.json").read_text(encoding="utf-8"))
            profile_data["status"] = "complete"
            profile.write_text(json.dumps(profile_data), encoding="utf-8")
            approval = create_blueprint_approval(Path(tmp), profile)
            vault = Path(tmp) / "vault"
            skills = Path(tmp) / "skills"
            report = Path(tmp) / "report.json"
            dry = run(
                script, "--profile", str(profile), "--approval-record", str(approval), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--dry-run",
            )
            plan = json.loads(dry.stdout)
            self.assertTrue(any(item["action"] == "create" for item in plan["actions"]))
            applied = run(
                script, "--profile", str(profile), "--approval-record", str(approval), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--report", str(report),
            )
            summary = json.loads(applied.stdout)
            self.assertGreater(summary["created"], 0)
            self.assertTrue((skills / "personal-start-work/SKILL.md").exists())
            self.assertTrue((skills / "work-market-research/SKILL.md").exists())
            second = run(
                script, "--profile", str(profile), "--approval-record", str(approval), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--report", str(report),
            )
            self.assertGreater(json.loads(second.stdout)["skipped"], 0)
            unsafe = run(
                script, "--profile", str(profile), "--approval-record", str(approval), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--force",
                check=False,
            )
            self.assertNotEqual(unsafe.returncode, 0)
            self.assertIn("--force requires --backup-dir", unsafe.stderr)

    def test_setup_rejects_incomplete_profile_without_writes(self) -> None:
        script = "skills/praxis-setup/scripts/scaffold_system.py"
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "profile.json"
            profile.write_text('{"profile_id":"unsafe"}\n', encoding="utf-8")
            vault = Path(tmp) / "vault"
            skills = Path(tmp) / "skills"
            result = run(
                script, "--profile", str(profile), "--vault", str(vault),
                "--skills-target", str(skills), "--dry-run", check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("profile is not setup-ready", result.stderr)
            self.assertFalse(vault.exists())
            self.assertFalse(skills.exists())

    def test_setup_rejects_symlink_destination(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unsupported")
        script = "skills/praxis-setup/scripts/scaffold_system.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile_data = json.loads((ROOT / "examples/profiles/marketer.json").read_text(encoding="utf-8"))
            profile_data["status"] = "complete"
            profile.write_text(json.dumps(profile_data), encoding="utf-8")
            approval = create_blueprint_approval(root, profile)
            sentinel = root / "outside.md"
            sentinel.write_text("outside\n", encoding="utf-8")
            target = root / "skills/personal-start-work"
            target.mkdir(parents=True)
            try:
                (target / "SKILL.md").symlink_to(sentinel)
            except OSError as exc:
                self.skipTest(f"cannot create symlink: {exc}")
            result = run(
                script, "--profile", str(profile), "--approval-record", str(approval),
                "--skills-target", str(root / "skills"),
                "--mode", "skills-only", "--force", "--backup-dir", str(root / "backup"),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "outside\n")

    def test_blueprint_approval_binds_profile_and_documents(self) -> None:
        scaffold = "skills/praxis-blueprint/scripts/blueprint_scaffold.py"
        approve = "skills/praxis-blueprint/scripts/approve_blueprint.py"
        setup = "skills/praxis-setup/scripts/scaffold_system.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile_data = json.loads((ROOT / "examples/profiles/marketer.json").read_text(encoding="utf-8"))
            profile_data["status"] = "complete"
            profile.write_text(json.dumps(profile_data), encoding="utf-8")
            blueprint = root / "blueprint"
            run(scaffold, "--profile", str(profile), "--output", str(blueprint))
            draft = run(
                approve, "--profile", str(profile), "--blueprint-dir", str(blueprint),
                "--approver", "Test Owner", "--confirm-approved", check=False,
            )
            self.assertNotEqual(draft.returncode, 0)
            for name in BLUEPRINT_FILES:
                path = blueprint / name
                text = path.read_text(encoding="utf-8")
                text = text.replace("TODO", "Reviewed")
                text = text.replace("Draft — requires explicit approval", "Approved")
                path.write_text(text, encoding="utf-8")
            completed = run(
                approve, "--profile", str(profile), "--blueprint-dir", str(blueprint),
                "--approver", "Test Owner", "--confirm-approved",
            )
            approval = Path(json.loads(completed.stdout)["record"])
            self.assertTrue(approval.is_file())
            (blueprint / "rollout-plan.md").write_text("# Changed after approval\n", encoding="utf-8")
            rejected = run(
                setup, "--profile", str(profile), "--approval-record", str(approval),
                "--skills-target", str(root / "skills"), "--mode", "skills-only",
                check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("changed", rejected.stderr)
            self.assertFalse((root / "skills").exists())

    def test_aggregate_metrics(self) -> None:
        script = "skills/praxis-retrospective/scripts/aggregate_metrics.py"
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "events.jsonl"
            events = [
                {"skill": "work-research", "outcome": "success", "duration_seconds": 10, "corrections": 1, "friction_tags": ["source-freshness"]},
                {"skill": "work-research", "outcome": "success", "duration_seconds": 20, "corrections": 0, "friction_tags": []},
                {"skill": "personal-finish-work", "outcome": "partial", "duration_seconds": 5, "quality_failures": 1},
            ]
            log.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
            result = run(script, str(log))
            report = json.loads(result.stdout)
            self.assertEqual(report["valid_lines"], 3)
            self.assertEqual(report["skills"]["work-research"], 2)
            self.assertEqual(report["duration_seconds"]["median"], 10.0)

    def test_aggregate_metrics_enforces_resource_limits(self) -> None:
        script = "skills/praxis-retrospective/scripts/aggregate_metrics.py"
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "events.jsonl"
            log.write_text("\n".join(json.dumps({"skill": f"skill-{i}"}) for i in range(4)) + "\n", encoding="utf-8")
            result = run(script, str(log), "--max-lines", "2", check=False)
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertEqual(report["error"], "resource limit exceeded")

    def test_release_readiness(self) -> None:
        result = run("scripts/validate_release.py")
        report = json.loads(result.stdout)
        self.assertTrue(report["valid"], msg=report)
        self.assertEqual(report["version"], "1.0.0")
        self.assertEqual(report["skill_count"], 7)

    def test_release_archives_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp) / "dist"
            run("scripts/build_release.py", "--dist", str(dist), "--clean")
            first = {path.name: path.read_bytes() for path in dist.iterdir()}
            self.assertIn("praxis-workflow-os-v1.0.0.zip", first)
            self.assertIn("praxis-workflow-os-v1.0.0.tar.gz", first)
            self.assertIn("SHA256SUMS", first)
            run("scripts/build_release.py", "--dist", str(dist), "--clean")
            second = {path.name: path.read_bytes() for path in dist.iterdir()}
            self.assertEqual(first, second)

    def test_release_builder_rejects_source_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            (source / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            sentinel = source / "keep.txt"
            sentinel.write_text("must survive\n", encoding="utf-8")
            for output in (source, source / "custom-output"):
                result = run(
                    "scripts/build_release.py", "--root", str(source),
                    "--dist", str(output), "--clean", check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(sentinel.exists())

    def test_release_clean_preserves_unowned_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            (source / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            (source / "payload.txt").write_text("payload\n", encoding="utf-8")
            output = Path(tmp) / "artifacts"
            output.mkdir()
            sentinel = output / "unrelated.txt"
            sentinel.write_text("preserve\n", encoding="utf-8")
            run(
                "scripts/build_release.py", "--root", str(source),
                "--dist", str(output), "--clean",
            )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve\n")

    def test_release_tools_reject_symlink_sources(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unsupported")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            (source / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            sentinel = root / "outside.txt"
            sentinel.write_text("private bytes\n", encoding="utf-8")
            try:
                (source / "external-link.txt").symlink_to(sentinel)
            except OSError as exc:
                self.skipTest(f"cannot create symlink: {exc}")

            dist = root / "dist"
            release = run(
                "scripts/build_release.py", "--root", str(source), "--dist", str(dist),
                check=False,
            )
            self.assertNotEqual(release.returncode, 0)
            self.assertFalse(dist.exists())

            manifest = source / "MANIFEST.sha256"
            result = run(
                "scripts/build_manifest.py", "--root", str(source), "--output", str(manifest),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(manifest.exists())

    def test_release_builder_rejects_untracked_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            (source / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            (source / "tracked.txt").write_text("tracked\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "VERSION", "tracked.txt"], check=True)
            (source / "unexpected.txt").write_text("untracked\n", encoding="utf-8")
            dist = root / "dist"
            result = run(
                "scripts/build_release.py", "--root", str(source), "--dist", str(dist),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("untracked release file", result.stderr)
            self.assertFalse(dist.exists())

    def test_manifest_valid(self) -> None:
        result = run("scripts/build_manifest.py", "--check")
        self.assertIn("Manifest valid", result.stdout)

    def test_installer_skips_existing_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            run("scripts/install.py", "--target", str(target))
            self.assertTrue((target / "praxis/SKILL.md").exists())
            second = run("scripts/install.py", "--target", str(target))
            self.assertEqual(json.loads(second.stdout)["skipped"], 7)

    def test_installer_rejects_backup_overlap_without_data_loss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            installed = target / "praxis"
            installed.mkdir(parents=True)
            sentinel = installed / "sentinel.txt"
            sentinel.write_text("original\n", encoding="utf-8")
            result = run(
                "scripts/install.py", "--target", str(target), "--include", "praxis",
                "--force", "--backup-dir", str(target), check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "original\n")

    def test_installer_refuses_existing_backup_and_stages_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            installed = target / "praxis"
            installed.mkdir(parents=True)
            sentinel = installed / "sentinel.txt"
            sentinel.write_text("original\n", encoding="utf-8")
            backup = Path(tmp) / "backup"
            (backup / "praxis").mkdir(parents=True)
            result = run(
                "scripts/install.py", "--target", str(target), "--include", "praxis",
                "--force", "--backup-dir", str(backup), check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "original\n")

            shutil.rmtree(backup)
            completed = run(
                "scripts/install.py", "--target", str(target), "--include", "praxis",
                "--force", "--backup-dir", str(backup),
            )
            self.assertEqual(json.loads(completed.stdout)["installed"], 1)
            self.assertEqual((backup / "praxis/sentinel.txt").read_text(encoding="utf-8"), "original\n")
            self.assertTrue((target / "praxis/SKILL.md").is_file())

    def test_installer_rejects_source_symlinks(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unsupported")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source/example-skill"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("---\nname: example-skill\ndescription: Use when testing safe installation.\n---\n\n# Example\n", encoding="utf-8")
            sentinel = root / "outside.txt"
            sentinel.write_text("outside\n", encoding="utf-8")
            try:
                (source / "linked.txt").symlink_to(sentinel)
            except OSError as exc:
                self.skipTest(f"cannot create symlink: {exc}")
            target = root / "target"
            result = run(
                "scripts/install.py", "--source", str(source.parent), "--target", str(target),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())

    def test_blueprint_force_requires_backup_and_rejects_symlink(self) -> None:
        script = "skills/praxis-blueprint/scripts/blueprint_scaffold.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "profile.json"
            profile.write_text("{}\n", encoding="utf-8")
            output = root / "blueprint"
            output.mkdir()
            existing = output / "workflow-constitution.md"
            existing.write_text("original\n", encoding="utf-8")
            unsafe = run(
                script, "--profile", str(profile), "--output", str(output), "--force",
                check=False,
            )
            self.assertNotEqual(unsafe.returncode, 0)
            self.assertEqual(existing.read_text(encoding="utf-8"), "original\n")

            backup = root / "backup"
            applied = run(
                script, "--profile", str(profile), "--output", str(output), "--force",
                "--backup-dir", str(backup),
            )
            self.assertEqual(applied.returncode, 0)
            self.assertEqual((backup / "workflow-constitution.md").read_text(encoding="utf-8"), "original\n")

            if not hasattr(os, "symlink"):
                return
            outside = root / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            linked = output / "acceptance-tests.md"
            linked.unlink()
            try:
                linked.symlink_to(outside)
            except OSError:
                return
            rejected = run(
                script, "--profile", str(profile), "--output", str(output), "--force",
                "--backup-dir", str(root / "backup-2"), check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_interview_force_requires_backup(self) -> None:
        script = "skills/praxis-interview/scripts/interview_state.py"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "praxis"
            run(script, "start", "--workspace", str(workspace))
            original = (workspace / "profile.json").read_bytes()
            rejected = run(script, "start", "--workspace", str(workspace), "--force", check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual((workspace / "profile.json").read_bytes(), original)
            backup = Path(tmp) / "backup"
            run(
                script, "start", "--workspace", str(workspace), "--force",
                "--backup-dir", str(backup),
            )
            self.assertEqual((backup / "profile.json").read_bytes(), original)

    def test_codex_distribution_metadata_is_present(self) -> None:
        plugin = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertEqual(marketplace["plugins"][0]["source"]["path"], "./")
        for skill in sorted((ROOT / "skills").iterdir()):
            if (skill / "SKILL.md").is_file():
                metadata = skill / "agents/openai.yaml"
                self.assertTrue(metadata.is_file(), msg=f"missing {metadata}")


if __name__ == "__main__":
    unittest.main()
