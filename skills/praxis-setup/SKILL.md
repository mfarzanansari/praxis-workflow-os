---
name: praxis-setup
description: Use when an approved Praxis blueprint must be implemented by safely creating or augmenting an Obsidian vault, governance files, note templates, and personalized Agent Skills. Use only after profile and blueprint approval, and whenever setup must preserve existing files, preview changes, create backups, or support rollback.
license: MIT
compatibility: Python 3.9+ and filesystem access. No network access or third-party packages required.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: implementation
---

# Praxis Setup

## Core principle

Implement the approved architecture with **predictable, reversible, non-destructive changes**. Existing work is more valuable than a clean scaffold.

## Preconditions

Before running setup, verify:

- `praxis/profile.json` exists and validates;
- the written blueprint is approved;
- vault and skill target paths are confirmed;
- the person has reviewed automation boundaries;
- the first rollout scope is explicit;
- any replacement has a backup directory and rollback plan.

If approval is missing, stop and return to `praxis-blueprint`.

## Setup modes

| Mode | Use |
|---|---|
| `augment` | Add only missing governance, MOCs, templates, and skills to an existing vault. Default. |
| `new-vault` | Create a new vault structure at an empty or absent path. |
| `skills-only` | Generate personalized skills without changing a vault. |

## Required dry run

Always preview before applying:

```bash
python scripts/scaffold_system.py \
  --profile praxis/profile.json \
  --vault "C:/path/to/vault" \
  --skills-target "C:/Users/name/.claude/skills" \
  --mode augment \
  --dry-run
```

Review every `create`, `skip`, `conflict`, and `replace` action with the user.

Apply only after approval:

```bash
python scripts/scaffold_system.py \
  --profile praxis/profile.json \
  --vault "C:/path/to/vault" \
  --skills-target "C:/Users/name/.claude/skills" \
  --mode augment
```

## Replacement policy

The safe default is **never overwrite**.

Replacement requires both:

```text
--force --backup-dir <path>
```

The script copies every replaced file to the backup directory before writing. Never improvise around this gate by deleting or renaming files manually.

## What setup creates

### Vault layer

Praxis preserves the person's existing coarse taxonomy and creates only missing support files:

```text
_meta/
├── Praxis System.md
├── Praxis Profile.json
├── Skill Map.md
├── Automation Boundaries.md
└── Templates/
    ├── Research Note.md
    ├── Decision Record.md
    ├── Memory Note.md
    ├── Prompt Note.md
    ├── Project State.md
    └── Workflow Review.md

Research/Research MOC.md
Decision Records/Decision Records MOC.md
Memory/Memory MOC.md
Prompts/Prompts MOC.md
Reviews/Reviews MOC.md
```

Existing files are skipped unless approved replacement is enabled.

### Personalized skill layer

The script derives:

```text
personal-start-work/
personal-finish-work/
personal-weekly-review/
work-<stream-id>/
```

Each generated skill includes profile/version provenance and concrete workflow fields. Generated skills are drafts until their acceptance tests pass.

## Post-setup validation

Run:

```bash
python ../../scripts/validate_repository.py --skills-root <skills-target>
```

Then inspect:

- generated descriptions and trigger boundaries;
- work-stream deliverables and quality gates;
- vault links and path conventions;
- human approval gates;
- skipped/conflicting files;
- install report and backup location.

Restart the agent client when skill discovery occurs only at session start.

## First-run test

Use one real task from the highest-value work stream:

1. run `personal-start-work`;
2. run the matching `work-<stream-id>`;
3. complete the deliverable;
4. run `personal-finish-work`;
5. use `praxis-distill` only for future-useful residue;
6. record friction for the first retrospective.

Do not install every imagined work-stream skill before this proof run.

## Completion report

Report:

- created, skipped, replaced, and conflicted paths;
- backup location;
- generated skill inventory;
- validation results;
- first proof workflow;
- exact rollback steps.

## Hard gates

- No setup before blueprint approval.
- No overwrite without `--force` and `--backup-dir`.
- No secret or credential content in generated notes.
- No network or package installation by bundled scripts.
- No hidden edits to existing Obsidian configuration.
- No broad skill rollout before the first proof workflow succeeds.

## Common mistakes

| Mistake | Correction |
|---|---|
| Treating scaffold output as a finished system | Generated artifacts require review and real-task tests. |
| Reorganizing the entire vault | Augment first; migrate only with explicit value and rollback. |
| Generating skills for every role label | Generate from approved work streams. |
| Overwriting “almost identical” MOCs | Skip and report; merge manually after review. |
| Installing without dry-run | Dry-run is required. |
| Adding plugins or dependencies automatically | Keep setup local, minimal, and auditable. |

See [references/generated-skill-contract.md](references/generated-skill-contract.md).
