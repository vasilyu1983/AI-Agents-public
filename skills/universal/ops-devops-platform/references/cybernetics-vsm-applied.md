# Cybernetics and VSM Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-cybernetics-vsm` § When to Apply](../../foundations-cybernetics-vsm/SKILL.md#when-to-apply) first. If the foundation's skip conditions match, use the foundation it names instead.

This file is a link adapter. It maps VSM functions onto platform, SRE and on-call structures and keeps the platform-specific decisions and pitfalls. The theory lives in the foundation:

- Primitive definitions: [`primitives-overview.md`](../../foundations-cybernetics-vsm/references/primitives-overview.md) and the templates in [`assets/templates/cybernetics-vsm/`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/).
- Ashby's law and the coverage test: [`02-ashbys-law.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md) and [`response-coverage-audit.md`](../../foundations-cybernetics-vsm/references/response-coverage-audit.md). Its worked example is a platform team.
- Traps: [`patterns-scenarios-traps.md`](../../foundations-cybernetics-vsm/references/patterns-scenarios-traps.md).

---

## Table of Contents

- [Platform-to-VSM Map](#platform-to-vsm-map)
- [Patterns](#patterns)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
- [Cross-References](#cross-references)
- [Sources](#sources)

---

## Platform-to-VSM Map

| VSM function | Platform implementation | Missing-function symptom |
|---|---|---|
| S1 operations | Product teams operating their own services and namespaces | Platform team runs product deploys (A1) |
| S2 coordination | GitOps sync waves and dependency ordering, migration gates, environment locks, admission policy | Deploy storms, table locks across teams, manual sequencing by the platform team |
| S3 internal control | Platform team: quotas, platform SLAs, policy-as-code, cost allocation | Policies with no accountability loop |
| S3* audit | Live-fire PRR, sampled audits of live services, chaos game days | Services pass PRR but fail real incidents (A3) |
| S4 intelligence | Technology and vendor radar, deprecation and CVE tracking | Emergency migrations from end-of-life notices (A5) |
| S5 identity/policy | Architecture or governance board; exception log | Policy erodes into case-by-case exceptions |
| Algedonic channel | Pager with bypass routing | Budget exhausted before the first page (A2) |

Team Topologies mapping (a practitioner heuristic, not Beer): stream-aligned teams ≈ S1; a platform team is both an S1 service provider and a variety amplifier for other S1s through self-service; enabling teams amplify S1 capability for a period; interaction modes are S2 protocols. See Skelton & Pais (2019) for the topology itself.

---

## Patterns

### P1 SLO Feedback Loop as Negative Control

An SLO regulates only when a measured deviation reaches an effector (deploy freeze, traffic shift, rollback, incident) before the budget is gone.

```text
Goal:       SLO target (99.9% over 30 days → ~43 min of full outage budget)
Sensor:     burn rate over paired long and short windows
Comparator: SRE Workbook Table 5-8 for 99.9%: page at 14.4× over 1h (5m short window),
            page at 6× over 6h (30m), ticket at 1× over 3d (6h)
Effector:   named in the runbook linked from the alert, before the SLO goes live
```

At 14.4× a 30-day budget lasts about 50 hours (720 h / 14.4). Keep the slow loop (SLO review feeding the backlog) separate from the fast loop (the page). Lowering the target to match observed performance is goal erosion; put target changes behind S5 approval (P7). Primitive: [`01-feedback-loops.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/01-feedback-loops.md).

### P2 Platform Team as S3 to Product-Team S1 Units

| S3 function | Platform implementation |
|---|---|
| Resource allocation | Namespace `ResourceQuota` and `LimitRange` |
| Accountability bargain | Written platform contract: platform SLA (availability, build and deploy P95) in exchange for teams operating within policy |
| Policy | OPA/Gatekeeper, network policy, image allowlists, required labels |
| Optimisation | Observability standards, golden path templates, cost allocation |

The platform team stays out of product teams' deploy path. Reconcile S3 (current SLA performance) with S4 (adaptation backlog) in one forum; the interval is set by change rate, not by convention. Primitive: [`05-vsm-system-3.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/05-vsm-system-3.md).

### P3 Golden Paths as Attenuation, Self-Service as Amplification

Do **not** size the platform problem by multiplying configuration options and subtracting a headcount-times-patterns figure. Those are linear counts, while Ashby's variety is logarithmic and bounds residual outcome variety from below, so the difference means nothing (see [`02-ashbys-law.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md)). Instead:

1. Group product-team requests by the response they need: standard provisioning, quota change, breaking migration, security exception, novel escalation.
2. For each class, check that it can be told apart from the request fields and that an authorised owner can meet its deadline. Use the [coverage table](../../foundations-cybernetics-vsm/references/response-coverage-audit.md).
3. **Attenuate** classes that differ only in irrelevant detail: golden path templates, request forms that keep the distinguishing fields.
4. **Amplify** where one owner is the bottleneck: IDP or Backstage self-service, Terraform modules, Helm libraries, delegated authority for tech leads.
5. **Coverage test the golden path itself:** list the distinct deployment patterns in use (stateful, batch, GPU, special networking or compliance) and confirm the path can express each one. Patterns it cannot express become shadow infrastructure (A4).

Primitives: [`10-variety-engineering.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/10-variety-engineering.md), [`02-ashbys-law.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md).

### P4 Pager as Algedonic Channel

| Element | Platform implementation |
|---|---|
| Trigger | Burn-rate pages (P1), plus business-impact triggers you calibrate yourself |
| Content | Service, severity, blast radius, last deploy, runbook and dashboard links |
| Bypass | Direct page to on-call and on-call lead; never via the ticket queue |
| Response window | Set per severity from the consequence deadline |
| De-escalation | Burn back below the page threshold for a sustained interval, with human acknowledgement for the top tier |

**Positive ("pleasure") signals:** a sustained traffic surge that calls for a capacity decision can use the same bypass with its own threshold.

**Channel integrity:** fix noisy triggers rather than muting the channel. Log every page as true positive, false positive or not actioned. Set the recalibration triggers (false-positive share, silence period, missed-signal share) from your own history; no source here supplies a universal value. Re-test after routing or rota changes. Primitive: [`11-algedonic-channels.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/11-algedonic-channels.md).

### P5 PRR and Chaos Game Days as S3* Audit

| PRR mode | Function | Risk |
|---|---|---|
| Checkbox review | S2 attenuation (normalises S1 output) | Teams optimise the form, not readiness |
| Live walkthrough | S3* probe of real runbooks, alerts and rota | Too costly for every deploy |
| Unannounced sampling of live services | Sporadic S3* | Must stay unpredictable and non-punitive |

A game day is S3* when it tests claims the reporting chain cannot: does the runbook work with the database down, does the page arrive in the window, does rollback finish before the budget is spent? Keep at least one element unannounced: the failure mode, the timing or the target. Primitive: [`06-vsm-system-3-star.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/06-vsm-system-3-star.md).

### P6 Technology and Vendor Radar as S4

| S4 function | Implementation |
|---|---|
| Scanning | Vendor briefings, CVE feeds, cloud-provider roadmaps and deprecation notices |
| Future model | Platform roadmap |
| S3/S4 negotiation | SLA performance reviewed in the same forum as the adaptation backlog |
| Signal to S3 | Deprecations and advisories become backlog items with urgency scores |

A vendor radar entry records usage scope, contract end, migration complexity and the reason for its ring. Update it when a vendor, security or regulatory signal changes, not only on a fixed cadence. Primitive: [`07-vsm-system-4.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/07-vsm-system-4.md).

### P7 Architecture and Governance Board as S5

The board holds identity (runtime, language set, security baseline), policy that S3 and S1 cannot override (data residency, secrets, segmentation) and S3/S4 conflict resolution. It issues directives and time-boxed exceptions, and logs both. An empty exception log means exceptions are happening silently. A board that approves deploys or PRs has collapsed into S3. Primitive: [`08-vsm-system-5.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/08-vsm-system-5.md).

### P8 CI and GitOps as S2

| Destructive oscillation | S2 mechanism |
|---|---|
| Deploy storms saturating the cluster | Argo CD sync waves, Flux dependency ordering, concurrency limits |
| Migrations locking shared tables | Backward-compatible migrations with a hold gate before cutover |
| Shared test-environment contention | Per-team namespaces with quotas; CI environment locks |
| Silent configuration drift | Admission-time policy-as-code |

If the platform team sequences deploys by hand, missing S2 automation has been replaced by S3 overhead. Primitive: [`04-vsm-system-2.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/04-vsm-system-2.md).

### P9 Recursion in Multi-Cluster Operations

```text
Level 3 org:       S5 governance board · S4 radar · S3 platform team · S2 state locking and provisioning pipeline · S1 clusters
Level 2 cluster:   S5 admission policy · S4 node-pool and maintenance tracking · S3 cluster on-call · S2 scheduler, admission, network policy · S1 namespaces
Level 1 namespace: S5 team policy · S4 tech lead · S3 team on-call · S2 service mesh · S1 services
```

A disturbance a level can absorb (a circuit breaker trips and recovers) should never reach the level above. Route each level's algedonic trigger to the next level's on-call. Primitive: [`09-recursion-levels.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/09-recursion-levels.md).

### P10 On-Call Coverage

Do not compare "services × failure types × contexts" with a count of runbook responses. Build a coverage table of failure classes against signal, runbook or automation, authorised responder and deadline, and mark uncovered or late classes. Then close them:

| Intervention | Type | Effect |
|---|---|---|
| Tested runbooks for the classes that recur | Amplifier | More classes have an effective response |
| Ownership tiering (non-core services escalate to their owners) | Attenuator | Fewer classes reach the primary on-call |
| Automated remediation for well-understood classes | Amplifier | No human needed for them |
| Standard telemetry labels (`service.name`, env, version) | Attenuator | One diagnosis method across services |

A PRR is the gate that keeps an unprepared service out of the primary rota.

---

## Anti-Patterns

### A1 Platform Team Collapses S3 into S1

The platform team writes product teams' Terraform, runs their deploys and approves their PRs. It is always overloaded, product teams wait, and S4 work never happens. Fix: a written platform contract separating S3 (policy, quota, SLA) from S1 execution; self-service until routine deploy requests stop arriving.

### A2 Pager Threshold Too High

The budget is gone before the first page; customers report incidents first. The threshold was raised until false positives stopped. Fix: work back from the budget and response window using the Table 5-8 windows (P1), and fire a synthetic fault in staging or a canary to confirm the page arrives in time.

### A3 PRR as S2 Filter Instead of S3* Probe

Services pass PRR but runbooks reference retired services, alert thresholds are stale and the on-call cannot be identified. Fix: live-fire the alert during PRR, run the runbook under a simulated fault, and sample live services, because readiness decays.

### A4 Golden Path Rigidity

Teams run shadow infrastructure and exceptions pile up because the path was built for the median case. Fix: coverage-test the path (P3 step 5), add documented extension points, and keep a public exception registry. Treat an exception that recurs across teams as a feature request.

### A5 S4 Absent

Migrations are driven by end-of-life notices; known CVEs arrive late; the roadmap is purely reactive. Fix: name an S4 owner (a rotation in small teams), protect time for it, and put radar output on the backlog next to SLA metrics. Set the time share from observed adaptation debt; this file supplies no sourced percentage.

---

## Recipes

### R1 Platform Accountability and Autonomy Charter

1. **Coverage audit:** list recent product-team requests by the response each needed and fill the coverage table (P3). The uncovered or bottlenecked classes are the golden-path and self-service candidates.
2. **S3/S1 boundary:**
   - Platform owns: cluster lifecycle, network policy framework, security baseline, shared observability, golden paths and IDP, platform SLA.
   - Product teams own: their deploys, runbooks, on-call rotas, flags and experiments.
3. **Quotas:** set per-namespace requests and limits from each team's SLO and traffic model. Renegotiate them jointly when demand or SLOs change.
4. **Policy catalogue:** every policy states its rationale, its exception route (to S5, not S3) and a review trigger.
5. **Platform SLOs with burn-rate alerts (P1).** Publish performance to product teams. A breach triggers a postmortem and a backlog item.
6. **Close three loops:**
   - Fast: alert → on-call.
   - Slow: SLA report → backlog → S4.
   - Governance: exception log → S5 review → policy change.

Success signals: routine deploy requests stop reaching the platform team; the exception log is non-empty and reviewed; SLA and roadmap are discussed in the same forum.

### R2 Algedonic Escalation Stack

1. **Tiers by recursion level:**

   | Tier | Trigger | Routes to |
   |---|---|---|
   | Top | Fast-burn page, confirmed security incident, or a business-impact trigger you have calibrated | Org level |
   | Middle | Slow-burn page, or a critical service down | Cluster/SRE level |
   | Team | Service-level ticket burn | Owning team only |

2. **Bypass routing:** top and middle tiers never go through ticketing. Escalate to the next responder on no-acknowledgement within a timeout chosen from the consequence deadline.
3. **Structured alert body:** severity, service and environment, impact, trigger metric and threshold, last deploy SHA, runbook link, dashboard link.
4. **De-escalation:** clear when burn falls below the page threshold for a sustained period. Never auto-clear the top tier without a human.
5. **Channel health:** track true-positive, false-positive and missed-signal (found by customers) rates. Recalibrate on thresholds you set from your own data. Run a synthetic test when the top tier has been silent for longer than your incident history makes plausible.
6. **Close-out:** a blameless postmortem that asks whether the channel fired, whether the threshold was right, and whether the bypass worked. Route the actions to the backlog with owners.

### R3 PRR as an S3* Audit Programme

1. **Tiers:**
   - A: every launch or major change.
   - B: unannounced sampling of live services.
   - C: triggered by incidents or by findings that recur in one category.
2. **Live validation:**
   - Inject a fault and confirm the right person is paged within the window.
   - Have the on-call follow the runbook to resolution.
   - Confirm dashboards and traces show the fault.
   - Compare declared dependencies with the mesh topology.
3. **Classify findings:**
   - Green: none.
   - Yellow: fix within an agreed window.
   - Red: alert not firing, no on-call, or no runbook. Remediation hold with a negotiated traffic cap.
4. **Feed back to S2:** when sampling finds the same class across several services, add it to the launch checklist, enforce it at admission time, or fix the golden path so teams no longer have to solve it themselves.
5. **Programme review:** reviews run, findings per audit, holds and their duration, and checklist items added from sampling. Hold the review whenever finding patterns shift.

**Starting order:** R1, then R2, then R3, then P6. An S4 roadmap built before the S3/S1 boundary exists cannot be executed.

---

## Cross-References

- [control-theory-applied.md](control-theory-applied.md): deployment and autoscaling feedback control (complements P1)
- [queueing-theory-applied.md](queueing-theory-applied.md): capacity and CI bottlenecks (P3, P10)
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md): CI/CD throughput constraint (P2)
- [platform-engineering-patterns.md](platform-engineering-patterns.md): IDP, golden paths, self-service (P3, R1)
- [sre-incident-management.md](sre-incident-management.md) and [operational-patterns.md](operational-patterns.md): incident, runbook and postmortem detail (R2, R3)
- [foundations-cybernetics-vsm](../../foundations-cybernetics-vsm/SKILL.md): primitives, coverage audit and sources

---

## Sources

- Ashby, W.R. (1956). *An Introduction to Cybernetics*, §11/7 (residual outcome variety bounded below). [https://ashby.info/Ashby-Introduction-to-Cybernetics.pdf](https://ashby.info/Ashby-Introduction-to-Cybernetics.pdf)
- Beer, S. (1972). *Brain of the Firm*; Beer, S. (1985). *Diagnosing the System for Organizations*.
- Google SRE Workbook (2018), ch. 5 "Alerting on SLOs", Table 5-8. [https://sre.google/workbook/alerting-on-slos/](https://sre.google/workbook/alerting-on-slos/)
- Google SRE Book (2016). [https://sre.google/sre-book](https://sre.google/sre-book)
- Skelton, M. & Pais, M. (2019). *Team Topologies*. IT Revolution.
- Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate*. IT Revolution.
- OPA/Gatekeeper documentation. [https://open-policy-agent.github.io/gatekeeper](https://open-policy-agent.github.io/gatekeeper)
