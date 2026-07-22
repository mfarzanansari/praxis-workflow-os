# Praxis Workflow OS v1.0.0 execution plan

- **Owner:** Farzan Ansari
- **Executor:** Codex GPT-5.6 Sol
- **Started:** 2026-07-22
- **Target:** <https://github.com/mfarzanansari/praxis-workflow-os/releases/tag/v1.0.0>
- **Execution state at release commit:** release candidate validated; publication pending

## Current-state evidence

The prepared source is a non-Git staging tree supplied with the release handoff. The public repository is `mfarzanansari/praxis-workflow-os`, is public, and has only the `main` branch. Independent Git and GitHub API checks found:

- `main` at `af11daeaff1c2a5ea7fddeda57b837f1809dbdec`;
- exactly the eight authorized bootstrap commits from `296afcf...` through `af11dae...`;
- no tags, GitHub releases, pull requests, Actions workflows, or Actions runs;
- a tip tree containing only `README.md` and `.bootstrap/part-00` through `.bootstrap/part-06`;
- no unexpected branches or user-authored product source.

This matches the guarded bootstrap-only state. Replacing it with a clean root commit is authorized only while the remote tip remains `af11dae...`; the push must use `--force-with-lease`.

The untouched staged source initially passed with Python 3.14.6:

```text
python3 scripts/validate_release.py             valid; version 1.0.0; 7 skills
python3 -m unittest discover -s tests -v       10 tests passed
python3 scripts/build_manifest.py --check      manifest valid
python3 scripts/build_release.py --clean        three release files built
```

The host has `python3` but no `python` alias. Release audits also found unsafe archive-cleanup and installer-backup edge cases, mutable/outdated action references, insufficient tag-to-artifact binding, and eight executable-bit warnings. All were repaired before publication. The hardened source passes strict validation with zero warnings and 14 unit tests, including destructive-path regressions. Actionlint v1.7.12 also passes both workflows.

Two independent final builds were byte-identical. The ZIP and tar.gz contained the same 82 files, their checksums verified, and both extracted trees independently passed strict skill validation, release validation, all 14 tests, and manifest verification.

## Phases and completion criteria

1. **Harden and validate source**
   - Resolve every critical/high release-audit finding.
   - Keep exactly seven skills and the standard-library-only/offline contract.
   - Pass strict repository validation, release validation, unit tests, and manifest check.
2. **Validate release artifacts**
   - Build deterministic ZIP and tar.gz assets plus `SHA256SUMS`.
   - Inspect and extract both archives; rerun validators and tests from each.
   - Confirm no Git metadata, bootstrap payload, cache, `dist`, handoff, credential, or machine path.
3. **Replace guarded bootstrap history**
   - Recheck remote tip, refs, releases, PRs, and tree immediately before push.
   - Save a local recovery bundle of the bootstrap history.
   - Create one root commit, `feat: release Praxis Workflow OS v1.0.0`.
   - Push `main` with an explicit lease for `af11dae...` and verify remote parity.
4. **Configure and verify GitHub**
   - Set the reviewed description and focused topics.
   - Confirm CI passes on Linux, Windows, and macOS for the exact release commit.
   - Enable appropriate security/repository presentation features where supported.
5. **Publish and verify v1.0.0**
   - Dispatch the pinned release workflow from the verified `main` commit.
   - Verify the annotated tag, release notes, assets, checksums, and attestations from GitHub.
   - Run clean discovery and temporary installation smoke tests.
6. **Publish the optional Prompt Polish companion boundary**
   - Inspect current `main`, open work, version history, and release convention.
   - Make only a standalone-compatible documentation/contract patch.
   - Publish only if it does not overwrite or conflict with active user work.
7. **Cross-repository closeout**
   - Verify reciprocal links, optionality, versions, public install commands, and remote/CI state.

## Command and check list

```text
python3 scripts/validate_repository.py --strict
python3 scripts/validate_release.py
python3 -m unittest discover -s tests -v
python3 scripts/build_manifest.py --check
python3 scripts/build_release.py --clean
git ls-remote --heads --tags <repository>
gh repo view / gh api / gh pr list / gh release list / gh run list
npx skills add mfarzanansari/praxis-workflow-os --list
gh attestation verify <asset> -R mfarzanansari/praxis-workflow-os
```

## Decisions made during execution

- Preserve Praxis and Prompt Polish as independently installable, independently versioned repositories.
- Replace only the exact disposable Praxis bootstrap history; retain a local recovery bundle and use an explicit force-with-lease.
- Pin third-party actions to reviewed full commit SHAs and keep Dependabot updates enabled.
- Bind release assets to the exact current `main` commit, require prior successful CI, and reject mismatched or lightweight release tags.
- Use `python3` for POSIX documentation and `python` for PowerShell/Windows examples.
- Do not weaken validators, safety gates, CI coverage, checksums, or provenance to obtain a green release.

## Failures and remediation

| Failure | Remediation | State |
|---|---|---|
| POSIX `python` command unavailable | Use and document `python3` on POSIX | resolved |
| Archive `--clean` could remove an unsafe directory | Restrict output overlap and clean only known artifacts | resolved; regression-tested |
| Installer backup/target overlap could destroy data | Add overlap and pre-existing-backup preflight plus staged replacement | resolved; regression-tested |
| Release tag and artifacts could diverge | Split build/publish privileges and verify exact commit, main, tag, and prior CI | resolved; actionlint passed |
| Action major tags were mutable and stale | Pin current reviewed action commits | resolved |
| Skill scripts emitted executable warnings | Preserve executable modes and enforce strict validation | resolved; zero warnings |

## Final release evidence

Final public verification is performed during closeout at these stable evidence locations:

- repository: <https://github.com/mfarzanansari/praxis-workflow-os>
- CI: <https://github.com/mfarzanansari/praxis-workflow-os/actions/workflows/ci.yml>
- release workflow: <https://github.com/mfarzanansari/praxis-workflow-os/actions/workflows/release.yml>
- release: <https://github.com/mfarzanansari/praxis-workflow-os/releases/tag/v1.0.0>

Completion requires public SHA parity, green matrix jobs, matching downloaded checksums, verified attestations, and seven-skill discovery/install smoke tests.
