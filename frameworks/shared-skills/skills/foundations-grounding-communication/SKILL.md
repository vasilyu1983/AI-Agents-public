---
name: foundations-grounding-communication
description: Grounding-theory primitives for human-AI and agent handoffs, common ground, acceptance evidence, repair, and ambiguity. Use when coordinating meaning.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Grounding & Communication Foundations


---

**Scope note — two senses of "grounding":** This skill covers the *Clark conversational sense*: establishing shared meaning between parties (common ground, acceptance evidence, repair). It does **not** cover the *LLM-attribution / RAG sense*: whether a generated response is grounded in retrieved documents (citation faithfulness, hallucination detection). For the attribution sense, see [`ai-rag`](../ai-rag/SKILL.md) and the FACTS Grounding / RAGAS / Wallat et al. frameworks (sources `FACTSGrounding2025`, `RAGAS2024`, `WallatFaithfulness2024` in `data/sources.json`).

---

10 canonical grounding-theory primitives for the process by which two or more parties establish *enough* shared understanding to coordinate. Founded by Herbert Clark and colleagues (1989, 1991, 1996), grounding theory is the most-cited formal account of how interlocutors solve the "do we mean the same thing?" problem efficiently.

It is the missing layer for multi-agent LLM systems: empirical work on multi-agent failures (MAST taxonomy, NeurIPS 2025) identifies system-design specification issues, inter-agent misalignment, and task-verification gaps across 1,600+ traces. Agents often proceed on different interpretations of the same brief. That is not only a coordination problem (information structure); it is a grounding problem (insufficient common ground at handoff). [foundations-team-theory](../foundations-team-theory/SKILL.md) tells you *whether* agents should communicate; this skill tells you *how* they actually establish shared meaning when they do.

**Static vs. dynamic grounding (2026).** The distinction now carries the most diagnostic weight. *Static* grounding maps language to a shared context in one shot; *dynamic* grounding requires negotiating meaning across turns — joint plan formation, commitment, and execution. Yao, Zou, and Hawkins (2026) show the gap is not a reasoning-capacity problem: in an iterated negotiation game with verifiable jointly optimal outcomes, agents that identify Pareto-optimal allocations *in isolation* consistently fail to reach them *as dyads*, across models. Their four failure modes — loss of shared interaction history, anchoring to early proposals, defaulting to equal splits over reward-maximizing coordination, and referential binding errors across turns — map onto primitives #1, #3, #8, and #6 respectively. Most benchmarks and most agent handoff designs still test only the static case.

## When to Apply

**Apply grounding-theory when:**
- Designing handoffs between subagents, or between a planner and an executor
- Drafting briefs, specs, or PRDs that downstream agents will interpret
- Diagnosing why a subagent did the wrong thing — was the brief grounded?
- Building human-in-the-loop confirmation flows
- Designing repair protocols ("re-ask if confidence < threshold")
- Modeling memory: what becomes part of the *common ground* between agent and user across sessions?
- Spec drift across long agent loops where context compresses

**Skip and use simpler alternatives when:**
- Single agent / no handoff — there is no second party to ground with
- The communication channel itself is the bottleneck → use [foundations-information-theory](../foundations-information-theory/SKILL.md) (channel capacity)
- The question is *whether to communicate at all* → use [foundations-team-theory](../foundations-team-theory/SKILL.md) (value of communication)
- Strategic / adversarial speech (negotiation, debate) → use [foundations-game-theory](../foundations-game-theory/SKILL.md)
- Pure user-research methodology → use [software-ux-research](../software-ux-research/SKILL.md)

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Anti-Patterns](#anti-patterns)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Judgment Calls](#judgment-calls)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | When to Reach For It |
|---|-----------|----------------------|
| 1 | [Common Ground](#1-common-ground) | Audit what each party already shares before drafting any handoff |
| 2 | [Grounding Criterion](#2-grounding-criterion) | "Grounded enough for what?" — set the bar before designing the protocol |
| 3 | [Contributions: Presentation + Acceptance](#3-contributions-presentation--acceptance) | Decompose a message into the two-step joint act it actually is |
| 4 | [Evidence of Understanding](#4-evidence-of-understanding) | Design the explicit/implicit signals that close the loop |
| 5 | [Repair](#5-repair) | Plan how misunderstandings get caught and fixed |
| 6 | [Presupposition](#6-presupposition) | Audit what the message assumes its audience already knows |
| 7 | [Audience Design](#7-audience-design) | Match the brief to *who* will read it (not who wrote it) |
| 8 | [Joint Commitment](#8-joint-commitment) | Treat communication as joint action, not unilateral signal |
| 9 | [Least Collaborative Effort](#9-least-collaborative-effort) | Optimize total effort across both parties, not just speaker effort |
| 10 | [Grounding Cost / Tracks](#10-grounding-cost--tracks) | Price the meta-channel — confirmations and repairs cost too |

Full definitions, inputs, outputs, failure modes, and worked examples: [`references/primitives-overview.md`](references/primitives-overview.md).

---

## Primitive Index

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | Common Ground | Treating "in the system prompt" as "shared with the agent" — common ground is what's *believed mutual*, not just present |
| 2 | Grounding Criterion | Over-grounding (excess confirmation overhead) or under-grounding (acting on uncertain interpretation) |
| 3 | Contributions: Presentation + Acceptance | "I sent the message, so we're done" — communication isn't complete until acceptance is signaled |
| 4 | Evidence of Understanding | Acknowledgment vs. understanding conflated; "ack" doesn't mean "got it". LLMs emit 3× fewer clarification initiations and 16× fewer follow-ups than humans (Rifts, ACL 2025); benchmark: aclanthology.org/2025.acl-long.1016/ |
| 5 | Repair | Errors compound silently because no repair protocol exists; agent acts on misinterpretation. LLMs fail to initiate repair-seeking acts at comparable human rates; early repair failures predict compounding breakdown (Rifts, ACL 2025). Repair is the weakest measured conversational competence: 5–75% accuracy on repeat requests vs 95–100% on plain answering (NC-Bench, 2026). Models also fail to *update assumptions after* a repair completes (Poelitz et al. 2026) — the repair lands but common ground doesn't move |
| 6 | Presupposition | Brief assumes context the recipient doesn't have; MAST-style specification failures live here |
| 7 | Audience Design | Brief written for the writer, not the reader; tokens spent on wrong abstractions. LLMs fail to pivot to audience-state-informed questions, instead repeating similar follow-ups (NewsInterview, ACL 2025) |
| 8 | Joint Commitment | Handoff treated as transmission rather than joint coordination. CRSA (EMNLP 2025) formalizes this: joint task distribution P(m_A,m_B,y) captures what both agents know about outcomes — a formal model of the mutual-obligation structure joint commitment requires |
| 9 | Least Collaborative Effort | One-sided optimization — fewer tokens for the speaker, more confusion for the listener. CRSA's gain function minimizes total communication effort across both agents over the full dialogue history — the formal analogue of least collaborative effort for multi-turn settings |
| 10 | Grounding Cost / Tracks | Confirmation/repair overhead ignored when budgeting communication |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Clark & Brennan grounding theory | Design handoff/confirmation protocols | #1, #2, #3, #4, #10 |
| Gricean implicature / pragmatics | Account for what is meant beyond what is said | #6, #7 |
| Conversation analysis (Sacks, Schegloff) | Repair sequences, turn-taking, adjacency pairs; Ubuntu-CG (Sarkar et al., ACL 2025) provides first real-world empirical validation: friction (failed repair initiation) predicts task failure; current LLMs detect implicit friction poorly (64.81% F1) | #5 |
| Joint action theory | Frame communication as coordinated activity, not message-passing | #8, #9 |
| Collaborative RSA (CRSA) | Multi-turn dialogue where agents hold private information and must converge on shared outcomes | #8, #9 |
| Dynamic grounding (Yao et al. 2026) | Coordination spans many turns and joint plans must be formed, committed to, and executed — not just interpreted once | #1, #3, #6, #8 |
| Protocol semantic layer (Yuan et al. 2026) | Deciding what the transport protocol gives you vs. what you must build; 18-protocol survey against communication/syntactic/semantic layers | #3, #5, #6 |
| Common-knowledge logic (Aumann, Lewis) | Need formal model of what is mutual belief | #1 |
| Audience design (Bell, Clark & Murphy) | Tailor message to recipient | #7 |

See [`references/primitives-overview.md`](references/primitives-overview.md) for theorem statements and a formal-vs-applied map.

---

## Anti-Patterns

| Anti-Pattern | Grounding Theory Diagnosis | Fix |
|---|---|---|
| "I put it in the system prompt, so the agent knows" | Common ground (#1) confused with content delivery; presence ≠ mutual belief | Verify common ground via grounded probe (ask the agent to summarize before acting). Detect friction as operational signal of CG misalignment — 61% of real conversations contain friction; successful conversations show significantly lower rates (Ubuntu-CG, ACL 2025) |
| Subagent acts immediately on first reading of the brief | Grounding criterion (#2) set to zero; no acceptance phase | Build acceptance into the protocol — agent restates intent before executing |
| User says "ok" / agent emits "ack" — taken as confirmation of understanding | Evidence of understanding (#4) confuses acknowledgment with comprehension | Require active evidence: paraphrase, plan, or worked example, not just acknowledgment. (Empirical: LLMs produce near-zero acknowledgement statements (~0%) vs ~9% in human dialogue — NewsInterview, ACL 2025) |
| No mechanism for "wait, I don't understand" once a task starts | Repair (#5) channel missing; errors compound | Provide explicit "ask for clarification" tool; reward its use when uncertainty is high. For irreversible actions, preemptive verification (infer task from action sequence, check against user intent) outperforms reactive repair (InferAct, EMNLP 2025) |
| Repair happens, but the agent proceeds on its pre-repair assumptions | Repair (#5) treated as an utterance rather than a common-ground update; the correction is acknowledged and then not propagated | After a correction, require restatement of the *revised* shared state, not of the correction. Empirically LLM collaborators fail to update assumptions post-repair, and their joint vocabulary with a partner shrinks rather than grows over trials (Poelitz et al. 2026) |
| Brief mentions "the dashboard" without antecedent | Presupposition (#6) failed; agent fills in wrong referent | Audit briefs for definite references; resolve antecedents before handoff |
| Brief written in domain shorthand the recipient doesn't share; LLMs repeat similar follow-ups rather than pivoting to audience-state-informed questions | Audience design (#7) failed; speaker-centric, listener state untracked | Rewrite for the recipient's vocabulary; check by having a peer (or different agent) read it cold |
| Handoff treated as fire-and-forget | Joint commitment (#8) violated; communication framed as transmission | Wait for acceptance signal before considering the handoff complete |
| Speaker minimizes own tokens, recipient must guess | Least collaborative effort (#9) optimized one-sidedly | Optimize total effort: a longer brief that prevents one repair round is cheaper than the round trip |
| Confirmation steps stripped to save tokens | Grounding cost (#10) underestimated; expected savings exceeded by failure cost | Compute expected total cost including failure-and-repair tail |

---

## Decision Checklist

- [ ] **What is already in common ground?** List communal (general world knowledge) and personal (this conversation) common ground (#1)
- [ ] **What is the grounding criterion for this task?** High-stakes / irreversible → high; routine → low (#2)
- [ ] **What is the acceptance phase?** How will the recipient signal "got it"? (#3)
- [ ] **What counts as evidence of understanding?** Paraphrase, plan, sample output — not just "ack" (#4)
- [ ] **What is the repair protocol?** When and how does the recipient ask for clarification? (#5)
- [ ] **Are presuppositions resolved?** Every "the X" should have a recoverable antecedent (#6)
- [ ] **Is the brief written for the recipient?** Vocabulary, frame, abstraction level (#7)
- [ ] **Is communication framed as joint action?** Both parties bear responsibility for grounding (#8)
- [ ] **Is total effort minimized, not speaker effort?** A longer brief that prevents a repair round is cheaper (#9)
- [ ] **Is grounding cost budgeted?** Confirmations and repairs are not free (#10)

---

## Composition Recipes

### Brief-to-subagent handoff (the dominant failure surface)

_Context_: Orchestrator dispatches a subagent on a non-trivial task. MAST data makes this a primary failure surface because prompt, role, context, and stopping-condition ambiguity all appear before or during execution.

1. Audit common ground (#1): what does the subagent already know from system prompt + context vs. what does it need from this brief?
2. Set grounding criterion (#2): is this a reversible exploration or an irreversible action? Higher stakes → higher criterion.
3. Resolve presuppositions (#6): every definite reference ("the file," "the user") must have a recoverable antecedent in the prompt.
4. Apply audience design (#7): does the subagent share the orchestrator's domain shorthand? If not, expand or substitute.
5. Build the acceptance phase (#3): require the subagent to restate the goal and plan *before* executing. Capture this as evidence of understanding (#4).
6. Provide a repair channel (#5): an explicit "ask the user / orchestrator" tool with a low threshold for use under uncertainty. Consider preemptive repair verification: before executing irreversible actions, a Task Inference + Task Verification unit can verify alignment between observed agent plan and stated user intent (InferAct pattern, EMNLP 2025, +8% Macro-F1 over baselines across 3 tasks).
7. Compute total cost (#9, #10): brief tokens + acceptance tokens + expected repair tokens. Optimize the sum, not just brief tokens.

**A2A/MCP note (2026).** Agent-to-Agent (A2A, Google/Linux Foundation, 2025) and MCP standardize the *transport* layer for inter-agent handoffs. They do not solve the grounding layer. Yuan et al. (2026) survey 18 agent communication protocols against a three-layer taxonomy — communication (reliable transmission), syntactic (message schemas), semantic (meaning alignment) — and find most provide "limited protocol-level mechanisms for clarification, context alignment, and verification." Agents "exchange messages correctly without ensuring they understand them in the same way." Semantic responsibilities get pushed into prompts, wrappers, and orchestration logic.

Practical consequence: the grounding layer is yours to build, per-integration, until protocols carry it. An A2A task delegation carries a structured payload, but whether the receiving agent shares the sending agent's interpretation of that payload is still a Clark-layer problem: resolve presuppositions (#6), apply audience design (#7), and build an acceptance phase into the A2A response before execution begins (#3).

**Worked example.** Orchestrator brief v1: "Refactor the auth module." Acceptance step: subagent restates: "I'll modify the OAuth2 handler in `src/auth/`, preserve existing endpoints, add tests." Orchestrator notices it missed a target file — the brief should have specified `src/auth/oauth2.py` not the whole module. Repair: 50 tokens. Without acceptance step: subagent rewrites a different file; repair cost 5,000+ tokens. Acceptance step earned its keep.

### Long-running agent context compression

_Context_: An agent loops for many turns; context gets compressed by the harness; common ground decays.

1. Identify what *must* persist in common ground vs. what is recomputable (#1).
2. Set grounding criterion (#2) higher near compression boundaries — verify shared state before acting.
3. Use repair (#5) proactively — re-establish key facts after compression rather than waiting for failure.
4. Track grounding cost (#10) — re-grounding has a token cost that competes with productive work; make it explicit in the budget.

### Multi-turn agent↔agent coordination (dynamic grounding)

_Context_: Two agents must converge on a joint plan over several turns — negotiation, resource allocation, division of labor, peer review. Distinct from a one-shot handoff: the failure is not a bad brief but a failure to *maintain and revise* shared state across turns. Individually capable agents still fail as dyads here (Yao et al. 2026).

1. Externalize the shared plan (#1, #8). Do not rely on each agent's reading of the transcript — keep a single explicit joint-state object both agents read and write. Loss of shared interaction history is failure mode #1 in the negotiation data.
2. Re-bind references every turn (#6). Referential binding errors across turns are a named failure mode: "the second option," "your earlier proposal," "that split" drift as the transcript grows. Restate referents by identity, not by position in the conversation.
3. Force explicit commitment steps (#3, #8). Distinguish "I am exploring X" from "I commit to X." Anchoring to early proposals is a named failure mode — untagged exploratory proposals get treated as commitments by the other side.
4. Watch for the fairness default (#2). Agents default to equal splits over reward-maximizing coordination. If the jointly optimal outcome is asymmetric, state that explicitly; symmetric-looking compromises are a grounding failure wearing the costume of a reasonable outcome.
5. Verify convergence, don't assume it (#4). Ask each agent independently to state the agreed plan. Agreement in the transcript is not agreement in their models.

### Human-AI handoff at end of agent run

_Context_: Agent finishes work and hands back to user.

1. Apply audience design (#7) — the user is not the agent; vocabulary, abstraction, and salient evidence differ.
2. Provide explicit evidence of work (#4) — what changed, what was decided, what wasn't done. Not "ack."
3. Joint commitment (#8) — frame handoff as "here's what I did and why; please verify or redirect," not "task complete."
4. Pre-empt repair (#5) — call out specific points where the user's intent might have been misread.

### Chatbot / conversational app — grounding acts in the UX layer

_Context_: Building a user-facing chatbot or AI assistant where misunderstanding or low clarification rate degrades experience. Empirical baseline: production LLMs clarify 3× less and follow up 16× less than human conversational partners (Rifts, ACL 2025), so the app must compensate structurally.

1. Audit personal common ground (#1) at session start — what does the system know about this user from prior sessions, profile, or context? Surface it explicitly rather than silently assuming it.
2. Set grounding criterion (#2) per intent type: high-stakes intent (booking, purchase, delete) → require restatement before acting; low-stakes (lookup, draft) → accept acknowledgment.
3. Design clarification UX to reward repair (#5): inline "Did you mean X or Y?" affordances lower the social cost of asking; agents trained on completion metrics suppress asking by default.
4. Apply audience design (#7): detect domain shorthand in user input and reflect back in the user's vocabulary, not internal API terminology.
5. Build a friction-detection signal (#1, #5): track turns where the user corrects or restates — high friction rates indicate common-ground gaps in the system prompt or prior bot turn, not user error.

---

## Judgment Calls

### Diagnosing grounding failure in a live team or product

A non-expert sees the symptom (wrong output, an angry user, a broken deploy) and reaches for a technical root cause. An expert triages the grounding layer first, because three failure signatures recur across very different systems and each has a distinct fix — and each has a cheap leading indicator that's easy to miss because the system looks fine on its face until the cost is already sunk.

| Signature | What it looks like | Distinguishing test | Fix |
|---|---|---|---|
| **Silent misalignment** | Two parties (human-human, human-agent, agent-agent) proceed for many turns or steps before anyone notices they meant different things — no error is ever raised, only a late, expensive divergence | Ask each party independently to state the current shared goal in one sentence. If they diverge and neither noticed, this is it | Scheduled, low-cost restatement checkpoints — don't wait for a symptom; under this failure mode there won't be one until the cost is sunk (#1, #2) |
| **Acknowledgment-without-understanding** | "LGTM," "sounds good," "ack," a rubber-stamp code review, a nodding stakeholder — social or procedural closure is mistaken for grounding | Ask the acknowledger to act on or restate the specific content, not just approve it. If they can't, the "ack" was backchannel, not evidence (#3, #4) | Replace approval gates with restatement or demonstration gates on anything irreversible; "approved" and "understood" are different claims — don't conflate them |
| **Costly-repair spiral** | A misunderstanding surfaces, gets "fixed," but the fix itself wasn't grounded either — repair attempts compound rather than converge, each round costing more than the last | Track repair-round cost (tokens, time, trust) over the incident. If it's rising rather than falling, the repair channel itself lacks an acceptance phase | Ground the repair the same way you'd ground the original contribution — restate the correction, get explicit acceptance, before the next attempt (#3, #5, #9) |

### When explicit verification protocols beat implicit grounding

Explicit protocols (restate-and-confirm, structured acceptance, mandatory paraphrase) cost tokens, time, and social friction on *every* interaction. Implicit grounding (proceed on inferred understanding, correct if wrong) costs nothing until it's wrong, then costs a lot. The judgment call is not "always verify" or "never verify" — it's pricing the crossover for a given interaction *class*, set deliberately once rather than improvised per instance.

**Reach for explicit verification when:** the action is irreversible or expensive to undo (deploys, sends, payments, deletes); personal common ground is low (new user, new subagent, session start, just after context compression); the medium has expensive repair (async, high-latency, no real-time interrupt — batch jobs, cross-team handoffs, long agent loops); or errors are silent by default — the system won't surface a wrong interpretation on its own, it will just produce plausible-looking wrong output.

**Stay with implicit grounding when:** the action is cheap to reverse and errors surface immediately (exploratory reads, drafts, low-stakes lookups); personal common ground is already rich (many prior turns validated the shared model); the medium has cheap repair (synchronous chat, pair programming, a fast interrupt path); or over-verifying has a real cost of its own — added friction lowers the rate at which people or agents *initiate* contact at all, which can be a bigger loss than the occasional repair.

**The trap runs both directions.** Defaulting to implicit because verification "feels slow" is the dominant failure in agent design (see Composition Recipes above). Defaulting to explicit-everywhere is the dominant failure in enterprise process design — approval theater that produces acknowledgment-without-understanding rather than real grounding, because the gate checks for a signature, not a restatement.

### Least collaborative effort as a UX and agent-design lens

Least collaborative effort (#9) is usually read as a dialogue-efficiency principle. Applied to product and agent design, it reframes a common local optimization as a false economy:

- **UX**: a form that asks fewer questions up front (minimizing the user's effort) but generates ambiguous submissions that support has to chase down later is not efficient — it moved cost from the user to a more expensive party. The efficient design asks the two or three questions whose absence would otherwise cost a support ticket.
- **Agent design**: a terse system prompt that saves orchestrator tokens but forces the subagent to guess, and the user to catch the guess later, is the same error. Price total expected cost (brief + acceptance + p(failure) × repair) before trimming a brief for length.
- **The diagnostic in both cases**: ask "whose effort did this design minimize, and whose did it defer?" If the answer is "the party who assembles the request, at the expense of whoever has to interpret or fix it," least collaborative effort was optimized one-sidedly — regardless of how efficient the interface looks in isolation.

---

## Workflow

1. Identify the handoff or communication boundary (subagent dispatch, user→agent, agent→user, agent→agent).
2. Audit common ground (#1) at that boundary.
3. Set the grounding criterion (#2) appropriate to the stakes.
4. Resolve presuppositions (#6) and apply audience design (#7) to the message.
5. Design the acceptance phase (#3) and the evidence of understanding (#4).
6. Build a repair channel (#5).
7. Cost it (#9, #10) — verify total expected cost is below the no-grounding alternative.

---

## ASCII Flow

```text
Communication or handoff boundary
  -> Identify participants, task, stakes, and current common ground
  -> Choose grounding criterion for the risk level
  -> Design presentation and acceptance evidence
  -> Resolve presuppositions and audience mismatch
     +-- misunderstanding detected -> repair and re-confirm
     +-- understanding evidenced -> proceed
  -> Cost grounding overhead against failure cost
```

---

## Navigation

- Domain-agnostic primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Formal theory map and production boundaries: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps for multi-agent / subagent handoffs: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

- [foundations-team-theory](../foundations-team-theory/SKILL.md) — *whether* to communicate; this skill is *how*
- [foundations-information-theory](../foundations-information-theory/SKILL.md) — channel capacity, information cost in bits/tokens
- [foundations-game-theory](../foundations-game-theory/SKILL.md) — strategic communication, debate, signaling under conflict
- [foundations-decision-theory](../foundations-decision-theory/SKILL.md) — value of information at the single-agent level
- `agents-subagents` — applied subagent patterns
- [docs-ai-prd](../docs-ai-prd/SKILL.md) — applied: PRDs and specs as grounding artifacts for coding agents
- [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md) — applied: prompts as grounding artifacts
- [software-ux-research](../software-ux-research/SKILL.md) — adjacent: user-research methods for human-side grounding

---

## Fact-Checking

- Clark and Brennan (1991) "Grounding in Communication." In *Perspectives on Socially Shared Cognition* (APA). Canonical paper for primitives #1–#5, #10.
- Clark (1996) *Using Language*. Cambridge University Press. Book-length treatment; primary source for #3, #8, #9.
- Clark and Schaefer (1989) "Contributing to Discourse." *Cognitive Science* 13. Presentation + acceptance phases.
- Grice (1975) "Logic and Conversation." In *Syntax and Semantics 3*. Foundation for presupposition and implicature (#6).
- Schegloff, Jefferson, and Sacks (1977) "The Preference for Self-Correction in the Organization of Repair." *Language* 53(2). Repair sequences (#5).
- Bell (1984) "Language Style as Audience Design." *Language in Society* 13. Audience design (#7).
- Cemri et al. (2025) "Why Do Multi-Agent LLM Systems Fail?" (MAST). NeurIPS. Empirical anchor for system-design, inter-agent misalignment, and task-verification failures across 1,600+ traces.
- Shaikh, Gligorić, Khetan, Gerstgrasser, Yang, Jurafsky (2024) "Grounding Gaps in Language Model Generations." NAACL-HLT 2024 (ACL Anthology 2024.naacl-long.348). Coined "presumptive grounders" — LLMs assume common ground rather than using grounding acts. Found that RLHF/preference training reduces grounding acts. Predecessor paper to Rifts 2025 (same first author). Supports #4, #5.
- Shaikh et al. (2025) "Navigating Rifts in Human-LLM Grounding." ACL 2025. Rifts benchmark. LLMs clarify 3× and follow up 16× less than humans. Supports #4, #5.
- Spangher et al. (2025) "NewsInterview." ACL 2025. 45,848-interview corpus; LLM acknowledgement rate ~0% vs human ~9%. Supports #4, #7.
- Sarkar et al. (2025) "Understanding Common Ground Misalignment." ACL 2025. Ubuntu-CG: 200 conversations, 7,590 turns; friction correlates with task failure; LLM friction detection 77.22% (overt) / 64.81% (implicit) F1. Supports #1, #5.
- Fang, Zhu, Gurevych (2025) "Preemptive Detection and Correction of Misaligned Actions." EMNLP 2025, pp. 222–244. InferAct: +8% avg Macro-F1, 11/12 settings best across 3 tasks × 4 LLMs. Extends #5.
- Estienne et al. (2025) "Collaborative Rational Speech Act." EMNLP 2025. CRSA extends RSA to multi-turn with private meaning spaces; speaker entropy 8.18 vs 14.27 baseline on medical dialogue. Grounds #8, #9.
- Yao, Zou, Hawkins (2026) "Talk is Cheap, Communication is Hard: Dynamic Grounding Failures and Repair in Multi-Agent Negotiation." arXiv 2605.01750. Iterated negotiation game with verifiable jointly optimal outcomes; agents solve in isolation but dyads fail across models; four named failure modes. Static-vs-dynamic grounding distinction. Preprint — no peer review confirmed.
- Poelitz, Doshi-Velez, Lindley (2026) "A Benchmark to Assess Common Ground in Human-AI Collaboration." arXiv 2602.21337. 40-participant Helper/Worker puzzle task, 2×2 design; measures task, object, and communication levels. AI Helpers show minimal efficiency gain across trials where humans improve; joint vocabulary shrinks; models fail to update assumptions after repair. Preprint — no peer review confirmed.
- Yuan et al. (2026) "Beyond Message Passing: A Semantic View of Agent Communication Protocols." arXiv 2604.02369. Surveys 18 protocols (MCP, A2A, Agora, ACP variants) against a communication/syntactic/semantic taxonomy; cites Clark's joint-activity framing to motivate the semantic layer. Preprint — no peer review confirmed.
- Moore, An, Ahmed, Gala (2026) "NC-Bench: An LLM Benchmark for Evaluating Conversational Competence." arXiv 2601.06426. 14 interaction patterns, 720 test cases, 6 open-source models (2–8B, Granite/Llama/Qwen). Repair (repeat) 5–75% vs answering 95–100%. Small-model sample — do not generalize the rates to frontier models; the *ordering* (repair weakest) is the transferable finding.
- Empirical numbers (e.g., MAST percentages, Rifts rates, NC-Bench accuracies) are dataset- and model-specific. Re-verify against your own production traces before treating as priors. The four 2026 entries above are arXiv preprints; the Clark canonical layer and the ACL/EMNLP 2025 layer are peer-reviewed.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
