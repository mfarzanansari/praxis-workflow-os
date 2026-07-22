from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


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


class PraxisScriptTests(unittest.TestCase):
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
        profile = ROOT / "examples/profiles/marketer.json"
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            skills = Path(tmp) / "skills"
            report = Path(tmp) / "report.json"
            dry = run(
                script, "--profile", str(profile), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--dry-run",
            )
            plan = json.loads(dry.stdout)
            self.assertTrue(any(item["action"] == "create" for item in plan["actions"]))
            applied = run(
                script, "--profile", str(profile), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--report", str(report),
            )
            summary = json.loads(applied.stdout)
            self.assertGreater(summary["created"], 0)
            self.assertTrue((skills / "personal-start-work/SKILL.md").exists())
            self.assertTrue((skills / "work-market-research/SKILL.md").exists())
            second = run(
                script, "--profile", str(profile), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--report", str(report),
            )
            self.assertGreater(json.loads(second.stdout)["skipped"], 0)
            unsafe = run(
                script, "--profile", str(profile), "--vault", str(vault),
                "--skills-target", str(skills), "--mode", "augment", "--force",
                check=False,
            )
            self.assertNotEqual(unsafe.returncode, 0)
            self.assertIn("--force requires --backup-dir", unsafe.stderr)

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


if __name__ == "__main__":
    unittest.main()
