# Changelog

All notable changes to Praxis Workflow OS are documented here. Release-specific user guidance lives under `docs/releases/`.

## 1.0.0 — 2026-07-22

### Added

- Stable lifecycle router, adaptive interview, blueprint, setup, distillation, retrospective, and skill-forge skills.
- Safe cross-platform installers and standard-library-only companion scripts.
- Profession-diverse example profiles, repository validation, unit tests, and model-eval portfolios.
- Open Agent Skills CLI installation guidance and a Claude Code marketplace manifest.
- GitHub Actions CI across Linux, Windows, and macOS.
- Deterministic ZIP and tar.gz release builder, SHA-256 checksums, and build-provenance attestations.
- Release-readiness validation, release workflow, version-specific release notes, governance, support, roadmap, code of conduct, issue forms, PR template, CODEOWNERS, and Dependabot configuration.
- Optional first-party integration boundary for the independently versioned Prompt Polish skill.

### Security

- Documented private vulnerability reporting, third-party skill intake, non-overwrite defaults, backup requirements, artifact verification, and release rollback.
- Reject unsafe or source-overlapping release output paths and clean only release-owned artifacts.
- Reject installer source/target/backup overlap, preserve existing backups, and stage replacements before changing live skills.
- Pin GitHub Actions to full commit SHAs and isolate read-only build validation from privileged publication.
- Bind releases to the exact current `main` commit, require successful CI for that commit, and require annotated tags.
- Enforce LF text checkouts so byte-level manifests remain stable on Windows, macOS, and Linux.
- Validate YAML-sensitive frontmatter scalars so standards-compliant skill discovery cannot silently omit a bundled skill.
- Reject symlinked or unexpected release inputs, make multi-file forced writes recoverable, validate setup-ready profiles, and bind setup to a content-hashed blueprint approval record.
- Add native Codex plugin metadata, per-skill UI metadata, objective eval assertions, and balanced near-miss trigger suites.
- Publish release assets through a serialized, exact-asset draft before GitHub locks the immutable release.
