# Grounding & Communication — Patterns, Scenarios, Traps


Applied patterns and traps for using grounding theory in subagent / multi-agent / human-AI handoff design. Direct translation of Clark's grounding framework to the regimes where modern LLM agents communicate.

## Table of Contents

- [Scenario Patterns](#scenario-patterns)
- [Mapping MAST Failure Modes to Grounding Theory](#mapping-mast-failure-modes-to-grounding-theory)
- [Traps](#traps)
- [Protocol Sketches](#protocol-sketches)
- [Source Quality and Verification](#source-quality-and-verification)

---

## Scenario Patterns

### Brief-to-subagent dispatch

_When_: Orchestrator hands a task to a subagent. The dominant failure surface in modern multi-agent LLM systems.

_Pattern_:
1. Audit common ground (#1) before drafting.
2. Set criterion (#2) by stakes — high for irreversible, low for exploration.
3. Resolve presuppositions (#6); rewrite for the subagent (#7).
4. Require presentation+acceptance (#3): subagent paraphrases brief and plan before executing.
5. Provide repair channel (#5).
6. Compute total cost (#9) — short brief + repair often costs more than long brief + acceptance.

_Watch for_: orchestrators that skip the acceptance step "to save tokens." This is the single most common false economy in agent design.

### Long agent loop with context compression

_When_: Multi-turn agent that runs through harness compression boundaries.

_Pattern_:
- Treat compression boundaries as common-ground decay events (#1).
- Re-establish key facts proactively (#5 self-initiated repair) rather than waiting for failure.
- Tag persistently-needed facts so they survive compression — don't rely on them being in scrollback.
- Raise grounding criterion (#2) immediately after compression.

_Watch for_: agents that confidently act on what they "remember" after a compression event, when the compressed summary may have lost the critical detail.

### User → agent at session start

_When_: User opens a fresh session and writes a request.

_Pattern_:
- Recognize the user's brief is almost always presupposition-rich (#6) — they have full context, the agent has none.
- Apply audience design awareness (#7) in reverse: detect domain shorthand and ask before guessing.
- High grounding criterion (#2) at session start; lower as personal common ground accumulates.

_Watch for_: agents that pattern-match user briefs to nearest training-data analog without verifying.

### Agent → user at session end

_When_: Agent finishes work and reports back.

_Pattern_:
- Apply audience design (#7): the user wants outcomes and risks, not implementation logs.
- Provide demonstration evidence (#4): what changed, what was decided, what was deliberately not done.
- Pre-empt repair (#5): call out specifically where intent might have been misread, lower the cost of catching mistakes.

_Watch for_: agents that report process ("I ran X, then Y") rather than outcome ("the auth flow now supports SSO; I did not change the password reset path").

### Agent ↔ agent peer messaging

_When_: Two subagents exchange intermediate results (the non-classical regime in [foundations-team-theory](../../foundations-team-theory/SKILL.md) #6).

_Pattern_:
- Each peer must establish common ground with the other; the orchestrator's common ground with each is not transitive.
- Acceptance phase (#3) between peers is rare in current agent frameworks — build it explicitly.
- Domain shorthand (#7) between peers is risky — they may have been prompted into different vocabularies.
- Externalize joint state (#1, #8). Over multiple turns, each peer's reconstruction of "what we agreed" drifts. Keep one shared object both write to.
- Tag proposals as exploratory vs. committed (#3, #8). Untagged exploratory proposals get read as commitments, producing the anchoring failure mode.

_Watch for_: orchestrators that assume "I told both agents the same thing, so they share common ground." They share *delivered content*, not common ground. Also watch for symmetric-looking compromises: agents default to equal splits over reward-maximizing coordination, so a tidy 50/50 outcome can be a grounding failure rather than a negotiated result (`DynamicGrounding2026`).

---

## Mapping MAST Failure Modes to Grounding Theory

The MAST taxonomy (Cemri et al. 2025) groups multi-agent LLM failures into system-design issues, inter-agent misalignment, and task-verification gaps. Grounding theory explains the specification and context-loss parts of those categories precisely:

| MAST-style sub-failure | Grounding primitive | Fix |
|---|---|---|
| Disobeying task specification | Presupposition (#6) failed; agent filled in different antecedent | Resolve definite references and pronouns before handoff |
| Step repetition / weak conversation history | Common ground (#1) decay; no shared state of "we already did X" | Persist key state outside context window; re-establish at compression boundaries |
| Information withholding | Audience design (#7) failure — sender assumed shared context that wasn't there | Rewrite for recipient; verify by cold read |
| Disobeying role specification | Common ground about *who-does-what* not established | Explicit role-acceptance phase before work begins |

For information-structure, communication-value, and verification-design failures, see [foundations-team-theory/references/patterns-scenarios-traps.md](../../foundations-team-theory/references/patterns-scenarios-traps.md). Grounding theory specifically addresses shared-meaning failures at the handoff boundary.

---

## Traps

### Trap: System-prompt-as-common-ground

The system prompt has been shown to the agent — but the orchestrator has not verified the agent's interpretation, and the agent hasn't confirmed. Common ground (#1) requires mutual belief, not delivered content. Treating prompt content as common ground is the single most common grounding error.

**Fix**: explicit acceptance phase. Subagent paraphrases the relevant prompt content before acting on it.

### Trap: Acknowledgment ≠ understanding

"Got it" / "ack" / "I'll do that" are weak evidence (#4). They confirm perception of the message, not understanding of it. Strong evidence is demonstration: paraphrase + plan + worked example.

**Fix**: scale evidence requirement to grounding criterion (#2). High-stakes work requires demonstration; routine work can accept acknowledgment.

### Trap: No repair channel

Agents trained on completion incentives default to guessing under uncertainty. Without a low-cost, *rewarded* path to ask for clarification, repair (#5) doesn't happen — failures compound silently until the work product surfaces them at maximum cost.

**Fix**: provide an explicit "ask for clarification" tool. Train (or prompt) the agent to use it when entropy over interpretations is high. Treat its use as a positive signal, not failure.

### Trap: Repair without common-ground update

The correction is delivered, acknowledged, and then not propagated. The agent says "understood, not that file" and proceeds on the rest of its pre-repair model — including whatever else that model got wrong. Repair (#5) was treated as an utterance to be received rather than a common-ground (#1) update to be applied.

This is distinct from "no repair channel": the channel worked, the message landed, the shared state didn't move. Poelitz et al. (2026) observe it directly — models fail to update assumptions after repairs, and joint vocabulary with a partner shrinks over trials where human pairs build it up.

**Fix**: after a correction, require restatement of the revised shared state rather than of the correction. Acknowledging a delta is weak evidence (#4); restating the resulting whole is demonstration.

### Trap: Static grounding mistaken for sustained grounding

An agent interprets the opening brief correctly, so the handoff is judged grounded. Over the next twenty turns the shared plan drifts, references rebind, and early proposals harden into assumed commitments — with no single moment where anything visibly failed.

Grounding a brief is static grounding. Maintaining a joint plan is dynamic grounding, and they come apart: agents that solve a task in isolation still fail as dyads (`DynamicGrounding2026`). Most handoff design and most benchmarks cover only the static case.

**Fix**: externalize joint state to an object both parties read and write; re-bind referents by identity each turn; tag proposals as exploratory or committed; verify convergence by asking each party independently what was agreed.

### Trap: Protocol conformance mistaken for shared meaning

The handoff uses A2A or MCP, the payload validates against its schema, so the integration is treated as sound. Schema validity is syntactic-layer conformance; whether the receiver's interpretation matches the sender's is a semantic-layer question the protocol does not answer (`SemanticProtocols2026`, 18 protocols surveyed).

**Fix**: treat clarification, context alignment, and verification as application responsibilities. A well-typed payload with an unresolved definite reference (#6) inside it is still a presupposition failure.

### Trap: Speaker-effort optimization

Briefs are routinely shortened to save orchestrator tokens. If the saved tokens are smaller than the expected repair cost, this is a net loss. Least collaborative effort (#9) is *joint*, not per-party.

**Fix**: estimate expected total cost = brief tokens + acceptance tokens + p(failure) × repair tokens. Optimize the sum.

### Trap: Audience-blind briefs

Orchestrator writes a brief in their own frame; subagent reads it in a different frame (different system prompt, different context, different vocabulary). Audience design (#7) failure — speaker-centric.

**Fix**: cold-read the brief from the subagent's available state. Better: have a different agent read it cold and report what they understood.

### Trap: Stripping confirmation steps to save tokens

Acceptance phases (#3) and repair channels (#5) cost tokens. Removing them produces a measurable token saving — and an unmeasured failure-rate increase. The hidden cost is the tail: 90% of tasks don't need the acceptance step, but the 10% that do generate disproportionate repair cost.

**Fix**: budget grounding cost (#10) as part of the total task cost. The expected savings rarely exceed the expected failure cost on non-trivial work.

### Trap: Treating grounding as one-shot

Common ground (#1) decays. In a long agent loop, what was grounded 50 turns ago may have been compressed away. Re-grounding is needed; it isn't a one-time setup cost.

**Fix**: re-verify common ground at compression boundaries. Treat key facts as needing periodic re-establishment.

### Trap: Identical briefs to differently-equipped agents

When fanning out to multiple subagents, each may have different system prompts, tools, or context. The same brief grounds differently in each. Audience design (#7) requires per-recipient tailoring.

**Fix**: tailor briefs per subagent, or verify via per-subagent acceptance phase that interpretation is consistent.

---

## Protocol Sketches

### Minimal viable acceptance protocol

```
Orchestrator → Subagent: <brief>
Subagent → Orchestrator: "I understand the goal as: <restated>. My plan: <steps>. I will need: <tools/context>. Confirming or correcting before I proceed?"
Orchestrator → Subagent: "Confirmed" OR "Correction: <delta>"
[loop until confirmed]
Subagent: <executes>
```

Cost: roughly 200 tokens added per dispatch. Saves: many high-cost specification, context-loss, and wrong-assumption failures when stakes warrant it.

### Repair-channel exposure

```
Tool: ask_clarification(question: str, options: list[str], blocking: bool)
- Subagent invokes when entropy over interpretations exceeds threshold
- Orchestrator (or user) responds; subagent updates plan
- Use is rewarded, not penalized, in completion metrics
```

### Compression-boundary re-grounding

```
On context compression event:
  1. Identify load-bearing facts (decisions made, constraints discovered, partial work)
  2. Re-state in compact form at top of compressed context
  3. Raise grounding criterion for next N turns
  4. Verify subagent acknowledges before next irreversible action
```

### AwN clarification protocol (Wang et al. EMNLP 2025)

Operationalizes Trap: No repair channel above. Ask-when-Needed framework: agent asks clarifying questions when it encounters an obstacle from unclear instructions, rather than hallucinating missing arguments.

```
Tool-use agent loop with AwN pattern:
  On instruction parse:
    If required_argument is missing or ambiguous:
      invoke ask_clarification(question=<specific gap>, options=<candidates>)
      Wait for user response
    Else:
      Proceed with tool call
  On obstacle during execution:
    Detect: "cannot proceed because <specific reason>"
    invoke ask_clarification(question=<gap>, blocking=True)
    Update plan on response
```

Benchmark: NoisyToolBench (ambiguous real-world tool-use instructions). AwN significantly outperforms baseline frameworks. Source: `AwN2025` in `data/sources.json`. Complements InferAct (#5, preemptive repair for misalignment) — AwN targets ambiguity-triggered clarification.

---

## Source Quality and Verification

- **Foundational layer (high confidence)**: Clark & Brennan (1991), Clark & Schaefer (1989), Clark (1996), Schegloff et al. (1977), Grice (1975). These are stable; results are decades-validated.
- **Pragmatics layer (high confidence)**: Stalnaker (1974), Sperber & Wilson (1986). Standard pragmatics.
- **Common-knowledge logic (high confidence)**: Aumann (1976), Lewis (1969). Stable.
- **Multi-agent LLM application layer (verify before using)**: MAST (Cemri et al. 2025) and related 2025–2026 work. Empirical percentages are dataset-specific — re-verify against your own production traces.
- **2026 preprint layer (direction solid, numbers provisional)**: `DynamicGrounding2026`, `CommonGroundBench2026`, `SemanticProtocols2026`, `NCBench2026`. None peer-reviewed as of 2026-08-14. Two carry sample-size caveats worth naming: the common-ground benchmark runs 40 participants, and NC-Bench evaluates only 2–8B open models, so its absolute accuracies should not be read as frontier-model rates. Use the qualitative findings (repair is the weakest competence; dyads underperform their members; protocols omit the semantic layer) and re-measure the quantities locally.
- **Audience design (mixed)**: Bell (1984) original is solid; computational adaptations to LLMs are recent and unsettled.

When in doubt, primary sources before secondary.
