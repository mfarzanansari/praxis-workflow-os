---
name: praxis
description: Use when a person wants to design, install, operate, review, or improve a customized AI-assisted workflow, personal operating system, Obsidian knowledge architecture, or reusable skill system—even when they describe it as productivity, memory, process, SOP, second brain, agent workflow, or "how I work."
license: MIT
compatibility: Agent Skills-compatible client with file access; Python 3.9+ is recommended for bundled utilities.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: orchestration
---

# Praxis

## Core principle

Route the person to the **smallest lifecycle capability that changes the current outcome**. Do not load or recreate the whole system for every task.

Praxis treats a workflow as a versioned operating model:

> Trigger → Evidence → Decisions → Actions → Deliverable → Verification → Durable learning

## Route by lifecycle stage

| Current need | Use |
|---|---|
| Understand the person and their real work | `praxis-interview` |
| Convert an approved profile into an architecture | `praxis-blueprint` |
| Create vault files and personalized skills | `praxis-setup` |
| Preserve useful residue from completed work | `praxis-distill` |
| Review evidence and improve the operating system | `praxis-retrospective` |
| Create or evolve a reusable skill | `praxis-skill-forge` |
| Materialize an approved contract for a named model | Optional `prompt-polish` companion, when installed or explicitly requested |

When more than one stage is requested, preserve this order:

```text
interview → blueprint approval → setup → real use → distillation → retrospective → skill evolution
```

## Routing procedure

1. Inspect the conversation and available artifacts. Reuse facts already known.
2. Identify the current lifecycle stage and the deliverable the user expects now.
3. Load only the matching skill.
4. State the route in one sentence, then execute it.
5. When the selected skill reaches an approval gate, stop. Do not silently continue into the next stage.

## Optional Prompt Polish handoff

Praxis owns intent, workflow structure, deliverables, quality gates, and human approval boundaries. When those are already approved and the user names a target model, `prompt-polish` may optionally turn that stable contract into a model-specific execution prompt.

Use the companion only when it is installed or explicitly requested. Pass the approved contract, target model, task form, constraints, and done-condition. Never ask Prompt Polish to invent or redefine the workflow, and never make core Praxis operation depend on it.

## Hard gates

- Do not scaffold a workflow before the profile and blueprint are approved.
- Do not create a new skill merely because a task exists once.
- Do not write raw transcripts into durable memory.
- Do not move, rename, delete, or overwrite a person's existing vault by default.
- Do not treat third-party skills as trusted because they are popular.
- Do not automate an action beyond the person's approved risk boundary.

## Existing-system mode

When the person already has a vault, prompts, SOPs, or skills:

1. inventory what exists;
2. infer the current architecture and naming conventions;
3. identify strengths worth preserving;
4. locate duplication, missing gates, stale references, and retrieval failures;
5. propose an augmentation path rather than a replacement.

## Completion contract

A routed Praxis task is complete when:

- the correct lifecycle skill was used;
- its artifact or decision was produced;
- unresolved assumptions are visible;
- any required human approval was obtained;
- the next lifecycle stage is named but not automatically executed.

## Common routing mistakes

| Mistake | Correction |
|---|---|
| Asking the entire interview in one message | Use `praxis-interview`; one consequential question per turn. |
| Creating folders before understanding the work | Blueprint and approval first. |
| Building a giant profession persona | Generate a small skill graph from work streams and shared primitives. |
| Saving everything as memory | Distill only future-useful residue. |
| Editing skills based on taste | Use evidence and `praxis-skill-forge`. |
| Loading every skill “just in case” | Route narrowly; progressive disclosure is part of the architecture. |

See [references/lifecycle.md](references/lifecycle.md) for the artifact contracts between stages.
