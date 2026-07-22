# Research Report — What Exceptional Agent Skill Systems Do Differently

- **Research date:** 2026-07-22
- **Purpose:** Derive a production-grade, profession-agnostic skill system for a personal Obsidian + agent workflow.
- **Resulting implementation:** Praxis Workflow OS in this repository.

## Executive conclusion

The strongest skill systems are not the ones with the longest prompts or the largest catalogs. They combine seven properties:

1. **Progressive disclosure:** tiny discovery metadata, focused procedural instructions, and on-demand resources.
2. **Workflow before execution:** understand intent, produce an approved design, then implement.
3. **Composable capability graphs:** route among small skills rather than loading a flat encyclopedia.
4. **Deterministic companion tooling:** scripts own state, validation, scaffolding, aggregation, and repetitive mechanics.
5. **Durable governance artifacts:** constitutions, specs, decisions, plans, and acceptance tests survive individual chats and model changes.
6. **Evidence-driven evolution:** baseline tests, with-skill comparisons, human review, regressions, and deprecation.
7. **Security and provenance:** third-party skills are treated as executable supply-chain dependencies, not harmless Markdown.

The most important empirical warning is that **skills do not automatically improve agents**. SWE-Skills-Bench found that 39 of 49 public software-engineering skills produced no pass-rate improvement, the average gain was only 1.2 percentage points, and several version-mismatched skills degraded performance. This strongly supports building a small, local, workflow-specific system instead of installing hundreds of generic skills.

Praxis therefore does not attempt to make one universal “expert persona.” It interviews the person, models recurring work streams, builds a small capability graph, preserves curated knowledge in Obsidian, and improves only from real evidence.

## 1. Research method

There is no authoritative “top-rated skills” leaderboard. Repository stars, installs, forks, shares, and catalog size measure different kinds of attention and are vulnerable to hype, age, and social effects. They were used as **discovery signals**, then the architecture and actual skill files were inspected.

The sample emphasized:

- official specifications and first-party documentation;
- highly adopted open-source systems;
- systems repeatedly adapted across agent clients;
- skill files, scripts, lifecycle artifacts, and maintenance mechanisms—not only README claims;
- empirical studies that test whether skills improve outcomes;
- recent security research on agent-skill supply chains.

Point-in-time adoption indicators observed during research included:

| System | Approximate adoption signal on 2026-07-22 | Why inspected |
|---|---:|---|
| `obra/superpowers` | 255k GitHub stars | Composable process skills, design gates, TDD discipline |
| `anthropics/skills` | 151k GitHub stars | Official Agent Skills examples and production document skills |
| `github/spec-kit` | 123k GitHub stars | Constitution → spec → plan → tasks → implementation lifecycle |
| `garrytan/gstack` | 123k GitHub stars | Opinionated role workflows, scripts, state, install/update productization |
| `bmad-code-org/BMAD-METHOD` | 48.1k GitHub stars | Scale-adaptive guided workflows and specialist collaboration |
| `wshobson/agents` | 38.1k GitHub stars | Multi-harness generation and large composable marketplace |
| `alirezarezvani/claude-skills` | 22.9k GitHub stars | Broad cross-domain packaging, interview tooling, scripts, references |

These numbers change and should never be interpreted as proof that a particular skill improves a particular workflow.

## 2. Official Agent Skills architecture

The Agent Skills standard defines a skill as a folder with a required `SKILL.md` and optional `scripts/`, `references/`, and `assets/`. `name` and `description` metadata are loaded for discovery; the body is loaded on activation; resources load only when required. The specification recommends keeping the main skill under 500 lines and using shallow relative references.

This progressive-disclosure model has several consequences:

- The description is not marketing copy. It is routing infrastructure.
- Catalog size has a persistent context cost even when bodies are not loaded.
- Heavy reference data should not live in the always-loaded metadata or core body.
- Scripts can execute repeatable logic without spending model context on implementation details.
- Skills should be portable, version-controlled source artifacts rather than one-off chat prompts.

Official authoring guidance also stresses starting from real expertise, refining with real execution, inspecting traces rather than only final outputs, and bundling scripts when repeated runs reinvent the same helper.

**Praxis adaptation:** every skill has a narrow trigger, core procedure, completion contract, eval file, provenance/version metadata, and only the scripts required for deterministic behavior.

Sources:

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/skill-creation/using-scripts
- https://agentskills.io/skill-creation/optimizing-descriptions
- https://github.com/anthropics/skills

## 3. Superpowers — skills as process enforcement

Superpowers is notable because it treats skills as a software-development methodology rather than a collection of isolated commands. Its workflow begins with understanding and design, proceeds through planning and execution, and adds verification, debugging, review, and subagent composition.

### Patterns worth adapting

**One question at a time.** Its brainstorming skill inspects the project, asks focused questions, proposes alternatives with a recommendation, and obtains approval before implementation.

**Hard gates where behavior must not drift.** It explicitly blocks implementation before approved design. This is stronger and more testable than “consider planning first.”

**Skill authoring as TDD.** The writing-skills doctrine maps RED–GREEN–REFACTOR to documentation:

- RED: observe how the agent fails without the skill;
- GREEN: write the minimum guidance that changes that behavior;
- REFACTOR: close loopholes, reduce waste, and rerun tests.

**Match instruction form to failure.** This is one of the strongest findings in the inspected systems:

- deliberate rule skipping needs hard gates and pressure tests;
- wrong output shape needs a positive recipe or output contract;
- missing fields need structural slots;
- conditional behavior needs observable predicates;
- deterministic repetition needs code.

**Avoid shortcut descriptions.** Superpowers reports that descriptions summarizing the workflow can cause agents to act from metadata without reading the full skill. Descriptions should primarily make the trigger boundary clear.

### What Praxis changes

Superpowers is software-development-centered and intentionally forceful. Praxis generalizes the useful process doctrine while allowing different consequence levels. A field technician's safety gate, a writer's source-verification gate, and a director's publication gate are not identical, but all are derived from the same risk model.

Source:

- https://github.com/obra/superpowers

## 4. GitHub Spec Kit — artifacts and governance outlive the chat

Spec Kit's strongest contribution is not an individual prompt; it is a **durable artifact chain**:

```text
constitution → specification → plan → tasks → implementation
```

It also includes clarification, consistency analysis, checklists, extensions, presets, hooks, and many client integrations.

### Patterns worth adapting

**Constitution first.** Principles, constraints, quality expectations, and governance are made explicit before downstream work.

**Artifact propagation.** Updating a governing principle requires checking dependent templates and commands. This prevents one document from saying “review required” while a later workflow silently bypasses it.

**Versioning and impact reports.** Changes are versioned and accompanied by an explanation of what changed and what remains pending.

**Cross-harness portability.** Canonical source artifacts can generate client-specific integration outputs.

### What Praxis changes

A personal workflow is broader and less deterministic than software specification. Praxis keeps the constitution and artifact-chain idea but replaces software-only artifacts with:

```text
profile → workflow constitution → work-stream map → skill graph
→ knowledge architecture → automation boundaries → rollout → acceptance tests
```

Source:

- https://github.com/github/spec-kit

## 5. gstack — a skill system becomes a product when operations are engineered

gstack demonstrates that widely used skills often contain much more than prompt text. Its repository includes role-focused workflows, runtime preambles, configuration, browser infrastructure, persistent learning, telemetry/consent logic, update checks, installation, and state management.

### Patterns worth adapting

**Opinionated defaults.** Users are not given an endless menu of equally weighted options. Skills lead with a recommendation and expose modes only when they change outcomes.

**Persistent operational state.** Learning and session state are stored outside the transient chat.

**Companion daemons and scripts.** Repeated browser and workflow mechanics are engineered once instead of regenerated every run.

**Install/update/config are part of quality.** A brilliant skill that cannot be safely installed, updated, inspected, or rolled back is not a complete system.

**Role lenses can be useful when bounded.** CEO, design, engineering, QA, and release viewpoints are valuable because each owns a specific decision surface—not merely because of the role title.

### What Praxis changes

Praxis uses work streams rather than fixed executive/engineering roles. It adopts safe installers, durable state, scripts, explicit permissions, and review logs, while avoiding mandatory telemetry and software-only assumptions.

Source:

- https://github.com/garrytan/gstack

## 6. BMAD Method — adaptive depth and collaborative thinking

BMAD is a large framework of specialist agents and guided workflows designed to scale from small changes to complex systems. Its core claim is that the AI should facilitate the user's thinking rather than replace it.

### Patterns worth adapting

- different workflow depths for different complexity;
- guided collaboration rather than autonomous assumption-making;
- specialist roles with explicit handoffs;
- navigation/help so a large system remains usable;
- extension builders and modules.

### What Praxis changes

Praxis applies adaptive depth to the interview—quick, standard, and deep—but intentionally keeps the initial personal skill graph small. It uses specialized work-stream skills only after the interview discovers stable recurring value.

Source:

- https://github.com/bmad-code-org/BMAD-METHOD

## 7. wshobson/agents — canonical source and multi-harness generation

This marketplace supports multiple agent clients and emphasizes a canonical source that can generate idiomatic artifacts for different harnesses.

### Patterns worth adapting

- distinguish source artifacts from installation outputs;
- compose small agents/skills into workflows;
- document authoring conventions;
- support multiple clients without manually forking behavior in every directory;
- keep external memory integration separate from skill definitions.

### What Praxis changes

Praxis ships standard Agent Skills source and a portable installer. Client-specific wrappers can be generated later, but the canonical source remains auditable and versioned.

Source:

- https://github.com/wshobson/agents

## 8. alirezarezvani/claude-skills and “grill-me” — interview discipline plus tooling

This broad repository packages hundreds of cross-domain skills, agents, commands, references, scripts, and converters. The inspected `grill-me` skill is especially relevant to Praxis.

### Patterns worth adapting

- ask one question per turn;
- provide a recommended answer rather than delegating all design burden to the user;
- inspect the codebase/artifacts before asking;
- walk decision dependencies depth-first;
- extract decision branches and persist session state with scripts;
- know when the interview has reached shared understanding.

### What Praxis changes

Praxis expands the interview beyond software design to work streams, stakeholders, human constraints, physical environment, accessibility, durable knowledge, privacy, and automation risk. Its state script makes no model calls; it only records confirmed/inferred/deferred/disputed decisions.

Source:

- https://github.com/alirezarezvani/claude-skills

## 9. Empirical research — why “install more skills” is the wrong strategy

### SWE-Skills-Bench

The 2026 benchmark paired 49 public skills with real repositories and controlled tests. Thirty-nine produced zero pass-rate improvement; the mean gain was 1.2 percentage points; seven specialized skills showed meaningful gains; and three degraded results because guidance conflicted with the project version/context.

**Design implication:** specialization and contextual compatibility matter far more than catalog size. Every Praxis skill must earn its catalog cost through local tests and version-aware references.

Source:

- https://arxiv.org/abs/2603.15401

### AgentSkillOS

AgentSkillOS organizes large ecosystems into capability trees and composes multiple skills as directed acyclic graphs. It reports that structured retrieval approximates oracle selection and that DAG orchestration outperforms native flat invocation at scale.

**Design implication:** use a router and explicit skill graph. Do not expose the model to an undifferentiated pile of hundreds of skills.

Source:

- https://arxiv.org/abs/2603.02176

### Ecosystem redundancy and security

Recent research has identified large-scale redundancy, dependency opacity, malicious or abandoned skill risk, and semantic attacks that manipulate discovery and selection through `SKILL.md` text itself.

**Design implication:** imported skills need provenance, pinning, full-folder inspection, dependency review, sandbox testing, and local adaptation. The description is operational input and part of the attack surface.

Sources:

- https://arxiv.org/abs/2605.11418
- https://arxiv.org/abs/2605.09594
- https://arxiv.org/abs/2607.01136

## 10. Why Praxis is profession-agnostic

A universal profession template fails because job titles hide huge variation. A “marketer” might mainly run paid acquisition, perform market research, manage launches, write copy, or coordinate agencies. Two people with the same title can need opposite systems.

Praxis models **work primitives** instead:

| Primitive | Software architect | Designer | Content writer | Marketer | Field technician |
|---|---|---|---|---|---|
| Trigger | feature/system change | approved brief | approved topic | campaign objective | assigned service call |
| Evidence | repo, constraints, ADRs | brief, brand, references | sources, voice examples | analytics, interviews, research | manual, label, measurements |
| Judgment | boundaries and trade-offs | hierarchy and visual intent | angle and evidence threshold | segment and message | safe diagnostic sequence |
| Deliverable | architecture brief | concept/review board | sourced draft | campaign plan/assets | diagnostic record/handoff |
| Verification | review, tests, operability | critique, accessibility | edit, fact-check | approval, measurement plan | safety, units, manual check |
| Durable residue | decision/research | decision/memory | research/prompt | research/memory | project state/safety lesson |

The interview fills these fields from real examples. Generated skills then contain the person's own triggers, quality gates, approvals, and retrieval patterns.

## 11. Adaptation to the supplied Obsidian vault

The supplied vault already has a strong coarse architecture:

- `Prompts/` contains reusable workflow software and kickoff briefs.
- `Research/` contains source-grounded studies and doctrine.
- `Decision Records/` captures consequential choices.
- `Memory/` contains reusable lessons, setup, and operating doctrine.
- `Spindle/` is a project/product knowledge domain with evidence, synthesis, decisions, and runbooks.
- `_meta/` owns taxonomy.

Praxis deliberately **does not replace this** with PARA, Zettelkasten, or another generic organization scheme. It adds governance and write policies:

- `Praxis Profile.json` and a human-readable system map in `_meta/`;
- automation boundaries and skill map;
- note templates with provenance, confidence, and review metadata;
- a `Reviews/` domain for evidence-based workflow evolution;
- generated start-work, finish-work, weekly-review, and work-stream skills;
- a distillation gate that prevents raw session dumps.

The existing MOCs/backlinks remain the human-readable navigation layer. A future Rust memory subsystem can serve runtime retrieval, ranking, and continuity without becoming the authoritative knowledge representation.

## 12. The final Praxis system

### Lifecycle skills

1. `praxis` routes lifecycle requests.
2. `praxis-interview` discovers the operating model one decision at a time.
3. `praxis-blueprint` creates and obtains approval for the architecture.
4. `praxis-setup` safely scaffolds vault and personalized skills.
5. `praxis-distill` writes curated durable residue.
6. `praxis-retrospective` diagnoses evidence and proposes one controlled experiment.
7. `praxis-skill-forge` creates/evolves tested skills.

### Deterministic scripts

- interview state persistence and profile validation;
- blueprint shell generation;
- safe non-overwriting vault/skill scaffolding;
- note-shell creation;
- metrics aggregation;
- skill scaffolding and validation;
- repository installation and validation.

All bundled scripts are standard-library-only and make no network calls. Stateful scripts expose dry-run or non-overwrite behavior. Replacement requires explicit force plus backup.

### Maintenance model

Every material change should have:

- evidence and failure classification;
- baseline or previous-version comparison;
- realistic positive and negative trigger tests;
- application, variation, missing-information, and pressure tests as appropriate;
- human review;
- semantic version and changelog;
- provenance, compatibility, and security review;
- rollback path.

## 13. What was intentionally not copied

Several popular patterns were rejected or narrowed:

- **Huge default catalogs:** selection and maintenance cost are too high.
- **Job-title mega-personas:** they imitate identity instead of encoding bounded work.
- **Raw transcript memory:** retrieval noise and authority ambiguity outweigh convenience.
- **Automatic vault reorganization:** destroys trust and existing retrieval habits.
- **Unreviewed third-party installers:** skills can contain scripts, network behavior, and semantic selection attacks.
- **Prompt-only deterministic work:** validators, scaffolds, and state transitions belong in scripts.
- **Big-bang setup:** adoption is proven with one work stream before expansion.
- **“Best practice” claims without tests:** a skill must change local behavior, not merely sound expert.

## 14. Validation status of this release

The repository validator reports seven structurally valid Agent Skills. The deterministic test suite covers:

- repository validation;
- all six profession-diverse example profiles;
- interview state lifecycle;
- non-overwriting note creation;
- safe setup dry-run/apply behavior;
- force-without-backup rejection;
- metrics aggregation;
- installer skip behavior.

Model-level eval prompts are bundled with every skill. They still need to be executed in the intended agent/model/client to measure trigger behavior, output quality, and variance. That limitation is explicit: deterministic script tests can be completed here; agent behavior cannot be honestly certified without running the target runtime.
