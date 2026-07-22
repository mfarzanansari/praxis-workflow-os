# Agent contribution instructions

When changing this repository:

1. Read `ARCHITECTURE.md`, `CONTRIBUTING.md`, and the relevant skill before editing.
2. Preserve the separation between workflow intent, orchestration, execution, curated knowledge, and runtime memory.
3. Do not add a skill without a recurring need or failing baseline.
4. Keep `SKILL.md` focused; move heavy reference material to `references/` and deterministic repetition to tested scripts.
5. Bundled scripts must remain auditable, non-destructive by default, and standard-library-only unless a reviewed decision explicitly changes that policy.
6. Never add hidden network calls, telemetry, package installation, credentials, absolute personal paths, or destructive defaults.
7. Update evals, tests, version metadata, changelog, and migration notes when behavior changes.
8. Run all release-readiness checks before claiming completion.
9. Treat Prompt Polish as an optional first-party sibling. Do not copy its model doctrine into Praxis.
