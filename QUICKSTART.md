# Praxis Quickstart

## Phase 0 — Install and validate

Recommended multi-agent installation:

```bash
npx skills add mfarzanansari/praxis-workflow-os --list
npx skills add mfarzanansari/praxis-workflow-os --skill '*' -g
```

Or clone and validate locally:

```bash
python3 scripts/validate_release.py
python3 -m unittest discover -s tests -v
python3 scripts/install.py --target ~/.claude/skills --dry-run
python3 scripts/install.py --target ~/.claude/skills
```

Restart the agent client if it discovers skills only at session start.

## Phase 1 — Interview

Prompt:

> Use `praxis-interview`. Build a workflow profile for me from the files and context already available. Ask one question per turn, show your recommended answer and why, and persist each confirmed decision.

Choose a depth:

- **Quick:** approximately 10–14 consequential decisions. Suitable for a first useful system in one sitting.
- **Standard:** approximately 20–30 decisions. Recommended default.
- **Deep:** 35+ decisions with separate branches for each work stream, stakeholder, risk boundary, and review loop.

The interview should produce:

```text
praxis/profile.json
praxis/interview-summary.md
praxis/open-questions.md
```

## Phase 2 — Blueprint

Prompt:

> Use `praxis-blueprint` with `praxis/profile.json`. Produce my workflow constitution, work-stream architecture, skill graph, Obsidian knowledge map, automation boundaries, rollout plan, and acceptance tests. Present the design in sections and wait for approval before setup.

Expected artifacts:

```text
praxis/workflow-constitution.md
praxis/work-streams.md
praxis/skill-map.md
praxis/knowledge-architecture.md
praxis/automation-boundaries.md
praxis/rollout-plan.md
praxis/acceptance-tests.md
```

## Phase 3 — Setup

Preview all filesystem changes:

```bash
python3 skills/praxis-setup/scripts/scaffold_system.py \
  --profile praxis/profile.json \
  --vault /path/to/vault \
  --skills-target ~/.claude/skills \
  --mode augment \
  --dry-run
```

Apply after reviewing the plan:

```bash
python3 skills/praxis-setup/scripts/scaffold_system.py \
  --profile praxis/profile.json \
  --vault /path/to/vault \
  --skills-target ~/.claude/skills \
  --mode augment
```

`augment` creates missing files only. It does not move, rename, or overwrite existing notes.

## Phase 4 — Operate

Start a recurring work stream:

> Use `personal-start-work` for the [work stream]. Load only the relevant context, identify the deliverable and quality gate, and create a compact execution brief.

Finish work:

> Use `personal-finish-work`. Verify the deliverable, record unresolved risks, and invoke `praxis-distill` only for residue that will matter later.

## Phase 5 — Improve

Weekly or after a major project:

> Use `praxis-retrospective`. Review the event log, recent outputs, corrections, repeated friction, and unused skills. Recommend the smallest evidence-backed system changes and preserve a rollback path.

Create or revise a skill only after a recurring failure is visible:

> Use `praxis-skill-forge` to turn this repeated failure into a tested skill. Run a no-skill baseline first, then create the minimum skill that changes the behavior.

## First-week rollout

- **Day 1:** interview and approve the constitution.
- **Day 2:** install only start-work, finish-work, and one high-value work-stream skill.
- **Days 3–6:** use them on real work; record corrections and friction.
- **Day 7:** run the retrospective. Remove what was ignored, tighten what was ambiguous, and add nothing without evidence.


## Optional — materialize a named-model prompt

After Praxis has approved the task or workflow contract, the separate `prompt-polish` skill may optionally adapt that contract for a named model:

```bash
npx skills add mfarzanansari/prompt-polish -g
```

Do not use prompt polishing to replace the interview, invent requirements, or bypass blueprint approval.
