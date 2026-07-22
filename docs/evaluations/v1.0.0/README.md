# v1.0.0 model evaluation

## Release conclusion

Praxis v1.0.0 passed its repository, security, deterministic-script, and behavior-remediation gates. Automatic skill selection remains an observed limitation: the final three-run trigger portfolio passed 275 of 336 runs (81.8%) in a crowded Codex catalog. The release records that limitation and tracks improvement publicly.

The methodology follows the Agent Skills guidance to compare with and without the skill, use objective assertions, test near misses, preserve execution evidence, and repeat trigger trials on the target client. See the [evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) and [description-optimization guide](https://agentskills.io/skill-creation/optimizing-descriptions).

## Environment

| Field | Value |
|---|---|
| Date | 2026-07-22 |
| Client | Codex CLI 0.144.6 |
| Model | `gpt-5.6-terra` |
| Filesystem | Fresh ephemeral workspaces; read-only sandbox |
| Network and external actions | Prohibited by each evaluation prompt |
| Target package | Local native Codex plugin, version 1.0.0 |
| Trigger repetitions | 3 per query |
| Trigger portfolio | 112 queries: 56 positive and 56 near-miss negative |

## Behavior assertions

Twenty-three cases contain 70 objective assertions. The first comparable portfolio ran every case once without the plugin and once with the explicitly loaded target skill. A strict schema-constrained grader passed an assertion only when the output explicitly and materially supported it; implicit or vague support failed.

| Skill | No-skill baseline | Initial with skill | Latest passing traces |
|---|---:|---:|---:|
| `praxis` | 5/8 | 8/8 | 8/8 |
| `praxis-blueprint` | 1/6 | 2/6 | 6/6 |
| `praxis-distill` | 3/9 | 8/9 | 9/9 |
| `praxis-interview` | 5/12 | 7/12 | 12/12 |
| `praxis-retrospective` | 3/9 | 8/9 | 9/9 |
| `praxis-setup` | 2/9 | 7/9 | 9/9 |
| `praxis-skill-forge` | 0/17 | 5/17 | 17/17 |
| **Total** | **19/70 (27.1%)** | **45/70 (64.3%)** | **70/70 (100%)** |

“Latest passing traces” is intentionally precise: failed cases were changed and rerun in focused refinement rounds, preserving the original results. It is not represented as three independent 70/70 full-portfolio runs.

Valid behavior evidence comprised 66 model executions and five strict grading passes. Cumulative model-execution duration was 1,653,974 ms, with 3,773,750 input tokens and 59,891 output tokens. Invalid harness attempts were quarantined and excluded: two isolation/configuration attempts and one iteration that loaded a stale plugin cache.

## Trigger selection

Each of seven skills has eight realistic positive queries and eight adjacent near-miss negatives. Every query ran three times without explicitly naming the target skill. A run passed only when Codex actually loaded the target `SKILL.md` for a positive or did not load it for a negative.

| Skill | All runs | Positive recall | Negative specificity |
|---|---:|---:|---:|
| `praxis` | 44/48 | 20/24 | 24/24 |
| `praxis-blueprint` | 40/48 | 22/24 | 18/24 |
| `praxis-distill` | 37/48 | 20/24 | 17/24 |
| `praxis-interview` | 35/48 | 21/24 | 14/24 |
| `praxis-retrospective` | 42/48 | 22/24 | 20/24 |
| `praxis-setup` | 41/48 | 18/24 | 23/24 |
| `praxis-skill-forge` | 36/48 | 18/24 | 18/24 |
| **Total** | **275/336 (81.8%)** | **141/168 (83.9%)** | **134/168 (79.8%)** |

All 336 client runs exited successfully. Cumulative model-execution duration was 8,496,500 ms, with 20,864,198 input tokens and 293,136 output tokens. The query portfolios are versioned beside each skill in `evals/trigger_queries.json`.

Observed failure clusters:

- adjacent lifecycle skills sometimes co-loaded for architecture, retrospective, and skill-maintenance requests;
- `praxis-interview` over-selected for customer-interview summarization and other lifecycle requests;
- `praxis-distill` missed a changing API-limit query and over-selected for architecture and retrospective requests;
- `praxis-setup` missed several safe installation phrasings;
- `praxis-skill-forge` over-selected for normal use of an installed skill and operational skill-removal reviews;
- the root `praxis` router occasionally lost to a specialized lifecycle skill or no skill.

## Client warnings and limits

Codex reported that skill descriptions were shortened to fit the client's 2% skills-context budget. Runs also emitted non-fatal client warnings about model-cache schema, state-database fallback, file watching, shell-snapshot cleanup, and plugin skill-metric tag characters. No evaluation run failed because of these warnings, but catalog pressure is a plausible contributor to model selection variance.

Claude Code plugin structure validation passed. The attempted Claude model behavior run returned organization-policy error `oauth_org_not_allowed`; the release does not substitute Codex results for missing Claude evidence.

## Reproduce

The release contains the assertion and trigger inputs. Model-level results can vary with client, model, installed catalog, permissions, and time. Reproduction therefore requires recording those fields and must not overwrite this point-in-time report.

Deterministic repository gates:

```bash
python3 scripts/validate_repository.py --strict
python3 scripts/validate_release.py
python3 -m unittest discover -s tests -v
```

## Release interpretation

The behavior evidence supports publishing the v1 workflow contracts and safe deterministic tooling. The trigger evidence does not support claiming perfect automatic routing. v1.0.0 is released with the measured routing limitation disclosed and with follow-up work scoped as public issues.
