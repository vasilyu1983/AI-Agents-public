---
name: foundations-theory-of-constraints
description: "Theory of Constraints primitives for focusing steps, drum-buffer-rope, throughput accounting, critical chain, and policy constraints. Use when sequencing by bottleneck."
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Theory of Constraints Foundations


11 canonical Theory of Constraints primitives for diagnosing and exploiting system constraints. Primitives are domain-agnostic: the same Five Focusing Steps that fix a production line apply to a software delivery pipeline, a product roadmap, or a consulting engagement. Each primitive solves a specific class of throughput-limiting problem.

## When to Apply

**Apply theory-of-constraints when:**
- One bottleneck demonstrably gates total system throughput (the system has a constraint, not many)
- Roadmap or capacity-allocation under a hard limited resource (eng-weeks, GPU-hours, account-managers)
- Funnel debug where a single step blocks downstream conversion
- Policy constraint suspected (a rule, not a physical limit, is what's holding throughput)
- Subordination question — "should other steps slow down to match the bottleneck?"
- Post-AI adoption reassessment — when AI coding tools improve individual velocity but delivery metrics (lead time, deployment frequency, change failure rate) stay flat, re-run 5FS; the constraint has likely shifted downstream to code review, verification, or integration (DORA 2025, n≈5,000; corroborated by IT Revolution 2026 and Logilica 2025)
- LLM / agent-pipeline optimization — when end-to-end latency or task throughput of a multi-step AI pipeline is not meeting targets despite adding models or workers; the constraint is usually a specific stage (LLM decode, serialized tool execution, or a guardrail/eval step), not aggregate capacity — profile per stage before scaling

**Skip and use simpler alternatives when:**
- System has multiple roughly equal bottlenecks — TOC's "elevate one" model misfires; use queueing networks (foundations-queueing-theory)
- Throughput question is really a feedback-control question (oscillation, instability) — use foundations-control-theory
- The "constraint" is actually a strategic choice (we want this to be the limit) — TOC is a diagnostic, not a strategy
- Bottleneck moves run-to-run (no stable system) — stabilise before applying 5 focusing steps
- T/CU ratio differences are < 20% across initiatives — ranking noise dominates the signal
- Pure capacity addition is cheap and uncontroversial — just add capacity; TOC analysis is overhead

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Anti-Patterns](#anti-patterns)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes) — Roadmap Re-Prioritization · Incident-Mode Flow Restoration · LLM / Agent-Pipeline Constraint Analysis · Policy Debugging
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Navigation](#navigation)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| Primitive | Core Question | Recipe Stub |
|-----------|--------------|-------------|
| [Five Focusing Steps](#1-five-focusing-steps) | Where should all improvement energy go? | Identify constraint → exploit → subordinate → elevate → repeat |
| [Drum-Buffer-Rope](#2-drum-buffer-rope) | How do we schedule flow around the constraint? | Constraint = drum; time buffer before constraint; rope limits intake |
| [Throughput Accounting](#3-throughput-accounting) | How do we measure with T, I, OE instead of cost? | Rank decisions by T/CU (Throughput per Constraint Unit) |
| [Evaporating Cloud](#4-evaporating-cloud) | How do we dissolve a conflict without compromise? | Map A→B→D / A→C→D′; challenge the assumption on each arrow |
| [Current Reality Tree](#5-current-reality-tree) | What is the root cause of our undesirable effects? | List 5–10 UDEs; trace with "If…Then" to one Core Problem |
| [Future Reality Tree](#6-future-reality-tree) | Will our injection actually fix the problem? | Map injection → effects; find Negative Branch Reservations |
| [Prerequisite Tree](#7-prerequisite-tree) | What intermediate objectives must come first? | List obstacles; derive IOs; sequence dependencies |
| [Transition Tree](#8-transition-tree) | What specific actions, in what order? | For each IO: Need → Action → Effect; verify each effect is observable |
| [Critical Chain](#9-critical-chain) | How do we schedule projects to prevent buffer hoarding? | Strip individual padding; add Project Buffer at end; track buffer consumption |
| [Policy Constraints](#10-policy-constraints) | Is the constraint a rule or metric, not capacity? | Audit rules and metrics before elevating physical capacity |
| [Thinking Processes](#11-thinking-processes) | Which TP tool do I need? | CRT (diagnose) → EC (resolve conflict) → FRT (design) → PRT+TT (execute) |

---

## Primitive Index

Each primitive has a full playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources).

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Five Focusing Steps](assets/templates/theory-of-constraints/01-five-focusing-steps.md) | Improvement energy scattered across non-constraints |
| 2 | [Drum-Buffer-Rope](assets/templates/theory-of-constraints/02-drum-buffer-rope.md) | WIP floods system; constraint starves; local optima destroy flow |
| 3 | [Throughput Accounting](assets/templates/theory-of-constraints/03-throughput-accounting.md) | Cost-accounting drives local optimization at expense of throughput |
| 4 | [Evaporating Cloud](assets/templates/theory-of-constraints/04-evaporating-cloud.md) | Conflict resolved by compromise; invalid assumption never surfaced |
| 5 | [Current Reality Tree](assets/templates/theory-of-constraints/05-current-reality-tree.md) | Root cause misidentified; multiple symptoms treated without finding cause |
| 6 | [Future Reality Tree](assets/templates/theory-of-constraints/06-future-reality-tree.md) | Solution deployed without validating it resolves root cause or checking side effects |
| 7 | [Prerequisite Tree](assets/templates/theory-of-constraints/07-prerequisite-tree.md) | Implementation stalls on unacknowledged obstacles |
| 8 | [Transition Tree](assets/templates/theory-of-constraints/08-transition-tree.md) | Action plan lists steps without logic connecting them; first obstacle stops progress |
| 9 | [Critical Chain](assets/templates/theory-of-constraints/09-critical-chain.md) | Projects chronically late despite individual tasks finishing "on time" |
| 10 | [Policy Constraints](assets/templates/theory-of-constraints/10-policy-constraints.md) | Throughput constrained by rules/metrics; physical capacity elevated without effect |
| 11 | [Thinking Processes](assets/templates/theory-of-constraints/11-thinking-processes.md) | Wrong TP tool selected; diagnosis and solution steps confused |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Systems constraint logic | Need to identify the current throughput-limiting factor | #1, #10 |
| Flow synchronization | Need WIP control around a constraint | #2 |
| Throughput accounting | Need financial decisions under constrained capacity | #3 |
| Conflict logic | Need to dissolve a policy or priority conflict | #4 |
| Cause-effect reasoning | Need root-cause diagnosis and effect validation | #5, #6, #11 |
| Implementation dependency logic | Need obstacle sequencing and action logic | #7, #8 |
| Project buffer theory | Need project delivery under resource constraints | #9 |

Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs boundaries between TOC, queueing, Lean, and general bottleneck language.

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Calling every problem a constraint | TOC constraint is the system throughput limiter | Identify the current limiting factor with observable flow evidence |
| Confusing the constraint with the bottleneck-of-the-day | A single bad week's deepest queue is not necessarily the persistent system limiter | Require 3–4 observation cycles showing the same step before naming a constraint; see `references/patterns-scenarios-traps.md#constraint-vs-bottleneck-of-the-day-expert-judgment` |
| Assuming exactly one constraint always exists | Matrix orgs, near-tied capacity, and unstable processes can violate the single-constraint model | Check `references/patterns-scenarios-traps.md#when-the-single-constraint-assumption-breaks` before forcing a 5FS ranking |
| Improving non-constraints | Local improvement does not raise system throughput | Subordinate non-constraints to the constraint |
| Buying capacity before exploitation | Elevation is step 4, not step 1 | Exploit and subordinate first |
| Treating policy constraints as physical limits | Rules and metrics can cap throughput invisibly | Audit policies before capacity spend |
| Using critical chain as rebranded critical path | CCPM removes local padding and manages buffers | Track buffer consumption, not only task dates |
| Skipping logic validation | Thinking Process diagrams can encode bad assumptions | Use Categories of Legitimate Reservation-style checks |

Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before using TOC as an operating prescription.

---

## Anti-Patterns

| Anti-Pattern | TOC Diagnosis | Fix |
|-------------|--------------|-----|
| Optimizing non-bottleneck steps | Violates step 3 of 5FS (subordinate); non-constraint improvements do not increase throughput | Apply 5FS first; put a "do not improve" hold on non-constraints until constraint is broken |
| Treating the constraint as fixed | "We can't change that" accepted without evidence | Apply the Evaporating Cloud to surface the assumption that the constraint is immutable |
| Capacity vs. policy constraint confusion | Physical constraint elevated while a policy constraint caps throughput upstream | Audit rules and metrics before purchasing capacity; policy constraints are invisible but common |
| Throughput accounting ignored in favor of cost accounting | T/CU ranking skipped; product mix optimized on margin → wrong mix at the constraint | Reframe every product-mix or roadmap decision as T/CU ranking before committing |
| Critical chain treated as critical path | Individual task padding hoarded; Project Buffer undersized; buffer management ignored | Strip individual padding; enforce Project Buffer; track buffer consumption, not milestones |
| Solution deployed without FRT validation | FRT skipped; injection creates unintended side effects | Build the FRT before implementation; explicitly search for Negative Branch Reservations |
| UDEs patched without CRT | Symptoms recur because root cause untouched | Build a CRT from the last five recurring problems; solve the core, not the surface |
| Conflict resolved by compromise | Evaporating Cloud not used; invalid assumption sustains the conflict | Build the cloud; challenge every assumption on every arrow |

---

## Decision Checklist

- [ ] **Where to focus**: Is the constraint identified before investing in improvement? → 5FS (#1)
- [ ] **Flow scheduling**: Is WIP piling up ahead of one step? → DBR (#2)
- [ ] **Financial decision**: Is the decision being made on gross margin instead of T/CU? → Throughput Accounting (#3)
- [ ] **Deadlocked conflict**: Is a team stuck between two seemingly incompatible actions? → Evaporating Cloud (#4)
- [ ] **Root cause unclear**: Are multiple UDEs present with no shared explanation? → CRT (#5)
- [ ] **Solution untested**: Has the proposed injection been validated for side effects? → FRT (#6)
- [ ] **Implementation blocked**: Are unacknowledged obstacles stopping progress? → PRT (#7)
- [ ] **Actions unclear**: Is the action plan missing the logic that connects steps? → TT (#8)
- [ ] **Project lateness**: Are projects chronically late despite individual tasks completing on time? → Critical Chain (#9)
- [ ] **Invisible constraint**: Is throughput not improving despite available capacity? → Policy Constraints (#10)
- [ ] **Tool selection**: Unsure which Thinking Process tool to use? → Thinking Processes overview (#11)

---

## Composition Recipes

### Roadmap Re-Prioritization

Re-sequence the product backlog by throughput impact, not stakeholder volume.

**Inputs:** List of initiatives, each with T (revenue impact per quarter, in currency) and CU (constraint units consumed, e.g. dev-weeks); total available CU for the planning period; any known policy constraints (mandatory-item rules, release gate policies) quoted verbatim.
**Rules:** Compute T/CU for each initiative; rank descending by T/CU; schedule initiatives in rank order until cumulative CU equals total available CU; record remaining CU as slack; if a policy constraint forces an out-of-rank item, name it explicitly and apply Evaporating Cloud (#4) before accepting the override — do not silently accept it.
**Outputs:** Ranked schedule table (initiative, T, CU, T/CU, rank, included/excluded); total CU consumed and slack; list of any policy constraints identified and their go/no-go disposition.

1. **Identify constraint** with 5FS (#1): which resource, team, or step caps delivery?
2. **Rank work by T/CU** with Throughput Accounting (#3): which items generate the most throughput per hour of constraint time?
3. **Audit for policy constraints** (#10): is the constraint a rule (approval gate, batch-release policy) rather than capacity?
4. **Add if conflict**: use Evaporating Cloud (#4) if two valid priorities conflict in the ranking.

**Worked example:** Q3 roadmap, eng capacity = constraint (40 dev-weeks). Throughput = revenue impact per quarter.

| Initiative | T (Δrev/qtr) | CU (dev-weeks) | T/CU | Rank |
|---|---|---|---|---|
| Checkout speedup | $180k | 6 | $30k | 1 |
| New onboarding flow | $240k | 12 | $20k | 2 |
| Admin redesign | $100k | 10 | $10k | 3 |

Schedule by T/CU descending until CU exhausted: 6 + 12 + 10 = 28 dev-weeks → all three fit; 12 weeks slack for unknowns. Anti-pattern: ranking by raw T puts onboarding first, but it consumes 2× the constraint per dollar. Fail signal: if a policy constraint (e.g., "every quarter must include a platform item") overrides T/CU, name and challenge the policy explicitly — most policy constraints are stale.

### Incident-Mode Flow Restoration

Restore throughput in a degraded or overloaded system without adding headcount.

**Inputs:** Current bottleneck step (identified by queue depth or utilization evidence); WIP count at each step upstream and downstream of the bottleneck; throughput target (units/hour, tickets/day, or equivalent); any intake or escalation policies that may be throttling flow.
**Rules:** Exploit before elevate — apply all five focusing steps in order; do not request additional headcount or capacity until exploitation of the current constraint is confirmed exhausted; set the bottleneck as the drum; size the time buffer to absorb statistical variation ahead of the constraint (not a fixed number — derive from observed cycle time variance); apply the rope to freeze new intake when WIP upstream of the constraint exceeds the buffer threshold; if throughput fails to improve after exploitation, audit for policy constraints (#10) before concluding that physical capacity elevation is required.
**Outputs:** Subordination plan specifying which upstream and downstream steps must change behavior to protect the drum; measurable throughput target with a named observation window (e.g., "≥ 40 tickets resolved per day over the next 5 business days"); buffer size and rope threshold with rationale; go/no-go on capacity elevation with supporting evidence.

1. **Identify constraint** with 5FS (#1): which step has the deepest queue right now?
2. **Apply DBR** (#2): set the constraint as the drum; add a time buffer in front of it; apply the rope to freeze new intake above the buffer threshold.
3. **Exploit before elevating**: squeeze maximum output from existing constraint capacity before requesting more resources.
4. **Add if constraint is a rule**: audit for policy constraints (#10) — is intake or escalation throttled by a policy, not capacity?

### LLM / Agent-Pipeline Constraint Analysis

Apply 5FS and DBR to a multi-step LLM inference or multi-agent workflow when end-to-end latency or task throughput is not meeting targets despite adding more models or workers.

**Inputs:** End-to-end latency profile per pipeline stage (e.g., prompt construction, prefill, decode, tool-call dispatch, guardrail/eval, output parsing); observed queue depth per stage; throughput target (tasks completed per minute or second); any rate-limit or concurrency policies on external APIs or GPU pools.
**Rules:** Apply 5FS to the pipeline — the constraint is the stage with the deepest queue or the highest share of wall-clock time. Do not assume which stage that is: measured breakdowns differ sharply by deployment. On-device agents split latency between prefill and decode (Agent-X, arXiv:2605.10380: decode 68.7%, prefill 21.7%, with Planner and Arbiter LLM calls together 90.4% of total), whereas server-class cloud inference is decode-dominated (>95% in the same paper's comparison). In tool-heavy agents the serialized LLM→tool loop dominates instead — tool execution is 36–60% of request time depending on task type (arXiv:2603.18897). Profile your own pipeline; the constraint stage is an empirical question. Exploit before scaling: cache KV state, batch or speculatively overlap tool calls, parallelize independent sub-agents, right-size models per stage (use a smaller model for routing/triage steps, reserve the large model for the constraint stage). Set the constraint stage as the drum; size a time buffer upstream of it to absorb burst variation; apply the rope by rate-limiting intake (e.g., max in-flight tasks) to prevent the constraint from starving. Audit for policy constraints (#10) — rate limits, context-window caps, and sequential-approval gates are common invisible policy constraints in agent pipelines.
**Outputs:** Constraint stage named with evidence (latency share or queue depth); exploitation plan (caching, batching, model right-sizing) applied before adding capacity; DBR configuration: drum = constraint stage, buffer size (in ms or task slots), rope threshold (max concurrent in-flight tasks upstream); policy constraint audit result with go/no-go on capacity elevation.

1. **Identify constraint** with 5FS (#1): profile latency per stage; the highest-latency or deepest-queued stage is the drum.
2. **Exploit** before scaling: cache reusable context; batch parallel tool calls; right-size models at non-constraint stages to free GPU/token budget for the constraint.
3. **Apply DBR** (#2): set the constraint stage as the drum; add a task-slot buffer upstream; apply the rope (max in-flight limit) to prevent queue flooding.
4. **Audit for policy constraints** (#10): check rate-limit tiers, sequential guardrail pipelines, and context-window policies — these are the most common invisible constraints in agent systems.

**Worked example:** agent pipeline — search → plan → tool-dispatch → eval → summarize. Profiling this pipeline shows plan-stage decode at 68% of wall-clock, so plan is the drum. Exploitation: cache the system prompt prefix (KV reuse); route simple planning decisions to a smaller model. Throughput roughly doubles; the constraint then moves to the eval/guardrail stage, so re-run 5FS. Note the profile is what identified the drum — a tool-heavy pipeline profiled the same way would likely have named tool-dispatch instead. Do not add GPUs before verifying exploitation is exhausted.

### Policy Debugging

Diagnose why throughput is not improving despite available capacity.

**Inputs:** 5–10 Undesirable Effects (UDEs) with frequency and severity for each; candidate policy constraint quoted verbatim (the exact rule or metric suspected of capping throughput).
**Rules:** Build a Current Reality Tree (CRT, #5) — connect ≥3 UDEs to a single root via If→Then chains, each arrow stating sufficiency (not mere correlation); the policy is confirmed as the root constraint if removing it in a thought experiment eliminates ≥2 UDEs without requiring any physical capacity change; if two legitimate requirements sustain the policy, build an Evaporating Cloud (#4) to surface the underlying assumption; validate the proposed policy change as an injection in a Future Reality Tree (#6) before implementing.
**Outputs:** CRT diagram with the named root cause and the candidate policy quoted verbatim; Evaporating Cloud with ≥3 assumption candidates on the arrows; go/no-go recommendation on policy change vs. capacity elevation, with the disconfirming evidence required to reverse the recommendation.

1. **Build a CRT** (#5): list the top UDEs; trace to root cause with "If…Then" logic.
2. **Apply Evaporating Cloud** (#4): if the root cause is sustained by a conflict between two requirements, build the cloud to surface and challenge the sustaining assumption.
3. **Validate with FRT** (#6): design the policy change as an injection; trace it forward to verify it resolves the UDEs without creating new ones.

---

## Workflow

1. Observe the system: collect 5–10 Undesirable Effects (UDEs) — concrete, negative, observable outcomes.
2. Use the [Decision Checklist](#decision-checklist) to select the right primitive.
3. Open the per-primitive playbook in [`assets/templates/theory-of-constraints/`](assets/templates/theory-of-constraints/) for the full definition, inputs, outputs, failure modes, and worked example.
4. For multi-question scenarios, use the [Composition Recipes](#composition-recipes) or the full [`assets/templates/theory-of-constraints/README.md`](assets/templates/theory-of-constraints/README.md) to stack primitives.
5. For domain-specific applications (ops, product, software architecture, data engineering), load the consumer skill's `references/theory-of-constraints-applied.md` when available.

---

## ASCII Flow

```text
Throughput-limiting system problem
  -> Collect observable undesirable effects
  -> Identify current constraint
     +-- no stable constraint -> stabilize or use queueing networks
     +-- constraint found -> exploit it before adding capacity
  -> Subordinate non-constraints to the bottleneck
  -> Elevate constraint only when exploitation is exhausted
  -> Repeat and return throughput, constraint, policy changes, and next constraint
```

---

## Related Skills

- _Consumer skills will link here when applied recipes are added._

---

## Navigation

- Per-primitive playbooks: [`assets/templates/theory-of-constraints/`](assets/templates/theory-of-constraints/) (one file per primitive)
- Composition guide: [`assets/templates/theory-of-constraints/README.md`](assets/templates/theory-of-constraints/README.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Fact-Checking

- All primitives are sourced from primary Goldratt texts and the leading secondary references (Dettmer 2007, Cox & Spencer 1998, Schragenheim et al.).
- Numeric claims (e.g., buffer sizing heuristics) are calibrated guidelines, not universal constants — validate against actual system data before applying.
- TOC was developed primarily in manufacturing and distribution contexts; knowledge-work and software applications are well-established. Canonical software-lineage sources: *The Phoenix Project* (Kim et al. 2013), *The DevOps Handbook* (Kim et al. 2016), *Project to Product / Flow Framework* (Kersten 2018), and *Flow Engineering* (Pereira & Davis 2024). All available at `data/sources.json`.
- The Five Focusing Steps, DBR, and Throughput Accounting are the most empirically validated primitives; the Thinking Processes are logic-based frameworks with strong practitioner support but limited controlled-study evidence.
- CCPM evidence base: de Oliveira Martins et al. (2025), *Applied Sciences* 15(15):8147, DOI 10.3390/app15158147 — systematic review of 62 CCPM studies (Scopus + Web of Science, 2014–2025). The strongest available peer-reviewed evidence for this primitive, but note what it does and does not establish: most included studies are modeling and simulation rather than controlled field trials, and construction/manufacturing dominate the sample. It is evidence that CCPM is actively researched and simulated favourably, not proof of field effect sizes in knowledge work. See `09-critical-chain.md`.
- AI-era constraint shift (dev workflow): upgraded 2026-08-14 from practitioner report to survey evidence. DORA's *2025 State of AI-assisted Software Development* (Google Cloud, n≈5,000, surveyed June–July 2025) found ~90% AI adoption and that higher AI adoption raises both delivery throughput and delivery *instability*, with time saved in generation reallocated to verification overhead — i.e. the constraint moves from writing code to reviewing and verifying it. Still correlational survey data, not a controlled trial. Corroborated by IT Revolution (Jan 2026) and Logilica (Dec 2025) practitioner analyses. Re-run 5FS after significant AI tool adoption.
- AI-era constraint shift (runtime / agent pipelines): corrected 2026-08-14. Earlier revisions stated that Planner/Arbiter decode accounts for "~70% of total agent latency" as a general pattern. That figure came from Agent-X (arXiv:2605.10380), which measures an **on-device** agent on an M4 Pro; the same paper reports that server-class cloud inference is decode-dominated at >95%, so the on-device split does not generalize to cloud pipelines. Separately, tool-heavy agents are bottlenecked by the serialized LLM→tool loop, with tool execution at 36–60% of request time (arXiv:2603.18897). The load-bearing claim is the method, not any single percentage: profile per stage before scaling, and exploit (KV reuse, tool-call overlap, model right-sizing) before adding GPU capacity. Evidence grade B+: peer-reviewed-venue preprints measuring specific systems, not a general law.
- **2026-07-11 correction**: earlier revisions of the per-primitive playbooks cited specific chapter numbers from Dettmer (2007), *The Logical Thinking Process*, for six primitives (5FS, Evaporating Cloud, CRT, FRT, PRT, TT). A spot-check against the publisher's table of contents confirmed the Evaporating Cloud chapter number was wrong (cited as Ch. 6; published contents place it at Ch. 5) and that the Five Focusing Steps citation to a specific Dettmer chapter was misleading (5FS originates in Goldratt's *The Goal*, not in Dettmer's Thinking-Processes-focused book). All chapter-specific citations across the six affected files were replaced with topic-level references and an explicit instruction to verify against the reader's own printing before citing a chapter number. Treat any chapter-level citation for this book as unverified until checked directly.
- TOC and Kanban are complementary, not competing: the modern Kanban Method draws directly on TOC constraint logic (WIP limits as rope, bottleneck exploitation as 5FS). See `references/formal-theory-map.md` for the practical distinction and the common failure mode (running Kanban without knowing the constraint).
- Critical Chain's multitasking-cost claims mix two evidence streams that should not be conflated: Goldratt's own throughput-loss percentages (practitioner illustration, not measured) and independent, peer-reviewed cognitive-psychology research on task-switching costs (Rubinstein, Meyer & Evans 2001) that corroborates the mechanism but not Goldratt's specific numbers. See `09-critical-chain.md`.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
