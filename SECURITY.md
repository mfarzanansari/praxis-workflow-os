# Security Policy

## Trust model

Agent Skills are operational dependencies. Their descriptions influence discovery, their instructions influence model behavior, and their scripts can affect the local system. Treat every third-party skill as untrusted software until its full dependency and instruction chain has been reviewed.

Praxis bundled scripts:

- require no network access;
- use only the Python standard library;
- do not install packages;
- are non-interactive;
- avoid overwriting by default;
- require an explicit backup directory for forced replacement;
- write structured results to stdout and diagnostics to stderr.

## Supported versions

Security fixes target the latest released version. A previous known-good tag or release archive should be retained for rollback.

## Reporting a vulnerability

Do **not** open a public issue for an exploitable vulnerability, credential exposure, unsafe destructive behavior, or private-data leak.

Use **Security → Report a vulnerability** in the GitHub repository when private vulnerability reporting is enabled. If that option is unavailable, contact the maintainer through a private channel listed on the maintainer's GitHub profile and provide only the minimum information needed to establish contact.

Include:

- affected version and skill/script;
- operating system and host client;
- minimal sanitized reproduction;
- observed and potential impact;
- whether the issue is already being exploited;
- suggested mitigation, if known.

Never include live credentials, client data, private vault contents, or a destructive proof against systems you do not own.

## Response process

The maintainer will attempt to acknowledge a credible private report, reproduce it, assess severity, prepare a fix and migration/rollback guidance, and coordinate disclosure. No response-time guarantee is made by the open-source project.

## Before installation

1. Review `SKILL.md`, scripts, references, assets, and marketplace metadata.
2. Verify release checksums when downloading an archive.
3. Verify GitHub build provenance when available.
4. Run `python3 scripts/validate_release.py` on POSIX, or `python scripts/validate_release.py` on Windows.
5. Run unit tests in a disposable workspace.
6. Use installer and setup `--dry-run` modes.
7. Do not provide credentials during initial evaluation.
8. Grant only the filesystem and tool access required by the selected workflow.

## Release artifact verification

```bash
sha256sum -c SHA256SUMS
```

GitHub attestation verification:

```bash
gh attestation verify praxis-workflow-os-v1.0.0.zip \
  -R mfarzanansari/praxis-workflow-os
```
