# Starter Architecture for the Supplied Obsidian Vault

This is an **inferred seed**, not a completed interview. It uses only the supplied vault tree and the explanation that Obsidian is your durable human-readable knowledge layer for agent workflows.

The machine-readable seed is:

`examples/profiles/obsidian-agent-architect-starter.json`

## What the current vault already gets right

Your structure separates several knowledge responsibilities that many systems collapse:

- **Prompts** are reusable workflow software and kickoff briefs.
- **Research** is evidence, prior art, synthesis, and doctrine-building.
- **Decision Records** preserve choices and rationale.
- **Memory** contains cross-project lessons, traps, verified setup, and operating doctrine.
- **Spindle/project folders** hold product-specific evidence, strategy, runbooks, and current truth.
- **_meta** owns taxonomy and should own workflow governance.

Praxis preserves this coarse structure. It does not recommend replacing it with a generic second-brain taxonomy.

## Initial skill graph inferred for you

```text
praxis
├── praxis-interview
├── praxis-blueprint
├── praxis-setup
├── praxis-distill
├── praxis-retrospective
└── praxis-skill-forge

first generated personal layer
├── personal-start-work
├── personal-finish-work
├── personal-weekly-review
└── work-research-fleet-synthesis

second-wave candidates, only after evidence
├── work-orchestrator-kickoff
└── work-skill-prompt-engineering
```

The first proof workflow should probably be **research fleet → defended synthesis** because your vault already shows repeated external research, multi-lens synthesis, verifier verdicts, and durable write-back. It is valuable, observable, and less destructive than beginning with autonomous product implementation.

## Proposed operating loop

```text
1. Start-work skill scans the relevant MOCs, project state, decisions, and doctrine.
2. It creates a compact execution brief and identifies freshness gaps.
3. The work-stream skill decomposes research lenses and bounded worker briefs.
4. The orchestrator integrates evidence and runs a verifier pass.
5. Finish-work checks the output contract and unresolved risks.
6. Distill writes only reusable research, decisions, lessons, prompts, or project state.
7. Retrospective reviews corrections and trigger behavior.
8. Skill Forge changes a skill only after a reproducible failure.
```

## Critical architectural boundary

Your Reddit description correctly identifies a central distinction:

> Obsidian can be a strong durable knowledge base without being the complete runtime memory layer.

The curated vault should remain legible, versionable, and intentionally written. A separate Rust memory layer can own retrieval indexes, working state, ranking, temporal continuity, and machine-oriented representations. Agents may retrieve from both, but durable write-back into Obsidian should pass the distillation threshold.

## Files Praxis would add, without moving existing notes

```text
_meta/
├── Praxis System.md
├── Praxis Profile.json
├── Skill Map.md
├── Automation Boundaries.md
└── Templates/

Reviews/
└── Reviews MOC.md
```

Existing MOCs and files are skipped by default. Replacement requires explicit force and a backup directory.

## Highest-value interview branches remaining

The interview should begin with one question, not all of these at once:

1. Which work stream should prove value first?
2. Which client/model combinations must be supported initially?
3. What is the planned Rust memory-layer interface and authority boundary?
4. Which data must remain local-only?
5. What correction do you most often make to orchestrators?
6. What makes a worker brief exceptional rather than merely complete?
7. Which residue should never be written back automatically?
8. What evidence should be required before a prompt becomes a released skill?

Recommended first question:

> **Which single workflow should this system improve first?**
>
> Recommended answer: **research fleet → defended synthesis**. It already recurs in your vault, has clear artifacts, and can prove context assembly, orchestration, verification, and write-back before the system touches more consequential build workflows.
