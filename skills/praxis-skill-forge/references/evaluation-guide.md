# Evaluation guide

## Separate the questions

1. **Selection:** Did the skill trigger when it should and stay quiet when it should not?
2. **Behavior:** Did the skill change the process in the intended way?
3. **Output:** Did the deliverable meet objective and subjective quality criteria?
4. **Efficiency:** Did time, tokens, tool calls, or human effort improve acceptably?
5. **Safety:** Did gates and permissions hold under pressure?
6. **Generalization:** Does improvement survive novel examples and held-out tests?
7. **Maintenance:** Is the benefit worth catalog, reference, and dependency cost?

## Baseline designs

- New skill: compare with no skill.
- Revised skill: compare with the previous released version.
- Description change: keep body constant and compare trigger behavior.
- Script addition: compare deterministic correctness and trace repetition.

## Variance

Run multiple repetitions when model behavior matters. A change that improves the mean but produces unstable interpretation may not be ready. Report distributions or at least pass count, duration range, and qualitative variance.

## Human review

Blind comparison is useful for subjective outputs. Hide which version produced each artifact, ask the reviewer to select the stronger output and explain why, then convert repeated preferences into clearer criteria when possible.
