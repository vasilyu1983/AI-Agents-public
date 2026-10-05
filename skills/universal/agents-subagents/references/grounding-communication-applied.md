---
description: Proportionate grounding and authority checks for agent handoffs.
last_verified: 2026-09-24
status: stable
---

# Grounding & Communication Applied to Agent Orchestration

> **Selective gate**: Use the [foundation](../../foundations-grounding-communication/SKILL.md) only when a load-bearing understanding gap can change the decision; otherwise keep the applied owner and proceed within existing authority.

Common ground, grounding criterion, evidence of understanding, repair, presupposition and audience design are explained in the foundation's [primitives overview](../../foundations-grounding-communication/references/primitives-overview.md), and the handoff fields are in its [handoff-state contract](../../foundations-grounding-communication/references/handoff-state-contract.md). A failure taxonomy describes categories, not how well an intervention works. Measure any benefit on paired local tasks with independent grading, latency and repair cost.

## Decision rules

1. **Scale the understanding check to what the action can break.** For clear, authorized, reversible work, state the interpretation and proceed with an inspectable first artifact. Before a consequential action, resolve only the ambiguity or missing authority that could change it. "Got it" confirms receipt, not understanding. For irreversible work, require a demonstration (paraphrase plus plan plus sample output). A paraphrase, a panel vote or silence never grants authority that is missing, and it never revokes explicit authority that exists.
2. **Audit presuppositions before dispatch, then cold-read.** For every "the X", pronoun and shorthand, check that exactly one referent is recoverable from the subagent's context, not yours. Then read the brief as the recipient, or have a differently prompted agent read it cold. If its interpretation differs from your intent, rewrite the brief rather than adding explanations. Tailor briefs per recipient when tools, prompts or providers differ.
3. **Give workers an explicit, low-cost repair channel.** Use a named tool with 2–4 candidate interpretations and a blocking flag. Treat a specific question as neutral or positive in completion metrics. More than one use per major step on routine work means the briefs are underspecified: fix the briefs, don't penalize the agent.
4. **Re-ground at every compression boundary.** Put the load-bearing decisions, constraints, in-progress items and open questions at the top of the compressed context. Raise the grounding criterion for the next 3–5 turns: verify a fact before any irreversible action that relies on it.

## Worked recipe — repair tool and post-compression block

```yaml
name: ask_clarification
description: Use when proceeding on your current reading risks a wrong action. A specific question is a good outcome, not a failure.
parameters:
  question: { type: string, description: The specific clarification needed. }
  options:  { type: array,  description: The 2–4 interpretations you are choosing between. If you can't list them, the question isn't specific yet. }
  blocking: { type: boolean, description: true = wait; false = continue on best guess and flag the assumption. }
  why:      { type: string, description: Missing antecedent, ambiguous reference, missing authority, etc. }
```

```text
## Load-bearing context (post-compression)
Decisions:    <decision> (because <rationale>)
Constraints:  <constraint> (source: <where>)
In progress:  <task> (status: accepted | open)
Open:         <question> (best guess: <X>, confidence: low | med | high)
```

Example: an authorized auth-module draft leaves OAuth vs. SAML unresolved. The worker sends a blocking `ask_clarification` on that choice only, keeps inspecting the unaffected tests, and propagates the answer to dependent workers. Draft authority stays valid, and release authority is a separate grant.

## Related

- [clarification-questions-protocol.md](clarification-questions-protocol.md): user-to-agent clarification.
- [initial-prompt-contract.md](initial-prompt-contract.md): brief design.
- [team-theory-applied.md](team-theory-applied.md): *whether* to open a channel. This file covers how to ground meaning once it exists.
- Primary sources: Clark & Brennan (1991); Clark (1996); Clark & Schaefer (1989), all cited in the foundation.
