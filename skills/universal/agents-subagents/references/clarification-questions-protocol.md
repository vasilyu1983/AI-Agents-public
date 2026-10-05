---
description: Members ask clarifying questions before fabricating detail; primary anti-slop gate.
last_verified: 2026-09-16
status: stable
---

# Clarification Questions Protocol

When a member receives an underspecified task, it asks focused clarifying questions instead of fabricating a detailed-looking answer. This is the primary anti-slop mechanism in the team runtime.

## Table of Contents

- [Summary](#summary)
- [Why This Protocol Exists](#why-this-protocol-exists)
- [Contract](#contract)
- [Question Quality Rules](#question-quality-rules)
- [End-to-End Flow](#end-to-end-flow)
- [Worked Example](#worked-example)
- [Relationship to Dynamic Team Expansion](#relationship-to-dynamic-team-expansion)
- [Guardrails](#guardrails)
- [When Not to Use](#when-not-to-use)
- [Related References](#related-references)

## Summary

Every member emits a `Clarifying Questions` block before (or alongside) its position whenever the task brief is missing a load-bearing fact. The synthesis owner collects all questions, deduplicates them, and emits a single `Clarification Request` to the lead thread if any question is load-bearing. The lead relays questions to the user, collects answers, re-dispatches the team with the updated brief, and synthesis proceeds.

This is the first defensive-output gate; the [Expertise-Gap / Expansion Request](dynamic-team-expansion.md) protocol is the second. Together they stop the team from producing plausible-sounding-but-slop output when the input was ambiguous or the team lacked expertise.

## Why This Protocol Exists

AI slop — confident prose that looks like an answer but papers over missing context — is the default failure mode of agent teams. It happens when:

- The brief is ambiguous and the member invents an interpretation
- The member fills in assumed values ("assuming B2B SaaS", "assuming mid-market")
- The member generates a generic framework response because the specific case is unclear
- Multiple members interpret the task differently and the synthesis masks the divergence

Clarifying questions convert ambiguity into an explicit exchange rather than a silent assumption. A short upfront question saves a long worthless answer.

## Contract

### Member side

Before (or alongside) the Round 1 position, every perspective-agent or canonical member may emit:

```
### Clarifying Questions (optional, omit if the brief is fully specified)

1. question: <the question — precise, answerable in one sentence>
   why_load_bearing: <how the answer changes your output>
   assumed_default: <what you will assume if the question is not answered>

2. ...
```

If any clarifying question is load-bearing, the member should:
- Emit the questions
- Produce a **conditional position** that states explicitly which assumption it rests on, OR
- Stop and wait (only for single-member dispatches where the lead can reprompt cheaply)

For team dispatch, the preferred pattern is **emit questions + conditional position** so the synthesis owner can still collect parallel perspectives while flagging the ambiguity.

### Synthesis owner side

Before producing the decision log:

1. Collect every `Clarifying Questions` entry across members.
2. Deduplicate by semantic overlap (two members asking "which jurisdiction?" counts once).
3. Drop any question whose `assumed_default` happens to be correct given the known brief.
4. Partition remaining questions into **load-bearing** (recommendation would flip) and **sharpening** (recommendation stays the same but precision improves).
5. If any question is load-bearing, emit a `Clarification Request` (see below) and stop. Do not produce the decision log yet.
6. If only sharpening questions remain, produce the decision log and list the sharpening questions under `Assumptions Taken` so the lead sees what was inferred.

Clarification Request format:

```
## Clarification Request

**Reason:** The team cannot produce a confident recommendation without these answers.

### Questions for the user

1. <question>
   why it matters: <one sentence>
   team's default if unanswered: <what assumption the team will fall back to>

2. ...

### After clarification
Re-dispatch the team with the updated brief, then re-synthesize.
```

### Lead thread side

When the synthesis returns a Clarification Request:

1. Present the questions to the user. Do not answer them yourself, even if you could guess.
2. Collect the user's answers.
3. Re-dispatch the team (not just one member — the entire team, because clarifications can change every perspective's framing).
4. Expect a clean decision log on the second pass. If a second Clarification Request follows, the brief is genuinely under-specified — surface that to the user rather than looping.

## Question Quality Rules

Members must follow these rules so clarifying questions stay useful rather than becoming their own slop:

1. **Maximum 3 questions per member.** If you need more, the brief is broken — say so directly instead of asking.
2. **Each question must be load-bearing or sharpening, not fact-gathering.** "What is the scope of X?" is fact-gathering; "Is X scoped to new users only or all users?" is a binary that changes the answer.
3. **Prefer binary or short-enum questions over open-ended ones.** "Which of the following applies: A, B, C?" beats "Tell me more about X."
4. **Never ask what the prepared context already answers.** Read the brief and context artifacts before emitting questions.
5. **Pair every question with an `assumed_default`.** This lets the user skip low-stakes questions safely and turns "what if I don't know?" into "accept the default."
6. **Do not ask the user to do your job.** Members are paid to have opinions. "Which approach do you prefer?" is an abdication, not a question.

## End-to-End Flow

```
Lead thread
   │
   ├─▶ Dispatch team members (parallel)
   │      │
   │      ├─▶ Member A → Clarifying Questions + conditional position
   │      ├─▶ Member B → position (no questions)
   │      └─▶ Member C → Clarifying Questions + conditional position
   │
   ├─▶ Synthesis owner
   │      │
   │      ├─▶ Collect + dedupe questions
   │      ├─▶ Load-bearing?
   │      │       yes → Clarification Request (stop)
   │      │       no  → Decision Log + Assumptions Taken
   │      └─▶
   │
   ├─▶ [If Clarification Request]
   │      ├─▶ Relay questions to user
   │      ├─▶ Collect answers
   │      └─▶ Re-dispatch team with updated brief
   │
   ├─▶ [Then: Expertise-Gap handling — see dynamic-team-expansion.md]
   │
   └─▶ Final Decision Log
```

Clarifying questions run **before** expertise-gap expansion. If the brief is underspecified, the team does not yet know what expertise it lacks.

## Worked Example

**Workflow mode**: `expert-board` with `monetization`, asked "help with our pricing".

**Member: `startup-pricing-advisor`** emits:

```
### Clarifying Questions
1. question: Is the goal to raise ARPU on existing customers, improve free-to-paid conversion, or both?
   why_load_bearing: "Raise ARPU" favors packaging changes; "free-to-paid" favors paywall and plan-boundary changes. Opposite experiments.
   assumed_default: Both, with free-to-paid as primary.

2. question: What is the current pricing model — per-seat, per-usage, flat-tier, hybrid?
   why_load_bearing: The value-metric analysis depends entirely on this.
   assumed_default: Per-seat SaaS based on the "B2B" framing in the brief.

### Position (conditional on assumed defaults above)
[… position …]
```

**Member: `marketing-strategist`** emits:

```
### Clarifying Questions
1. question: Is pricing positioned against a specific competitor, or are you category-defining?
   why_load_bearing: Anchoring against a competitor caps upside; category-defining pricing has more latitude.
   assumed_default: Anchoring against a named competitor.
```

**Synthesis owner (`startup-pricing-advisor`)** collects three questions, sees that Q1 from pricing-advisor is load-bearing (the entire recommendation flips), emits:

```
## Clarification Request

**Reason:** The monetization goal determines whether this is a packaging problem or a conversion problem — opposite experiments.

### Questions for the user

1. Is the goal to raise ARPU on existing paying customers, improve free-to-paid conversion, or both?
   why it matters: Decides whether to change packaging or paywall. We cannot do both in one experiment.
   team's default if unanswered: Both, with free-to-paid as primary.

2. What is the current pricing model — per-seat, per-usage, flat-tier, or hybrid?
   why it matters: Sets the value-metric analysis frame.
   team's default if unanswered: Per-seat SaaS.

### After clarification
Re-dispatch the team with the updated brief, then re-synthesize.
```

User answers "free-to-paid conversion, per-seat SaaS". Lead re-dispatches. Clean decision log follows.

## Relationship to Dynamic Team Expansion

The two protocols are ordered and complementary:

| Protocol | Trigger | Fix |
|---|---|---|
| Clarifying Questions | Brief is ambiguous | User provides missing facts |
| Expertise-Gap / Expansion | Team lacks expertise for the task | Pull additional members from the catalog |

Run order:

1. **Clarifying Questions first.** If the brief is ambiguous, the team doesn't yet know what expertise it lacks.
2. **Expertise-Gap second.** Only after the brief is clear can members honestly flag where their expertise runs out.

A synthesis pass can emit one or the other but never both at once. If a second pass still triggers Expansion Request after the clarification round, handle it normally — that's the protocol working, not a failure.

## Guardrails

- **Hard cap: 3 questions per member, ~5 questions per team per round.** More than that means the brief is broken; say so.
- **No recursive clarification.** If a second Clarification Request fires after the first, stop and tell the user the task is under-specified.
- **Defaults must be honest.** Picking a default that is obviously wrong to force the user to answer is passive-aggressive; write briefs, not traps.
- **User can always say "use defaults".** The protocol must tolerate skipping every question cleanly.

## When Not to Use

- **Time-boxed or incident work.** Speed beats precision; take the default and move. The post-incident review is where you ask questions.
- **Trivial or reversible tasks.** Asking three questions about a one-line edit is worse than just doing it.
- **The brief is explicitly exploratory** ("sketch options", "brainstorm"). Clarification questions defeat exploration.

## Related References

- [agents/templates/perspective-agent.md](../../../../agents/templates/perspective-agent.md) — member-side Clarifying Questions block and conditional position
- [agents/templates/debate-synthesizer.md](../../../../agents/templates/debate-synthesizer.md) — synthesis-side CQ collection and Clarification Request format
- [dynamic-team-expansion.md](dynamic-team-expansion.md) — sibling protocol: Expertise-Gap / Expansion Request (runs after clarification). The **§End-to-End Walkthrough: Both Gates Together** section in that file shows both protocols running on the same task step by step, including cost shape and runtime behavior on Claude Code and Codex
- [initial-prompt-contract.md](initial-prompt-contract.md) — launch-prompt fields that reduce the need for clarification up front
- [traps-and-antipatterns.md](traps-and-antipatterns.md) — AI-slop anti-patterns this protocol prevents
- [foundations-grounding-communication](../../foundations-grounding-communication/SKILL.md) — theory owner for grounding and clarification: when to ask vs. proceed, and what counts as evidence of understanding
