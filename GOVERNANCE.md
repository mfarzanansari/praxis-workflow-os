# Governance

## Project model

Praxis Workflow OS is an open-source project maintained by Farzan Ansari. The maintainer is responsible for repository direction, release integrity, security response, and final merge decisions.

Contribution does not automatically grant governance authority, but sustained high-quality participation may lead to delegated review or maintenance responsibilities.

## Decision hierarchy

1. User safety, consent, privacy, and reversibility.
2. Demonstrated workflow outcomes and regression evidence.
3. Stable public contracts and compatibility.
4. Simplicity, maintainability, and clear ownership.
5. Novelty and feature breadth.

Popularity, model hype, or repository stars do not override evidence or safety.

## Change classes

### Routine changes

Documentation fixes, clearer examples, validator improvements, and compatible bug fixes may proceed through a normal pull request with relevant checks.

### Material changes

New skills, trigger changes, profile/schema fields, filesystem behavior, security boundaries, external dependencies, model-specific doctrine, or public workflow-contract changes require:

- a motivating issue or decision record;
- baseline or previous behavior;
- test and evaluation changes;
- compatibility and migration analysis;
- security and provenance review;
- semantic-version decision.

### Architecture decisions

Cross-cutting or difficult-to-reverse decisions are recorded under `docs/decisions/` before implementation. Accepted decisions can be superseded by a later decision record; they are not silently rewritten.

## Releases

Only the maintainer publishes official releases. A release requires the checklist in [RELEASING.md](RELEASING.md), passing CI, version alignment, release notes, archives, checksums, and a rollback point.

## Deprecation

A capability should be deprecated when it is unused, duplicated, harmful, version-incompatible, or more reliably handled by a host primitive. Deprecations receive a migration note for at least one compatible release unless immediate removal is required for security.
