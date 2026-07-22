# Contributing

Thank you for improving Praxis. Contributions are evaluated by whether they improve an observed workflow behavior, output, trigger, safety property, accessibility property, or maintenance property. Novelty alone is not sufficient.

## Before opening a pull request

Use the issue forms for substantial features or skills. Search existing work first, and read:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [MAINTENANCE.md](MAINTENANCE.md)
- [SECURITY.md](SECURITY.md)
- [AGENTS.md](AGENTS.md) when using an AI coding agent

Small documentation and bug fixes may go directly to a focused pull request.

## Required change record

For a material skill or workflow change, include:

- motivating evidence or issue;
- baseline or previous behavior;
- failure classification;
- proposed mechanism and alternatives;
- evals added or changed;
- deterministic tests;
- human-review result where applicable;
- compatibility, accessibility, security, and migration impact;
- provenance and license of adapted material;
- semantic-version decision and release-note impact.

A new skill needs a demonstrated recurring need or failing baseline. A repeated deterministic operation may need a script instead. Project-specific facts belong in project state, not the general catalog.

## Development checks

```bash
python3 scripts/validate_release.py
python3 -m unittest discover -s tests -v
python3 scripts/build_manifest.py --check
python3 scripts/build_release.py --clean
```

Delete `dist/` after inspecting local archives so the repository remains release-clean.

## Skill quality rules

- Keep `SKILL.md` focused and use progressive disclosure.
- Write narrow trigger descriptions with realistic near-miss tests.
- Prefer positive output contracts over long prohibition lists for shaping behavior.
- Use hard gates only when baseline pressure tests justify them or safety requires them.
- Add scripts only for deterministic recurring work and test them.
- Keep time-sensitive references versioned and sourced.
- Avoid duplicating host primitives or existing skills.
- Treat Prompt Polish as an optional sibling; do not copy its model doctrine into Praxis.

## Dependencies and network behavior

The bundled runtime is standard-library-only and offline. New external dependencies, network calls, telemetry, shell execution, or permission expansion require a material-change proposal, pinned versions, provenance, threat review, tests, user-visible documentation, and a rollback plan.

## Pull requests

Keep pull requests small enough to review. Complete the pull-request template, include screenshots or artifacts only when they clarify behavior, and remove secrets and private data. Maintainers may request a decision record for cross-cutting changes.
