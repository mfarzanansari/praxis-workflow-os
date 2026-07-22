# Source and Design Provenance

Praxis Workflow OS is an original synthesis by Farzan Ansari. It was informed by public patterns from:

- the Agent Skills specification and Anthropic's public skills repository;
- obra/superpowers;
- GitHub Spec Kit;
- garrytan/gstack;
- BMAD Method;
- wshobson/agents;
- alirezarezvani/claude-skills;
- current GitHub repository, release, and supply-chain guidance;
- empirical and security research listed in `RESEARCH_REPORT.md`.

No third-party runtime code is bundled. The included Python scripts were authored for Praxis and use the standard library only. Public workflow ideas were adapted at the level of architecture and methodology; copied text should not be assumed unless explicitly attributed in a file.

## Prompt Polish

Prompt Polish is a separate first-party project by the same maintainer. Praxis does not copy or vendor its model-doctrine references. The projects integrate through a documented optional handoff and retain independent versioning, installation, tests, changelogs, and release ownership.
