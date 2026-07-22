---
name: praxis-interview
description: Use when a person wants an AI workflow, personal operating system, customized skills, Obsidian system, SOP architecture, or better way of working and the system must first understand their outcomes, work streams, judgment, tools, constraints, accessibility, risks, and memory needs. Also use when auditing an existing workflow before redesign.
license: MIT
compatibility: File access required for durable profile state. Python 3.9+ recommended for scripts.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: discovery
---

# Praxis Interview

## Outcome

Produce an evidence-grounded `praxis/profile.json` that is detailed enough to design the person's initial workflow system without pretending every future detail is known.

The interview is a **guided design conversation**, not a questionnaire dump.

## Non-negotiable interview discipline

1. **Inspect before asking.** Read available notes, folders, examples, calendars, SOPs, project files, prompts, and prior corrections when access is available.
2. **Ask one consequential question per turn.** Never bundle a list for the user's convenience; bundled questions reduce answer quality and hide dependencies.
3. **Explain the decision.** State in one sentence why the answer changes the architecture.
4. **Recommend an answer.** Use current evidence to give a default and rationale. The person can accept, edit, reject, defer, or say unknown.
5. **Walk dependencies depth-first.** Finish the branch needed for a decision before opening an unrelated branch.
6. **Separate evidence states.** Record answers as `confirmed`, `inferred`, `deferred`, or `disputed` with source and confidence.
7. **Do not force false precision.** Unknown is valid; record consequence and resolution method.
8. **Stop at sufficient understanding.** The purpose is a high-value first architecture, not an exhaustive biography.

## Start

1. Extract all usable facts from the conversation and artifacts.
2. Select interview depth:
   - `quick`: 10–14 consequential decisions;
   - `standard`: 20–30 decisions; recommended default;
   - `deep`: 35+ decisions with separate branches for major work streams.
3. Initialize durable state:

```bash
python scripts/interview_state.py start --workspace praxis --depth standard
```

4. Record evidence-derived facts before asking questions. Mark them `inferred` until confirmed.
5. Ask the first unresolved, architecture-changing question.

## Per-turn pattern

Use this compact structure:

```text
Q[resolved/estimated]: [one question]
Why it matters: [architectural consequence]
Recommended answer: [specific default] — [brief rationale]

[2–4 options when useful, including “something else” or “defer”]
```

After the person answers:

1. reflect the answer in one sentence;
2. surface a contradiction only when it affects the design;
3. persist the decision;
4. ask the next dependent question.

Example persistence:

```bash
python scripts/interview_state.py record \
  --workspace praxis \
  --question-id outcomes.primary \
  --question "What should this system improve first?" \
  --path outcomes.primary \
  --value '"Reduce repeated context assembly and preserve reusable lessons"' \
  --state confirmed \
  --source user
```

For list items:

```bash
python scripts/interview_state.py append \
  --workspace praxis \
  --path work_streams \
  --value '{"id":"market-research","name":"Market research","frequency":"weekly"}' \
  --state confirmed \
  --source user
```

## Decision tree

Use [references/question-bank.md](references/question-bank.md) selectively. Do not read questions mechanically in order.

### Branch A — consent and system boundary

Resolve first:

- What artifacts may the agent inspect?
- What data must never leave the local environment?
- What may the system create or change?
- How much change can the person realistically adopt now?

### Branch B — outcomes and failure costs

Discover:

- the first observable improvement;
- stakeholders and beneficiaries;
- current pain and workarounds;
- cost of being wrong, late, inconsistent, unsafe, or misunderstood;
- success measures that can be observed in real work.

### Branch C — work streams

Identify recurring units of value, not job-title categories. For each initial work stream resolve:

- trigger and frequency;
- inputs and sources of truth;
- decisions and quality criteria;
- deliverable and audience;
- verification and approval;
- handoff and durable residue.

Start with at most three high-value streams. A bloated first system will not be adopted.

### Branch D — judgment and quality

Ask for real examples and anti-examples. Discover:

- what excellent looks like;
- what is unacceptable even when technically correct;
- recurring corrections the person makes;
- where judgment is tacit, aesthetic, interpersonal, physical, or domain-specific;
- which decisions need alternatives and trade-off explanation.

### Branch E — tools and evidence

Determine:

- current tools and their authoritative roles;
- files, databases, people, and external sources used;
- versions and compatibility constraints;
- collaboration and handoff surfaces;
- what may be automated deterministically.

### Branch F — human constraints

Treat these as architectural requirements, not personal defects:

- attention and energy patterns;
- accessibility needs;
- interruptions and mobile/field conditions;
- deadlines and response expectations;
- language and communication preferences;
- physical, organizational, legal, or safety constraints.

### Branch G — knowledge and memory

Resolve:

- what deserves durable retention;
- source/provenance requirements;
- confidence, expiry, and review rules;
- preferred retrieval paths;
- existing taxonomy worth preserving;
- separation between curated knowledge and runtime memory.

### Branch H — automation boundaries

Classify actions:

- autonomous;
- review before action;
- explicit per-action approval;
- forbidden.

Use reversibility, cost, safety, privacy, legal, reputation, and interpersonal impact—not convenience alone.

### Branch I — adoption and governance

Define:

- first-week rollout;
- review cadence;
- system owner;
- versioning and rollback;
- evidence required for new skills or automations.

## Evidence-first behavior

When a question can be answered by inspecting artifacts, inspect first and ask for confirmation:

```text
I found that your vault already separates Research, Decision Records, Memory,
and Prompts. I recommend preserving that coarse taxonomy and adding only
_meta governance files. Confirm?
```

Do not ask the person to retype information the system can reliably observe.

## Contradictions

When two answers conflict:

1. name the conflict neutrally;
2. explain the architectural consequence;
3. recommend a resolution;
4. resolve it before continuing if downstream decisions depend on it;
5. otherwise mark it `disputed` and place it in open questions.

## Stop rule

The interview may stop when all of these are true:

- consent and privacy boundaries are known;
- one primary outcome is confirmed;
- at least one high-value work stream has a complete primitive chain;
- quality and failure criteria are usable;
- tools and sources of truth are identified;
- knowledge retention and automation boundaries are defined;
- adoption capacity and review cadence are known;
- remaining questions do not change the initial rollout.

Run:

```bash
python scripts/validate_profile.py praxis/profile.json
python scripts/interview_state.py complete --workspace praxis
python scripts/interview_state.py export --workspace praxis
```

If validation fails, ask only the highest-impact missing question.

## Completion output

Report:

- confirmed architecture-changing facts;
- initial work streams;
- human gates and forbidden zones;
- existing practices to preserve;
- open questions and their consequences;
- recommendation to proceed to `praxis-blueprint`.

Do not scaffold files or skills during the interview.

## Failure modes

| Failure | Correction |
|---|---|
| Generic profession checklist | Follow the person's actual work streams. |
| Twenty questions in one turn | One consequential question. |
| “What do you think?” with no guidance | Recommend a default using evidence. |
| Asking what files already show | Inspect, infer, then confirm. |
| Treating accessibility or energy as optional | Encode them as workflow constraints. |
| Interview never ends | Apply the sufficient-understanding stop rule. |
| Assuming Obsidian is runtime memory | Keep curated knowledge and runtime state distinct. |
| Designing while interviewing | Record facts; blueprint after profile confirmation. |
