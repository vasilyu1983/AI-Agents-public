---
name: foundations-theory-of-constraints
description: "Theory of Constraints primitives for focusing steps, drum-buffer-rope, throughput accounting, critical chain, and policy constraints. Use when sequencing by bottleneck."
compatibility: Portable core only.
version: "1.3"
last_validated: 2026-08-14
---

# Theory of Constraints Foundations


## When to Apply

**Apply theory-of-constraints when:**
- One bottleneck demonstrably gates total system throughput (the system has a constraint, not many)
- Roadmap or capacity-allocation under a hard limited resource (eng-weeks, GPU-hours, account-managers)
- Funnel debug where a single step blocks downstream conversion
- Policy constraint suspected (a rule, not a physical limit, is what's holding throughput)
- Subordination question — "should other steps slow down to match the bottleneck?"
- Post-AI adoption reassessment — when AI coding tools improve individual velocity but delivery metrics stay flat (DORA's throughput group: change lead time, deployment frequency, failed-deployment recovery time; instability group: change fail rate, deployment rework rate), re-run 5FS; the constraint has likely shifted downstream to code review, verification, or integration (DORA 2025, n≈5,000; corroborated by IT Revolution 2026 and Logilica 2025)
- LLM / agent-pipeline optimization — when end-to-end latency or task throughput of a multi-step AI pipeline is not meeting targets despite adding models or workers; the constraint is usually a specific stage (LLM decode, serialized tool execution, or a guardrail/eval step), not aggregate capacity — profile per stage before scaling

**Skip and use simpler alternatives when:**
- System has multiple roughly equal bottlenecks — TOC's "elevate one" model misfires; use queueing networks (foundations-queueing-theory)
- Throughput question is really a feedback-control question (oscillation, instability) — use foundations-control-theory
- The "constraint" is actually a strategic choice (we want this to be the limit) — TOC is a diagnostic, not a strategy
- Bottleneck moves run-to-run (no stable system) — stabilise before applying 5 focusing steps
- T or CU estimate ranges overlap enough that the ordering flips inside those ranges — ranking noise dominates the signal (no universal percentage cutoff; report ranges and check flip-sensitivity)
- Pure capacity addition is cheap and uncontroversial — just add capacity; TOC analysis is overhead

## Quick Reference

| # | Primitive | Core Question | Failure Mode It Addresses | Playbook |
|---|-----------|--------------|--------------------------|----------|
| 1 | Five Focusing Steps | Where should all improvement energy go? | Improvement energy scattered across non-constraints | [01](assets/templates/theory-of-constraints/01-five-focusing-steps.md) |
| 2 | Drum-Buffer-Rope | How do we schedule flow around the constraint? | WIP floods system; constraint starves; local optima destroy flow | [02](assets/templates/theory-of-constraints/02-drum-buffer-rope.md) |
| 3 | Throughput Accounting | How do we measure with T, I, OE instead of cost? | Cost-accounting drives local optimization at expense of throughput | [03](assets/templates/theory-of-constraints/03-throughput-accounting.md) |
| 4 | Evaporating Cloud | How do we dissolve a conflict without compromise? | Conflict resolved by compromise; invalid assumption never surfaced | [04](assets/templates/theory-of-constraints/04-evaporating-cloud.md) |
| 5 | Current Reality Tree | What is the root cause of our undesirable effects? | Root cause misidentified; multiple symptoms treated without finding cause | [05](assets/templates/theory-of-constraints/05-current-reality-tree.md) |
| 6 | Future Reality Tree | Will our injection actually fix the problem? | Solution deployed without validating it resolves root cause or checking side effects | [06](assets/templates/theory-of-constraints/06-future-reality-tree.md) |
| 7 | Prerequisite Tree | What intermediate objectives must come first? | Implementation stalls on unacknowledged obstacles | [07](assets/templates/theory-of-constraints/07-prerequisite-tree.md) |
| 8 | Transition Tree | What specific actions, in what order? | Action plan lists steps without logic connecting them; first obstacle stops progress | [08](assets/templates/theory-of-constraints/08-transition-tree.md) |
| 9 | Critical Chain | How do we schedule projects to prevent buffer hoarding? | Projects chronically late despite individual tasks finishing "on time" | [09](assets/templates/theory-of-constraints/09-critical-chain.md) |
| 10 | Policy Constraints | Is the constraint a rule or metric, not capacity? | Throughput constrained by rules/metrics; physical capacity elevated without effect | [10](assets/templates/theory-of-constraints/10-policy-constraints.md) |
| 11 | Thinking Processes | Which TP tool do I need? | Wrong TP tool selected; diagnosis and solution steps confused | [11](assets/templates/theory-of-constraints/11-thinking-processes.md) |

Formal grounding (systems constraint logic, flow synchronization, throughput accounting, conflict logic, cause-effect reasoning, dependency logic, project buffer theory) is mapped per primitive in [references/formal-theory-map.md](references/formal-theory-map.md) — load it when the task needs boundaries between TOC, queueing, Lean, and general bottleneck language.

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Calling every problem a constraint | TOC constraint is the system throughput limiter | Identify the current limiting factor with observable flow evidence |
| Confusing the constraint with the bottleneck-of-the-day | Persistent queue depth nominates a candidate but does not prove throughput sensitivity | Use multiple windows to screen candidates, then vary effective capacity or policy and measure accepted end-to-end throughput at fixed quality; see `references/patterns-scenarios-traps.md#constraint-vs-bottleneck-of-the-day-expert-judgment` |
| Assuming exactly one constraint always exists | Matrix orgs, near-tied capacity, and unstable processes can violate the single-constraint model | Check `references/patterns-scenarios-traps.md#when-the-single-constraint-assumption-breaks` before forcing a 5FS ranking |
| Improving non-constraints | Local improvement does not raise system throughput | Subordinate non-constraints to the constraint |
| Buying capacity before exploitation | Elevation is step 4, not step 1 | Exploit and subordinate first |
| Treating policy constraints as physical limits | Rules and metrics can cap throughput invisibly | Audit policies before capacity spend |
| Using critical chain as rebranded critical path | CCPM removes local padding and manages buffers | Track buffer consumption, not only task dates |
| Skipping logic validation | Thinking Process diagrams can encode bad assumptions | Use Categories of Legitimate Reservation-style checks |

Check [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) before using TOC as an operating prescription.

---

## Anti-Patterns

| Anti-Pattern | TOC Diagnosis | Fix |
|-------------|--------------|-----|
| Optimizing non-bottleneck steps | Violates step 3 of 5FS (subordinate); non-constraint improvements do not increase throughput | Apply 5FS first; prioritize the constraint without suspending required safety, maintenance or quality work |
| Treating the constraint as fixed | "We can't change that" accepted without evidence | Apply the Evaporating Cloud to surface the assumption that the constraint is immutable |
| Capacity vs. policy constraint confusion | Physical constraint elevated while a policy constraint caps throughput upstream | Audit rules and metrics before purchasing capacity; policy constraints are invisible but common |
| Throughput accounting ignored in favor of cost accounting | T/CU ranking skipped; product mix optimized on margin → wrong mix at the constraint | Define the goal, mandatory obligations, demand and shared capacities. Use T/CU ordering only for divisible independent work against one linear capacity; dependencies, deadlines, indivisibility or multiple capacities require a global feasible mix/schedule comparison |
| Critical chain treated as critical path | Individual task padding hoarded; Project Buffer undersized; buffer management ignored | Strip individual padding; enforce Project Buffer; track buffer consumption, not milestones |
| Solution deployed without FRT validation | FRT skipped; injection creates unintended side effects | Build the FRT before implementation; explicitly search for Negative Branch Reservations |
| UDEs patched without CRT | Symptoms recur because root cause untouched | Build a CRT from the last five recurring problems; solve the core, not the surface |
| Conflict resolved by compromise | Evaporating Cloud not used; invalid assumption sustains the conflict | Build the cloud; challenge every assumption on every arrow |

---

## Composition Recipes

### Roadmap Re-Prioritization

Re-sequence the product backlog by throughput impact, not stakeholder volume.

**Inputs:** List of initiatives, each with T (incremental sales revenue minus incremental totally variable costs per quarter, in currency) and CU (constraint units consumed, e.g. dev-weeks); total available CU for the planning period; any known policy constraints (mandatory-item rules, release gate policies) quoted verbatim.
**Rules:** T/CU is a screening ranking for one verified scarce resource with comparable marginal throughput, divisible work and no binding dependencies or demand caps. For indivisible initiatives, dependencies or multiple resources, formulate a constrained allocation and hand off to foundations-mathematical-optimization; ratio-greedy is not guaranteed optimal. Keep mandatory safety/compliance work as explicit feasibility constraints rather than treating it as a policy to eliminate.
**Outputs:** Ranked schedule table (initiative, T, CU, T/CU, rank, included/excluded); total CU consumed and slack; list of any policy constraints identified and their go/no-go disposition.

1. **Identify constraint** with 5FS (#1): which resource, team, or step caps delivery?
2. **Rank work by T/CU** with Throughput Accounting (#3): which items generate the most throughput per hour of constraint time?
3. **Audit for policy constraints** (#10): is the constraint a rule (approval gate, batch-release policy) rather than capacity?
4. **Add if conflict**: use Evaporating Cloud (#4) if two valid priorities conflict in the ranking.

**Synthetic worked example:** Q3 roadmap, eng capacity = constraint (40 dev-weeks). T is incremental sales revenue minus incremental totally variable costs per quarter; see [Goldratt UK’s throughput definition](https://goldratt.co.uk/sales-vs-throughput-know-which-of-your-sales-generate-the-most-revenue/).

| Initiative | T (Δthroughput/qtr) | CU (dev-weeks) | T/CU | Rank |
|---|---|---|---|---|
| Checkout speedup | $180k | 6 | $30k | 1 |
| New onboarding flow | $240k | 12 | $20k | 2 |
| Admin redesign | $100k | 10 | $10k | 3 |

Schedule by T/CU descending until CU exhausted: 6 + 12 + 10 = 28 dev-weeks → all three fit; 12 weeks slack for unknowns. Anti-pattern: ranking by raw T puts onboarding first, but it consumes 1.5× as much constraint time per dollar of T as checkout (12/240 versus 6/180). Fail signal: if a policy constraint (e.g., "every quarter must include a platform item") overrides T/CU, name and challenge the policy explicitly — a policy can encode legitimate obligations; investigate its rationale and preserve required constraints.

### Incident-Mode Flow Restoration

Restore throughput in a degraded or overloaded system without adding headcount.

**Inputs:** Candidate bottleneck steps from queue, wait-time, and utilization profiles; WIP at each step; accepted-throughput target and fixed quality definition; and capacity or policy interventions available for a replay, controlled change, or natural experiment.
**Rules:** Queue and utilization signals screen candidates. Before choosing the drum, verify that changing a candidate's effective capacity or policy changes accepted end-to-end throughput at the target quality. Apply the five focusing steps to the verified constraint; exploit and subordinate before buying capacity. Size the buffer from observed variation and apply the rope to bound intake. Re-test throughput sensitivity after each change because the constraint can move.
**Outputs:** Subordination plan specifying which upstream and downstream steps must change behavior to protect the drum; measurable throughput target with a named observation window (e.g., "≥ 40 tickets resolved per day over the next 5 business days"); buffer size and rope threshold with rationale; go/no-go on capacity elevation with supporting evidence.

1. **Identify constraint** with 5FS (#1): which step's marginal capacity or policy relaxation increases completed-system throughput? Use queue depth as a clue, then verify with a controlled change or natural experiment.
2. **Apply DBR** (#2): set the constraint as the drum; add a time buffer in front of it; apply the rope to freeze new intake above the buffer threshold.
3. **Exploit before elevating**: squeeze maximum output from existing constraint capacity before requesting more resources.
4. **Add if constraint is a rule**: audit for policy constraints (#10) — is intake or escalation throttled by a policy, not capacity?

### LLM / Agent-Pipeline Constraint Analysis

Apply 5FS and DBR to a multi-step LLM inference or multi-agent workflow when end-to-end latency or task throughput is not meeting targets despite adding more models or workers.

**Inputs:** End-to-end latency profile per pipeline stage (e.g., prompt construction, prefill, decode, tool-call dispatch, guardrail/eval, output parsing); observed queue depth per stage; throughput target (tasks completed per minute or second); any rate-limit or concurrency policies on external APIs or GPU pools.
**Rules:** Apply 5FS to the pipeline. Latency share and queue depth identify candidates, but the constraint is the stage whose added effective capacity or relaxed policy raises end-to-end throughput at the target quality. Confirm it with a controlled capacity change, shadow replay, or natural experiment; a slow stage can sit off the critical path, and a deep queue can be caused upstream. Profile your own pipeline, exploit before scaling, then set the verified constraint as the drum. Size a time buffer upstream from observed variation and apply the rope by rate-limiting intake. Audit rate limits, context caps, and serialized gates as possible policy constraints.
**Outputs:** Candidate stages from latency/queue profiles; intervention or replay result showing end-to-end throughput sensitivity at the fixed target quality; verified constraint stage; exploitation plan; DBR configuration; and policy-constraint audit.

1. **Identify constraint** with 5FS (#1): profile the flow, form candidates from latency/queues, then verify which stage changes end-to-end throughput when its effective capacity changes.
2. **Exploit** before scaling: cache reusable context; batch parallel tool calls; right-size models at non-constraint stages to free GPU/token budget for the constraint.
3. **Apply DBR** (#2): set the constraint stage as the drum; add a task-slot buffer upstream; apply the rope (max in-flight limit) to prevent queue flooding.
4. **Audit for policy constraints** (#10): check rate-limit tiers, sequential guardrail pipelines, and context-window policies — these are the most common invisible constraints in agent systems.

**Worked example:** agent pipeline — search → plan → tool-dispatch → eval → summarize. Profiling shows plan-stage decode at 68% of wall-clock, so plan is a candidate. In a shadow replay at the same task mix and quality threshold, increasing plan capacity by 50% raises accepted end-to-end completions by 31%, while increasing tool-dispatch capacity by 50% changes them by 2%; plan is therefore the current constraint. Prefix caching is then tested at the same quality gate. After it raises accepted throughput, repeat the intervention because the constraint may have moved to eval. The figures are illustrative protocol outputs, not portable performance claims.

### Policy Debugging

Diagnose why throughput is not improving despite available capacity.

**Inputs:** 5–10 Undesirable Effects (UDEs) with frequency and severity for each; candidate policy constraint quoted verbatim (the exact rule or metric suspected of capping throughput).
**Rules:** Build a Current Reality Tree (CRT, #5) — connect ≥3 UDEs to a single root via If→Then chains, each arrow stating sufficiency (not mere correlation); a thought experiment resolving UDEs makes the policy a candidate explanation, not a confirmed cause; validate with a controlled change, replay or natural experiment at fixed quality before claiming throughput sensitivity; if two legitimate requirements sustain the policy, build an Evaporating Cloud (#4) to surface the underlying assumption; validate the proposed policy change as an injection in a Future Reality Tree (#6) before implementing.
**Outputs:** CRT diagram with the named root cause and the candidate policy quoted verbatim; Evaporating Cloud with ≥3 assumption candidates on the arrows; go/no-go recommendation on policy change vs. capacity elevation, with the disconfirming evidence required to reverse the recommendation.

1. **Build a CRT** (#5): list the top UDEs; trace to root cause with "If…Then" logic.
2. **Apply Evaporating Cloud** (#4): if the root cause is sustained by a conflict between two requirements, build the cloud to surface and challenge the sustaining assumption.
3. **Validate with FRT** (#6): design the policy change as an injection; trace it forward to verify it resolves the UDEs without creating new ones.

---

## Workflow

1. Observe the system: collect 5–10 Undesirable Effects (UDEs) — concrete, negative, observable outcomes.
2. Use the [Quick Reference](#quick-reference) to select the right primitive. If no stable constraint exists (multiple roughly equal bottlenecks), stabilize first or use foundations-queueing-theory instead of TOC's "elevate one" model.
3. Open the per-primitive playbook in [assets/templates/theory-of-constraints/](assets/templates/theory-of-constraints/) for the full definition, inputs, outputs, failure modes, and worked example.
4. For multi-question scenarios, use the [Composition Recipes](#composition-recipes) or the full [assets/templates/theory-of-constraints/README.md](assets/templates/theory-of-constraints/README.md) to stack primitives.
5. For domain-specific applications (ops, product, software architecture, data engineering), load the consumer skill's `references/theory-of-constraints-applied.md` when available.

---

## Related Skills

The following consumer skills carry a domain `references/theory-of-constraints-applied.md` — load the consumer's copy for domain-specific recipes, thresholds, and worked examples; it points back here for the primitives:

- `agents-subagents`, `dev-ai-coding-metrics`, `ops-devops-platform`, `product-management`, `software-architecture-design`, `startup-business-models`

---

## Practical Decision Record

Use [decision and validation worksheet](references/decision-and-validation.md) for intake, model boundaries, uncertainty and checkable acceptance examples. [Regression cases](data/regression-cases.json) provide independent prompts and expected answers; these are fixtures, not executed agent results.

## Navigation

- Per-primitive playbooks: [assets/templates/theory-of-constraints/](assets/templates/theory-of-constraints/) (one file per primitive)
- Composition guide: [assets/templates/theory-of-constraints/README.md](assets/templates/theory-of-constraints/README.md)
- Formal theory map: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview: [references/primitives-overview.md](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Evidence Notes

- Primitives are sourced from primary Goldratt texts and leading secondary references (Dettmer 2007, Cox & Spencer 1998, Schragenheim et al.); numeric claims are calibrated guidelines, not universal constants — validate against your own system data. 5FS, DBR, and Throughput Accounting are the most empirically validated primitives; the Thinking Processes have strong practitioner support but limited controlled-study evidence. CCPM's strongest evidence is de Oliveira Martins et al. (2025), *Applied Sciences* 15(15):8147 — a review of mostly modeling/simulation studies, not field trials.
- AI-era constraint-shift claims (dev workflow and agent-pipeline latency) are correlational survey/preprint evidence, not controlled trials; see `data/sources.json` for the DORA 2025, Agent-X, and PASTE citations and their exact scope.
- Full dated correction history (Dettmer chapter-citation fix, DORA/agent-latency version updates, source drift) is in [references/evidence-log.md](references/evidence-log.md) — read it before citing a chapter number or an AI-era figure from this skill.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
