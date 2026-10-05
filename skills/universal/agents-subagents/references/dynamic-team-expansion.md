---
description: Expertise-Gap and Expansion Request protocol for pulling more members mid-task.
last_verified: 2026-09-16
status: stable
---

# Dynamic Team Expansion Protocol

When a team realizes mid-task that it lacks expertise, pull additional members from the installed pool without redesigning the team. This document defines the contract between members, the synthesis owner, and the lead thread.

**Runs second, after [clarification-questions-protocol.md](clarification-questions-protocol.md).** If the brief is ambiguous, the team does not yet know what expertise it lacks — clarify first, then expand.

## Table of Contents

- [Summary](#summary)
- [Why This Protocol Exists](#why-this-protocol-exists)
- [Pattern Used](#pattern-used)
- [Contract](#contract)
- [End-to-End Flow](#end-to-end-flow)
- [Worked Example](#worked-example)
- [End-to-End Walkthrough: Both Gates Together](#end-to-end-walkthrough-both-gates-together)
- [Guardrails](#guardrails)
- [When Not to Use](#when-not-to-use)
- [Related References](#related-references)

## Summary

A team member can flag missing expertise as a structured `Expertise Gaps` entry naming a specific installed member and a narrow question. The synthesis owner collects those entries, partitions them into load-bearing vs. nice-to-have, and either emits an `Expansion Request` (blocking) or proceeds while listing unaddressed gaps. The lead thread sees the expansion request, re-dispatches the named member, and feeds the response back for a second synthesis pass.

No new runtime features are needed. The contract runs over existing Claude Code subagents and Codex agents.

## Why This Protocol Exists

Teams are composed at install time. Real tasks reveal gaps that team designers could not predict. Without a protocol, gaps either go unspoken (the team produces a confident-sounding answer built on wobbly ground) or cause the user to manually dispatch follow-ups (slow, breaks the synthesis flow). This protocol makes the gap explicit, auditable, and automatic.

## Pattern Used

This is the **lead-mediated escalation** pattern (also called supervisor-worker or orchestrator-worker in the literature). Every major multi-agent framework converges on it:

- Claude Agent SDK: orchestrator-workers ([Building effective agents](https://www.anthropic.com/research/building-effective-agents))
- LangGraph: `supervisor` graph
- AutoGen: `GroupChat` with speaker selection
- CrewAI: `Process.hierarchical`
- OpenAI Agents SDK: `handoff` with dynamic targets

Peer-to-peer self-augmentation (member-spawns-member) is technically possible in some runtimes but creates cost, auditability, and coordination problems. This protocol stays lead-mediated.

## Contract

### Member side — flag the gap

Every perspective-agent output may include an `Expertise Gaps` block (already wired into `agents/templates/perspective-agent.md`):

```
### Expertise Gaps (optional, omit if none)
- missing_member: <exact name from ~/.claude/agents/ or ~/.codex/agents/>
  question: <one sentence — the narrow question this member would answer>
  load_bearing: <true | false>
```

Rules:
- Only flag when a concrete catalog member could resolve the gap. "Need more context" is not a gap.
- Name must match an installed member. Unknown roles are dead ends.
- Load-bearing means synthesis **cannot** reach a confident recommendation without this input. Nice-to-have means the input would sharpen, not change, the recommendation.

### Synthesis owner side — handle the gaps

The debate synthesizer (or the team's designated `synthesis_owner`) runs gap handling before producing the decision log (already wired into `agents/templates/debate-synthesizer.md`):

1. Collect all gap entries; deduplicate by member.
2. If any gap is load-bearing → emit an `Expansion Request` block and stop.
3. If only nice-to-have gaps exist → proceed with the decision log and list them under `Unaddressed Gaps`.

Expansion Request format:

```
## Expansion Request

**Reason:** <why the team cannot finish without more input>

### Members to dispatch
- <member-name> — <narrow question>
- <member-name> — <narrow question>

### After expansion
Re-synthesize with the additional input, then produce the decision log.
```

### Lead thread side — re-dispatch and re-synthesize

When the synthesis returns an Expansion Request:

1. Verify each named member exists in the local agent pool. If missing, surface the miss to the user and stop — do not silently skip.
2. Dispatch each named member with only the narrow question, not the full task context. Narrow scope keeps the second pass cheap and auditable.
3. Collect responses.
4. Re-invoke the synthesizer with the original perspectives **plus** the new inputs, marked as a second pass.
5. Expect either a decision log or at most one more expansion request. If a third expansion is requested, escalate to the user — runaway expansion is a signal the original team composition is wrong for the task.

## End-to-End Flow

```
Lead thread
   │
   ├─▶ Dispatch team members (parallel)
   │      │
   │      ├─▶ Member A → position + possibly Expertise Gaps
   │      ├─▶ Member B → position + possibly Expertise Gaps
   │      └─▶ Member C → position
   │
   ├─▶ Synthesis owner
   │      │
   │      ├─▶ Scan for gaps
   │      ├─▶ If load-bearing → Expansion Request (stop)
   │      └─▶ Else → Decision Log + Unaddressed Gaps section
   │
   ├─▶ [If Expansion Request]
   │      ├─▶ Dispatch named members with narrow questions
   │      └─▶ Re-invoke synthesis owner with extended context
   │
   └─▶ Final Decision Log
```

## Worked Example

**Workflow mode**: `expert-board` with `idea-evaluation`, evaluating a proposed SaaS observability tool.

**Perspectives dispatched**: product-strategist, startup-painpoint-scout, startup-competitive-analyst, software-solution-architect, ops-cost-optimizer, dev-feature-researcher.

`software-solution-architect` output includes:

```
### Expertise Gaps
- missing_member: software-appsec-pipeline-engineer
  question: Does this vendor's ingest agent create a supply-chain attack path when embedded in our CI runners?
  load_bearing: true
```

`ops-cost-optimizer` output includes:

```
### Expertise Gaps
- missing_member: data-governance-privacy-lead
  question: Are the vendor's log-retention defaults compatible with UK-ICO retention obligations for user-tagged logs?
  load_bearing: true
```

Synthesis owner (`product-strategist`) emits:

```
## Expansion Request

**Reason:** Two load-bearing gaps block the adopt/reject recommendation: CI supply-chain exposure and log-retention compliance.

### Members to dispatch
- software-appsec-pipeline-engineer — Does this vendor's ingest agent create a supply-chain attack path when embedded in our CI runners?
- data-governance-privacy-lead — Are the vendor's log-retention defaults compatible with UK-ICO retention obligations for user-tagged logs?

### After expansion
Re-synthesize with the additional input, then produce the decision log.
```

Lead thread dispatches both, feeds responses back, second synthesis pass produces the final decision log.

## End-to-End Walkthrough: Both Gates Together

The previous sections define the contract. This section shows what actually happens, step by step, when both the clarification gate and the expansion gate fire on the same task. Use this to understand runtime behavior before launching a team for the first time.

### Scenario

You type into your main session (Claude Code or Codex):

> "Run expert-board in idea-evaluation mode to evaluate adopting Datadog as our observability platform."

### Step 1 — Lead dispatches the full team

The main session (= lead thread) dispatches all 6 members in parallel with the team brief and the debate method plus masks from the repository recipe.

```
Lead ──┬──▶ product-strategist
       ├──▶ startup-painpoint-scout
       ├──▶ startup-competitive-analyst
       ├──▶ software-solution-architect
       ├──▶ ops-cost-optimizer
       └──▶ dev-feature-researcher
```

### Step 2 — Members run and emit outputs

Each member follows the perspective-agent contract. Two members hit issues.

`ops-cost-optimizer` returns (abbreviated):

```markdown
## ops-cost-optimizer Position

### Clarifying Questions
1. question: What is the current log volume (GB/day) and host count?
   why_load_bearing: Datadog pricing scales non-linearly; recommendation flips above ~500 hosts or 200GB/day.
   assumed_default: ~50 hosts, ~20GB/day logs.

**Stance:** conditional
[arguments, risks, modifications...]

### Expertise Gaps
- missing_member: data-governance-privacy-lead
  question: Do Datadog's default log retention settings meet UK-ICO obligations?
  load_bearing: true
```

`software-solution-architect` returns:

```markdown
## software-solution-architect Position

### Expertise Gaps
- missing_member: software-appsec-pipeline-engineer
  question: Does Datadog's ingest agent create a supply-chain path through our CI runners?
  load_bearing: true

**Stance:** conditional
[arguments...]
```

The other four return clean positions.

### Step 3 — Synthesizer runs the gates in order

The synthesizer (= the team's `synthesis_owner`, `product-strategist` here) runs Gate 1 before Gate 2.

**Gate 1 — Clarifying Questions**. Collects: "What is the current log volume and host count?" Load-bearing. Synthesizer **stops** and does **not** run Gate 2 yet. Emits:

```markdown
## Clarification Request

**Reason:** Cost recommendation flips on infrastructure scale; cannot proceed without it.

### Questions for the user
1. What is the current log volume (GB/day) and host count?
   why it matters: Datadog pricing scales non-linearly; above 500 hosts or 200GB/day the TCO case inverts.
   team's default if unanswered: ~50 hosts, ~20GB/day logs.

### After clarification
Re-dispatch the team with the updated brief, then re-synthesize.
```

### Step 4 — Lead relays to you

The main session shows you the Clarification Request. You answer:

> "180 hosts, 80GB/day logs, growing ~15% per quarter."

### Step 5 — Lead re-dispatches the full team

All 6 members run again with the updated brief. This time nobody emits clarifying questions (the brief now has the scale numbers). Synthesizer moves to Gate 2.

**Gate 2 — Expertise Gaps**. The two gaps from Step 2 still stand. Synthesizer emits:

```markdown
## Expansion Request

**Reason:** Two load-bearing gaps block the adopt/reject recommendation.

### Members to dispatch
- software-appsec-pipeline-engineer — Does Datadog's ingest agent create a supply-chain path through our CI runners?
- data-governance-privacy-lead — Do Datadog's default log retention settings meet UK-ICO obligations?

### After expansion
Re-synthesize with the additional input, then produce the decision log.
```

### Step 6 — Lead dispatches the two additional members

Lead verifies both members exist in `~/.claude/agents/`. Dispatches each with **only the narrow question**, not the full task context. Narrow scope keeps the second pass cheap and auditable.

```
Lead ──┬──▶ software-appsec-pipeline-engineer (narrow question only)
       └──▶ data-governance-privacy-lead (narrow question only)
```

### Step 7 — Synthesizer runs a second pass

Synthesizer now has 6 post-clarification perspectives plus 2 narrow second-pass answers. Both gates pass (no new clarifying questions, no new expertise gaps). Produces the decision log:

```markdown
## Decision Log

**Decision prompt:** Adopt Datadog as observability platform?
**Date:** 2026-04-23
**Personas consulted:** [6 team + 2 expansion, with stances]

### Recommendation
[Clear verdict]

### Rationale
[Strongest arguments across all 8 perspectives]

### Key Tradeoff
[What is being sacrificed and why acceptable]

### Dissent
[Strongest opposing argument, why it lost]

### Conditions
[Guardrails — e.g., "If log volume exceeds 200GB/day, re-run this analysis"]

### Assumptions Taken
- Growth trajectory ~15% per quarter — user-supplied; used as-is

### Unaddressed Gaps
(none — both load-bearing gaps resolved via expansion)

### Action Items
- [ ] ...
```

### What the user sees

Three lead-thread messages total across the run:

1. **Clarification Request** from the team → user answers
2. **Expansion Request** from the team → user approves (or redirects)
3. **Decision Log** from the team → final output

### Dispatch graph

```
          ┌─────────────────────────────┐
          │  LEAD THREAD (your session) │
          └──────────────┬──────────────┘
                         │
       ┌─────────────────┼───────────────────┐
       │                 │                   │
  dispatch 1        dispatch 2          dispatch 3
 (full team, 6)    (re-dispatch, 6)    (narrow 2-member)
       │                 │                   │
       ▼                 ▼                   ▼
 Clarification       Expansion        Final Decision
  Request            Request              Log
       │                 │
       └── your answer ──┴── your approve ───┘
```

Three dispatches from the lead thread. Members never call each other directly. Every decision point is visible and user-steered. No silent assumptions — every one is either answered, defaulted with the default named, or flagged as unaddressed.

### Cost shape

Relative cost units (single member-run = 1x):

| Dispatch | Members | Cost |
|---|---|---|
| 1. Initial team | 6 | 6x |
| 2. Re-dispatch after clarification | 6 | 6x |
| 3. Expansion (narrow questions) | 2 | ~0.5x (narrow scope, short prompt) |
| 4. Synthesizer passes | 3 | ~1.5x |
| **Total** | 17 member-runs (6 + 6 + 2 + 3) | **~14x** |

The protocol adds discovery, specialist, critic, and synthesis passes. Price it from observed calls, model/effort, cache usage, tools, and retries; do not reuse a fixed multiplier across runtimes. Compare the defended recommendation with a simpler baseline on decision quality and rework before claiming the extra passes were economical.

### Runtime parity — Claude Code and Codex

The protocol runs identically on both runtimes because all three dispatches originate from the lead thread, not from peer members. Members in both catalogs have the same read-only tool set (no `Agent` tool by default), so peer-to-peer spawning is not used. See [runtime-surfaces.md](runtime-surfaces.md) for the surface-by-surface detail.

### Short-circuits

Common variations on this flow:

- **No clarification needed**: Step 3 Gate 1 is empty → skip to Gate 2 directly. If Gate 2 also empty, decision log on the first pass (simple 6x + synthesis).
- **Clarification only, no gaps**: after Step 5, Gate 2 is also empty → decision log. ~12x total.
- **Gaps only, no clarification**: Step 3 Gate 1 empty, Gate 2 fires → expansion → decision log. ~8.5x total.
- **User declines to answer clarification**: team applies the stated defaults and the decision log lists them under `Assumptions Taken`. No re-dispatch.
- **User redirects on expansion**: user says "skip the AppSec check, we'll handle that separately" → synthesizer proceeds without it and records it under `Unaddressed Gaps`.

## Guardrails

- **Budget the expansion**: one expansion cycle per task is typical, two is tolerable, three is a signal that the team was wrong for the task.
- **Narrow questions only**: the second-pass member receives one question, not the full task context. Keeps cost and latency bounded.
- **Auditability**: the final decision log must reference which members were dispatched in the second pass so the audit trail stays clean.
- **No silent skipping**: if a named member is missing from the local pool, surface it — do not pretend the synthesis is complete.

## When Not to Use

- **Low-stakes or time-boxed tasks**: if the decision is reversible and the user needs an answer in minutes, accept the nice-to-have gaps in the decision log rather than triggering expansion.
- **Incident response**: speed beats completeness; run the team's best current answer and follow up async.
- **Single-member dispatches**: expansion is for teams. A standalone subagent that hits an expertise wall should simply return a "I cannot answer this — try X" message to the user.

## Defensive-Output Pattern Family

This protocol is one of two defensive-output patterns the runtime uses to prevent AI slop. The two run in order:

| Order | Protocol | Trigger | Fix |
|---|---|---|---|
| 1st | [clarification-questions-protocol.md](clarification-questions-protocol.md) | Brief is ambiguous | User provides missing facts |
| 2nd | Expertise-Gap / Expansion (this doc) | Team lacks expertise for the task | Pull additional members from the catalog |

Both protocols are explicit, structured, and bounded — they replace the silent-assumption failure mode with a visible request.

## Related References

- [clarification-questions-protocol.md](clarification-questions-protocol.md) — prior-gate defensive output; runs before expansion
- [agents/templates/perspective-agent.md](../../../../agents/templates/perspective-agent.md) — member-side output contract including `Expertise Gaps`
- [agents/templates/debate-synthesizer.md](../../../../agents/templates/debate-synthesizer.md) — synthesis-side gap handling and Expansion Request format
- [team-member-matrix.md](team-member-matrix.md) — which members are available to pull in
- [debate-quickstart.md](debate-quickstart.md) — base debate flow this protocol extends
- [cost-control.md](cost-control.md) — cost implications of second-pass expansion
- [traps-and-antipatterns.md](traps-and-antipatterns.md) — silent-assumption and confident-slop anti-patterns these protocols prevent
