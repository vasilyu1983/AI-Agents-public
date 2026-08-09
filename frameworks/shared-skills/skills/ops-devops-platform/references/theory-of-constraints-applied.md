# Theory of Constraints Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-theory-of-constraints` § When to Apply](../../foundations-theory-of-constraints/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-02._

Theory of Constraints is not abstract here. Every CI/CD pipeline is a multi-step flow system with one rate-limiting step. Every platform-spend decision involves throughput, investment, and operating expense. Every deployment-velocity stall has a root cause reachable by "If…Then" logic. This reference maps the 11 primitives from [foundations-theory-of-constraints](../../foundations-theory-of-constraints/SKILL.md) onto the concrete problems that platform and DevOps engineers face daily.

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 CI/CD Pipeline Bottleneck Identification via 5FS](#p1-cicd-pipeline-bottleneck-identification-via-5fs)
  - [P2 DBR-Style Scheduling on Shared CI Capacity](#p2-dbr-style-scheduling-on-shared-ci-capacity)
  - [P3 Throughput Accounting for Platform Spend Decisions](#p3-throughput-accounting-for-platform-spend-decisions)
  - [P4 Evaporating Cloud for Build-vs-Buy Conflicts](#p4-evaporating-cloud-for-build-vs-buy-conflicts)
  - [P5 CRT to Diagnose Deployment-Velocity Stalls](#p5-crt-to-diagnose-deployment-velocity-stalls)
  - [P6 FRT to Validate a Proposed Pipeline Policy Change](#p6-frt-to-validate-a-proposed-pipeline-policy-change)
  - [P7 Policy-Constraint Detection on Merge Gates and Review Queues](#p7-policy-constraint-detection-on-merge-gates-and-review-queues)
  - [P8 Critical Chain for Platform Projects](#p8-critical-chain-for-platform-projects)
- [Anti-Patterns](#anti-patterns)
  - [A1 Optimizing Fast Tests When Slow Tests Are the Bottleneck](#a1-optimizing-fast-tests-when-slow-tests-are-the-bottleneck)
  - [A2 Treating CI Capacity as Fixed Rather Than Elevatable](#a2-treating-ci-capacity-as-fixed-rather-than-elevatable)
  - [A3 Cost-Accounting Platform Decisions Instead of Throughput-Accounting](#a3-cost-accounting-platform-decisions-instead-of-throughput-accounting)
  - [A4 Critical-Path Scheduling on Platform Projects with High Uncertainty](#a4-critical-path-scheduling-on-platform-projects-with-high-uncertainty)
  - [A5 Ignoring Policy Constraints While Adding CI Parallelism](#a5-ignoring-policy-constraints-while-adding-ci-parallelism)
- [Recipes](#recipes)
  - [R1 CI/CD Throughput Recovery](#r1-cicd-throughput-recovery)
  - [R2 Review-SLA Constraint Surfacing](#r2-review-sla-constraint-surfacing)
  - [R3 Platform Spend Reallocation via Throughput Accounting](#r3-platform-spend-reallocation-via-throughput-accounting)
- [Composition Guide](#composition-guide)
- [Sources](#sources)

---

## Patterns

### P1 CI/CD Pipeline Bottleneck Identification via 5FS

**Primitive**: [Five Focusing Steps](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md)

**Problem**: A team invests weeks parallelizing unit tests, cache-warming build steps, and containerizing test environments — and cycle time barely moves. The improvement energy landed on non-constraints. In a CI/CD pipeline, the throughput metric is deployable artifacts per unit time. The constraint is the single stage where queue depth is deepest and wait time is longest, not the stage that developers find most annoying.

**Structure**:

```
Identify: measure queue depth and wait time at each pipeline stage
  - Unit tests:         queue_depth=2, avg_wait=45s
  - Integration tests:  queue_depth=18, avg_wait=22min   ← constraint
  - Code review:        queue_depth=4, avg_wait=3min
  - Deploy/smoke:       queue_depth=1, avg_wait=8min

Exploit: maximize throughput of integration tests without new spend
  - Parallelize integration test suite by package boundary
  - Eliminate duplicate environment setup (reuse pre-warmed containers)
  - Target: reduce avg_wait from 22min to 12min

Subordinate: adjust all non-constraints to feed the integration stage optimally
  - Unit test stage: cap at max_parallel=4; excess jobs queue rather than
    pre-saturating shared runner pool
  - Code review: open review on PR creation, not on CI completion
    (review begins while integration tests run in parallel)
  - Deploy: hold artifacts until integration stage clears; no pre-deploy queuing

Elevate (if exploit + subordinate insufficient):
  - Add a dedicated integration runner pool (cost decision → apply P3/R3 first)
  - Investigate flaky test elimination before adding hardware

Repeat: once integration tests improve, re-measure — code review or
  deploy/smoke typically becomes the new constraint
```

**Implementation practice**: instrument each stage with a start-time and ready-time metric. A simple GitHub Actions expression `${{ github.event.workflow_run.timing.jobs }}` gives per-job queue time. Export to Datadog or Prometheus. Set a queue-depth alert rather than a duration alert — queue depth identifies the constraint; duration identifies slow individual runs.

**5FS discipline**: explicitly designate non-constraints as "do not improve" until the constraint shifts. This is counter-intuitive for platform teams that default to making everything faster everywhere. Document the constraint and the do-not-improve list in the team's sprint board as a first-class constraint card.

---

### P2 DBR-Style Scheduling on Shared CI Capacity

**Primitive**: [Drum-Buffer-Rope](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md)

**Problem**: A shared runner pool serves multiple teams. During end-of-sprint surges, PRs from all teams hit the pool simultaneously — the queue floods, builds time out, and flaky-test retries amplify the overload. The system has no mechanism to throttle intake relative to constraint capacity.

**Structure**:

```
Drum: the shared runner pool at its sustainable throughput
  sustainable_throughput = runner_count × 0.80  (80% utilization ceiling)
  Example: 20 runners → drum pace = 16 concurrent jobs

Buffer: a time buffer in front of the constraint
  buffer_size = 0.33 × runner_count  (rule of thumb: 1/3 of pool)
  Example: 20 runners → buffer = 6 queued jobs (green zone)
  Buffer zones:
    green  → queue_depth < 6:   admit freely
    yellow → queue_depth 6–12:  reduce merge-queue max_parallel by 2
    red    → queue_depth > 12:  reduce to 1; alert platform team

Rope: release signal controlling when new work enters the pool
  Rope trigger: when buffer drops from yellow to green
  Implementation: GitHub Actions concurrency group with
    max-parallel = floor(runner_count × 0.80)
    cancel-in-progress = false (queue, do not cancel — preserve signal)
```

**Buffer management in practice**: emit a `ci_queue_depth` metric per team (tag by `repository` and `team`). Plot buffer consumption rate — not instantaneous queue depth — as the primary operational health metric. A steadily rising buffer consumption rate predicts saturation 10–15 minutes in advance, giving the platform team time to add ephemeral runners (GitHub Actions Runner Controller on Kubernetes) before SLO degradation.

**Rope discipline**: the rope is most frequently ignored in practice because no one owns the intake gate. Assign ownership: the merge queue policy is owned by the platform team. Document the WIP cap explicitly. Non-critical teams that bypass the rope during surges (by force-pushing or using the API directly) should route through a labeled bypass path that is audited.

**Worked example**: a team of 30 engineers with 80–100 PRs per day and a 20-runner pool. Before DBR: P95 build wait = 34 minutes during end-of-sprint. After implementing the buffer/rope with ARC-based autoscaling: P95 build wait = 7 minutes at normal load, 18 minutes during end-of-sprint surge, with zero timeout-induced failures.

---

### P3 Throughput Accounting for Platform Spend Decisions

**Primitive**: [Throughput Accounting](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md)

**Problem**: A platform team is asked to reduce CI infrastructure spend by 20%. The instinct is to shrink runner pool size, reduce caching storage, or eliminate dev-environment tooling. These are cost-accounting decisions. Throughput accounting reframes the same budget as: which platform investments most directly increase the rate at which features reach production (T), reduce WIP held in CI/CD queues (I), or reduce waste in the pipeline (OE)?

**Throughput Accounting applied to platform engineering**:

```
T  (Throughput):   deployable features per week × business value per feature
                   Proxy: deploy frequency × sprint velocity (from DORA)
I  (Inventory/WIP): PRs open, builds queued, features in review, infra changes
                    pending approval — all represent work started but not shipped
OE (Operating Expense): platform team salaries + CI compute + SaaS tooling +
                        cloud infrastructure costs

Goal: increase T, reduce I, minimize OE — in that priority order.
```

**Spend ranking by T/CU (Throughput per Constraint Unit)**:

| Platform investment | T impact | I reduction | OE delta | T/CU rank |
|---------------------|----------|-------------|----------|-----------|
| Add 10 integration-test runners | High (+30% throughput at constraint) | High | +$800/mo | 1 |
| Upgrade CI cache storage (500 GB) | Low (non-constraint stage faster) | None | +$200/mo | 4 |
| Automated canary analysis (Flagger) | Medium (reduces failed deploys re-queued) | Medium | +$150/mo | 2 |
| Third-party test flakiness tracker | Low | Low | +$400/mo | 5 |
| Pre-warmed integration test containers | Medium (exploit before elevate) | Medium | +$100/mo | 3 |

**Decision rule**: invest in the constraint first. Any spend that does not directly improve the constraint stage's throughput does not increase system T — it only increases OE. The cache storage upgrade (rank 4) should be deferred until integration tests are no longer the constraint.

**Cost-reduction case**: when budget pressure forces a cut, rank cuts by inverse T/CU impact. Remove tooling that is furthest from the constraint first. A 20% cost reduction that removes $1,200/month in SaaS tools (ranks 4 and 5 above) has near-zero T impact. A 20% cut that removes integration runners reduces T immediately and visibly.

---

### P4 Evaporating Cloud for Build-vs-Buy Conflicts

**Primitive**: [Evaporating Cloud](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/04-evaporating-cloud.md)

**Problem**: Platform teams recurrently face the conflict: build an internal tool tailored to the organization's specific workflow, or buy a SaaS solution that covers 80% of the need but requires adaptation. Both options have strong proponents, both have valid rationale, and the team cycles through the argument every 18 months without resolving it. The Evaporating Cloud surfaces the hidden assumption that sustains the conflict.

**Cloud diagram — internal tool vs. SaaS platform**:

```
A: Deliver reliable CI/CD platform that enables engineering throughput

B: Control the full feature set and integration points
   → D: Build an internal tool (own the code, own the behavior)

C: Minimize platform team maintenance burden and time-to-value
   → D′: Buy a SaaS/OSS solution (off-the-shelf, vendor-maintained)

Conflict: D (build) ↔ D′ (buy)
```

**Assumption audit — arrow by arrow**:

| Arrow | Assumption | Challenge |
|-------|-----------|-----------|
| A → B | "We need full control to meet our integration requirements" | Are the integration requirements actually unique, or assumed unique? Run a feature gap analysis against the SaaS solution before concluding they are irreconcilable. |
| A → C | "Minimizing maintenance burden is necessary to ship platform features" | Maintenance burden is only minimized if the SaaS solution does not require heavy customization. For highly customized workflows, SaaS can become as burdensome as an internal tool. |
| B → D | "Full control requires owning the code" | Invalid in many cases: well-designed OSS tools (Argo Workflows, Tekton) give code ownership without greenfield build cost. The assumption conflates "control" with "custom build." |
| C → D′ | "Maintenance burden is reduced by buying" | Invalid when the SaaS solution requires extensive plugin development, workarounds, or custom API integrations. |

**Injection**: separate "control over behavior" from "build from scratch." Use an OSS tool where the organization owns the deployment and configuration (not the codebase). This satisfies B (behavioral control via configuration and plugin APIs) and C (no greenfield maintenance burden). The conflict evaporates.

**Validation**: take the injection to the Future Reality Tree (P6) before committing. Map: "If we adopt Argo Workflows with custom step templates, then integration requirements X, Y, Z are met → platform team velocity is maintained → engineering throughput target is reached." Check for Negative Branch Reservations (e.g., "learning curve delays onboarding by 2 sprints" → trim: dedicate one sprint to migration tooling before rolling out broadly).

---

### P5 CRT to Diagnose Deployment-Velocity Stalls

**Primitive**: [Current Reality Tree](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md)

**Problem**: A team's deploy frequency is declining — from 15 deploys/week to 6 — despite no major architectural changes. Engineers report several unrelated-seeming problems: "CI is slow," "reviews take forever," "deploys are risky," "we keep having incidents." A CRT maps these as a connected causal chain rather than independent complaints.

**CRT construction (simplified)**:

```
UDEs collected from team retro:
  UDE1: Deploy frequency declining (15 → 6/week)
  UDE2: Post-deploy incidents increasing (1/week → 3/week)
  UDE3: Code review queue growing (avg review time 2 days → 5 days)
  UDE4: Engineers reluctant to deploy on Fridays
  UDE5: Hotfix rate increasing (3/month → 9/month)

Tracing with If…Then:

If deploys are risky → then engineers batch more changes per deploy
If changes are batched → then each deploy has more blast radius
If blast radius is larger → then incidents per deploy increase      → UDE2
If incidents increase → then engineers avoid Fridays              → UDE4
If engineers avoid Fridays → then Thursday afternoon becomes a
  deploy surge → then CI queue spikes → then review queue grows   → UDE3

If hotfix rate increases → then senior engineers review hotfixes
  urgently → then normal PR review is deprioritized               → UDE3
If hotfixes skip the normal pipeline → then canary analysis is
  bypassed → then incidents continue                              → UDE2

Root trace:
  All UDEs trace to:
  Core Problem: "Deploys are not safe enough to be small and frequent,
                so batching is rational, which makes each deploy riskier."

  One level deeper:
  Core Problem root: "No automated quality gate enforces deploy safety —
                     deploy safety depends on human judgment at review time."
```

**Action**: the CRT identifies that code review time (UDE3) is a symptom, not the root cause. Adding reviewers would not fix deploy frequency. The root intervention is an automated quality gate (canary analysis, smoke test suite, automated rollback) that decouples deploy safety from reviewer vigilance. Design that injection with the FRT (P6).

---

### P6 FRT to Validate a Proposed Pipeline Policy Change

**Primitive**: [Future Reality Tree](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/06-future-reality-tree.md)

**Problem**: After a CRT identifies the root cause (P5), the team proposes an injection: implement automated canary analysis with defined rollback thresholds before removing the VP-sign-off gate. Before investing 6 weeks in the implementation, the FRT validates whether the injection actually dissolves the UDEs — and surfaces any Negative Branch Reservations.

**FRT (simplified)**:

```
Injections:
  I1: Automated canary analysis (error rate, P99 latency, CPU saturation)
      with defined rollback thresholds — replaces manual VP sign-off
  I2: Smoke test suite covering top-5 critical user flows (15 min runtime)
      runs on every deploy before canary traffic shift

If I1 and I2 deployed →
  Deploys are safe at small batch sizes (no manual gate blocking frequent deploys)
  ↓
If deploys are safe at small batch sizes →
  Engineers deploy small PRs frequently
  ↓
If small, frequent deploys →
  Blast radius per deploy shrinks
  ↓
If blast radius shrinks →
  Post-deploy incidents decline                           → DE: UDE2 resolved
  Engineers comfortable deploying any day including Friday → DE: UDE4 resolved
  Hotfix rate declines                                   → DE: UDE5 resolved
  ↓
If hotfix rate declines →
  Senior engineer time freed from urgent reviews
  ↓
If senior engineer time freed →
  Normal PR review time returns to baseline (2 days)     → DE: UDE3 resolved
  ↓
If review time normalizes + deploys are frequent →
  Deploy frequency recovers                              → DE: UDE1 resolved
```

**Negative Branch Reservations found**:

| NBR | Branch | Trim |
|-----|--------|------|
| "Canary analysis creates false positives, triggering rollbacks on benign traffic spikes" | Canary rollback rate increases → engineers lose confidence in automation → bypass canary | Require 3-of-5 metric samples to breach threshold before rollback (multi-sample confirmation); instrument and alert on false-positive rollback rate separately |
| "Smoke test suite adds 15 min to every deploy cycle" | Deploy time increases → engineers batch again to amortize overhead | Run smoke tests in parallel with canary traffic shift rather than sequentially; target total added time < 5 min |

**Go/no-go**: FRT validates the injection resolves all five UDEs with both NBRs trimmed. Proceed to Prerequisite Tree (primitive 07) to sequence the implementation obstacles.

---

### P7 Policy-Constraint Detection on Merge Gates and Review Queues

**Primitive**: [Policy Constraints](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md)

**Problem**: A platform team triples the runner pool, implements parallel test sharding, and introduces caching — but deployment frequency barely moves. Throughput is constrained by rules, not capacity. Policy constraints in DevOps are common and invisible: merge gates, required-reviewer rules, fixed deploy windows, and review SLA policies all throttle flow regardless of pipeline speed.

**Policy audit checklist for a CI/CD pipeline**:

```
Measurement policies (reward wrong behavior):
  □ "All PRs require 2 approvals regardless of change size"
     → small refactors and dependency bumps have same gate as architectural changes
     → engineers batch changes to amortize review cost
  □ "Engineers measured on features-completed, not features-shipped"
     → no incentive to clear the deploy gate; work piles up at the merge step

Decision-rule constraints (approval chains that throttle flow):
  □ "Production deploys require VP sign-off"
     → 24–48 hour approval lag independent of CI result
  □ "Deploys only allowed Tuesday and Thursday" (fixed deploy window)
     → reduces max deploy frequency to 2/week regardless of CI throughput
  □ "Any infra change requires security team review within 72 hours"
     → 72-hour floor on infra PR cycle time

Behavioral policies (norms that create WIP):
  □ "Review when you have time" (no review SLA)
     → review queue grows unbounded; effective SLA is 3–5 days
  □ "Authors do not merge their own PRs" with no auto-merge
     → completed PRs wait in queue for a reviewer to hit merge

Incentive misalignment:
  □ Security team measured on "zero unapproved infra changes"
     → review speed is not their incentive; thoroughness is
     → review queue grows even when reviewers are available
```

**Detection heuristic**: measure the ratio of PR open time to CI run time. For a 15-minute pipeline, if average PR-to-merge time is 3 days, 99% of cycle time is human wait time — the constraint is policy, not capacity. Adding more runners would have zero throughput impact.

**Injection priority**: remove the highest-throughput-damage policy constraint first. In the example above, the fixed deploy window (2/week ceiling) is likely the binding constraint — removing it releases the constraint entirely, independent of runner count or test speed. Document the policy change in the FRT (P6) before removing it to validate it does not create new UDEs.

---

### P8 Critical Chain for Platform Projects

**Primitive**: [Critical Chain](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/09-critical-chain.md)

**Problem**: A platform migration project (e.g., CI/CD system migration from Jenkins to GitHub Actions + ARC) is 6 months late despite individual tasks completing "on time." The root causes are typical: senior engineers are shared across migration and production support; task estimates are padded individually; milestones are tracked but buffer consumption is not; the critical chain was computed as a critical path without accounting for resource contention.

**Critical Chain applied to a platform migration**:

```
Project: Jenkins → GitHub Actions migration
Tasks (median estimates, padding stripped):
  T1: Audit existing Jenkins pipelines (1 engineer, 3 days)
  T2: Design GitHub Actions templates (1 senior eng, 5 days)
  T3: Migrate 20 service pipelines (2 engineers, 10 days) — depends on T2
  T4: Set up ARC runner cluster (1 senior eng, 4 days) — depends on T2
  T5: Validate performance (1 senior eng + 1 engineer, 3 days) — depends on T3, T4
  T6: Cutover and decommission Jenkins (2 engineers, 2 days) — depends on T5

Critical path (task dependencies only): T1 → T2 → T3 → T5 → T6 = 23 days
Critical chain (task + resource dependencies):
  Senior engineer assigned to T2, T4, T5 — cannot run T2 and T4 in parallel
  Critical chain = T1 → T2 → T4 → T5 → T6 = 17 days (T3 feeds via Feeding Buffer)

Project Buffer: 0.5 × 17 = 8.5 days (pooled from removed individual padding)
Feeding Buffer (T3 → T5): 0.5 × 5 = 2.5 days (T3 feeds critical chain at T5)

Total project commitment: 17 + 8.5 = 25.5 days ≈ 26 working days
```

**Buffer management**:

```
At day 8 (31% of chain complete):
  Critical chain consumed: 6 days (35% of chain)
  Project Buffer consumed: 2 days (24% of PB)
  Buffer consumption rate > chain progress rate → yellow
  → investigate: is T4 (ARC cluster) taking longer than median estimate?

At day 14 (54% of chain complete):
  Critical chain consumed: 11 days (65% of chain)
  Project Buffer consumed: 3 days (35% of PB)
  Consumption rate normalized → green
  → no escalation needed
```

**Resource buffer for senior engineer**: insert a Resource Buffer notification 2 days before the senior engineer must shift from T2 to T4. This prevents the classic CCPM failure where the constrained resource is unavailable when the critical chain reaches them because they are still finishing a lower-priority task.

**Key difference from critical path**: the critical path calculation would show T2 and T4 in parallel, promising a shorter schedule that is impossible to achieve with one senior engineer. CCPM surfaces this contention explicitly and builds the buffer to absorb it.

---

## Anti-Patterns

### A1 Optimizing Fast Tests When Slow Tests Are the Bottleneck

**TOC diagnosis**: violating step 3 of 5FS — improving non-constraints. The team measures individual stage duration and invests in the stages with the highest absolute duration. But constraint identification requires queue depth, not duration. A 2-minute unit test stage with a queue depth of 0 is not the constraint. A 20-minute integration test stage with a queue depth of 15 is — even if individual runs look "fast."

**Symptom**: the team adds unit test parallelism, introduces test result caching, and enables test splitting. P95 unit test time drops from 90 seconds to 35 seconds. CI cycle time (commit to deploy-ready) does not change, because engineers are waiting on integration tests, not unit tests.

**Concrete example**: a monorepo with 8,000 unit tests (45 sec parallel) and 200 integration tests (18 min serial, shared DB fixtures). Reducing unit test time by 50% frees 22.5 seconds per PR. Reducing integration test time by 50% frees 9 minutes per PR. The improvement ratio is 24× in favor of the integration tests — but unit tests are improved first because they are "the annoying slow part" according to engineers who wait for them during local development.

**Fix**: apply 5FS (#1) before any test infrastructure investment. Measure queue depth and average wait time at each pipeline stage. Build a constraint card and a "do not improve" list. Any improvement to a non-constraint stage requires a constraint-stage improvement of greater T/CU to be approved first.

---

### A2 Treating CI Capacity as Fixed Rather Than Elevatable

**TOC diagnosis**: failure to complete the 5FS loop — elevate is never reached. Teams often exhaust exploit and subordinate options and then accept the constraint as a permanent ceiling: "We have 20 runners; that is all we can afford." This assumption is never examined against throughput accounting.

**Symptom**: after exploit (parallelism, caching, test sharding) and subordinate (merge queue policy, WIP caps), integration test wait time is 12 minutes — down from 22 but still above target (8 minutes). The team concludes "we have done all we can." Deploy frequency plateaus.

**Why this is wrong**: the elevation cost is $800/month for 10 additional runners (from P3). The throughput value of reducing wait time from 12 to 8 minutes — enabling 2 additional deploy cycles per day across 8 services — is estimated at 30% faster feature velocity. At even a conservative value-per-deploy, the T/CU ratio of the elevation investment is strongly positive. The constraint was treated as fixed because no one ran the throughput accounting calculation.

**Fix**: any time exploit and subordinate have been fully applied and throughput is still below target, run the throughput accounting calculation (P3/R3) before accepting the ceiling. Elevation decisions must be made on T/CU, not on OE alone. "We can't afford more runners" is a cost-accounting statement. "Adding runners generates T/CU of X at a cost of OE+Y; the marginal gain is Z" is a throughput-accounting decision.

---

### A3 Cost-Accounting Platform Decisions Instead of Throughput-Accounting

**TOC diagnosis**: cost-accounting bias — OE reductions feel safe, T is invisible. Platform decisions made purely on cost reduction destroy throughput without appearing on any metric until engineering velocity collapses.

**Symptom**: the platform team is asked to cut 20% of cloud spend. They remove 6 integration runners (saving $480/month). CI wait time rises from 12 to 28 minutes. Deploy frequency drops from 18 to 9 deploys/week. Sprint velocity declines 15% over the following quarter. The cost saving cost far more in reduced T than it saved in OE — but this was never calculated.

**Root cause**: cost accounting treats all spend as equivalent. A dollar of runner compute and a dollar of unused SaaS seat are both "cost" — but their T impact is completely different. Throughput accounting distinguishes investments that directly constrain T from those that are overhead relative to the constraint.

**Fix**: before any platform cost-reduction decision, run the T/CU ranking (P3). Identify which spend is directly at the constraint and which is not. Cost cuts should come from non-constraint OE first. Document the T impact of any cut to constraint-stage capacity as a known throughput risk to be accepted explicitly by the business, not just the platform team.

---

### A4 Critical-Path Scheduling on Platform Projects with High Uncertainty

**TOC diagnosis**: critical path ignores resource contention and behavioral effects (student syndrome, Parkinson's Law), producing schedules that are deterministically wrong under uncertainty.

**Symptom**: a 3-month platform migration is scheduled on a critical path. Tasks are assigned "safe" durations (90th percentile estimates). Individual tasks complete on time or early, but the project is 6 weeks late. Post-mortem finds: senior engineers were shared across multiple tasks that the critical path showed as parallel; each task was completed exactly at its padded estimate (Parkinson's Law); and the critical path was never updated when a resource was reassigned to a production incident for 2 weeks.

**Why critical path fails for platform projects**: platform projects have high resource contention (few senior engineers, many tasks that require them) and high uncertainty (migration complexity is often discovered during execution). Critical path does not model resource contention. It also does not have a mechanism for buffer management — when tasks slip, the delay propagates invisibly until the project is past its deadline.

**Fix**: apply Critical Chain (P8) to platform projects. Strip individual padding; pool it into a Project Buffer. Identify resource contention explicitly in the chain calculation. Track buffer consumption rate (not milestone dates) as the progress metric. When buffer consumption rate exceeds chain progress rate, escalate immediately — not at the next milestone review.

---

### A5 Ignoring Policy Constraints While Adding CI Parallelism

**TOC diagnosis**: elevating physical capacity without checking for upstream policy constraints. Classic case of the constraint appearing physical (runner pool) while the binding constraint is a policy (review SLA, merge gate, deploy window).

**Symptom**: platform team adds 20 runners, implements test parallelism, cuts integration test time from 18 to 8 minutes. CI throughput increases 2×. Deploy frequency does not change. The constraint was never the runner pool.

**Root cause**: the binding constraint was a policy — required 2-approval merge gate with no review SLA. PR-to-merge time is 4 days. A faster CI pipeline does not move the 4-day human gate. Doubling runner capacity doubled CI throughput of a step that was not the system constraint.

**Detection**: measure the ratio of CI time to total PR cycle time. If CI time is < 10% of total cycle time, physical CI capacity is not the constraint. Total cycle time = time from PR open to merge to deploy-complete. Break it down:

```
PR open to first review:       28 hours  (review wait — policy constraint)
First review to approval:       4 hours  (review work — potentially physical)
Approval to merge:              2 hours  (merge wait — policy: 2-approval rule)
Merge to CI complete:          12 min   (CI — physical capacity)
CI complete to deploy:          8 min   (deploy — physical)

Physical constraint (CI) = 20 min out of 34+ hours total.
Policy constraint (review + merge gate) = 34 hours.
```

**Fix**: audit the full PR cycle time breakdown before investing in CI infrastructure. Run the policy-constraint checklist from P7 first. Identify the binding policy. Remove or reform it with FRT validation (P6) before spending on CI capacity.

---

## Recipes

### R1 CI/CD Throughput Recovery

**Goal**: systematically recover deploy throughput from a stalled CI/CD pipeline using the full 5FS loop, DBR scheduling, and policy-constraint audit.

**Primitives used**: 5FS (#1), DBR (#2), Policy Constraints (#10).

**Tooling**: GitHub Actions (or equivalent), Prometheus/Datadog, GitHub Actions Runner Controller.

```
Step 1 — Measure (Identify)
  Instrument each pipeline stage with queue_depth and avg_wait_time metrics.
  Emit from each job's pre/post steps:
    ci_stage_queue_depth{stage="unit_test|integration|review|deploy"}
    ci_stage_wait_seconds{stage="..."}

  Collect over 2 weeks (covers sprint patterns and surge events).
  Identify the constraint: stage with highest avg_wait_time AND non-zero
  queue depth consistently.

  Also measure: PR-to-merge time vs CI time ratio.
    If CI time < 10% of PR-to-merge time → constraint is policy, not capacity.
    → Skip to Step 5 (Policy audit) before steps 2–4.

Step 2 — Exploit (no new spend)
  At the identified constraint stage, apply in order:
  a. Parallelize: split test suite by package/module into parallel shards.
     Target: reduce stage wall-clock time by ≥ 30%.
  b. Eliminate setup waste: use pre-warmed containers or layer caching
     (Docker BuildKit cache, GitHub Actions cache action).
  c. Eliminate test waste: run flaky-test detector (pytest-flakefinder, or
     GitHub Actions re-run analysis). Remove or quarantine tests with
     flakiness rate > 5%. Each flaky test that triggers a retry doubles
     its slot consumption.
  d. Exploit target: reduce constraint stage avg_wait_time by ≥ 40%
     before moving to Step 3.

Step 3 — Subordinate (adjust non-constraints to feed constraint)
  a. Set merge-queue max_parallel proportional to constraint stage throughput:
       max_parallel = floor(constraint_throughput × 0.80)
     This is the Rope — new work enters only as fast as constraint clears it.

  b. Reorder stage sequence if possible: move the constraint stage earlier.
     Build → Constraint stage → Review-ready (not Build → Review → Constraint).
     Engineers get fast signal from the constraint before investing review time.

  c. Non-constraint stage WIP caps: for any stage that feeds the constraint,
     set a WIP cap of 2× the constraint's throughput rate.
     Jobs above the cap queue at intake, not at the constraint.

  d. Buffer monitoring: deploy a Grafana dashboard with:
     - Buffer zone: green/yellow/red based on queue depth relative to runner count
     - Alert: PagerDuty/Slack on red zone entry (queue > 2× runner count)

Step 4 — Elevate (if exploit + subordinate insufficient)
  Run throughput accounting calculation (see R3):
    Cost of additional capacity: $X/month
    T impact: estimated Y% increase in deploy frequency
    T/CU: value per constraint-unit added
  Approve elevation only if T/CU is positive and constraint has been
  fully exploited (Step 2 complete) and subordinated (Step 3 complete).

  Elevation options (in T/CU order):
    1. Ephemeral autoscaled runners (ARC on Kubernetes) — pay-per-use,
       eliminates idle cost, scales to demand within 2–3 minutes
    2. Dedicated runner pool for the constraint stage — predictable cost,
       no cold-start latency, higher idle cost
    3. Migrate constraint stage to faster compute tier (larger instance type)

Step 5 — Policy audit (run before or instead of Steps 2–4 if indicated)
  Measure PR-to-merge time broken down by component (P7 checklist).
  If any policy component > 3× CI time, it is the binding constraint.

  Common injections:
    Review SLA → set explicit SLA: first review within 4 working hours
    2-approval gate → tiered by change size: trivial changes (< 20 lines,
      no logic) auto-merge on CI green; complex changes require 2 approvals
    Deploy window → remove fixed deploy days; replace with operational-risk
      score gate (P7 pattern) that blocks only during active incidents or
      high-risk windows

Step 6 — Repeat
  After each elevation or policy change, re-measure all stage metrics.
  Constraint has likely shifted. Return to Step 1.
  Document the current constraint and do-not-improve list as a
  team Notion/Confluence card updated each sprint.
```

**Sequence discipline**: Steps 1–3 should be completed before any spend. In most teams, exploit + subordinate alone recover 30–50% of lost throughput. Elevation (Step 4) is warranted only when exploit and subordinate have been exhausted. Policy audit (Step 5) should be run in parallel with Step 1 — if it identifies the binding constraint as a policy, Steps 2–4 become premature investments.

---

### R2 Review-SLA Constraint Surfacing

**Goal**: use CRT to map why deployment velocity stalls, Evaporating Cloud to resolve the review-vs-quality conflict, and FRT to design and validate a new review policy.

**Primitives used**: CRT (#5), Evaporating Cloud (#4), FRT (#6), Policy Constraints (#10).

**Tooling**: GitHub PR metrics (cycle time, review wait time), DORA dashboard, team retro data.

```
Step 1 — Collect UDEs (CRT input)
  Run a retro or structured survey. Gather 5–8 observable negative outcomes:
    UDE1: Features take 3× longer to ship than engineering estimates predict
    UDE2: Engineers report high frustration with "waiting for review"
    UDE3: Senior engineers are overloaded with review requests
    UDE4: Code quality incidents traced to missed-review edge cases
    UDE5: Junior engineers submit fewer PRs (intimidated by review backlog)
    UDE6: Hotfix PRs skip review gate entirely due to urgency

  Validate each UDE is observable and negative (not a solution statement).

Step 2 — Build the CRT
  Trace with If…Then logic:

  If there is no review SLA →
    Reviews are done when time permits →
    Review wait averages 2–4 days                           → UDE1, UDE2

  If senior engineers have no review routing →
    All PRs route to senior engineers by default →
    Senior engineers are overloaded                          → UDE3, UDE2

  If review is overloaded →
    Hotfixes skip review to unblock production              → UDE6
    Junior engineers deprioritize PRs (don't want to add to the pile) → UDE5

  If review quality is inconsistent (no checklist, no standards) →
    Some reviews miss edge cases                            → UDE4
    Reviewers spend extra time re-checking basics           → UDE3

  Root causes identified:
    CP1: No review SLA and no routing policy
    CP2: No review standards (checklist / automated pre-review checks)

Step 3 — Evaporating Cloud on the review-vs-quality conflict
  A: Maintain engineering throughput and code quality

  B: Ensure thorough code review catches defects early
     → D: Require senior engineer review on all PRs
           (no SLA; review takes as long as it takes)

  C: Unblock engineers quickly to maintain flow and morale
     → D′: Minimal or no review gate; auto-merge on CI green

  Conflict: D (thorough senior review) ↔ D′ (fast/no review)

  Assumption audit:
    B → D: "Only senior engineers can catch critical defects"
      Challenge: automated static analysis (semgrep, SonarQube),
      type checking, and test coverage gates catch a large class of
      defects before review. Senior review catches architectural and
      security issues — not syntax or logic errors. The assumption
      overstates the scope of senior review.

    C → D′: "Fast review means minimal review"
      Challenge: fast review is achievable with routing + SLA without
      reducing depth. A 4-hour SLA with a trained reviewer pool is
      faster than D and deeper than D′.

  Injection: tiered review policy
    Tier 1 (trivial changes < 30 lines, no security/infra scope):
      automated checks only; 1 any-engineer review; 4-hour SLA; auto-merge
    Tier 2 (standard feature changes):
      1 domain-team review; 4-hour SLA; senior review on rotation
    Tier 3 (security, infra, architectural changes):
      2 reviews minimum; 24-hour SLA; senior engineer required

Step 4 — Build the FRT for the tiered policy injection
  Map the injection forward:

  If tiered review policy deployed →
    Tier-1 PRs merge in < 4 hours (vs. current 2–4 days) →
    Throughput of small changes increases 5–10× →
    Engineers break large PRs into smaller Tier-1 units →
    Blast radius per deploy shrinks                          → DE: UDE1 resolved

  If senior engineers removed from Tier-1 review →
    Senior review load drops 40–60% →
    Senior engineers available for Tier-3 architectural review →
    Tier-3 review quality increases                          → DE: UDE3, UDE4 resolved

  If review process feels fair and fast →
    Junior engineers submit more PRs →
    Junior engineer velocity increases                       → DE: UDE5 resolved

  If hotfixes have an explicit Tier-3 fast lane (24h → 4h SLA) →
    Hotfixes no longer skip review entirely                  → DE: UDE6 resolved

  NBR check:
    NBR1: "Tier-1 auto-merge without senior review lets security bugs through"
      Trim: Tier-1 classification requires semgrep + bandit + no changed
      security scope (no auth code, no infra, no secrets handling).
      Any PR touching these areas is auto-upgraded to Tier 3.

    NBR2: "Teams game the tier classification to get fast merges"
      Trim: tier classification is determined by automated file-change
      analysis (diff scope), not author self-selection.

Step 5 — Instrument and verify
  After policy change, measure:
    review_wait_time_p50 and p95 by tier (target: Tier-1 < 2h, Tier-2 < 6h)
    deploy_frequency (target: ≥ 30% increase within 4 weeks)
    code_quality_incidents (monitor for 8 weeks: must not increase)
    senior_engineer_review_load (target: < 30% of available hours)

  Review at 4 weeks. If any metric has worsened, re-run 5FS to find the
  new constraint.
```

**Strongest signal**: if PR-to-merge time drops but deploy frequency does not, the constraint has shifted to the deploy stage or a remaining policy constraint. Re-run the policy audit (P7) before investing in CI infrastructure.

---

### R3 Platform Spend Reallocation via Throughput Accounting

**Goal**: apply T/I/OE analysis to map current platform spend against the identified constraint, then reallocate investment to maximize throughput per dollar.

**Primitives used**: Throughput Accounting (#3), 5FS (#1), Policy Constraints (#10).

**Tooling**: cloud cost explorer (AWS Cost Explorer, GCP Billing, Azure Cost Management), DORA metrics dashboard, sprint velocity data.

```
Step 1 — Identify the constraint (prerequisite: 5FS Step 1 from R1)
  Assume constraint = integration test stage (avg_wait = 22min, queue_depth = 18)
  Constraint capacity: 20 runners, 80% utilization = 16 effective slots

Step 2 — Map current spend to T/I/OE buckets

  T-generating spend (directly at constraint or enabling deploys):
    Integration test runners × 20:     $1,600/mo  ← constraint stage
    Artifact storage (S3/GCS):          $200/mo   ← enables deploy
    Container registry:                 $150/mo   ← enables deploy
    Automated canary (Flagger/Argo):    $120/mo   ← reduces failed deploys
    Subtotal T-generating:            $2,070/mo

  I (inventory/WIP holding cost — spend that extends cycle time):
    Manual review tooling (GitHub Enterprise):  $800/mo  ← enables policy constraint
    Ticket/project tracking (Jira):              $600/mo  ← coordination overhead
    Subtotal I-related:                        $1,400/mo

  OE (operating expense not tied to constraint):
    Build cache storage (500 GB):        $200/mo  ← non-constraint stage
    Unit test parallelism (8 runners):   $640/mo  ← non-constraint stage
    Unused SaaS CI seats (12 seats):     $480/mo  ← idle
    Dev-env SaaS tool (low usage):       $300/mo  ← non-constraint
    Subtotal OE (non-constraint):       $1,620/mo

  Total current spend: $5,090/mo

Step 3 — Rank investment options by T/CU

  T/CU = estimated throughput gain (%) per $100/month of constraint spend

  Option A: Add 10 integration runners (elevate constraint)
    Cost: +$800/mo
    T impact: +30% deploy frequency (estimated from queue model)
    T/CU: 30% / 8 units = 3.75%/unit  ← highest

  Option B: Migrate integration tests to ARM runners (30% faster per run)
    Cost: +$100/mo (ARM premium)
    T impact: +15% constraint throughput (faster runs = more capacity)
    T/CU: 15% / 1 unit = 15%/unit ← effectively same as A at lower cost

  Option C: Upgrade cache storage for unit tests
    Cost: +$200/mo
    T impact: ~0% (non-constraint stage)
    T/CU: 0

  Option D: Implement tiered review SLA (R2 recipe — mostly labor cost)
    Cost: +$0 incremental tooling
    T impact: +40% PR-to-merge throughput (from R2 FRT)
    T/CU: ∞ (no additional spend)

Step 4 — Reallocation decision

  Eliminate non-constraint OE:
    Remove 12 unused SaaS CI seats:     −$480/mo saved
    Reduce cache storage (non-constraint): −$100/mo saved
    Cancel low-usage dev-env tool:       −$300/mo saved
    Total freed: $880/mo

  Reinvest in constraint:
    Option D first (zero cost, implement R2 tiered review policy)
    Option B next ($100/mo for ARM migration — exploit before elevate)
    Option A with freed budget ($800/mo for integration runner elevation)
    Total reinvestment: $900/mo (absorbed by $880 freed + $20 net increase)

  Net result:
    Spend unchanged (−$880 + $900 = +$20/mo net increase)
    T impact: +40% (review policy) × +15% (ARM migration) × +30% (elevation)
    Compounded throughput gain estimate: ~90–100% over current baseline

Step 5 — Verify and recheck constraint
  After 4 weeks of policy change (R2) and ARM migration:
    Re-run 5FS measurement (Step 1 of R1)
    Constraint likely shifts to deploy stage or code review
    Repeat reallocation analysis for new constraint

  Review platform spend quarterly against current constraint.
  Any spend that is not at or enabling the constraint is a candidate
  for reallocation or elimination.
```

**Key principle**: the reallocation exercise should be run quarterly, not once. As the constraint shifts through the pipeline (integration tests → review → deploy → infra provisioning), the T-generating spend classification changes. Static budget allocations that made sense when the constraint was in CI will be wrong once the constraint is review latency.

---

## Composition Guide

TOC primitives in DevOps compose across timescales and decision types. The most effective platform operations apply multiple primitives in sequence:

| Problem class | Entry primitive | Composition |
|---------------|-----------------|-------------|
| Throughput not improving despite CI investment | Policy Constraints (#10) | P7 audit → CRT (#5) → EC (#4) if conflict → FRT (#6) |
| Deploy frequency stall with unknown root cause | CRT (#5) | P5 → FRT (#6) for injection design → PRT (#7) for implementation |
| Shared CI capacity contention | 5FS (#1) + DBR (#2) | P1 identifies constraint → P2 schedules flow → P3 decides elevation |
| Platform spend decision | Throughput Accounting (#3) | R3 → 5FS to identify constraint → elevation decision |
| Build-vs-buy architectural conflict | Evaporating Cloud (#4) | P4 → FRT (#6) to validate injection |
| Platform migration project lateness | Critical Chain (#9) | P8 → resource buffer planning → buffer management discipline |
| Review SLA policy reform | CRT + EC + FRT | R2 full sequence |

**Composition rule**: identify the constraint before applying any other primitive. 5FS is always the entry point. Throughput Accounting ranks investments once the constraint is known. DBR schedules flow around the known constraint. CRT/FRT diagnose and design when the constraint is policy-driven. Critical Chain manages projects where the constraint is a shared resource across tasks.

**Starting order for a new platform team**:

1. **R1 (throughput recovery)** — measure and identify where the constraint actually is. Most teams are surprised by the answer.
2. **P7 (policy audit)** — run in parallel; if policy is the binding constraint, skip CI investment entirely.
3. **R2 (review SLA reform)** — the highest-T/CU intervention in most organizations, and it costs nothing in infrastructure.
4. **R3 (spend reallocation)** — once constraint is identified and policy is reformed, reallocate budget to the constraint before adding net new spend.

---

## Sources

- Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press.
- Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press.
- Goldratt, E.M. (1994). *It's Not Luck*. North River Press.
- Goldratt, E.M. (1997). *Critical Chain*. North River Press.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press.
- Corbett, T. (1998). *Throughput Accounting*. North River Press.
- Schragenheim, E., Dettmer, H.W. & Patterson, J.W. (2009). *Supply Chain Management at Warp Speed*. CRC Press.
- Leach, L.P. (2000). *Critical Chain Project Management*. Artech House.
- Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution.
- Kim, G., Humble, J., Debois, P. & Willis, J. (2016). *The DevOps Handbook*. IT Revolution.
- DORA State of DevOps Report 2023. [https://dora.dev](https://dora.dev)
- Google SRE Book (2016). Chapter 17: "Testing for Reliability." [https://sre.google/sre-book](https://sre.google/sre-book)
- GitHub Actions documentation — merge queues and concurrency. [https://docs.github.com/en/actions](https://docs.github.com/en/actions)
- Argo Rollouts documentation. [https://argoproj.github.io/rollouts](https://argoproj.github.io/rollouts)
