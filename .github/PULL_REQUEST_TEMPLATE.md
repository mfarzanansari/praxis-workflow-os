## Problem and evidence

What observed behavior, issue, or maintenance problem motivates this change?

## Change

What mechanism changed, and why is it the smallest appropriate intervention?

## Before / after

Describe observable behavior before and after. Include baseline output or traces for material skill changes.

## Validation

- [ ] `python scripts/validate_release.py`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `python scripts/build_manifest.py --check`
- [ ] Relevant model-level evals or human comparative review
- [ ] Near-miss trigger tests for description changes

## Safety, compatibility, and migration

Describe filesystem effects, permissions, network behavior, dependencies, private-data handling, client compatibility, version impact, migration, and rollback. Write “none” where appropriate.

## Documentation and release

- [ ] Documentation updated
- [ ] Evals/tests updated
- [ ] Version decision recorded
- [ ] Changelog/release notes updated when user-visible
- [ ] Provenance and licenses recorded for adapted material
