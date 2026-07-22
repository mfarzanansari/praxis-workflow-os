# Releasing Praxis Workflow OS

## Release checklist

1. Confirm the target version and public contract.
2. Update `VERSION` and every bundled skill's `metadata.version`.
3. Update `.claude-plugin/marketplace.json` metadata and plugin versions.
4. Add `docs/releases/<version>.md` and update `CHANGELOG.md`.
5. Run:

   ```bash
   python3 scripts/validate_repository.py --strict
   python3 scripts/validate_release.py
   python3 -m unittest discover -s tests -v
   python3 scripts/build_manifest.py --check
   python3 scripts/build_release.py --clean
   ```

6. Inspect the generated ZIP, tar.gz, and `dist/SHA256SUMS`.
   Verify the checksums locally with `sha256sum -c dist/SHA256SUMS` from the
   `dist/` directory, or an equivalent SHA-256 tool.
7. Open a release PR and let CI pass on all supported operating systems.
8. Merge to `main`.
9. Run the **Release** workflow with `v<version>`, or push the matching tag.
10. Verify the GitHub release, assets, checksums, and build-provenance attestation.
11. Smoke-test both installation paths:

    ```bash
    npx skills add mfarzanansari/praxis-workflow-os --list
    ```

    Install into a disposable target with:

    ```bash
    python3 scripts/install.py --target <temporary-directory>
    python3 scripts/validate_repository.py --skills-root <temporary-directory> --strict
    ```

    ```text
    /plugin marketplace add mfarzanansari/praxis-workflow-os
    /plugin install praxis@praxis-workflow-os
    ```

12. Publish migration notes and cross-project compatibility notes where relevant.

## Version policy

- **MAJOR:** incompatible workflow contract, schema, safety boundary, or removed public capability.
- **MINOR:** compatible new skill, profile field, script, integration, or substantial behavior.
- **PATCH:** compatible bug fix, documentation, validation, example, or non-semantic refinement.

## Rollback

Never rewrite an existing public release. Publish a corrective patch or revert in a new version. Keep prior tags and release assets available unless removal is necessary for security.
