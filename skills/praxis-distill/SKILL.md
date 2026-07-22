---
name: praxis-distill
description: Use when completed work, research, a meeting, a decision, an agent session, a correction, or a project checkpoint may contain reusable knowledge worth preserving in Obsidian. Use to decide what deserves a research note, decision record, memory note, prompt, project-state update, or workflow-review entry without dumping raw transcripts.
license: MIT
compatibility: File access required. Python 3.9+ recommended for non-overwriting note creation.
metadata:
  author: Farzan Ansari
  version: "1.0.0"
  category: knowledge
---

# Praxis Distill

## Core principle

Durable knowledge is **future decision support**, not an activity log. Preserve only residue likely to change how someone understands, decides, executes, verifies, or resumes work later.

“Nothing worth preserving” is a valid and often correct result.

Changing facts are never durable as bare values. A price, version, policy, role, schedule, market fact, or similar claim must carry its source, an `as of` date, and an explicit review date or expiry condition. If any of those are unavailable, preserve the item only as an unresolved claim or omit it.

## Distillation threshold

Create a durable note when at least one is true:

- the evidence or synthesis is likely to be reused;
- a consequential decision has alternatives, rationale, or reversal conditions;
- a lesson generalizes beyond the immediate task;
- a repeated workflow has stable inputs, outputs, and quality gates;
- project state is needed to resume or hand off accurately;
- workflow evidence supports a future system change.

Do not create a durable note for:

- a raw transcript;
- a trivial preference;
- temporary chatter;
- duplicated information with no stronger synthesis;
- unverified claims presented as fact;
- sensitive material outside the approved retention policy.

## Classification

| Type | Use when | Default folder |
|---|---|---|
| Research | evidence, sources, and synthesis may support future work | `Research/` |
| Decision | a consequential choice was made among alternatives | `Decision Records/` |
| Memory | a reusable lesson, trap, doctrine, or verified setup emerged | `Memory/` |
| Prompt | a workflow has become stable and reusable | `Prompts/` |
| Project state | another session/person needs current project truth | approved project folder |
| Workflow review | evidence may justify changing the system | `Reviews/` |

When one event produces several note types, separate them only when each has a distinct retrieval purpose. Prefer one strong note over six fragments.

## Procedure

### 1. Gather residue

Review:

- deliverable and execution brief;
- sources and freshness;
- decisions and alternatives;
- corrections and quality failures;
- verification evidence;
- unresolved risks;
- likely future retrieval questions.

### 2. Apply the future-use test

For each candidate, answer:

1. Who will look for this?
2. In what future situation?
3. What decision or action will it change?
4. What evidence and limits must travel with it?
5. Is an existing note a better destination?

Discard candidates without a credible retrieval situation.

### 3. Select the note contract

Use [references/note-contracts.md](references/note-contracts.md). Every note should include, where relevant:

- type and status;
- created/updated dates;
- provenance and source links;
- confidence;
- scope and non-applicability;
- review or expiry date;
- links to related MOCs, projects, and decisions.

### 4. Create safely

Preview a note shell:

```bash
python scripts/create_note.py \
  --vault /path/to/vault \
  --type memory \
  --title "Use the primitive, do not hand-roll it" \
  --dry-run
```

Create it:

```bash
python scripts/create_note.py \
  --vault /path/to/vault \
  --type memory \
  --title "Use the primitive, do not hand-roll it" \
  --source "project:retell" \
  --source "session:2026-07-22"
```

The script never overwrites. If a likely duplicate exists, inspect and update the existing note manually after review.

### 5. Write synthesis, not chronology

Lead with the reusable conclusion. Include only enough context to understand why it is true and when it applies.

Good memory shape:

```markdown
# Use the Primitive, Do Not Hand-Roll It

## Reusable lesson
Use the substrate's built-in primitive when it already owns lifecycle,
concurrency, persistence, or cleanup.

## Applies when
...

## Evidence
...

## Failure modes
...
```

Weak shape:

```markdown
First I asked the agent to do X, then it tried Y, then I said Z...
```

### 6. Verify the note

Before writing, check:

- Is the title a likely retrieval phrase?
- Does the note separate fact, inference, and recommendation?
- Can the source be found again?
- Are version and freshness limits visible?
- Is sensitive content permitted?
- Does this duplicate an existing note?
- Are links useful rather than decorative?

## Existing-note preference

When an existing note has the same retrieval purpose:

1. inspect it;
2. decide whether the new residue confirms, refines, contradicts, or supersedes it;
3. update with date and provenance after review;
4. preserve disagreement rather than silently rewriting history;
5. create a new note only when the concept or scope is genuinely distinct.

## Confidence and expiry

Use confidence labels intentionally:

- `verified` — directly tested or confirmed by authoritative evidence;
- `high` — strong converging evidence;
- `medium` — useful but incomplete;
- `low` — hypothesis worth retaining only with warning;
- `unknown` — shell or unresolved item.

Add a review/expiry date for software versions, market data, policies, personnel, prices, regulations, schedules, and other changing facts.

## Completion output

Report:

- candidates considered;
- candidates discarded and why;
- notes created or updated;
- confidence and freshness limits;
- links added;
- unresolved items intentionally not promoted to durable knowledge.

## Common mistakes

| Mistake | Correction |
|---|---|
| Saving the whole session | Preserve only future-useful synthesis. |
| Turning every correction into memory | Require recurrence or meaningful generalization. |
| Removing uncertainty | Record confidence, scope, and disagreement. |
| New note for every thought | Update an existing note when retrieval purpose matches. |
| Time-sensitive fact with no review date | Add version/freshness metadata. |
| Project status stored as universal memory | Put current truth in project state. |
