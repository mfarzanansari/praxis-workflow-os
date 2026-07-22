# ADR 0001 — Integrate Prompt Polish without absorbing it

- **Status:** Accepted
- **Date:** 2026-07-22
- **Decision owners:** Farzan Ansari / Praxis Workflow OS

## Context

Praxis Workflow OS and Prompt Polish are related but operate at different architectural layers.

Praxis discovers and governs a person's work system: outcomes, work streams, evidence, decisions, deliverables, quality gates, knowledge write-back, human approval boundaries, and evolution.

Prompt Polish performs one narrow transformation: it turns a rough prompt into a concise, model-specific prompt using versioned model doctrine while preventing task drift, invention, and instruction inflation.

Prompt Polish also has an existing public identity and a clean install/trigger contract. Folding it directly into the Praxis repository would couple two different change rates:

- Praxis changes when workflow contracts, schemas, safety policy, setup mechanics, or lifecycle skills change.
- Prompt Polish changes when model-specific prompting doctrine or supported models change.

## Decision

Keep Prompt Polish as an independently versioned first-party repository and integrate it into Praxis as an **optional companion capability**.

Praxis may hand a stable workflow or task contract to Prompt Polish when all of these are true:

1. the deliverable and success criteria are already settled;
2. a named target model is known;
3. model-specific wording is likely to change execution quality;
4. the user has installed or explicitly requested Prompt Polish.

Praxis must not require Prompt Polish for interviewing, blueprinting, setup, operation, distillation, retrospectives, or skill authoring.

## Integration boundary

```text
Praxis: intent and workflow contract
           ↓ optional handoff
Prompt Polish: model-specific prompt materialization
           ↓
Target model or agent execution
```

The handoff includes only:

- the approved task or workflow contract;
- target model;
- intended form: one-off task, build, agent, review, design, or pipeline;
- known constraints and done-condition.

Prompt Polish must not redefine the workflow, add deliverables, or override Praxis approval gates.

## Consequences

### Positive

- Preserves Prompt Polish's focused discovery and existing audience.
- Avoids duplicated model doctrine inside Praxis.
- Allows model updates without forcing a Praxis release.
- Keeps Praxis model-agnostic and useful without a specific prompt optimizer.
- Creates a coherent first-party ecosystem instead of a monolith.

### Costs

- Users who want both capabilities install two repositories.
- Cross-repository compatibility must be documented and occasionally tested.
- Breaking changes require coordinated notes rather than one combined changelog.

## Conditions that would justify a future merge

Reconsider only if independent operation creates measurable user harm, such as persistent installation failure, incompatible contracts, duplicated maintenance, or routing confusion that cannot be solved with documentation and tests.

Social attention or repository size alone is not a reason to merge.
