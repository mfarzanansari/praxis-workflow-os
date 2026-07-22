# Praxis Workflow OS — Architecture

## 1. Architectural thesis

A useful personal agent system is not a universal prompt, a folder template, or a collection of personas. It is a **versioned operating model** that joins:

- a person's actual work and constraints;
- a small graph of procedural skills;
- deterministic utilities for repeatable mechanics;
- durable human-readable knowledge;
- explicit human approval boundaries;
- evaluation and maintenance loops.

The architecture separates five layers that are often mixed together:

| Layer | Responsibility | Typical artifact |
|---|---|---|
| Intent | Outcomes, values, risk tolerance, non-negotiables | workflow constitution |
| Orchestration | Select and order capabilities | router + skill graph |
| Execution | Perform a bounded workflow | work-stream skills |
| Knowledge | Preserve curated reusable residue | Obsidian notes and MOCs |
| Runtime memory | Temporary state, retrieval indexes, session continuity | agent/runtime-specific store |

Obsidian is the durable knowledge layer, not the entire runtime memory architecture.

## 2. Universal work model

Every recurring work stream is modeled through eight primitives:

1. **Trigger** — what starts the work and how urgency is detected.
2. **Inputs and evidence** — source material, tools, people, and provenance.
3. **Judgment** — decisions, trade-offs, standards, and escalation criteria.
4. **Transformation** — analysis, creation, coordination, or physical action.
5. **Deliverable** — the observable result and its audience.
6. **Verification** — tests, review, approval, rehearsal, inspection, or feedback.
7. **Handoff** — who receives it, what context they need, and how completion is acknowledged.
8. **Residue** — what deserves to become research, a decision record, a reusable lesson, a prompt, or updated project state.

A workflow skill is generated from these primitives. A profession changes their content, not the architecture.

## 3. Skill graph

```text
praxis (router)
├── praxis-interview
├── praxis-blueprint
├── praxis-setup
├── praxis-distill
├── praxis-retrospective
└── praxis-skill-forge

Generated per-person layer
├── personal-start-work
├── personal-finish-work
├── personal-weekly-review
└── work-<stream-id> × N
```

The router is intentionally small. It identifies lifecycle stage, loads only the relevant skill, and refuses to bypass approval gates.

## 4. Interview engine

The interview is a stateful decision-tree traversal, not a static survey.

### Rules

- Inspect available evidence before asking.
- Ask one question per turn.
- State why the decision matters.
- Provide a recommended answer based on current evidence.
- Offer compact options when they reduce cognitive load.
- Resolve prerequisites before dependent decisions.
- Record confirmed, inferred, deferred, and disputed answers differently.
- Allow “unknown,” but record the consequence and a method for resolving it.
- Stop when additional questions no longer change the initial architecture.

### Branches

1. Consent, privacy, and scope.
2. Outcomes, stakeholders, and failure costs.
3. Recurring work streams.
4. Inputs, sources of truth, and tools.
5. Judgment, quality, examples, and anti-examples.
6. Collaboration, accessibility, energy, time, and environment.
7. Knowledge, provenance, retention, and retrieval.
8. Automation boundaries and human gates.
9. Adoption capacity, review cadence, and change budget.

The script stores state; the model performs semantic interviewing and recommendations.

## 5. Blueprint compiler

The blueprint converts profile facts into these contracts:

- **Workflow constitution:** purpose, principles, constraints, governance, version.
- **Work-stream map:** one contract per recurring stream.
- **Skill map:** trigger boundaries, dependencies, and conflict resolution.
- **Knowledge architecture:** note types, folder mapping, metadata, and write policies.
- **Automation boundaries:** autonomous, review-before-action, and forbidden zones.
- **Rollout plan:** smallest useful deployment sequence.
- **Acceptance tests:** what must improve and what must not regress.

The blueprint is approved before setup. This preserves user agency and prevents a generic scaffold from becoming the architecture by accident.

## 6. Skill design contract

A production Praxis skill should contain:

- valid Agent Skills metadata;
- a narrow trigger boundary;
- a concise core principle;
- a positive output or behavior contract;
- explicit decision points and approval gates;
- relevant examples and anti-examples;
- common failure modes grounded in tests;
- references only when needed;
- scripts only for deterministic repeated work;
- eval prompts and assertions;
- version and provenance metadata.

### Selecting the instruction form

| Observed baseline failure | Preferred intervention |
|---|---|
| Agent knowingly skips a rule under pressure | hard gate, red flags, rationalization counter-table |
| Output has the wrong structure | positive output contract/template |
| Required element is omitted | mandatory field in a generated artifact |
| Behavior depends on circumstance | observable conditional rule |
| Repetitive deterministic mechanics | script with structured output |
| Domain facts are missing or stale | reference file with version/provenance |

## 7. Knowledge write policy

Write durable notes only when information is likely to change future work.

| Note type | Write when | Do not write |
|---|---|---|
| Research | evidence and synthesis may be reused | raw search transcript |
| Decision record | a consequential choice has alternatives and rationale | trivial preference |
| Memory | a generalizable lesson, trap, or verified setup recurs | project-only status |
| Prompt | a reusable workflow has stable inputs/outputs | one-off chat wording |
| Project state | another session needs current truth to continue | complete activity log |
| Review | system evidence supports a change | vague feeling without examples |

Every durable note should include provenance, confidence, scope, and review/expiry information when relevant.

## 8. Safety and permissions

Risk is classified across reversibility, financial cost, safety, legal/compliance, privacy, reputation, and interpersonal impact.

- **Autonomous:** reversible, local, low-cost operations with observable validation.
- **Review before action:** external communication, publication, spending, deletion, irreversible changes, consequential recommendations.
- **Forbidden without explicit per-action instruction:** credential handling beyond required local use, covert monitoring, deceptive activity, unsafe physical instructions, unauthorized access, or bypassing organizational controls.

Filesystem scripts default to dry-run or non-overwrite behavior. Network access is not required by bundled scripts.

## 9. Evolution model

```text
Observe → classify failure → reproduce baseline → change one mechanism
→ run with-skill test → compare → human review → release or rollback
```

A change is not accepted because it sounds better. It must improve a real behavior, output, trigger, or maintenance property without unacceptable regressions.

Setup is also bound to evidence: `blueprint-approval.json` records the approver plus SHA-256 digests of the completed profile and all seven blueprint documents. Any post-approval edit invalidates setup authorization until the person reviews and approves the new bytes.

## 10. Portability

The source format follows the Agent Skills directory standard. Client-specific installers or generated wrappers should be treated as build outputs. The canonical source remains this repository so behavior can be compared and regenerated across Claude Code, Codex, Cursor, Gemini, OpenCode, and other compatible clients.
