---
name: praxis-skill-forge
description: Use when creating, adapting, testing, packaging, maintaining, auditing, or deprecating an Agent Skill, especially after a recurring workflow failure, repeated correction, missed trigger, false trigger, duplicated helper script, stale reference, or need to convert proven expertise into reusable procedural guidance.
license: MIT
compatibility: Agent Skills folder format. Python 3.9+ supports scaffold and validation scripts; model-level evals require the target agent/client.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: skill-engineering
---

# Praxis Skill Forge

## Core principle

A skill is **tested workflow software expressed through instructions, references, and deterministic tools**. Create one only when real evidence shows that reusable procedural guidance can improve future behavior.

The governing loop is:

```text
Observe need → reproduce baseline failure → classify failure → draft minimum skill
→ test with skill → compare → human review → refine → release → monitor
```

## When a skill is justified

Create or revise a skill when at least one is demonstrated:

- a non-obvious technique recurs across tasks;
- the person repeats the same correction;
- an agent violates a consequential rule under realistic pressure;
- outputs repeatedly omit or mis-shape required elements;
- the same deterministic helper is reinvented across runs;
- a domain reference must be bundled with clear version constraints;
- a recurring work stream has stable triggers, judgment, deliverables, and verification.

Do not create a skill for:

- a one-off task;
- project-specific facts better placed in project instructions or state;
- a mechanical constraint better enforced by a validator/script;
- generic advice already handled well without the skill;
- a profession persona with no bounded workflow;
- an untested collection of “best practices.”

## Response gates

Before drafting or accepting the requested remedy, classify the observed failure and make the next evidence requirement explicit:

| Request or evidence | Required response |
|---|---|
| “Make a skill” without real examples | Ask for representative inputs, expected outputs, concrete failures/corrections, and constraints; define a no-skill baseline and with-skill eval portfolio before calling it finished. |
| Output omitted a field or used the wrong shape | Require the field in a positive output contract or structural template and test it; do not turn the symptom into a pile of `NEVER` rules. |
| A third-party skill is popular | Treat popularity only as discovery. Before adaptation, enumerate author and license provenance; pin the version; inspect all scripts, dependencies, network calls, permissions, secret handling, and destructive behavior; then reproduce the benefit with a local baseline and with-skill eval. |
| Provided examples all pass | State that copied examples are insufficient. Add varied held-out prompts, near-miss and regression cases, and repeated runs on the target client/model to expose memorization and model variance. |

Do not let urgency or a requested output count waive these gates. A useful answer may provide an evaluation plan or minimum positive contract, but must not represent an unevaluated skill as complete.

The next-turn response must make the correction observable:

- for an omission or output-shape failure, name that classification and explicitly decline a requested prohibition pile before giving the positive required field or template;
- for third-party adaptation, do not compress the gate into “security review.” Explicitly name the pinned version, author and license, scripts and dependencies, network access, permissions and secret handling, destructive behavior, and local baseline/with-skill evaluation;
- for copied examples, explicitly require held-out variation, near-miss trigger tests, regression checks, and repeated target-model/client runs to measure variance.

## Phase 1 — capture intent and provenance

Before authoring, record:

- user outcome;
- trigger situations and near misses;
- expected output or behavior;
- domain evidence and representative examples;
- corrections, failures, and constraints;
- tools, versions, permissions, and network needs;
- author/source/license of adapted material;
- what would prove the skill unnecessary or harmful.

Inspect existing artifacts and execution traces before interviewing. Ask one unresolved question at a time.

## Phase 2 — RED: establish the baseline

**Do not write or revise the skill until a baseline test demonstrates the target problem.**

Choose tests by skill type:

| Skill type | Baseline tests |
|---|---|
| Discipline / safety | pressure scenarios combining urgency, authority, sunk cost, and fatigue |
| Technique | novel application, variation, and missing-information cases |
| Output-shaping | examples where output naturally takes the wrong form or omits fields |
| Reference | retrieval, correct application, version/compatibility, and gap tests |
| Router / trigger | realistic should-trigger and near-miss should-not-trigger prompts |

Record the exact failure and any rationalization. If the no-skill baseline already succeeds reliably, do not author a skill; improve tooling, context, or measurement instead.

## Phase 3 — classify the failure

The intervention must match the observed failure:

| Baseline failure | Write this | Avoid this |
|---|---|---|
| Knows a rule but skips it under pressure | hard gate, red flags, explicit loophole counters | vague “prefer” language |
| Produces the wrong shape | positive output contract or recipe | long prohibition list |
| Omits a required element | structural required field/template | reminder buried in prose |
| Behavior varies by condition | rule keyed to an observable predicate | unconditional rule with fuzzy exceptions |
| Repeats deterministic mechanics | bundled script and unit tests | asking the model to reinvent code |
| Lacks domain facts | concise versioned reference | timeless claims about changing systems |
| Selects the wrong skill | narrow trigger description and routing tests | broad keyword stuffing |

## Phase 4 — scaffold the skill

```bash
python scripts/scaffold_skill.py \
  --root ./skills \
  --name example-skill \
  --description "Use when ..." \
  --type technique \
  --with-scripts \
  --with-references
```

The canonical structure is:

```text
example-skill/
├── SKILL.md
├── evals/evals.json
├── scripts/       # only when justified
├── references/    # only when justified
└── assets/        # only when output needs reusable assets
```

## Phase 5 — write the minimum effective skill

### Metadata

- Name uses lowercase letters, numbers, and hyphens; it matches the folder.
- Description clearly states what the skill does **and when to use it**, using realistic user intent and relevant keywords.
- Keep the description concise enough for the always-loaded catalog.
- Add license, compatibility, version, author, and provenance metadata where useful.

### Body

Prefer this shape:

```markdown
# Skill title
## Core principle
## Inputs / preconditions
## Procedure
## Output or behavior contract
## Decision points and approval gates
## Failure modes / common mistakes
## Available scripts and references
## Completion criteria
```

Explain the reason behind judgment rules. Use hard prohibitions only when baseline tests show deliberate rule-skipping or safety risk.

### Progressive disclosure

- Keep `SKILL.md` focused and ideally below 500 lines / 5000 tokens.
- Move heavy domain material to `references/`.
- Put repeatable deterministic logic in `scripts/`.
- Use relative paths and shallow references.
- Do not force-load a web of unrelated documents.

### Scripts

Bundle a script when multiple traces independently reinvent the same deterministic operation or when correctness requires machine enforcement.

Every bundled script should:

- be non-interactive;
- support `--help`;
- validate inputs;
- use structured stdout and diagnostics on stderr;
- have safe, idempotent defaults;
- support `--dry-run` for stateful/destructive work;
- use meaningful exit codes;
- avoid network access unless explicitly required and documented;
- have unit tests;
- avoid secrets in arguments, output, or generated files.

## Optional model-specific prompt materialization

A skill contract and a model-specific execution prompt are different artifacts. First stabilize the skill's trigger, intent, inputs, output contract, gates, and tests. Only then, when a named target model is known, optionally hand the bounded execution prompt to the standalone `prompt-polish` skill.

Prompt Polish may reduce noise and adapt wording to the target model. It must not change the task, add deliverables, replace skill evals, or override Praxis safety and approval gates. Keep the integration optional and independently versioned.

## Phase 6 — create the eval portfolio

Start with 2–5 realistic task prompts, then expand after the skill works.

Save to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "A realistic request with context and constraints",
      "expected_output": "Observable behavior or artifact characteristics",
      "files": [],
      "assertions": []
    }
  ]
}
```

Include:

- representative success case;
- edge/variation case;
- missing-information case;
- pressure case when a hard gate matters;
- should-trigger and near-miss negative trigger cases;
- regression case from a real past failure.

Assertions should be objective where possible. Use human comparative review for aesthetics, tone, strategic quality, and other irreducibly subjective outcomes.

## Phase 7 — GREEN: run with-skill comparison

Run baseline and with-skill tests under comparable conditions. When supported, launch them in the same batch to reduce environmental drift.

Capture:

- final outputs;
- execution traces;
- assertion results;
- human feedback;
- duration, token/cost, and variance where available;
- new failure modes or rationalizations.

For deterministic assertions, use a script rather than visual inspection.

## Phase 8 — REFACTOR without overfitting

Read traces, not only final outputs.

- Remove instructions that cause unproductive work.
- Generalize from the feedback instead of patching only the example.
- Add a script when repeated helper creation is visible.
- Tighten a trigger only with positive and near-miss tests.
- Add a hard gate only when pressure tests justify it.
- Keep one excellent example rather than many mediocre examples.
- Re-run the complete regression set after each material change.

Stop when:

- the person approves outputs;
- assertions and non-regressions pass reliably;
- feedback is empty or low-value;
- further changes do not produce meaningful improvement.

## Phase 9 — validate and release

Run:

```bash
python scripts/validate_skill.py path/to/example-skill
```

Release checklist:

- baseline evidence exists;
- trigger tests include near-miss negatives;
- skill improves the intended behavior;
- scripts have unit tests and safe defaults;
- references state version/freshness;
- permissions and network behavior are explicit;
- provenance and license are recorded;
- semantic version and changelog are updated;
- rollback or prior version is available;
- third-party content has been security-reviewed.

## Third-party adaptation

Popularity, stars, shares, and installs are discovery signals—not proof of quality or safety.

Before adapting a skill:

1. pin the repository and commit/version;
2. record author and license;
3. inspect the full folder, not only `SKILL.md`;
4. review descriptions for selection manipulation;
5. inspect scripts, dependencies, network calls, permissions, secrets, and destructive actions;
6. identify version-specific guidance;
7. reproduce the claimed benefit in the local workflow;
8. rewrite or narrow the skill to the person's context;
9. keep a provenance record and update path.

Use [references/security-review.md](references/security-review.md).

## Description optimization

A skill only helps when selected correctly.

Build 16–24 realistic queries:

- half should trigger;
- half should be near-miss negatives;
- include casual language, typos, file paths, project context, and cases that compete with adjacent skills;
- avoid trivially irrelevant negatives.

Test multiple repetitions on the target client/model. Select the description by held-out performance, not by memorizing the training examples.

## Maintenance

At each review:

- check usage and false triggers;
- inspect version-sensitive references;
- compare outputs with current acceptance tests;
- remove duplication;
- deprecate skills that do not justify catalog cost;
- review third-party provenance and dependency changes;
- update semantic version and changelog.

## Red flags — stop and investigate

- no baseline failure exists;
- the skill is primarily a persona or inspirational essay;
- the description promises behavior not present in the folder;
- a script installs packages or calls the network without explicit need;
- credentials, tokens, or private data appear in examples;
- a broad skill competes with several existing skills;
- guidance assumes a product version that is not recorded;
- tests all mirror the exact examples in the skill;
- the only quality evidence is stars or social sharing;
- a change is being released without rerunning regressions.

## Completion contract

A skill is complete only when it has:

- a justified scope;
- baseline and with-skill evidence;
- a valid, concise folder;
- realistic evals and non-regressions;
- reviewed scripts/references;
- provenance, version, and rollback;
- human approval for release.
