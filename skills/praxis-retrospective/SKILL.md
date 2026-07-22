---
name: praxis-retrospective
description: Use when reviewing a personal workflow system after real use, at the configured weekly/monthly cadence, after a major project, or when skills feel noisy, stale, unused, unsafe, hard to trigger, or ineffective. Use to make evidence-backed keep/change/remove decisions and define controlled improvement experiments.
license: MIT
compatibility: Can operate from notes and examples alone; Python 3.9+ supports optional JSONL metrics aggregation.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: governance
---

# Praxis Retrospective

## Core principle

Improve the workflow from **observed behavior and outcomes**, not novelty, aesthetics, or the assumption that more automation is progress.

The default decision is not “add a skill.” The valid decisions are:

```text
keep → clarify → narrow → script → split → merge → deprecate → remove → experiment
```

## Evidence hierarchy

Prefer, in order:

1. actual deliverables and verification results;
2. user corrections and rejected outputs;
3. execution traces and repeated manual work;
4. invocation and event logs;
5. missed or false-positive trigger examples;
6. user-reported friction with a concrete example;
7. impressions without examples.

Do not make consequential system changes from level 7 alone.

Missing evidence blocks a permanent change, not a disciplined learning step. When evidence is thin, leave the system unchanged and propose one explicitly provisional, bounded experiment that can create the missing evidence. It must name the hypothesis, one primary change or observation, success criterion, non-regression condition, and rollback/stop criterion.

## Inputs

Review a representative period, not only the worst run:

- generated outputs;
- execution briefs and finish reports;
- corrections and rework;
- quality-gate failures;
- skill usage and trigger misses;
- durable notes created and later retrieved;
- time/token/cost data when available;
- safety or approval-gate events;
- user experience and adoption.

Optional aggregation:

```bash
python scripts/aggregate_metrics.py praxis/events.jsonl --output praxis/metrics-summary.json
```

## Procedure

### 1. Re-state the intended outcome

Read the workflow constitution and acceptance tests. A system cannot be judged without the outcome it was designed to improve.

### 2. Build the evidence table

For each repeated observation record:

| Observation | Evidence | Frequency | Impact | Confidence | Affected component |
|---|---|---:|---:|---|---|

Separate:

- one-off task difficulty;
- model/harness limitation;
- stale or missing reference;
- weak trigger description;
- unclear skill procedure;
- wrong output contract;
- missing deterministic script;
- poor knowledge retrieval;
- overly strong or weak human gate;
- adoption/UI friction.

### 3. Diagnose before prescribing

Use this mapping:

| Failure | Likely intervention |
|---|---|
| Skill does not load when needed | trigger-description eval and optimization |
| Skill loads for adjacent tasks | narrow trigger; add near-miss tests |
| Agent knows rule but skips under pressure | hard gate, red flags, rationalization tests |
| Output shape varies or omits fields | positive output contract or structural template |
| Every run reimplements the same helper | bundle and test a deterministic script |
| Guidance conflicts with current tool/version | refresh or pin reference; mark compatibility |
| Too many skills compete | merge/deprecate and improve router |
| Notes exist but cannot be found | improve retrieval cues, MOCs, titles, metadata |
| Too much low-value memory | raise distillation threshold; prune/archive |
| Human gate blocks harmless local work | narrow condition using observable risk |
| Agent acts beyond authority | strengthen gate and pressure-test it |

### 4. Decide keep/change/remove

For every active skill and major knowledge rule, make one explicit decision with rationale.

A skill should be removed or archived when:

- it is unused across a representative period;
- another skill fully owns the same trigger;
- it causes repeated false triggers;
- its guidance is stale or harmful;
- the task is better handled by a script, tool, or project instruction;
- its benefit cannot be demonstrated.

### 5. Choose the smallest experiment

Change one primary mechanism at a time. Define:

- hypothesis;
- exact change;
- test prompts or real tasks;
- success metric;
- non-regression condition;
- review date;
- rollback trigger and method.

Example:

```markdown
Hypothesis: `personal-start-work` loads too much context because project state
and general memory are not distinguished.
Change: require project-state first; load general memory only for a named decision.
Success: median referenced notes falls from 12 to ≤5 with no missed quality gate.
Rollback: restore v0.3.1 if two tasks miss a required prior decision.
```

### 6. Route the change

- wording or reference correction → update with tests;
- recurring skill failure → `praxis-skill-forge`;
- profile assumption changed → `praxis-interview` for that branch, then blueprint amendment;
- architecture changed → `praxis-blueprint` and explicit approval;
- deterministic repeated work → script with unit tests;
- no meaningful evidence → keep the system unchanged.

## Review output contract

```markdown
# Praxis Retrospective — [period/project]

## Intended outcomes and evidence reviewed

## What worked

## Failure and friction patterns

## Skill decisions
| Component | Keep/change/remove | Evidence | Rationale |

## Knowledge-system decisions

## Safety and approval review

## One prioritized experiment
- Hypothesis:
- Change:
- Tests:
- Success:
- Non-regression:
- Rollback:
- Review date:

## Deferred observations
```

## Governance gate

Do not apply material changes during the review. Present the retrospective and experiment for approval. Apply approved skill changes through `praxis-skill-forge` and architecture changes through `praxis-blueprint`.

## Common rationalizations

| Rationalization | Reality |
|---|---|
| “More skills will cover more cases.” | Larger flat catalogs worsen selection and maintenance unless routing and evidence justify growth. |
| “The prompt sounds clearer now.” | Test the behavior; elegant wording may not change outcomes. |
| “One bad output proves the skill is broken.” | Diagnose task difficulty, model variance, missing evidence, and instruction failure separately. |
| “Nobody used it, so people need training.” | Unused may mean poor trigger, low value, or unnecessary capability. |
| “We should save more context to be safe.” | More context can create retrieval noise and stale authority. |
| “This gate is annoying, remove it.” | Compare friction with consequence; narrow gates rather than deleting risk controls blindly. |

See [references/diagnosis-guide.md](references/diagnosis-guide.md).
