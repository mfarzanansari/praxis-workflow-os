# Maintaining Praxis and Generated Skills

## Release policy

Use semantic versioning:

- **MAJOR** — changed workflow contract, removed capability, or incompatible profile/schema change.
- **MINOR** — new skill, reference, script, profile field, or substantial compatible behavior.
- **PATCH** — wording, examples, validation, bug fixes, or non-semantic refinements.

Every release should contain:

1. evidence or issue motivating the change;
2. affected skills and profile fields;
3. before/after behavior;
4. tests run and observed variance;
5. migration and rollback notes;
6. changelog entry;
7. version-specific release notes;
8. validated archives, checksums, and a known rollback point.

## Weekly system review

Review no more than the evidence justifies:

- Which skills were invoked?
- Which should have triggered but did not?
- Which triggered unnecessarily?
- Where did the person correct the agent?
- Which outputs required avoidable rework?
- Which repeated operations should become scripts?
- Which references are stale or version-mismatched?
- Which notes were never retrieved?
- Which human gates were too weak or too burdensome?

Prefer deletion, narrowing, or better defaults before adding another skill.

## Skill evolution gate

A new skill or substantial revision requires:

- a recurring task or demonstrated failure;
- a no-skill or previous-version baseline;
- realistic test prompts;
- explicit success criteria;
- human review of outputs;
- trigger tests including near-miss negatives;
- provenance and version metadata;
- security inspection of scripts and dependencies.

## Test portfolio

Use several kinds of tests because no single test proves skill quality:

| Test | Purpose |
|---|---|
| Trigger positive | skill loads when genuinely needed |
| Trigger near-miss negative | skill does not hijack adjacent tasks |
| Application | technique works on a novel example |
| Variation | edge cases and different professions work |
| Missing-information | skill asks or defers rather than inventing |
| Pressure | hard gates survive urgency, sunk cost, authority, and fatigue |
| Output contract | required fields and ordering are present |
| Script unit test | deterministic mechanics are correct |
| Regression | prior successful scenarios remain successful |
| Human comparative review | quality is genuinely better, not merely different |

Run multiple repetitions for model-dependent tests. Variance is itself a failure signal.

## Reference freshness

Each time-sensitive reference should state:

- source;
- version or retrieval date;
- scope;
- known compatibility limits;
- next review date.

Do not encode fast-changing product behavior as timeless doctrine. Prefer official documentation or a version-pinned reference.

## Third-party skill intake

Treat every imported skill as untrusted software.

1. Record origin, author, license, version/commit, and checksum.
2. Read all instructions, scripts, references, and assets.
3. Search for network calls, shell execution, credential access, destructive operations, obfuscated content, package installation, and indirect dependencies.
4. Compare the description with the actual behavior.
5. Run in an isolated environment with least privilege.
6. Re-author the useful doctrine locally when provenance or maintenance is weak.
7. Pin known-good versions and review updates as code changes.

Popularity is evidence of attention, not a security or quality guarantee.

## Deprecation

Mark a skill deprecated when it is unused, duplicated, superseded, version-incompatible, or consistently harms outcomes. Keep a migration note for one release, then remove it from active discovery. Archived skills must not remain in the default skill catalog.

## Automated release path

The GitHub `Release` workflow accepts a semantic `vMAJOR.MINOR.PATCH` tag or a manual workflow input. It verifies version alignment, runs validation and deterministic tests, builds reproducible ZIP and tar.gz archives, generates SHA-256 checksums, attests the archives, and publishes the GitHub release.

Do not modify an existing release artifact in place. Publish a new patch or higher version and preserve the affected release for investigation unless security requires removal.

## First-party companion compatibility

Prompt Polish is independently versioned. Review the optional handoff when either project changes the task-contract shape, supported invocation, output contract, or model-routing behavior. A Praxis release must not silently acquire a hard dependency on Prompt Polish.
