---
description: Theory of Constraints applied to product management — roadmap re-prioritization by constraint, funnel-stage bottleneck identification, throughput accounting on feature delivery, CRT for backlog stalls, FRT for intervention design, policy-constraint detection on roadmaps, and critical chain for milestone-driven delivery. Anchored to primitives #1–#11 from foundations-theory-of-constraints.
last_verified: 2026-05-02
status: stable
---

# Theory of Constraints Applied: Product Management

> **Gate before invoking:** Check [`foundations-theory-of-constraints` § When to Apply](../../foundations-theory-of-constraints/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Roadmap Re-Prioritization by Constraint (5FS)](#p1--roadmap-re-prioritization-by-constraint-5fs)
  - [P2 — Funnel-Stage Bottleneck Identification (DBR)](#p2--funnel-stage-bottleneck-identification-dbr)
  - [P3 — Throughput Accounting Applied to Feature Delivery](#p3--throughput-accounting-applied-to-feature-delivery)
  - [P5 — Current Reality Tree to Diagnose Backlog Stalls](#p5--current-reality-tree-to-diagnose-backlog-stalls)
  - [P6 — Future Reality Tree to Design Interventions](#p6--future-reality-tree-to-design-interventions)
  - [P9 — Critical Chain for Milestone-Driven Delivery](#p9--critical-chain-for-milestone-driven-delivery)
  - [P10 — Policy-Constraint Detection on Roadmaps](#p10--policy-constraint-detection-on-roadmaps)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Prioritizing High-Impact Items That Are Not Blocking Flow](#a1--prioritizing-high-impact-items-that-are-not-blocking-flow)
  - [A2 — Cost-Accounting Features Instead of Throughput-Accounting Them](#a2--cost-accounting-features-instead-of-throughput-accounting-them)
  - [A3 — Optimizing a Non-Bottleneck Stage](#a3--optimizing-a-non-bottleneck-stage)
  - [A4 — Critical-Path Estimation on Roadmap Items](#a4--critical-path-estimation-on-roadmap-items)
  - [A5 — Ignoring Policy Constraints in Scope Cuts](#a5--ignoring-policy-constraints-in-scope-cuts)
- [Recipes](#recipes)
  - [R1 — Backlog Re-Rank by Bottleneck](#r1--backlog-re-rank-by-bottleneck)
  - [R2 — Funnel Debug via TOC](#r2--funnel-debug-via-toc)
  - [R3 — Roadmap T-I-OE Check](#r3--roadmap-t-i-oe-check)
- [Composition](#composition)
- [Sources](#sources)

---

## Framing Note

Most roadmap decisions are made the wrong way: stakeholder pressure, loudest voice, or RICE scores that don't account for where work actually gets stuck. The underlying failure is the same one Goldratt diagnosed in factories — improvement energy scatters across the entire system instead of concentrating on the single stage that limits total throughput.

This file applies the 11 primitives from `foundations-theory-of-constraints` to the specific situations that arise in product roadmaps, activation funnels, and milestone-driven delivery. The primitives are domain-agnostic; this file is the PM-specific application layer. For the underlying mechanics of each primitive — definitions, failure modes, and worked examples — open the linked playbooks in the foundation skill.

A note on pattern numbering: pattern numbers (P1, P2, etc.) match the TOC primitive number from the foundation skill to make cross-referencing unambiguous. P3, P5, P6, P9, and P10 match the primitives directly; P1 and P2 are also numbered to match.

---

## Pattern Catalog

### P1 — Roadmap Re-Prioritization by Constraint (5FS)

**The PM problem.** The quarterly roadmap has 14 items ranked by a RICE scorecard. Engineering says they can finish 6. The PM negotiates to fit 8 by compressing estimates. Six weeks in, 3 items are blocked waiting for design review, 2 more are waiting for a data infrastructure dependency, and the team is shipping at half the planned rate. The ranking was wrong.

**What actually happened.** The RICE score measured impact and confidence per item in isolation. It did not account for which delivery stage is the system constraint — the resource or step that caps total output regardless of how much other steps improve. A highly-scored item that arrives at the constraint while it is already saturated adds zero additional throughput. It just joins the queue.

**The TOC fix.**

Apply the Five Focusing Steps (#1) to the delivery system before committing the roadmap sequence:

1. **Identify** the constraint: which stage is the current bottleneck? Count work-items waiting at each stage. Common candidates: design review, backend review, data infrastructure, legal/compliance sign-off, QA. The stage with the longest queue is almost always the constraint.

2. **Exploit** the constraint: maximize output from that stage without adding resources. In PM terms: sequence only work that is fully ready to enter the constraint. Do not start items that will stall upstream and create a false sense of progress.

3. **Subordinate** everything else: all other stages should run at the pace set by the constraint. This means accepting that non-constraint stages will have idle time — which is not waste, it is system health. Resist the instinct to fill every engineer's queue. Fill the constraint's queue.

4. **Elevate** the constraint only after steps 2–3 are exhausted: add design capacity, hire a specialist, add a data infrastructure sprint.

5. **Repeat**: after elevation, the constraint moves. Re-identify.

**PM output.** Re-sequence the ranked backlog so that the items which arrive at the constraint ready-to-process are at the top. Items that require pre-work upstream of the constraint are re-dated to a later sprint, even if their RICE score is higher. The roadmap now reflects system flow, not individual item scores.

**Primitive links.** Five Focusing Steps (#1) → Throughput Accounting (#3) for ranking within the constraint → Policy Constraints (#10) to check for non-physical blockers.

---

### P2 — Funnel-Stage Bottleneck Identification (DBR)

**The PM problem.** Activation rate is flat despite shipping three onboarding improvements in two quarters. Each improvement looked promising in isolation — the signup page conversion went up 12%, the profile setup step now takes half the time, and the welcome email open rate improved. But 30-day retention hasn't moved.

**What actually happened.** The improvements targeted stages before the constraint. Throughput through a funnel is limited by its single slowest or lowest-converting stage. Improving any stage before that stage increases the rate at which users arrive at the bottleneck — but since they still stall there, total throughput (activated, retained users) does not change.

**The TOC fix.**

Apply Drum-Buffer-Rope (#2) to the activation funnel:

1. **Identify the drum** (the bottleneck stage): map the funnel with conversion rates at each stage. The stage with the lowest conversion rate, or where users abandon at the highest rate and do not return, is the drum. In a typical B2B SaaS onboarding funnel this is often the "aha-moment action" — the first meaningful value delivery event. In a B2C product it is often the social or habit-formation trigger.

2. **Protect the drum with a buffer**: ensure that enough users arrive at the drum stage with full context and intent intact. If users arrive at the drum stage confused (missing a completion prerequisite), they will abandon even if the drum stage itself is well-designed. The buffer is: ensure prerequisite stages have sufficient completion before users hit the drum.

3. **Apply the rope** (intake control): do not drive more users into the top of the funnel faster than the drum can process them to activation. Marketing spend that floods the top of the funnel with users who stall at the drum generates acquisition cost without retention return. The rope is the metric: "don't increase paid acquisition CPMs above the level at which drum-stage throughput can absorb."

**PM output.** A funnel diagnosis that names the drum stage, the minimum buffer completion rate needed before the drum, and the acquisition ceiling above which spend stops generating activated users. The next roadmap item is an improvement to the drum stage, not to pre-drum stages (even if those look like easier wins).

**Primitive links.** Drum-Buffer-Rope (#2) → Five Focusing Steps (#1) to verify the drum is the actual system constraint → Current Reality Tree (#5) if the drum stage has multiple symptoms with unclear root cause.

---

### P3 — Throughput Accounting Applied to Feature Delivery

**The PM problem.** Engineering estimates that Feature A will take 3 weeks, Feature B will take 6 weeks, and Feature C will take 2 weeks. The PM ranks them by RICE and schedules A, C, B in sequence. The CFO wants Feature B because it has the highest projected ARR. The design team is already busy with Feature A. The debate goes in circles.

**What actually happened.** Every comparison is being made on local metrics: build cost (engineering weeks), projected ARR (revenue potential per feature). None of these metrics capture what actually matters: how much throughput (activated users, revenue, key metric movement) does each feature generate per unit of the constraint's time?

**The TOC fix.**

Apply Throughput Accounting (#3), using the constraint as the denominator:

```
T/CU = Throughput of feature (projected impact on the key metric)
       / Constraint Units consumed (hours of the bottleneck resource)
```

1. **Name the constraint resource**: the resource that limits delivery speed. Often: senior engineer capacity on the critical path, or design review hours, or data infrastructure time.

2. **Estimate constraint consumption per feature**: how many hours (or sprint slots) of the constraint resource does each feature consume?

3. **Estimate throughput per feature**: expressed in units of the key metric — e.g., expected new activated users per quarter, expected ARR generated, expected retention-week improvement.

4. **Rank by T/CU**: the feature with the highest throughput per constraint unit goes first, regardless of raw build cost or raw impact.

**Concrete example.**

| Feature | Projected Impact (activated users) | Constraint Hours (design review) | T/CU |
|---------|-------------------------------------|----------------------------------|------|
| A (onboarding step redesign) | 1,200 | 8 h | 150 |
| B (new reporting module) | 4,000 | 40 h | 100 |
| C (email trigger timing fix) | 600 | 2 h | 300 |

T/CU ranking: C → A → B. Feature C should ship first even though it has the lowest raw impact. Feature B should wait even though it has the highest raw ARR projection.

**PM output.** A re-ranked backlog with T/CU as the explicit ranking criterion, and a one-paragraph explanation for each stakeholder who pushed for a lower-ranked item: their item's impact is acknowledged, but it does not justify displacing a higher T/CU item at the constraint.

**Primitive links.** Throughput Accounting (#3) → Five Focusing Steps (#1) to confirm which resource is the current constraint → Policy Constraints (#10) to check whether review SLAs or approval gates are consuming constraint time artificially.

---

### P5 — Current Reality Tree to Diagnose Backlog Stalls

**The PM problem.** The backlog keeps growing. Items that were "top priority" three quarters ago are still not shipped. The team says they're busy. The PM adds more refinement ceremonies, installs a new project tracking tool, and splits epics into smaller stories. The backlog still grows.

**What actually happened.** The visible symptoms (backlog growth, slipping dates, busy team with no shipped throughput) are Undesirable Effects (UDEs). But each fix has targeted the symptoms, not their common root cause. The fixes may even be making things worse — more ceremonies consume the time that could go to the constraint.

**The TOC fix.**

Build a Current Reality Tree (#5) from the UDEs:

1. **List 5–10 UDEs** from the last 90 days. Examples:
   - Items marked "in progress" for more than 3 weeks without shipping
   - Refinement sessions that end without acceptance criteria
   - PRs open for more than 5 days without review
   - Design handoffs that cycle back to revision more than once
   - Sprint demos that present half-finished items as "progress"

2. **Trace with "If…Then" logic** to find the root cause. Connect UDEs upward until they converge. A well-built CRT typically shows 5–10 symptoms converging on 1–2 core problems.

3. **Common PM root causes the CRT surfaces:**
   - **Unclear acceptance criteria as input to engineering**: items enter the constraint underdeveloped; they stall because engineers must re-clarify rather than build.
   - **Concurrent over-commitment**: the team is nominally working on too many items; context-switching consumes the constraint's effective capacity.
   - **Invisible dependency on a shared resource**: a data infrastructure team, a platform team, or a compliance reviewer is the real constraint, and the PM has not accounted for their queue.
   - **A policy constraint**: a release gate, an approval SLA, or a quality standard that adds a fixed overhead per item regardless of its size.

**PM output.** A 1-page CRT diagram and a one-sentence statement of the identified core problem. The core problem is the target for the next round of intervention design (P6). All previous fixes that targeted UDEs without reaching the core problem should be suspended — they consume capacity without improving throughput.

**Primitive links.** Current Reality Tree (#5) → Evaporating Cloud (#4) if the core problem is sustained by a conflict between two valid requirements → Future Reality Tree (#6) to validate the proposed intervention.

---

### P6 — Future Reality Tree to Design Interventions

**The PM problem.** The CRT (P5) identified the core problem: items enter engineering without complete acceptance criteria. The PM proposes a solution: require a signed-off acceptance criteria doc before any item enters the sprint. A senior engineer objects: "That will just create a documentation backlog and delay everything. We've tried gates before." The PM proceeds anyway. Two sprints later, there is a new queue — this one at the acceptance criteria review — and throughput has not improved.

**What actually happened.** The proposed injection was not validated forward. The solution fixed the original symptom but created a new bottleneck. A Future Reality Tree (#6) run before implementation would have revealed this Negative Branch Reservation.

**The TOC fix.**

Build a Future Reality Tree (#6) before implementing any backlog-stall intervention:

1. **State the injection** as a concrete change: "Starting next sprint, no item enters the sprint unless it has a linked acceptance criteria document that has been reviewed by the lead engineer."

2. **Trace forward with "If…Then" logic**: if the injection is applied, what effects follow? For each positive effect (items enter engineering ready to build), also trace for Negative Branch Reservations — new undesirable effects the injection might cause.

3. **Check Negative Branch Reservations actively**:
   - Does the injection create a new queue upstream? (Acceptance criteria review becomes the new constraint)
   - Does it add overhead at a non-bottleneck stage? (PM time spent writing criteria documents instead of talking to customers)
   - Does it require a resource that is already constrained? (Lead engineer reviewing criteria while also reviewing PRs)

4. **Modify the injection to address reservations**: if the FRT reveals that "sign-off from lead engineer" creates a new bottleneck, modify the injection — perhaps criteria review is async via a shared doc, with a 24-hour review SLA, and sign-off is a lightweight emoji rather than a synchronous ceremony.

5. **Validate that the modified injection resolves all original UDEs** from the CRT.

**PM output.** A validated intervention design — the injection plus any modifications needed to neutralize identified Negative Branch Reservations. This becomes the spec for the process change. The FRT diagram is a one-page artifact that can be shared with engineering leadership to build confidence in the change.

**Primitive links.** Future Reality Tree (#6) → Evaporating Cloud (#4) if a Negative Branch Reservation surfaces an unresolvable conflict → Prerequisite Tree (#7) to sequence the implementation steps if the injection has dependencies.

---

### P9 — Critical Chain for Milestone-Driven Delivery

**The PM problem.** A product launch is scheduled for the end of Q3. The PM builds a Gantt chart with individual task estimates. Each task has a buffer built in. The team delivers each task "on time." The launch still slips by six weeks because integration, testing, and final review always take longer than planned, and individual buffers were consumed early (Parkinson's Law and Student Syndrome).

**What actually happened.** Individual task safety was hoarded at the task level instead of being pooled at the project level. Classic critical path scheduling treats each task's estimate as a commitment, which triggers both Parkinson's Law (work expands to fill the time) and Student Syndrome (people start late because there's buffer). The shared contingency at the end — where integration problems appear — runs out.

**The TOC fix.**

Apply Critical Chain (#9) to the launch plan:

1. **Identify the critical chain**: the longest chain of dependent tasks, taking into account not just task duration but also resource contention. The critical chain is often longer than the critical path because it accounts for the same engineer or designer appearing multiple times across tasks.

2. **Strip individual task padding**: reduce each task estimate to the 50th-percentile duration (the "aggressive but achievable" estimate, not the padded estimate). Do not let teams add contingency per task.

3. **Create a Project Buffer**: add a single shared buffer at the end of the critical chain, sized at 50% of the total safety removed from individual tasks. This is the contingency for the entire launch.

4. **Create Feeding Buffers**: where non-critical-chain tasks feed into the critical chain, add a feeding buffer at the junction. This protects the critical chain from delays in parallel work.

5. **Manage by buffer consumption, not task completion**: at each status check, report "what percentage of the Project Buffer has been consumed?" rather than "are individual tasks on time?" A task being late is not alarming if buffer consumption is low. Buffer consuming faster than the project progressing is the alarm signal.

**PM output.** A critical chain schedule with explicit Project Buffer and Feeding Buffers, and a weekly buffer burn-down chart as the primary delivery health metric. Milestone reviews shift from "is task X done?" to "where is the project in the buffer?" This gives the PM real signal about launch date confidence instead of false comfort from individual task green statuses.

**Primitive links.** Critical Chain (#9) → Five Focusing Steps (#1) to identify resource constraints that lengthen the chain → Policy Constraints (#10) to check whether release gates or approval cycles are adding padding that inflates the chain artificially.

---

### P10 — Policy-Constraint Detection on Roadmaps

**The PM problem.** Engineering has spare capacity. Design is ahead of schedule. The roadmap has clear priorities. Yet delivery is slower than it should be. Adding more engineers didn't help. The PM suspects a process problem but can't name it.

**What actually happened.** The constraint is not a physical resource — it is a policy. Review SLAs, design availability windows, approval gates, release train schedules, or quality sign-off processes are consuming constraint-equivalent time without being recognized as constraints.

**The TOC fix.**

Audit for policy constraints (#10) before investing in physical capacity:

1. **Map all approval and review steps** in the delivery pipeline. For each:
   - What is the SLA? (e.g., design review: 72-hour turnaround)
   - What is the actual lead time? (e.g., average 9 days in the last quarter)
   - Is the step triggered by a rule or a schedule? (e.g., "releases only go out on Tuesdays," "legal review required for any customer-facing copy change")

2. **Identify policy constraints** — steps where the policy, not the physical capacity of the person doing the review, is the binding constraint. Signs:
   - The reviewer has available time but the SLA extends beyond the available time
   - The step has a batch cadence (weekly release train, monthly legal review cycle)
   - The step applies universally to items that pose no actual risk (legal review required for every in-app tooltip change)

3. **Challenge the policy, not the person**: ask "why does this policy exist?" and "what risk does it prevent?" For each policy constraint, run an Evaporating Cloud (#4) — what is the conflict the policy is resolving? Is the assumption sustaining the conflict still valid?

4. **Common PM roadmap policy constraints**:
   - Weekly release cadence on a product where daily deploys are technically feasible
   - Design review SLA applied equally to pixel-level adjustments and full UX redesigns
   - Legal sign-off required for any email copy, regardless of whether it makes claims
   - Approval required from a VP for any feature with a metrics impact, even in alpha
   - Platform team sprint-planning cycle that gates all infrastructure work to biweekly start dates

**PM output.** A policy audit table listing each policy constraint, the time it adds per delivery cycle, whether the risk it prevents justifies the overhead, and a proposed change (e.g., tiered design review: major redesigns go to full review; minor adjustments use async approval with a 24-hour window). Presenting this to leadership as a throughput analysis — "this policy costs us X engineering-weeks per quarter" — frames the policy change as a business decision, not a process complaint.

**Primitive links.** Policy Constraints (#10) → Evaporating Cloud (#4) to resolve the conflict that sustains a policy constraint → Five Focusing Steps (#1) to re-identify the constraint after the policy is changed.

---

## Anti-Pattern Catalog

### A1 — Prioritizing High-Impact Items That Are Not Blocking Flow

**Description.** The roadmap is ranked by impact (RICE, ICE, or opportunity score). The highest-impact items are at the top. The team works the top of the list. Delivery rate is slow and the constraint queue is long.

**Why it fails.** A high-impact item that does not address the current system constraint adds zero throughput until the constraint is resolved. Worse, it consumes engineering time that could have been spent clearing the constraint queue. The bottleneck is not relieved; it deepens. The Five Focusing Steps (#1) require that all improvement energy focus on the constraint — not on the highest-impact item in isolation.

**Concrete damage.** A team builds a sophisticated analytics dashboard (high RICE score, requested by enterprise customers) while the activation funnel has a 40% drop-off at a broken deep-link. The dashboard ships; activation does not improve; the enterprise customers who wanted the dashboard churn anyway because they never reached the aha moment.

**Fix.** Run the T/CU ranking (P3) before committing a roadmap sequence. The ranking criterion is: throughput per constraint unit, not raw impact. A medium-impact item that directly relieves the constraint outranks a high-impact item that does not touch the constraint.

---

### A2 — Cost-Accounting Features Instead of Throughput-Accounting Them

**Description.** Feature decisions are made on build cost (engineering weeks) and revenue potential (projected ARR), compared as a ratio (ROI). Features with the best ROI go to the top of the roadmap.

**Why it fails.** Cost-accounting on individual features is the exact mistake Throughput Accounting (#3) was designed to prevent. Local optimization on ROI per feature ignores the system constraint. A cheap feature with high ROI that does not consume constraint resources looks great in isolation but may displace a slightly lower-ROI feature that directly relieves the bottleneck — reducing total system throughput.

**Concrete damage.** A SaaS product ranks a "pricing page redesign" (low build cost, high conversion impact on the pricing page) over an "API rate-limit increase" (moderate build cost, moderate direct conversion impact). The pricing page conversion improves, but users who sign up encounter API throttling errors during onboarding and churn. The constraint — API capacity — was never addressed. Net throughput (retained, paying users) does not improve.

**Fix.** Replace the ROI ranking with a T/CU ranking for all items that consume the identified constraint resource. Reserve ROI analysis for items that do not touch the constraint — these can be evaluated independently as long as they don't consume constraint capacity.

---

### A3 — Optimizing a Non-Bottleneck Stage

**Description.** The PM identifies that users struggle with the profile setup step (high drop-off rate, qualitative complaints). Engineering invests two sprints improving the profile setup UX. The drop-off at profile setup drops from 35% to 18%. Total activation does not improve.

**Why it fails.** Profile setup was not the bottleneck — it was a high-visibility pain point that the team treated as the constraint. The actual bottleneck was downstream: the "connect your first data source" step, which had a 60% drop-off rate and was never measured because it required backend instrumentation. Improving a non-bottleneck stage increases the rate at which users arrive at the real bottleneck — it does not increase throughput. In Five Focusing Steps (#1) terms, this violates step 3: subordinate non-constraint steps to the constraint, do not optimize them.

**Concrete damage.** Two sprints of engineering capacity, a redesign of the profile setup step, and a measured conversion improvement — all of which produce zero throughput gain. The team concludes "improving onboarding doesn't work" and considers other approaches, when the root issue is mis-identification of the constraint.

**Fix.** Measure conversion at every funnel stage before selecting which stage to improve. The stage with the lowest conversion rate and the highest volume through it is the candidate constraint. Verify with DBR analysis (P2) before committing a sprint to onboarding work.

---

### A4 — Critical-Path Estimation on Roadmap Items

**Description.** The PM uses a Gantt chart to plan a product launch. Each engineering task has an estimate with a built-in buffer ("add 20% for unknowns"). Tasks that finish early are considered done. The team checks off tasks on time. The launch still slips.

**Why it fails.** Critical-path scheduling with per-task buffers guarantees Parkinson's Law (work expands to the estimated time regardless of actual complexity) and Student Syndrome (engineers start tasks late because they have "buffer time"). When integration and testing arrive — the steps at the tail of the critical chain — all individual buffers have been consumed and there is no safety left. The Critical Chain method (#9) exists specifically because critical-path scheduling fails for this reason in every domain, including product launches.

**Concrete damage.** A product launch planned for week 12 slips to week 18. Post-mortem: "every individual task finished on time or close to it, but integration took longer than expected." This is a structural outcome of the scheduling method, not a one-time failure. It repeats on every launch.

**Fix.** Strip per-task buffers and create a single Project Buffer sized at 50% of the stripped safety. Track buffer consumption as the primary launch health metric. Do not report task-level green status as evidence of launch health (P9).

---

### A5 — Ignoring Policy Constraints in Scope Cuts

**Description.** The team is behind. The PM cuts scope — removes three features, reduces a fourth to MVP. The delivery rate does not improve because the remaining items still go through the same review and approval queue that was creating the delay.

**Why it fails.** Scope cuts address the wrong variable. If the constraint is a policy — a release cadence, an approval gate, a review SLA — then cutting the number of items does not increase throughput. Each remaining item still consumes the same constraint time per unit. The pipeline is less full, but the bottleneck is just as clogged per item.

**Concrete damage.** After the scope cut, the team ships the same number of items at the same rate. Leadership concludes "the team needs more capacity" and adds headcount. The new engineers produce more items that queue at the same policy constraint. Throughput remains flat; costs increase.

**Fix.** Before any scope cut, audit for policy constraints (P10). If the delay is driven by a policy (e.g., a 5-day legal review SLA on all copy changes), the fix is to change the policy — not to cut features. The scope cut is useful only if the constraint is physical capacity, not a rule.

---

## Recipes

### R1 — Backlog Re-Rank by Bottleneck

**Goal.** Re-sequence the product backlog so that items with the highest throughput per constraint unit are worked first, and items that do not address the constraint are correctly deprioritized regardless of their individual impact scores.

**When to use.** After any quarterly planning session where the backlog has been ranked by RICE, ICE, or stakeholder priority without accounting for the delivery system's current constraint.

**Stack.**

**Step 1: Identify the constraint stage** (5FS #1, [01-five-focusing-steps.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md)).

Count items waiting at each delivery stage (discovery, design, engineering, code review, QA, deployment, legal/compliance):

```
Stage               | Items waiting | Avg wait time
--------------------|---------------|---------------
Discovery           | 2             | 3 days
Design              | 1             | 2 days
Engineering         | 7             | 12 days   ← constraint
Code review         | 3             | 4 days
QA                  | 1             | 2 days
Legal review        | 0             | —
```

The stage with the longest queue and longest average wait time is the constraint. In this example: Engineering.

**Step 2: Audit for policy constraints** (#10, [10-policy-constraints.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md)).

Before treating Engineering as the constraint, check whether it is capacity-constrained or policy-constrained. Is there a sprint-planning cadence that gates Engineering intake to biweekly? Is there a prerequisite (design sign-off, acceptance criteria doc) that adds 3+ days per item before engineering can start? If so, the real constraint may be the policy, not the engineers.

**Step 3: Compute T/CU for each backlog item** (#3, [03-throughput-accounting.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md)).

For each item, estimate:
- **T** (Throughput): projected impact on the key metric (activated users, ARR, retention improvement — expressed in consistent units).
- **CU** (Constraint Units): hours of engineering capacity (or whichever resource is the constraint) the item requires.
- **T/CU** = T / CU.

Rank items descending by T/CU.

**Step 4: Subordinate scope to the constraint** (5FS step 3).

Items that do not consume constraint capacity (e.g., design-only items, copy changes, analytics instrumentation) are not ranked by T/CU — they can proceed in parallel. Items that consume constraint capacity are sequenced strictly by T/CU. If a high-T/CU item requires a prerequisite that is not ready, the item moves down until the prerequisite clears — do not start an item at the constraint until it is fully ready.

**Step 5: Elevate only after exploiting** (5FS step 4).

If the constraint is at maximum output after steps 2–4 and throughput is still insufficient, elevate: add engineering capacity, add a design-to-engineering handoff protocol that reduces clarification cycles, or change the sprint cadence. Elevation is the last step, not the first response to a slow delivery rate.

**Output artifact.** A re-ranked backlog table with T/CU scores, constraint-unit estimates, and a one-sentence non-goal statement for each item that moved down in ranking. Feeds into [assets/roadmap/outcome-roadmap.md](../assets/roadmap/outcome-roadmap.md) as the sequencing input for the "now" column.

---

### R2 — Funnel Debug via TOC

**Goal.** Diagnose why activation is flat despite onboarding improvements, identify the true bottleneck funnel stage, and design an intervention that is validated before implementation.

**When to use.** Activation rate has not improved over two or more quarters despite shipping onboarding changes. The team is uncertain whether to invest further in onboarding or whether the problem is elsewhere.

**Stack.**

**Step 1: Build a CRT on activation UDEs** (#5, [05-current-reality-tree.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md)).

List 5–10 UDEs from the activation data:

```
UDE1: 30-day retention has not improved despite three onboarding releases
UDE2: Users complete profile setup but do not proceed to the core action within 7 days
UDE3: Support tickets in week 1 cluster around "I don't know what to do next"
UDE4: Email re-engagement triggers fire within 48 hours for 55% of new signups
UDE5: NPS from users who completed the core action is 72; from those who did not: 11
```

Trace with "If…Then" logic. The CRT will typically converge on: "Users do not reach the aha-moment action within the critical time window because [root cause]." Common root causes the CRT surfaces in activation:

- The aha-moment action requires a configuration step that users are not guided to complete
- The product's value proposition is not apparent until the aha-moment, but onboarding does not set up the expectation of what that moment is
- A policy constraint (e.g., email verification required before accessing the core feature, gated behind a 24-hour email delivery SLA)

**Step 2: Identify the drum stage** (DBR #2, [02-drum-buffer-rope.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md)).

Map the funnel with conversion rates:

```
Signup               → 100%
Email verified       → 78%  (22% drop: policy constraint candidate)
Profile complete     → 61%  (17% drop: pre-drum stage)
Core action (aha)    → 29%  (32% drop: drum candidate)
Day-7 return         → 18%  (11% drop: post-drum outcome)
30-day retention     → 12%  (6% drop)
```

The drum is the core action stage (32% drop-off). Email verification may be a policy constraint adding a delay that causes the 22% initial drop — check whether the drop is time-of-day-related (users who sign up outside business hours experience a longer email delay and drop more).

**Step 3: Build an Evaporating Cloud** (#4, [04-evaporating-cloud.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/04-evaporating-cloud.md)) if a conflict blocks the fix.

If the drum-stage fix requires a trade-off — e.g., "we should remove the email verification gate to reduce drop-off" vs. "we must keep the email verification gate to maintain data quality" — build the Evaporating Cloud:

```
A (Objective): Maximize activation throughput

B (Need 1):    Guide users to the core action with no blocking gates
D (Want 1):    Remove email verification before core action access

C (Need 2):    Maintain data integrity and prevent fake-account abuse
D' (Want 2):  Require email verification before any meaningful action

Assumption to challenge: email verification must happen before the core action.
→ Challenge: can we allow access to the core action with a persistent banner and
  limited data persistence, verifying email within 72 hours before data is saved?
```

Surfacing and challenging the sustaining assumption often produces an injection that satisfies both needs.

**Step 4: Validate the injection with an FRT** (#6, [06-future-reality-tree.md](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/06-future-reality-tree.md)).

Before shipping the drum-stage intervention, trace it forward:

- Injection: allow access to core action before email verification, with a 72-hour verification window.
- Positive effects: 78% → 95% through verification gate; more users reach the core action stage.
- Negative Branch Reservation check: does deferring email verification increase fake accounts? Does it create a support burden when data is purged at 72 hours?
- Modification: add a visible timer and explicit warning at signup; set purge at 96 hours to reduce support edge cases.

**Output artifact.** A one-page funnel diagnosis with: drum stage identified, policy constraint noted, Evaporating Cloud summary, and a validated injection ready for sprint planning. Ties directly to the activation definition in [references/pmf-measurement.md](pmf-measurement.md) and to the metric tree in [assets/metrics/metric-tree.md](../assets/metrics/metric-tree.md).

---

### R3 — Roadmap T-I-OE Check

**Goal.** Apply Throughput Accounting to a quarterly roadmap to identify whether the planned item mix maximizes throughput per constraint unit, and reallocate engineering time toward higher-T/CU items before the quarter begins.

**When to use.** During quarterly planning, before engineering estimates are finalized. Also useful as a retrospective check after a quarter where throughput was lower than expected despite the team being fully utilized.

**Stack.**

**Step 1: Name the key metric (T proxy)**.

Choose one north-star metric that the roadmap items are expected to move. This is the Throughput proxy — expressed in consistent units per quarter. Examples: activated users, retained users at Day 30, ARR increments, weekly active users.

**Step 2: Identify the constraint resource (CU denominator)**.

Run the bottleneck identification from R1 (Step 1). Name the constraint. Typical PM-planning examples:

- Senior engineering capacity (if the team is top-heavy with junior engineers who require review)
- Design review hours (if a single design lead is reviewing all work)
- Data infrastructure capacity (if 60% of roadmap items require new data pipelines)

Express the constraint in a standard unit: engineering-weeks of senior time, design-review-hours, infrastructure-sprint-slots.

**Step 3: For each roadmap item, estimate T and CU**.

```
Item                      | T (activated users) | CU (sr-eng weeks) | T/CU
--------------------------|---------------------|-------------------|------
New user onboarding v2    | 800                 | 4                 | 200
Billing flow redesign     | 300                 | 3                 | 100
API rate-limit increase   | 1,200               | 6                 | 200
Advanced search           | 400                 | 8                 | 50
Notification preferences  | 150                 | 1                 | 150
Mobile home tab           | 600                 | 5                 | 120
```

**Step 4: Sort by T/CU and compare to current planned sequence**.

```
T/CU ranking:             Current planned sequence:
1. Onboarding v2 (200)    1. Advanced search ← ranked 6th by T/CU
2. API rate-limit (200)   2. Mobile home tab
3. Notifications (150)    3. Billing redesign
4. Mobile home tab (120)  4. Notifications
5. Billing redesign (100) 5. API rate-limit
6. Advanced search (50)   6. Onboarding v2 ← ranked 1st by T/CU
```

Advanced search was planned first because a key enterprise account requested it (stakeholder pressure). Onboarding v2 was deprioritized because it "has been on the list a while." The T/CU analysis reveals that the planned sequence would deliver approximately 60% of the T/CU-optimal sequence outcome with the same constraint investment.

**Step 5: Compute the reallocation case**.

Total constraint capacity available this quarter: 27 senior-engineering-weeks.

T/CU-optimal sequence (until capacity is exhausted):
- Onboarding v2: 4 CU, 800 T
- API rate-limit: 6 CU, 1,200 T
- Notifications: 1 CU, 150 T
- Mobile home tab: 5 CU, 600 T
- Billing redesign: 3 CU, 300 T
- [Capacity exhausted at 19 CU; advanced search deferred]

Projected T: 3,050 activated users

Current planned sequence (same 27 CU cap):
- Advanced search: 8 CU, 400 T
- Mobile home tab: 5 CU, 600 T
- Billing redesign: 3 CU, 300 T
- Notifications: 1 CU, 150 T
- API rate-limit: 6 CU, 1,200 T
- [Capacity exhausted at 23 CU; onboarding v2 deferred]

Projected T: 2,650 activated users

Reallocation gain: ~15% more activated users in the same quarter with the same team.

**Step 6: Restate Operating Expense (OE)**.

Operating Expense in Throughput Accounting is the cost of running the system regardless of output — salaries, infrastructure, tooling. It does not change with the sequence. The reallocation does not add cost; it increases T without increasing OE.

The case to leadership: "Same team, same quarter, same budget. Resequencing the roadmap by T/CU is projected to produce 400 more activated users — roughly equivalent to what a new sales hire would generate, at zero incremental cost."

**Output artifact.** A T/CU ranking table, a comparison of planned vs. T/CU-optimal sequence with projected throughput, and a one-paragraph reallocation brief. Feeds into [assets/prioritization/prioritization-scorecard.md](../assets/prioritization/prioritization-scorecard.md) as the T/CU column and into [assets/roadmap/outcome-roadmap.md](../assets/roadmap/outcome-roadmap.md) as the "now" sequence justification.

---

## Composition

The three recipes compose into a full quarterly planning and execution cycle:

| Stage | Recipe / Pattern | TOC Primitives |
|-------|-----------------|----------------|
| Pre-planning: roadmap sequence | R3: T-I-OE check | #1, #3, #10 |
| Pre-planning: funnel health | R1: Backlog re-rank | #1, #3, #10 |
| Planning: identify root causes | P5: CRT for backlog stalls | #5, #4 |
| Planning: validate interventions | P6: FRT for interventions | #6, #4, #7 |
| Execution: funnel bottleneck | R2: Funnel debug | #2, #4, #5, #6 |
| Execution: milestone delivery | P9: Critical chain | #9, #1, #10 |
| Review: constraint detection | P10: Policy-constraint audit | #10, #4, #1 |

**Cross-cutting rule.** Every pattern and recipe starts by identifying the constraint (5FS #1) before applying any other primitive. Applying Throughput Accounting (#3) without first identifying the constraint produces a ranking optimized for the wrong denominator. Applying DBR (#2) without identifying the drum produces a buffer that protects the wrong stage.

**Primitive coverage in this file:**

| Primitive | Where used |
|-----------|-----------|
| #1 Five Focusing Steps | P1, P2, P3, P9, P10, A1, A2, A3, R1, R2, R3 |
| #2 Drum-Buffer-Rope | P2, A2, A3, R2 |
| #3 Throughput Accounting | P3, A1, A2, R1, R3 |
| #4 Evaporating Cloud | P5, P6, P10, R2 |
| #5 Current Reality Tree | P5, A3, R2 |
| #6 Future Reality Tree | P6, R2 |
| #7 Prerequisite Tree | P6 |
| #9 Critical Chain | P9, A4 |
| #10 Policy Constraints | P3, P10, A5, R1, R2, R3 |
| #11 Thinking Processes | (tool-selection layer underlying all TP patterns above) |

---

## Sources

1. Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press. — Five Focusing Steps, constraint identification, throughput thinking.
2. Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press. — Throughput Accounting: T, I, OE definitions; T/CU product-mix ranking.
3. Goldratt, E.M. (1994). *It's Not Luck*. North River Press. — Thinking Processes: CRT, EC, FRT, PRT, TT applied to business decisions.
4. Goldratt, E.M. (1997). *Critical Chain*. North River Press. — Critical Chain project scheduling; Project Buffer and Feeding Buffer mechanics; buffer management vs. milestone tracking.
5. Corbett, T. (1998). *Throughput Accounting*. North River Press. — T/CU ranking; why cost accounting fails for product mix decisions.
6. Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press/St. Lucie Press. — Canonical definitions of all 11 primitives; policy constraint taxonomy.
7. Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. — CRT, FRT, EC construction rules; Negative Branch Reservation methodology.
8. Schragenheim, E. & Dettmer, H.W. (2001). *Manufacturing at Warp Speed*. CRC Press. — DBR in non-manufacturing environments; policy constraint detection.
9. Leach, L.P. (2000). *Critical Chain Project Management*. Artech House. — CCPM application in knowledge-work projects; buffer sizing heuristics.

---

**Cross-links.**
- TOC primitives: [foundations-theory-of-constraints/SKILL.md](../../foundations-theory-of-constraints/SKILL.md)
- Primitives overview: [foundations-theory-of-constraints/references/primitives-overview.md](../../foundations-theory-of-constraints/references/primitives-overview.md)
- Prioritization scorecard: [assets/prioritization/prioritization-scorecard.md](../assets/prioritization/prioritization-scorecard.md)
- Outcome roadmap: [assets/roadmap/outcome-roadmap.md](../assets/roadmap/outcome-roadmap.md)
- PMF measurement: [references/pmf-measurement.md](pmf-measurement.md)
- Metric tree: [assets/metrics/metric-tree.md](../assets/metrics/metric-tree.md)
- Causal inference applied (companion file): [references/causal-inference-applied.md](causal-inference-applied.md)
