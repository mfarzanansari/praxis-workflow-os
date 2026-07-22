# Praxis Workflow OS

**A profession-agnostic Agent Skills operating system that learns how you work, compiles a personalized workflow architecture, installs the minimum useful capabilities, and improves the system from evidence.**

[![CI](https://github.com/mfarzanansari/praxis-workflow-os/actions/workflows/ci.yml/badge.svg)](https://github.com/mfarzanansari/praxis-workflow-os/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/mfarzanansari/praxis-workflow-os)](https://github.com/mfarzanansari/praxis-workflow-os/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

Praxis is for software architects, designers, directors, writers, marketers, operators, researchers, educators, tradespeople, technicians, founders, and anyone whose work has recurring inputs, judgment, deliverables, quality standards, and lessons worth retaining.

It does **not** begin with a job-title template. It begins with the universal structure of work:

> **Trigger → Evidence → Decisions → Actions → Deliverables → Verification → Handoff → Durable learning**

The interview discovers what those primitives mean in one person's real life. The blueprint turns them into a small skill graph, knowledge architecture, human approval gates, and maintenance loop.

## Why Praxis exists

Most personal AI systems fail in one of two ways:

- they are generic prompt packs that never learn the user's actual work; or
- they become sprawling collections of agents, notes, automations, and rules that compete for attention.

Praxis treats a personal workflow as an **operating model**: explicit contracts, small composable skills, deterministic utilities, durable human-readable knowledge, consequence-aware approval gates, and an evidence-driven evolution loop.

## What is included

| Skill | Purpose |
|---|---|
| `praxis` | Routes the current request to the smallest relevant lifecycle skill. |
| `praxis-interview` | Runs a one-question-at-a-time adaptive interview with durable session state. |
| `praxis-blueprint` | Produces the workflow constitution, work-stream map, skill graph, knowledge model, boundaries, rollout plan, and acceptance tests. |
| `praxis-setup` | Safely scaffolds an Obsidian vault and personalized skills without overwriting existing work. |
| `praxis-distill` | Converts useful session residue into curated research, decisions, memory, prompts, and project-state notes. |
| `praxis-retrospective` | Reviews evidence, detects friction, and proposes the smallest justified improvements. |
| `praxis-skill-forge` | Creates and evolves skills with baselines, evals, provenance, versioning, security review, and release gates. |

The repository also includes:

- standard-library-only Python utilities;
- safe dry-run, non-overwrite, backup, and rollback behavior;
- example profiles for seven very different professions;
- repository, release, profile, and skill validators;
- deterministic unit tests and model-level eval portfolios;
- cross-platform installers;
- a Claude Code marketplace manifest;
- automated release archives, checksums, and build-provenance attestations;
- research, architecture, governance, security, and maintenance documentation.

## Install

### Open Agent Skills CLI — recommended

List the available skills:

```bash
npx skills add mfarzanansari/praxis-workflow-os --list
```

Install the complete system globally:

```bash
npx skills add mfarzanansari/praxis-workflow-os --skill '*' -g
```

Install only the interview and blueprint first:

```bash
npx skills add mfarzanansari/praxis-workflow-os \
  --skill praxis \
  --skill praxis-interview \
  --skill praxis-blueprint \
  -g
```

### Claude Code marketplace

```text
/plugin marketplace add mfarzanansari/praxis-workflow-os
/plugin install praxis@praxis-workflow-os
```

### Local installer

```bash
git clone https://github.com/mfarzanansari/praxis-workflow-os.git
cd praxis-workflow-os
python3 scripts/validate_release.py
python3 scripts/install.py --target ~/.claude/skills --dry-run
python3 scripts/install.py --target ~/.claude/skills
```

PowerShell:

```powershell
git clone https://github.com/mfarzanansari/praxis-workflow-os.git
Set-Location praxis-workflow-os
python scripts\validate_release.py
.\install.ps1 -Target "$HOME\.claude\skills" -DryRun
.\install.ps1 -Target "$HOME\.claude\skills"
```

## Start in five minutes

Ask your agent:

> Use `praxis-interview` to design my personal workflow system. Inspect the context and files I have already provided before asking anything. Ask one consequential question at a time, include your recommended answer and rationale, and persist every confirmed decision.

The interview creates:

```text
praxis/profile.json
praxis/interview-summary.md
praxis/open-questions.md
```

Then ask:

> Use `praxis-blueprint` with `praxis/profile.json`. Produce my workflow constitution, work-stream architecture, skill graph, knowledge model, automation boundaries, rollout plan, and acceptance tests. Present the design in sections and wait for approval before setup.

See [QUICKSTART.md](QUICKSTART.md) for the complete lifecycle.

## The lifecycle

```text
Inspect existing context
        ↓
Adaptive interview
        ↓
Approved workflow blueprint
        ↓
Safe, minimal setup
        ↓
Real work and verification
        ↓
Curated durable write-back
        ↓
Evidence-based retrospective
        ↓
Test-driven skill evolution
```

Praxis separates five concerns that are often mixed together:

1. **Intent** — outcomes, principles, constraints, and risk tolerance.
2. **Orchestration** — selecting and sequencing the right capability.
3. **Execution** — completing a bounded recurring workflow.
4. **Knowledge** — preserving curated, human-readable residue.
5. **Runtime memory** — temporary state and retrieval handled by the agent runtime.

Obsidian can be the durable knowledge layer. It is not required to pretend that a note vault is the whole memory system.

## Obsidian architecture

Praxis augments a working vault instead of forcing a fashionable taxonomy:

```text
Prompts/            reusable workflow software and kickoff briefs
Research/           source-backed evidence and synthesis
Decision Records/   choices, alternatives, rationale, consequences
Memory/             reusable lessons, traps, doctrine, verified setup
<Project>/          project evidence, state, runbooks, and outputs
_meta/              profile, taxonomy, skill map, and governance
```

Existing files are skipped by default. Replacements require explicit force, backup, and review.

## Prompt Polish integration

[`prompt-polish`](https://github.com/mfarzanansari/prompt-polish) remains a focused standalone skill and a first-party Praxis companion.

Praxis defines **what the workflow must accomplish**. Prompt Polish can then materialize a stable workflow contract into a concise, model-specific prompt when that extra adaptation is useful. The integration is optional: Praxis works without Prompt Polish, and Prompt Polish retains its own install path, trigger boundary, model-doctrine references, and release cadence.

Install both:

```bash
npx skills add mfarzanansari/praxis-workflow-os --skill '*' -g
npx skills add mfarzanansari/prompt-polish -g
```

Read the architecture decision in [docs/decisions/0001-prompt-polish-integration.md](docs/decisions/0001-prompt-polish-integration.md).

## Design principles

1. **Inspect before asking.** Existing artifacts often answer questions more accurately than memory.
2. **One consequential question at a time.** Depth should not become questionnaire overload.
3. **Model work primitives, not stereotypes.** A title does not define a workflow.
4. **Skills teach judgment; scripts enforce mechanics.** Deterministic repetition belongs in code.
5. **Curated knowledge is not transcript storage.** Write only residue that can change future work.
6. **Human gates follow consequence.** Irreversibility, cost, safety, legal, privacy, reputation, and interpersonal impact determine approval strength.
7. **Every skill earns its place.** New skills start with demonstrated friction or a failing baseline.
8. **Small graph, strong routing.** Capability trees beat giant flat catalogs.
9. **Evidence drives evolution.** Change one mechanism, compare behavior, then release or roll back.
10. **Third-party skills are untrusted software.** Review the whole folder, dependency chain, permissions, provenance, and network behavior.

## Validate and verify a release

```bash
python3 scripts/validate_release.py
python3 -m unittest discover -s tests -v
python3 scripts/build_manifest.py --check
```

Downloaded release assets include `SHA256SUMS`. For releases built by GitHub Actions, provenance can also be verified with GitHub CLI:

```bash
gh attestation verify praxis-workflow-os-v1.0.0.zip \
  -R mfarzanansari/praxis-workflow-os
```

## Project documentation

- [Architecture](ARCHITECTURE.md)
- [Quickstart](QUICKSTART.md)
- [Research report](RESEARCH_REPORT.md)
- [Release research](RELEASE_RESEARCH.md)
- [Maintenance model](MAINTENANCE.md)
- [Governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Support](SUPPORT.md)
- [v1.0.0 release notes](docs/releases/v1.0.0.md)

## Status

`v1.0.0` defines the first stable public workflow contract. Bundled scripts are deterministic and tested locally; model-level eval portfolios are included for target-client validation because model behavior can vary by client, model version, permissions, and available tools.

## License

MIT. See [LICENSE](LICENSE).
