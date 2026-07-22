# Workflow diagnosis guide

## Trigger problem

Evidence:

- should-trigger prompt did not load the skill;
- adjacent prompt loaded it incorrectly;
- agent followed a short description shortcut rather than the full skill.

Action:

- rewrite description around user intent and concrete contexts;
- remove workflow details from the description when they encourage shortcuts;
- add realistic positive and near-miss negative queries;
- test several repetitions on the actual target client/model.

## Procedure problem

Evidence:

- skill triggers correctly but output is wrong;
- agent wanders through multiple approaches;
- required judgment or gate is absent.

Action:

- inspect traces;
- identify baseline failure type;
- choose positive contract, structural field, conditional, or hard gate accordingly;
- remove instructions that do not pull their weight.

## Reference problem

Evidence:

- fact, API, version, law, policy, price, or tool behavior is wrong;
- skill works in one environment and fails in another.

Action:

- use authoritative version-pinned sources;
- state compatibility and review date;
- separate general doctrine from volatile reference data.

## Script opportunity

Evidence:

- different runs independently generate the same parser, formatter, validator, scaffold, or aggregation code;
- human error occurs in a mechanical step;
- output must be machine-readable and repeatable.

Action:

- bundle a minimal non-interactive script;
- add `--help`, structured stdout, diagnostics on stderr, safe defaults, dry-run, and unit tests.

## Knowledge problem

Evidence:

- useful information was not written;
- written notes were never found;
- stale notes overrode current truth;
- raw transcript volume obscures synthesis.

Action:

- adjust write threshold, titles, provenance, expiry, MOCs, or source-of-truth rules;
- do not compensate by loading the entire vault.
