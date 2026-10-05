---
name: foundations-grounding-communication
description: Grounding-theory primitives for common ground and repair. Use when deciding whether to ask a clarifying question, confirming a handoff was understood, or fixing multi-turn drift.
compatibility: Portable core only.
version: "1.3"
last_validated: 2026-08-14
---

# Grounding & Communication Foundations


---

**Scope note — two senses of "grounding":** This skill covers the *Clark conversational sense*: establishing shared meaning between parties (common ground, acceptance evidence, repair). It does **not** cover the *LLM-attribution / RAG sense*: whether a generated response is grounded in retrieved documents (citation faithfulness, hallucination detection). For the attribution sense, see [`ai-rag`](../ai-rag/SKILL.md) and the FACTS Grounding / RAGAS / Wallat et al. frameworks (sources `FACTSGrounding2025`, `RAGAS2024`, `WallatFaithfulness2024` in `data/sources.json`).

---

Use the ten primitives below to establish enough shared understanding for the task. Delivered context, an acknowledgment, and demonstrated understanding are different evidence; none grants authority.

**Static vs. dynamic grounding.** Interpreting an opening brief is different from maintaining a joint plan across turns. Yao, Zou, and Hawkins (2026, preprint) observe dyads missing optimal allocations despite solving the negotiation task individually. Their observed failures motivate preserving settled state, identifying referents explicitly, and distinguishing exploratory proposals from commitments. These are application conventions, not a guarantee that an agent understood.

Laban et al. (2025) measure multi-turn degradation: LLMs lose an average of 39% across six generation tasks in underspecified multi-turn settings, and once a model takes a wrong turn it "gets lost" and does not recover — a reliability failure, not mainly a capability one. **Operational inference**: in multi-turn underspecified work, periodically consolidate accumulated requirements into one restated spec (#1, #3) rather than patching state in place; after a detected wrong turn, restart execution from the consolidated spec instead of continuing to build on the compromised thread.

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
- Autonomous single-agent internal computation with no recipient or coordination ambiguity. A human plus one assistant are two interlocutors: use proportionate grounding when meaning, authority or version risk exists
- The communication channel itself is the bottleneck → use [foundations-information-theory](../foundations-information-theory/SKILL.md) (channel capacity)
- The question is *whether to communicate at all* → use [foundations-team-theory](../foundations-team-theory/SKILL.md) (value of communication)
- Strategic / adversarial speech (negotiation, debate) → compose [foundations-game-theory](../foundations-game-theory/SKILL.md) for incentives with grounding for shared referents, proposal versions and repair
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
- [Related Skills](#related-skills)

---

## Quick Reference

| # | Primitive | When to Reach For It |
|---|-----------|----------------------|
| 1 | [Common Ground](references/primitives-overview.md#1-common-ground) | Audit what each party already shares before drafting any handoff |
| 2 | [Grounding Criterion](references/primitives-overview.md#2-grounding-criterion) | "Grounded enough for what?" — set the bar before designing the protocol |
| 3 | [Contributions: Presentation + Acceptance](references/primitives-overview.md#3-contributions-presentation--acceptance) | Decompose a message into the two-step joint act it actually is |
| 4 | [Evidence of Understanding](references/primitives-overview.md#4-evidence-of-understanding) | Design the explicit/implicit signals that close the loop |
| 5 | [Repair](references/primitives-overview.md#5-repair) | Plan how misunderstandings get caught and fixed |
| 6 | [Presupposition](references/primitives-overview.md#6-presupposition) | Audit what the message assumes its audience already knows |
| 7 | [Audience Design](references/primitives-overview.md#7-audience-design) | Match the brief to *who* will read it (not who wrote it) |
| 8 | [Joint Commitment](references/primitives-overview.md#8-joint-commitment) | Treat communication as joint action, not unilateral signal |
| 9 | [Least Collaborative Effort](references/primitives-overview.md#9-least-collaborative-effort) | Optimize total effort across both parties, not just speaker effort |
| 10 | [Grounding Cost / Tracks](references/primitives-overview.md#10-grounding-cost--tracks) | Price the meta-channel — confirmations and repairs cost too |

Failure modes, checks, and supporting evidence: [references/primitives-overview.md](references/primitives-overview.md).

---

## Primitive Index

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | Common Ground | Treating "in the system prompt" as "shared with the agent" — common ground is what's *believed mutual*, not just present |
| 2 | Grounding Criterion | Over-grounding (excess confirmation overhead) or under-grounding (acting on uncertain interpretation) |
| 3 | Contributions: Presentation + Acceptance | "I sent the message, so we're done" — communication isn't complete until acceptance is signaled |
| 4 | Evidence of Understanding | Acknowledgment mistaken for task-specific understanding |
| 5 | Repair | Correction acknowledged while pre-repair assumptions still drive actions |
| 6 | Presupposition | Brief assumes context the recipient doesn't have; MAST-style specification failures live here |
| 7 | Audience Design | Brief depends on the writer’s private vocabulary or context |
| 8 | Joint Commitment | Sending a handoff mistaken for joint coordination |
| 9 | Least Collaborative Effort | Sender saves tokens while shifting larger interpretation and repair costs to recipients |
| 10 | Grounding Cost / Tracks | Confirmation/repair overhead ignored when budgeting communication |

---

## Formal Supporting Theory

Read [references/formal-theory-map.md](references/formal-theory-map.md) when source-level justification or production boundaries matter. Empirical evidence and its scope live in [`data/sources.json`](data/sources.json) and [references/primitives-overview.md](references/primitives-overview.md).

The classical layer is stable; check publication status of newer preprints before citing them. Benchmark rates are specific to their datasets and models and require local measurement before becoming policy.

---

## Anti-Patterns

| Anti-Pattern | Grounding Theory Diagnosis | Fix |
|---|---|---|
| "I put it in the system prompt, so the agent knows" | Common ground (#1) confused with content delivery; presence ≠ mutual belief | Verify common ground via grounded probe (use a proportionate probe or inspectable first artifact). Track corrections as a candidate misalignment signal; test its relation to failures in your own traces |
| Subagent acts on an ambiguous or high-cost brief without exposing its interpretation | Grounding criterion (#2) is below the task risk | For reversible work, expose the working interpretation while proceeding; require an explicit restatement/response only when ambiguity can change an irreversible or costly action |
| User says "ok" / agent emits "ack" — taken as confirmation of understanding | Evidence of understanding (#4) confuses acknowledgment with comprehension | Use task-specific paraphrase, plan, or worked example when the criterion requires stronger evidence |
| No mechanism for "wait, I don't understand" once a task starts | Repair (#5) channel missing; errors compound | Provide explicit "ask for clarification" tool; reward its use when uncertainty is high. For consequential actions, compare the inferred task with user intent before execution (InferAct pattern); preserve existing authority |
| Repair happens, but the agent proceeds on its pre-repair assumptions | Repair (#5) treated as an utterance rather than a common-ground update; the correction is acknowledged and then not propagated | After a correction, require restatement of the *revised* shared state, not of the correction. Poelitz et al. (2026, preprint) observed unreliable post-repair updates in a GPT-4.1 puzzle study; test the same failure locally |
| A correction is silently adopted even when it conflicts with verified artifact state or a source | Repair (#5) conflated with sycophancy — a correction is evidence, not truth, and propagating it faithfully is not the same as propagating it correctly | Before restating the revised shared state, check a conflicting correction against verified state; if it conflicts, surface the conflict rather than silently adopting it. See `ai-evals`'s sycophancy gate ([`references/conversational-feedback-signals.md`](../ai-evals/references/conversational-feedback-signals.md)) for the accuracy-anchored check this composes with |
| Brief mentions "the dashboard" without antecedent | Presupposition (#6) failed; agent fills in wrong referent | Audit briefs for definite references; resolve antecedents before handoff |
| Brief written in domain shorthand the recipient doesn't share; LLMs repeat similar follow-ups rather than pivoting to audience-state-informed questions | Audience design (#7) failed; speaker-centric, listener state untracked | Rewrite for the recipient's vocabulary; check by having a peer (or different agent) read it cold |
| Handoff treated as fire-and-forget | Joint commitment (#8) violated; communication framed as transmission | Use proportionate acceptance evidence; block only for unresolved consequential ambiguity or missing authority |
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
5. Choose proportionate acceptance evidence (#3): for reversible work, a visible working interpretation or first artifact can demonstrate understanding without pausing. Before costly or irreversible execution, require a restatement or other active evidence (#4).
6. Provide a repair channel (#5): an explicit "ask the user / orchestrator" tool for missing required information or ambiguity that changes the action. Consider preemptive repair verification: before executing irreversible actions, a Task Inference + Task Verification unit can verify alignment between observed agent plan and stated user intent (InferAct pattern, EMNLP 2025). For the concrete question caps, defaults, and question-quality rules that bound over-asking, see [`agents-subagents/references/clarification-questions-protocol.md`](../agents-subagents/references/clarification-questions-protocol.md) (bundle load-bearing questions and include a safe assumed default where possible).
7. Compute total cost (#9, #10): brief tokens + acceptance tokens + expected repair tokens. Optimize the sum, not just brief tokens.

**Protocol lookup at integration time.** Read the deployed [A2A specification](https://a2a-protocol.org/latest/specification/) for interrupted task states and the negotiated [MCP elicitation specification](https://modelcontextprotocol.io/specification/draft/client/elicitation) for modes, allowed data, and response semantics. Do not assume a response meaning from another protocol revision: URL-mode acceptance does not establish completion of the out-of-band interaction. These mechanisms support turn-taking and authority checks; they do not prove shared interpretation.

For clear, authorized reversible work, expose the working interpretation or first artifact and continue. Wait only when unresolved ambiguity or missing authority can change a consequential action.

**Worked example.** For a reversible draft, the subagent replies, "Working interpretation: refactor the OAuth2 handler under `src/auth/` while preserving endpoints," and begins with an inspectable first diff. The orchestrator can interrupt if that interpretation is wrong. If the same ambiguity controls a production auth migration or credential change, the subagent stops after the restatement and waits because the repair cost and authorization boundary justify blocking acceptance.

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

For end-of-run reports, use the [agent-to-user handoff pattern](references/patterns-scenarios-traps.md#agent--user-at-session-end) rather than duplicating the recipe here.

### Chatbot / conversational app — grounding acts in the UX layer

_Context_: Building a user-facing chatbot or AI assistant where misunderstanding or low clarification rate degrades experience. Rifts (ACL 2025) observed lower clarification and follow-up rates in its sampled conversations; measure missed asks and unnecessary asks in the app rather than treating those rates as a production baseline.

1. Audit personal common ground (#1) at session start — what does the system know about this user from prior sessions, profile, or context? Surface remembered context when staleness or a disputed assumption could change the action; ordinary settled context can be used without reconfirmation.
2. Set grounding criterion (#2) per intent type: for booking, purchase, or deletion, verify target and authority before acting; for a reversible lookup or draft, an inspectable result can suffice.
3. Design clarification UX to reward repair (#5): inline "Did you mean X or Y?" affordances lower the social cost of asking; agents trained on completion metrics suppress asking by default.
4. Apply audience design (#7): detect domain shorthand in user input and reflect back in the user's vocabulary, not internal API terminology.
5. Build a friction-detection signal (#1, #5): track turns where the user corrects or restates — test whether these turns predict failures; a correction count alone does not establish cause or fault.

---

## Judgment Calls

### Diagnosing grounding failure in a live team or product

Test shared-meaning failures alongside technical root causes when the output diverges from the agreed task.

| Signature | What it looks like | Distinguishing test | Fix |
|---|---|---|---|
| **Silent misalignment** | Two parties (human-human, human-agent, agent-agent) proceed for many turns or steps before anyone notices they meant different things — no error is ever raised, only a late, expensive divergence | Ask each party independently to state the current shared goal in one sentence. If they diverge and neither noticed, this is it | Scheduled, low-cost restatement checkpoints — don't wait for a symptom; under this failure mode there won't be one until the cost is sunk (#1, #2) |
| **Acknowledgment-without-understanding** | "LGTM," "sounds good," "ack," a rubber-stamp code review, a nodding stakeholder — social or procedural closure is mistaken for grounding | Ask the acknowledger to act on or restate the specific content, not just approve it. If they can't, the "ack" was backchannel, not evidence (#3, #4) | Replace approval gates with restatement or demonstration gates on anything irreversible; "approved" and "understood" are different claims — don't conflate them |
| **Costly-repair spiral** | A misunderstanding surfaces, gets "fixed," but the fix itself wasn't grounded either — repair attempts compound rather than converge, each round costing more than the last | Track repair-round cost (tokens, time, trust) over the incident. If it's rising rather than falling, the repair channel itself lacks an acceptance phase | Ground the repair the same way you'd ground the original contribution — update and expose the revised shared state before the next affected action; require a response only if consequential action still depends on unresolved ambiguity or missing authority (#3, #5, #9) |

### When explicit verification protocols beat implicit grounding

Explicit protocols (restate-and-confirm, structured acceptance, mandatory paraphrase) cost tokens, time, and social friction on *every* interaction. Implicit grounding (proceed on inferred understanding, correct if wrong) costs nothing until it's wrong, then costs a lot. The judgment call is not "always verify" or "never verify" — it's pricing the crossover for a given interaction *class*, set deliberately once rather than improvised per instance.

**Reach for explicit verification when:** the action is irreversible or expensive to undo (deploys, sends, payments, deletes); personal common ground is low (new user, new subagent, session start, just after context compression); the medium has expensive repair (async, high-latency, no real-time interrupt — batch jobs, cross-team handoffs, long agent loops); or errors are silent by default — the system won't surface a wrong interpretation on its own, it will just produce plausible-looking wrong output.

**Stay with implicit grounding when:** the action is cheap to reverse and errors surface immediately (exploratory reads, drafts, low-stakes lookups); personal common ground is already rich (many prior turns validated the shared model); the medium has cheap repair (synchronous chat, pair programming, a fast interrupt path); or over-verifying has a real cost of its own — added friction lowers the rate at which people or agents *initiate* contact at all, which can be a bigger loss than the occasional repair.

A signature or acknowledgment can close an approval gate while leaving interpretation untested. Choose evidence that detects the specific misunderstanding at issue.

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
6. Build a repair channel (#5). On a detected misunderstanding, require restatement of the revised shared state, not just acknowledgment of the correction, before proceeding.
7. Cost it (#9, #10) — verify total expected cost is below the no-grounding alternative.

## Local Validation Artifact

- [Operational record, worked case and regression checks](references/handoff-state-contract.md). Read before translating a mechanism into a deployment recommendation.

## Navigation

- Domain-agnostic primitives overview: [references/primitives-overview.md](references/primitives-overview.md)
- Formal theory map and production boundaries: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps for multi-agent / subagent handoffs: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

- [foundations-team-theory](../foundations-team-theory/SKILL.md) — *whether* to communicate; this skill is *how*
- [foundations-information-theory](../foundations-information-theory/SKILL.md) — channel capacity, information cost in bits/tokens
- [foundations-game-theory](../foundations-game-theory/SKILL.md) — strategic communication, debate, signaling under conflict
- [foundations-decision-theory](../foundations-decision-theory/SKILL.md) — value of information at the single-agent level
- [agents-subagents](../agents-subagents/SKILL.md) — applied subagent patterns
- [docs-ai-prd](../docs-ai-prd/SKILL.md) — applied: PRDs and specs as grounding artifacts for coding agents
- [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md) — applied: prompts as grounding artifacts
- [software-ux-research](../software-ux-research/SKILL.md) — adjacent: user-research methods for human-side grounding

---

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
