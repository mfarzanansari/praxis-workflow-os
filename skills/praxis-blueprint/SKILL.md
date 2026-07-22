---
name: praxis-blueprint
description: "Use when a completed or sufficiently detailed workflow profile must be converted into an approved personal operating architecture: workflow constitution, work-stream contracts, skill graph, Obsidian knowledge model, automation gates, rollout plan, and acceptance tests. Use before creating folders or installing generated skills."
license: MIT
compatibility: Requires a Praxis profile or equivalent interview findings and file access for blueprint artifacts.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: architecture
---

# Praxis Blueprint

## Core principle

Turn the person's real work into **a small, explicit, testable operating architecture**. The blueprint is a design contract, not a motivational productivity plan.

## Inputs

Prefer:

- `praxis/profile.json`;
- `praxis/interview-summary.md`;
- existing vault or workflow inventory;
- representative inputs, outputs, corrections, and anti-examples.

If the profile is structurally incomplete, return to `praxis-interview` for the single highest-impact gap. Do not invent key risk or quality decisions.

Treat the person's existing folders, note types, skills, and working practices as constraints to preserve, not blank space to redesign. When the available profile is sufficient for a safe partial result, present a bounded first-rollout draft rather than withholding all design work. Label unresolved assumptions, keep the first rollout to the smallest useful work-stream graph, and state explicitly that setup and installation remain blocked until the completed blueprint is approved and its content-hashed approval record exists.

If only one work stream is known, the next response must still sketch an incremental first rollout for that stream: intake, bounded draft, verification, approval where required, and evidence capture. Ask for the single missing fact that most changes this skeleton, but do not replace the skeleton with a refusal or question alone.

If asked to replace a working taxonomy with PARA or another framework, explicitly decline that migration by default. Keep the person's named folders at their existing paths; do not relabel or map them into replacement destinations. Add only missing governance support. Any skill candidates must be several small capabilities derived from observed triggers, decisions, and deliverables; when examples are missing, label the candidates provisional and state what work samples must validate them.

Tie every provisional capability to the evidence that suggested it. Existing `Research`, `Prompts`, `Decision Records`, `Memory`, and project artifacts, for example, support separate evidence, production, decision, distillation, and project-handoff candidates; name that provenance rather than presenting a generic lifecycle list.

## Architecture rules

1. Preserve existing practices that already work.
2. Start with one to three high-value work streams.
3. Model shared primitives once; avoid duplicate skills by profession label.
4. Give every skill a narrow trigger and explicit handoff.
5. Use scripts only for deterministic, repeated mechanics.
6. Keep curated knowledge separate from runtime memory.
7. Align human approval gates with consequence and reversibility.
8. Design the first-week rollout for adoption, not theoretical completeness.
9. Define measurable acceptance tests before setup.
10. Include versioning, review cadence, and rollback.
11. Keep model-specific prompt doctrine outside the core architecture; record only an optional Prompt Polish handoff when a named-model prompt is genuinely required.

## Procedure

### 1. Validate and summarize the profile

Run:

```bash
python ../praxis-interview/scripts/validate_profile.py praxis/profile.json
```

Summarize:

- primary outcome;
- initial work streams;
- strongest constraints;
- existing structure to preserve;
- critical risk boundaries;
- unresolved assumptions.

### 2. Generate candidate architectures

Create 2–3 approaches when a genuine architectural choice exists. Typical dimensions:

- minimal overlay vs deeper vault integration;
- one general work-stream skill vs several specialized skills;
- manual distillation vs assisted distillation;
- local-only scripts vs tool integrations;
- centralized project MOC vs distributed backlinks.

Lead with the recommendation and explain the trade-off. Do not manufacture alternatives when one option is clearly dictated by constraints.

Prefer several narrow capabilities with explicit handoffs when a proposed general skill would combine distinct triggers, evidence, or output contracts. Preserve the existing knowledge taxonomy by default; propose migration only when its concrete value, cost, and rollback are explicit.

### 3. Present the design incrementally

Present and obtain approval in this order:

1. constitution and non-negotiables;
2. work-stream architecture;
3. skill graph and routing;
4. knowledge architecture;
5. automation boundaries;
6. rollout and acceptance tests.

Ask for approval after each meaningful section. Revise before continuing when the person disagrees.

### 4. Write the approved blueprint

Use the exact artifact set below:

```text
praxis/
├── workflow-constitution.md
├── work-streams.md
├── skill-map.md
├── knowledge-architecture.md
├── automation-boundaries.md
├── rollout-plan.md
└── acceptance-tests.md
```

You may create initial shells with:

```bash
python scripts/blueprint_scaffold.py \
  --profile praxis/profile.json \
  --output praxis \
  --dry-run
```

The model must then complete and review the content. A generated shell is not an approved architecture.

After the person explicitly approves all seven completed documents, record the exact approved bytes:

```bash
python scripts/approve_blueprint.py \
  --profile praxis/profile.json \
  --blueprint-dir praxis \
  --approver "Person name" \
  --confirm-approved
```

The approval command fails while any blueprint document still contains an unfinished placeholder or the scaffold's draft marker. It creates `praxis/blueprint-approval.json`; any later profile or blueprint change invalidates that record and requires renewed review.

## Artifact contracts

### Workflow constitution

Include:

- purpose and primary outcome;
- 5–9 testable operating principles;
- privacy and safety boundaries;
- source-of-truth hierarchy;
- quality doctrine;
- knowledge doctrine;
- amendment, versioning, review, and rollback process.

Principles must be observable. Replace vague “be efficient” language with behavior such as “inspect existing artifacts before asking the user to restate them.”

### Work-stream map

For every initial stream include:

| Field | Required content |
|---|---|
| Trigger | observable start condition |
| Inputs | sources and provenance |
| Decisions | judgment points and alternatives |
| Actions | bounded transformation steps |
| Deliverables | concrete outputs and audience |
| Quality gates | checks, review, or inspection |
| Human approval | who approves what and when |
| Handoff | completion and context transfer |
| Durable residue | note types worth preserving |
| Failure modes | likely errors and escalation |

### Skill map

Define:

- skill name and trigger boundary;
- dependencies and terminal state;
- inputs and output contract;
- scripts/references required;
- conflicts and precedence;
- whether it is universal, personal, or project-specific;
- tests needed before release.

The initial generated layer should normally be:

```text
personal-start-work
personal-finish-work
personal-weekly-review
work-<highest-value-stream>
```

Add more work-stream skills only when the rollout plan justifies them.

### Knowledge architecture

Map the person's existing system to durable note types. For the supplied Obsidian pattern, preserve:

```text
Prompts/            reusable workflow software
Research/           source-backed evidence and synthesis
Decision Records/   consequential choices and rationale
Memory/             reusable lessons, traps, doctrine, verified setup
<Project>/          project state, evidence, runbooks, outputs
_meta/              profile, taxonomy, skill map, governance
```

Specify:

- frontmatter fields;
- provenance and confidence;
- expiry/review rules;
- MOC/backlink strategy;
- write thresholds;
- retrieval paths;
- what must never be stored.

### Automation boundaries

Create a table with:

- action;
- risk dimensions;
- default permission class;
- validation;
- rollback;
- required human.

Permission classes:

1. autonomous;
2. review before action;
3. explicit per-action approval;
4. forbidden.

### Rollout plan

Use staged adoption:

- first proof workflow;
- minimum installed skills;
- first-week usage;
- evidence collection;
- review checkpoint;
- expansion criteria;
- rollback criteria.

### Optional prompt-materialization handoff

When a work stream will be executed through a named model, the blueprint may define an optional handoff to the standalone `prompt-polish` skill. The blueprint remains the authority for intent, constraints, approvals, deliverables, and verification. Prompt Polish may adapt wording only after those contracts are approved. Do not copy model doctrine into Praxis or make the blueprint depend on Prompt Polish.

### Acceptance tests

Define outcomes and non-regressions. Examples:

- context assembly time decreases;
- repeated corrections decrease;
- deliverables preserve required quality fields;
- no existing notes are overwritten;
- the agent does not publish or send without approval;
- retrieval finds relevant prior decisions;
- skill catalog remains small enough to route reliably.

## Blueprint self-review

Before seeking final approval, check:

- every work stream has all eight primitives;
- skills do not duplicate each other;
- every script has deterministic responsibility;
- every risky action has a gate and rollback;
- every durable note type has a write threshold;
- existing structures are preserved unless a migration is explicitly justified;
- unresolved assumptions are visible;
- rollout begins smaller than the final envisioned system;
- acceptance tests can be observed.

## Hard gate

Do not invoke `praxis-setup`, create the vault structure, or install generated skills until the person explicitly approves the written blueprint and the content-hashed approval record exists.

## Common mistakes

| Mistake | Correction |
|---|---|
| One giant “do my job” skill | Compose a small graph around work streams and shared lifecycle skills. |
| Architecture by job title | Use observed triggers, decisions, deliverables, and quality gates. |
| Automation chosen for impressiveness | Automate only repeated deterministic mechanics within approved risk. |
| Replacing a working vault taxonomy | Augment and preserve unless migration value is explicit. |
| No acceptance tests | Define observable gains and non-regressions before setup. |
| Blueprint silently becomes implementation | Stop for explicit approval. |

See [references/blueprint-quality-rubric.md](references/blueprint-quality-rubric.md).
