# Release Architecture Research

## Research question

How should a serious open-source Agent Skills workflow operating system be packaged, released, evolved, and connected to an already successful focused skill?

## Systems reviewed

The release design was informed by current public practices in:

- GitHub repository and release documentation;
- the Agent Skills ecosystem and the `skills` CLI;
- Anthropic's public skills repository and Claude Code marketplace format;
- Superpowers release notes and its skill/plugin separation history;
- GitHub Spec Kit's versioned installation and workflow artifacts;
- BMAD's stable/prerelease channels, modular packaging, and migration-oriented notes;
- mature open-source community-health and supply-chain practices.

The broader skill-system architecture remains documented in [RESEARCH_REPORT.md](RESEARCH_REPORT.md).

## Findings

### 1. A release is a reproducible, named contract

A public release should identify an immutable point in history, declare compatibility, describe behavior changes, publish user-facing notes, and provide artifacts that can be verified. A repository snapshot without a tag, changelog, tests, or checksums is source availability—not a complete release process.

Praxis therefore uses:

- semantic versions and a root `VERSION` file;
- tag-oriented release automation;
- version-specific release notes;
- deterministic ZIP and tar.gz archives;
- SHA-256 checksums;
- GitHub build-provenance attestations;
- a release-readiness validator.

### 2. Install paths should match how people already discover skills

The strongest ecosystems minimize bespoke installation. Praxis supports:

- the open `npx skills` CLI for multi-agent installation;
- a Claude Code marketplace manifest for native plugin discovery;
- direct Git clone and local Python installers for auditable or offline use.

The canonical source remains ordinary Agent Skills directories under `skills/`.

### 3. The repository should be understandable before installation

High-adoption open-source projects make the first screen answer:

- what this is;
- who it is for;
- why it differs;
- how to install it;
- what happens next;
- how to verify it;
- how to report bugs, request features, contribute, and report security issues.

Praxis includes a layered README, quickstart, architecture, security policy, governance, support guide, contribution guide, issue forms, pull-request template, roadmap, release notes, provenance, and maintenance doctrine.

### 4. Modular systems need a small stable core and independently evolvable capabilities

Large skill systems repeatedly move toward capability graphs, explicit routing, and smaller independently maintained components. Monolithic repositories are attractive at launch but couple unrelated release schedules and increase discovery competition.

This directly shaped the Prompt Polish decision: integrate it as a first-party companion, but keep its repository, trigger contract, doctrine references, and version lifecycle independent.

### 5. Release notes should lead with user impact

Good notes distinguish:

- headline capability;
- installation and upgrade path;
- major additions;
- fixes;
- breaking changes and migrations;
- compatibility;
- validation performed;
- known limits;
- contributor attribution.

Praxis uses that structure in `docs/releases/` rather than treating the changelog as a commit dump.

### 6. Community and security files are part of the product

Agent Skills can steer models and execute scripts. Trust requires more than an MIT license. The release includes explicit contribution evidence, security boundaries, third-party intake rules, support routing, code ownership, structured issue reports, CI, checksum verification, and provenance.

## Release decision

Release **Praxis Workflow OS** as its own public repository at:

```text
mfarzanansari/praxis-workflow-os
```

Publish `v1.0.0` as the first stable public workflow contract after all release-readiness checks pass.

Keep **Prompt Polish** public and independently installable at:

```text
mfarzanansari/prompt-polish
```

Cross-link the projects and test the optional handoff contract. Do not copy Prompt Polish's model doctrine into Praxis.
