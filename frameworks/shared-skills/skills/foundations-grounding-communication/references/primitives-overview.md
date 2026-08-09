# Grounding & Communication Primitives — Overview


Canonical primitive definitions for grounding theory. Each entry: definition, inputs, outputs, failure modes, multi-agent application.

For applied patterns and traps specific to subagent handoff and human-AI communication, see [`patterns-scenarios-traps.md`](patterns-scenarios-traps.md).

## Table of Contents

1. [Common Ground](#1-common-ground)
2. [Grounding Criterion](#2-grounding-criterion)
3. [Contributions: Presentation + Acceptance](#3-contributions-presentation--acceptance)
4. [Evidence of Understanding](#4-evidence-of-understanding)
5. [Repair](#5-repair)
6. [Presupposition](#6-presupposition)
7. [Audience Design](#7-audience-design)
8. [Joint Commitment](#8-joint-commitment)
9. [Least Collaborative Effort](#9-least-collaborative-effort)
10. [Grounding Cost / Tracks](#10-grounding-cost--tracks)

---

## 1. Common Ground

**Definition (Clark & Brennan 1991; Clark 1996).** The set of beliefs, knowledge, and assumptions that two or more parties believe is *mutual* between them. Two layers:

- **Communal common ground**: shared by membership in groups (cultural, professional, linguistic). What "compile" means to programmers; what "GAAP" means to accountants.
- **Personal common ground**: built from shared interaction history. What you and a specific user have discussed in past sessions.

The crucial property: it isn't enough for both parties to *know* X. They must each believe the other knows X, and believe the other believes they know X (recursive mutual belief — see Aumann 1976, Lewis 1969).

**Why it matters for agents**: text in a system prompt is *content delivered*, not common ground. The agent hasn't confirmed it; the orchestrator hasn't verified the agent's interpretation. Treating prompt content as common ground is the single most common grounding error in agent design.

**Diagnostic**: ask the agent to summarize the brief in its own words *before* acting. If the summary diverges, you didn't have the common ground you assumed.

**Failure modes**:
- "I told the model in the system prompt" treated as mutual belief
- Common ground decays under context compression but is treated as still present
- Communal common ground assumed across human-AI boundary (the model doesn't share your team's slang)

---

## 2. Grounding Criterion

**Definition.** "The mutual belief that the addressee has understood what the speaker meant *to a criterion sufficient for current purposes*" (Clark & Schaefer 1989). The bar is task-relative.

**Inputs**: stakes of the task, reversibility, downstream cost of misunderstanding.

**Outputs**: target confidence level for shared understanding before proceeding.

**Why it matters**: grounding is expensive. Over-grounding (every message confirmed three ways) wastes tokens; under-grounding (act on first reading) creates MAST-style specification and inter-agent misalignment failures. The right amount depends on what the action does.

**Practical scale**:
- Reversible exploration → low criterion (act, observe, correct)
- Costly side effects (writes, sends, payments) → high criterion (require explicit acceptance)
- Irreversible (deletes, posts, deploys) → maximum criterion (paraphrase + plan + confirm)

**Failure modes**:
- Single criterion applied across all task types
- Criterion not actually checked — set in policy, ignored at runtime

---

## 3. Contributions: Presentation + Acceptance

**Definition (Clark & Schaefer 1989).** A *contribution* to discourse is a two-phase joint act:

1. **Presentation phase**: speaker presents an utterance for the addressee.
2. **Acceptance phase**: addressee signals (explicitly or implicitly) that the contribution is grounded — understood to the current criterion.

Communication isn't complete after presentation. It is complete after acceptance.

**Why it matters**: most agent handoffs skip the acceptance phase. The orchestrator dispatches; the subagent starts working. There is no checkpoint. Without it, drift is undetectable until the work product appears — by which point the cost of repair is much higher than acceptance would have been.

**Acceptance signals can be**:
- Explicit: "Got it. I will do X, Y, Z."
- Implicit: relevant next move that presupposes understanding (only safe at low grounding criterion)
- Backchannel: "uh-huh," "ack" — *weakest form*; only confirms perception, not understanding

**Failure modes**:
- Treating presentation alone as a contribution
- Backchannel acceptance treated as evidence of understanding (see #4)

---

## 4. Evidence of Understanding

**Definition.** The signal the addressee produces to demonstrate they have grounded the contribution. Strength varies (Clark & Brennan 1991, weakest to strongest):

1. **Continued attention** — addressee remains engaged
2. **Initiation of relevant next contribution** — moves the discourse forward
3. **Acknowledgment** — "yes," "ok," "ack"
4. **Demonstration** — shows what was understood (paraphrase, repetition)
5. **Display** — performs the understanding (executes a plan, produces an artifact consistent with it)

**Why it matters**: the strength of evidence required scales with grounding criterion (#2). Backchannel "ack" is the weakest evidence; relying on it for high-stakes work is the second-most-common grounding error after #1.

**Practical heuristic for subagent handoff**: require demonstration (paraphrase + plan) for any irreversible action. Acknowledgment alone is insufficient.

**Failure modes**:
- Acknowledgment treated as demonstration
- "I will do X" with no specifics treated as a plan
- Display (the work product) used as the only evidence — by then it's too late to cheaply repair

---

## 5. Repair

**Definition (Schegloff et al. 1977).** The mechanism by which interlocutors detect and correct trouble in conversation. Four types:

| Type | Initiated by | Repaired by |
|---|---|---|
| Self-initiated self-repair | Speaker | Speaker (most common in human conversation; rare in LLMs) |
| Self-initiated other-repair | Speaker (asks for help) | Addressee |
| Other-initiated self-repair | Addressee (signals trouble) | Speaker |
| Other-initiated other-repair | Addressee | Addressee (least preferred — face-threatening) |

**Why it matters**: agents almost never self-repair. They commit to interpretations and execute. Without an explicit *other-initiated* repair channel — a tool or pattern by which the agent flags uncertainty back upstream — misinterpretations compound silently until they surface as failed work products.

**Practical fix**: provide an explicit "ask for clarification" tool, and *reward its use* when uncertainty is high. Agents trained on completion incentives default to guessing.

**Multi-agent evidence typing (GSAR 2026, preprint).** Kamelhar (arXiv 2604.23366) maps Clark grounding vocabulary to multi-agent output verification via a four-way claim typology that formalizes repair evidence types: *grounded* (evidence-backed — Clark's demonstration evidence), *ungrounded* (no acceptance evidence), *contradicted* (failed repair; conflicting evidence), *complementary* (new common-ground contribution). Coupled with a three-tier recovery function (proceed / regenerate / replan) under compute budget. Treat as validate-before-adopting: arXiv preprint April 2026, peer review unconfirmed, code not yet in public repo.

**Failure modes**:
- No repair channel at all — agent guesses and proceeds
- Repair channel exists but using it is implicitly punished by completion-rate metrics
- Repair only happens after work is wrong; no preventive other-initiated repair
- No distinction between evidence types — treating "ungrounded" and "contradicted" claims identically degrades recovery targeting

---

## 6. Presupposition

**Definition (Grice 1975; Stalnaker 1974).** Information that an utterance assumes is already in common ground. "The dashboard is broken" presupposes that there is a unique salient dashboard already known to the addressee.

**Why it matters**: presupposition failures are the textbook form of specification ambiguity. The brief says "the file"; the agent has to pick one. The brief says "the user"; multiple users exist in the conversation history. Each unresolved presupposition is a coin flip the agent will lose some fraction of the time.

**Diagnostic**: read the brief as a stranger. Every definite reference ("the X"), every pronoun ("it", "they"), every domain shorthand — does it have a recoverable antecedent in the agent's available context? If not, that's a presupposition failure waiting to happen.

**Failure modes**:
- Definite descriptions with no antecedent in the agent's context
- Pronouns referencing entities last mentioned hours ago, now compressed out of context
- Domain shorthand assumed in communal common ground that the agent doesn't share

---

## 7. Audience Design

**Definition (Bell 1984; Clark & Murphy 1982).** Speakers tailor their utterances to the actual or expected recipient — vocabulary, abstraction level, presupposition set, formality.

**Why it matters**: briefs to subagents are routinely written in the orchestrator's frame, not the subagent's. The orchestrator has rich context; the subagent has the brief plus its system prompt. A brief that makes sense reading-from-the-orchestrator's-state may be incoherent reading-only-from-the-subagent's-state.

**Diagnostic**: read the brief in the subagent's expected context only. Does it stand alone? If you need the orchestrator's context to interpret it, audience design failed.

**Practical heuristic**: when designing handoffs across agent boundaries, write as if the recipient is a competent stranger. Then trim what is genuinely shared (communal common ground), and verify what you've trimmed actually is shared.

**Failure modes**:
- Speaker-centric briefs that depend on speaker's private context
- Over-trimming on assumed shared context that isn't actually shared
- Identical briefs sent to differently-equipped agents

---

## 8. Joint Commitment

**Definition (Clark 1996).** Communication is *joint action* — both parties commit to coordinating on the act, not just to producing or receiving a signal. The speaker commits to making themselves understood; the addressee commits to grounding.

**Why it matters**: the message-passing metaphor (which dominates agent framework design) treats communication as transmission. Joint-action theory says it's coordinated. The framing matters because it changes responsibility allocation: under message-passing, "I sent the message" closes the loop; under joint action, both parties are responsible for grounding.

**Practical implication**: design protocols where both sides have responsibility — orchestrator for clarity, subagent for verification. Single-side responsibility (either "the orchestrator should write better prompts" or "the subagent should be smarter") is incomplete.

**Failure modes**:
- One-sided responsibility allocation
- Communication framed as broadcast (one→many) loses joint-action structure entirely

---

## 9. Least Collaborative Effort

**Principle (Clark & Wilkes-Gibbs 1986).** Interlocutors aim to minimize *joint* effort across both parties combined, not their own effort individually.

**Why it matters**: a brief that saves the orchestrator 200 tokens but requires three repair rounds with the subagent (3,000 tokens) is locally efficient, jointly wasteful. The temptation to minimize speaker effort is strong; the result is often higher total cost.

**Practical heuristic**: when sizing a brief, estimate expected total cost = brief tokens + acceptance tokens + p(failure) × repair tokens. Minimize the sum.

**Failure modes**:
- Optimizing per-message tokens
- Stripping context "to save tokens" without modeling expected repair cost
- Asymmetric optimization: one party's effort treated as cheap, the other as costly

---

## 10. Grounding Cost / Tracks

**Definition (Clark & Brennan 1991).** Grounding has its own cost — separate from the cost of the primary message. Costs vary by *track* (the medium):

- **Cost of formulation** (writing the message)
- **Cost of production** (transmitting it)
- **Cost of reception** (parsing it)
- **Cost of understanding** (interpreting it)
- **Cost of acceptance signaling** (responding)
- **Cost of repair** (fixing trouble)

Different communication mediums make different costs cheap or expensive. Synchronous voice has cheap repair (interrupt) but expensive review (no scrollback). Async text has expensive repair but cheap review.

**Why it matters for agents**: the orchestrator↔subagent channel has its own cost profile — high token cost per round trip, no real-time interruption, partial scrollback through context. This shapes what protocols pay off. Cheap acceptance + expensive repair → invest more in upfront acceptance signaling than in error recovery. The cost asymmetry argues *for* explicit acceptance phases, not against them.

**Failure modes**:
- Treating grounding cost as zero
- Applying protocol from a different medium (synchronous chat patterns to async batch jobs) without re-pricing
- Stripping grounding mechanisms to save tokens, paying more in repair tail
