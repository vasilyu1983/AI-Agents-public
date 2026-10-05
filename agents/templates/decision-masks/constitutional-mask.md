---
name: Constitutional Mask
mask_id: 7
layer: per-agent
status: stable
last_verified: 2026-05-01
sources:
  - https://arxiv.org/abs/2212.08073
---

# Constitutional Mask — Self-Critique Against a Principles List

Decorates a single agent's brief with a two-pass self-critique loop:

1. **Draft pass** — produce the answer normally.
2. **Critique pass** — re-read the draft against an explicit principles list. For each principle, flag where the draft violates or under-honors it.
3. **Revise pass** — rewrite the draft incorporating the critique.

Output is the revised draft + a short critique log (which principles were tightened, which were already met).

Source: Anthropic's *Constitutional AI* method, adapted for per-agent decoration in a multi-agent team.

## When to Use

- Single-agent reviewers operating on a brief that has explicit non-negotiables (security, compliance, accessibility, brand voice).
- Solo agents whose output ships without a debate round behind it (no second voice to push back).
- Critic / red-team / risk-reviewer roles where missing a principle is the primary failure mode.
- Any agent whose role description ends with "...and must comply with X, Y, Z."

## When NOT to Use

- Inside a debate team. The debate already provides external critique — adding self-critique on top inflates tokens for marginal gain.
- Generative / brainstorming roles. Constitutional mask suppresses risk-taking; use Inversion or First-Principles instead.
- When the principles list is implicit or fuzzy. Self-critique against vague principles produces vague critiques.

## Authoring the Principles List

Keep it short and behavioral, not aspirational. Each principle is a checkable statement:

```text
PRINCIPLES:
1. Never recommend an action that requires escalated permissions without flagging the escalation.
2. Cite the file and line for every code claim.
3. Distinguish "I observed" from "I infer" in the verdict.
4. Surface uncertainty rather than guess (e.g., "I do not know X — should I check Y?").
5. Match the user's stated jurisdiction (UK by default for this user).
```

5-10 principles. More than 10 means the critic gets distracted; the agent ignores the tail.

## How It Plugs Into a Brief

```markdown
### Constitutional Mask

You operate in two passes.

**Pass 1 — Draft.** Produce your normal output.

**Pass 2 — Critique.** Re-read your draft against:
1. [principle 1]
2. [principle 2]
...

For each principle, answer: did the draft honor it? If no, mark the violation.

**Pass 3 — Revise.** Rewrite the draft to fix the violations. Output:
- The revised draft (primary output).
- A short critique log: principles tightened vs already met.
```

## Composition

- **Pairs with G13 (Reasoning-Tree Audit)** — critic role uses Constitutional mask; auditor checks the revision against the principles.
- **Pairs with G11 (Prediction Market)** — confidence stake forces the revise pass to be honest; "I'm 0.95 confident" after a vague critique is a red flag.
- **Stacks under any reviewer member** in `agents/claude/` — drop the mask block into the Inline Brief.
- **Conflicts with Inversion mask** — constitutional reins in, inversion provokes. Pick one per agent.

## Anti-Patterns

- **Principle bloat.** 20-principle constitutions get scanned, not honored. Cap at 10.
- **Aspirational principles.** "Be helpful" is unfalsifiable. Use "If the user's request is ambiguous, ask one clarifying question before proceeding."
- **Skipping the revise pass.** Some agents emit critique without revision. The mask requires both — verify the revised draft differs from the original.
- **Self-sycophancy.** Agents that score themselves "9/10 on every principle" are not critiquing. Force at least one flagged violation per pass; if the draft truly is clean, log "no violations found, here's why" with concrete evidence.

## Calibration

Audit 10 outputs: did the revise pass meaningfully change the draft? If 9/10 are unchanged, the principles are too easy or the agent is gaming. Tighten principles or add a verification game (e.g., a separate auditor agent grades the critique log).

## Sources

- arxiv 2212.08073 — *Constitutional AI: Harmlessness from AI Feedback* (Anthropic, 2022). Foundational paper.
- Anthropic's Constitutional Classifiers and downstream work establish the self-critique → revise loop as a robust per-agent pattern.
