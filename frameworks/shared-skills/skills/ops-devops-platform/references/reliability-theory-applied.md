# Reliability Theory Applied — Ops & DevOps Platform

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Reliability-theory primitives mapped to platform engineering practice: SLO design and error-budget policy,
multi-region availability composition, deploy-gate FMEA, on-call MTTR reduction, redundancy sizing for
Kubernetes workloads, and chaos game-day design. Each section names the anchoring primitive and links
its full reference.

---

## Table of Contents

- [Why Reliability Theory Matters for Platform Engineering](#why-reliability-theory-matters-for-platform-engineering)
- [Patterns](#patterns)
  - [P1 — SLO Derivation from MTBF/MTTR Baselines](#p1--slo-derivation-from-mtbfmttr-baselines)
  - [P2 — Multi-AZ Active-Active Availability Composition](#p2--multi-az-active-active-availability-composition)
  - [P3 — Error-Budget Policy as a Deploy Gate](#p3--error-budget-policy-as-a-deploy-gate)
  - [P4 — Pre-Launch FMEA for CI/CD Pipelines](#p4--pre-launch-fmea-for-cicd-pipelines)
  - [P5 — Reliability Allocation Across Microservices](#p5--reliability-allocation-across-microservices)
  - [P6 — Kubernetes Replica Redundancy Sizing](#p6--kubernetes-replica-redundancy-sizing)
  - [P7 — Golden-Signal Rollback as MTTR Lever](#p7--golden-signal-rollback-as-mttr-lever)
- [Anti-Patterns](#anti-patterns)
  - [A1 — SLO Set to Match Current Measured Availability](#a1--slo-set-to-match-current-measured-availability)
  - [A2 — Shared Error Budget Across Independent Services](#a2--shared-error-budget-across-independent-services)
  - [A3 — Correlated Multi-AZ Replicas Treated as Independent](#a3--correlated-multi-az-replicas-treated-as-independent)
  - [A4 — No FMEA Before Major Platform Changes](#a4--no-fmea-before-major-platform-changes)
  - [A5 — Reliability Allocation Skipped for Third-Party Dependencies](#a5--reliability-allocation-skipped-for-third-party-dependencies)
- [Recipes](#recipes)
  - [R1 — SLO + Error-Budget Bootstrap for a New Service](#r1--slo--error-budget-bootstrap-for-a-new-service)
  - [R2 — Multi-Region Capacity Plan from Availability Targets](#r2--multi-region-capacity-plan-from-availability-targets)
  - [R3 — Chaos Game Day Designed Against FMEA RPN Ranking](#r3--chaos-game-day-designed-against-fmea-rpn-ranking)
- [Cross-References](#cross-references)

---

## Why Reliability Theory Matters for Platform Engineering

Platform teams own the availability of the systems they build and the systems that run on top of them.
Without a quantitative framework, availability targets are set by intuition, error budgets are managed by
feel, and redundancy decisions are made by copying prior art. The result is SLOs that do not reflect
customer need, error budgets that are silently exhausted before anyone acts, and replica counts that
either over-provision by 3× or fail during the first AZ-level fault.

Reliability theory provides the arithmetic to close each of those gaps:
MTBF and MTTR anchor SLO targets to measured data; availability composition formulas translate component
numbers into system numbers before infrastructure is provisioned; error-budget arithmetic converts
abstract percentages into concrete deploy decisions; FMEA surfaces failure modes before they reach
production; and reliability allocation distributes responsibility to the team or service that can
actually close each gap. These are not heavyweight formalisms — each can be applied in a 30-minute
platform review or a 2-hour game day with nothing more than a spreadsheet and production metrics.

---

## Patterns

### P1 — SLO Derivation from MTBF/MTTR Baselines

**Derives from Primitive 1: MTBF/MTTR** and **Primitive 2: Availability Formulas**

**The problem.** SLOs set by guessing ("99.9% sounds right") are divorced from the system's measured
failure rate and recovery speed. The resulting SLOs are either aspirational targets that are
immediately breached or trivial ones that provide no customer signal.

**The approach.** Compute the system's operational availability from historical incident data, then set
the SLO relative to a realistic improvement goal rather than the current baseline.

```text
MTBF = total_uptime_hours / incident_count
MTTR = total_downtime_hours / incident_count
A_current = MTBF / (MTBF + MTTR)

Example (payment API, last 90 days):
  total_uptime  = 2,154 h
  incidents     = 9
  total_downtime = 4.5 h

  MTBF = 2,154 / 9 = 239 h  (~10 days between incidents)
  MTTR = 4.5 / 9   = 0.5 h  (30 min to restore)
  A_current = 239 / 239.5 ≈ 0.99791  (99.79%)
```

**SLO target selection heuristic.**

- Set the SLO above A_current to signal a reliability improvement goal.
- Set it no more than one nines step above what the team can realistically achieve in 2 quarters
  without rewiring architecture (e.g., moving from 99.79% to 99.9% requires cutting MTTR from
  30 min to ~13 min — achievable with better runbooks; moving to 99.99% requires structural changes).
- Express the improvement as a concrete MTBF or MTTR target so each team knows which lever to pull:

```text
99.9% target:
  A = MTBF / (MTBF + MTTR) = 0.999
  Holding MTBF constant at 239 h:
    0.999 = 239 / (239 + MTTR)  →  MTTR = 0.239 h = ~14 min

  Action: reduce on-call response + triage time from 30 min to 14 min
  (runbook automation, pre-baked rollback, alerting latency reduction).
```

**On-call implication.** Tracking MTTR per team over rolling 30-day windows is a stronger signal than
the raw SLO percentage. A team consistently closing incidents in 10 min will reliably hold a 99.9% SLO
even under moderate increase in incident frequency.

---

### P2 — Multi-AZ Active-Active Availability Composition

**Derives from Primitive 7: Redundancy Math** and **Primitive 2: Availability Formulas**

**The problem.** "We're multi-AZ, so we're highly available" is a common claim that is rarely verified
against the actual service topology. Active-active arrangements improve availability only when the
redundancy is genuinely independent and the switchover is reliable.

**Active-active AZ composition formula.**

For n identical, independent AZ replicas (1-of-n active redundancy):

```text
A_multi_az = 1 - (1 - A_single_az)^n
```

For a service with A_single_az = 0.9995 (53 min/year downtime per AZ):

```text
2 AZs:  A = 1 - (0.0005)^2 = 1 - 0.00000025 ≈ 0.999999750  (five and a half nines)
3 AZs:  A = 1 - (0.0005)^3 ≈ 0.999999999875  (eight nines — overkill for most SLOs)
```

**Imperfect coverage matters more than replica count.**

The redundancy gain collapses when the load-balancer, DNS failover, or Kubernetes service routing
that detects a failed AZ and redirects traffic has its own reliability shortfall:

```text
R_covered = c × A_parallel + (1 - c) × A_single
```

If your ALB/NLB health-check routing has c = 0.995 (fails to detect or redirect 0.5% of AZ failures):

```text
R = 0.995 × 0.999999750 + 0.005 × 0.9995
  ≈ 0.99499 + 0.0049975
  ≈ 0.99999  (five nines — not eight)
```

The coverage mechanism is the binding constraint. Investing in faster, more accurate health checks
(shorter intervals, deeper synthetic probes) yields more availability than adding a third AZ when
c < 0.999.

**Full stack composition example.**

A three-tier web service across 2 AZs:

```text
Load balancer (single, managed):  A_lb  = 0.9999
App layer (2 AZs, active-active): A_app = 1 - (1 - 0.9995)^2 = 0.999999750
Database (2 replicas + failover):
  A_db_single = 0.9997
  coverage c  = 0.99   (RDS Multi-AZ failover occasionally misses in-progress txns)
  A_db = 0.99 × (1 - (1-0.9997)^2) + 0.01 × 0.9997 ≈ 0.999991

System: A = 0.9999 × 0.999999750 × 0.999991 ≈ 0.99989  (99.989%)
Annual downtime: (1 - 0.99989) × 8,760 h ≈ 0.96 h/year
```

The load balancer (A = 0.9999) is the tightest constraint; the app layer active-active arrangement
buys almost nothing because LB availability already dominates.

---

### P3 — Error-Budget Policy as a Deploy Gate

**Derives from Primitive 8: Error Budgets**

**The problem.** Most CI/CD pipelines gate deploys on test pass and security scans but ignore current
error-budget state. A deploy that consumes the remaining 3 minutes of a 43-minute monthly budget
turns a healthy service into an SLO breach before anyone is paged.

**Error-budget burn-rate deploy gate.**

Compute the multi-window burn rate before every production deploy:

```text
monthly_budget = (1 - SLO) × 43,800 min

Fast-burn alert threshold (1-hour window):
  if consumed_1h > monthly_budget / 72  → block deploy; page

Slow-burn alert threshold (6-hour window):
  if consumed_6h > monthly_budget / 168 → require SRE approval before deploy
```

**Deploy risk tiers based on budget state.**

| Budget remaining | Allowed deploys |
|-----------------|----------------|
| > 50%           | All deploys allowed including risky migrations |
| 25%–50%         | Feature deploys allowed; no schema migrations or config overhauls |
| 10%–25%         | Bugfixes and rollbacks only; all other deploys require SRE sign-off |
| < 10%           | Freeze; only emergency rollbacks with dual approval |

**Policy in CI/CD pipeline (pseudocode).**

```python
def deploy_gate_check(service: str, slo: float, window_min: int = 43_800) -> str:
    budget = (1 - slo) * window_min          # total budget in minutes
    consumed_1h = get_downtime_minutes(service, last_hours=1)
    consumed_6h = get_downtime_minutes(service, last_hours=6)
    consumed_30d = get_downtime_minutes(service, last_days=30)
    remaining_pct = (budget - consumed_30d) / budget

    if consumed_1h > budget / 72:
        return "BLOCK"          # fast burn: 1h pace exhausts budget in 3 days
    if consumed_6h > budget / 168:
        return "REQUIRE_APPROVAL"
    if remaining_pct < 0.10:
        return "FREEZE"
    if remaining_pct < 0.25:
        return "BUGFIX_ONLY"
    return "ALLOW"
```

**GitOps integration.** Embed the gate as a pre-deploy GitHub Actions step or Argo CD pre-sync hook.
Surface the budget state in the PR description so the developer sees the risk context before
requesting merge. Output the raw numbers (budget, consumed, remaining) alongside the verdict so the
gate is auditable and not a black box.

---

### P4 — Pre-Launch FMEA for CI/CD Pipelines and Platform Changes

**Derives from Primitive 6: FMEA**

**The problem.** CI/CD pipelines and platform components (Terraform modules, admission controllers,
secrets backends) are treated as infrastructure rather than services. They receive no design review
for failure modes. When they fail, they block every team simultaneously — the blast radius is
platform-wide.

**FMEA worksheet for a CD pipeline.**

Run a 2-hour FMEA sprint before major pipeline or platform changes. Scope: every component that
participates in a deploy or in steady-state production traffic.

| Component | Failure Mode | Effect on Deploys | S (1–10) | O (1–10) | D (1–10) | RPN | Action |
|-----------|-------------|-------------------|----------|----------|----------|-----|--------|
| Secrets manager (Vault) | Unsealed vault unavailable | All new pods fail to start | 9 | 3 | 3 | 81 | Cache secrets in init-container with 15-min TTL |
| Container registry | Rate-limit or outage | Image pull failures; pods stuck Pending | 8 | 4 | 4 | 128 | Mirror critical images to regional ECR/Artifact Registry |
| Terraform state backend (S3+DynamoDB) | Lock contention or S3 outage | Plan/apply blocked; IaC drift unresolvable | 7 | 3 | 5 | 105 | Separate state buckets per environment; add state backup |
| Admission webhook (OPA/Kyverno) | Webhook timeout > FailurePolicy | Pod creation blocked cluster-wide | 10 | 2 | 3 | 60 | Set `failurePolicy: Ignore` for non-critical webhooks; add QoS |
| CI runner pool | All runners exhausted | Deploys and PRs queue indefinitely | 6 | 5 | 6 | 180 | Autoscale runner pool; set queue depth alert |

**Prioritise by RPN; never ignore S ≥ 9 regardless of RPN.**

The CI runner exhaustion (RPN 180) and image registry outage (RPN 128) are the top two priorities.
Note that admission webhook has S = 10 (cluster-wide blast) and should be addressed even at lower RPN.

**Closing the FMEA loop.** After each production incident, add the failure mode to the FMEA worksheet
with its observed S, O, and D scores. Over time this turns the worksheet into a living failure catalog
anchored to real events rather than speculation.

---

### P5 — Reliability Allocation Across Microservices

**Derives from Primitive 11: Reliability Allocation**

**The problem.** A platform must meet a top-level SLO (e.g., 99.95% monthly checkout availability)
but the SLO is defined at the product level. Microservice teams lack a per-service target and invest
in reliability improvements arbitrarily — sometimes over-investing in already-reliable services and
under-investing in the actual bottleneck.

**Equal allocation as the starting point.**

For n services in series under the checkout critical path:

```text
R_system = 0.9995  (99.95%)
n = 5 series services (API gateway, auth, inventory, payment, order DB)

Equal allocation:
  Rᵢ = R_system^(1/n) = 0.9995^(1/5) = 0.9999^(1/5) ≈ 0.9999
  Each service must achieve 99.99% monthly availability.
```

**ARINC re-allocation to concentrate investment at the weakest link.**

After measuring current service availabilities, re-allocate using failure-rate proportional weighting:

```text
Current service availabilities (monthly, last 3 months):
  API gateway:  0.99995
  Auth:         0.99992
  Inventory:    0.99980  ← weakest; 8.8 min downtime/month
  Payment:      0.99988
  Order DB:     0.99985

System actual: 0.99995 × 0.99992 × 0.99980 × 0.99988 × 0.99985
             = 0.99940  (misses the 0.9995 target)

ARINC allocation concentrates the improvement budget on Inventory (largest failure-rate share):
  Required improvement: bring Inventory from 99.980% to 99.992%
  Lever: halve MTTR from ~9 min to ~4 min via faster cache failover
  Then: system reaches 0.9999 × 0.99992 × 0.99992 × 0.99988 × 0.99985 ≈ 0.9996 [OK]
```

**Output for each team.** Convert the allocated availability target into concrete MTBF and MTTR
sub-targets:

```text
Inventory service — allocated Rᵢ = 0.99992 monthly
  Budget:   0.00008 × 43,800 min = 3.5 min downtime/month
  Current MTTR: ~9 min
  Required MTTR: ≤ 3.5 min (only 1 incident per month allowed before budget is spent)
  Or:  MTTR 7 min + MTBF doubled (from 21 days to 42 days between incidents)
```

Providing teams with MTBF and MTTR sub-targets (not just a percentage) tells them which lever to pull:
faster detection + rollback (MTTR), or fewer deploys of risky changes (MTBF).

---

### P6 — Kubernetes Replica Redundancy Sizing

**Derives from Primitive 7: Redundancy Math** and **Primitive 2: Availability Formulas**

**The problem.** Replica counts in Kubernetes deployments are set by developers based on load handling,
not by availability arithmetic. A two-replica deployment provides essentially no availability
improvement if both replicas run on the same node or the same AZ.

**Minimum replica count from k-of-n formula.**

For a service to survive the loss of 1 of n pods (1-of-n active redundancy) with per-pod availability
A_pod = 0.9990:

```text
n=1: A = 0.9990  (no redundancy)
n=2: A = 1 - (1-0.9990)^2 = 1 - 0.000001 = 0.999999  (five nines — but only if pods are independent)
n=3: A = 1 - (1-0.9990)^3 ≈ 0.9999999990  (overkill unless pods are correlated)
```

**With imperfect coverage (rolling update or eviction risk).**

During a rolling deploy, Kubernetes maintains `maxUnavailable` pods unavailable. If maxUnavailable = 1
and the service needs k-of-n, then the effective redundancy during the rollout is (n-1)-of-n.
A 2-replica deployment with maxUnavailable=1 is effectively a single-replica deployment for the
duration of each pod replacement — availability collapses to the single-pod value.

```text
minAvailable for 2 replicas:  set maxUnavailable: 0 (creates 3rd pod before removing)
  or use PodDisruptionBudget:  minAvailable: 2

For 3 replicas + maxUnavailable: 1:
  Rolling update maintains 2-of-3 at all times
  A_rolling = 1 - (1-0.9990)^2 ≈ 0.999999  (maintains five nines through deploy)
```

**Topology spread for true independence.**

Pod anti-affinity ensures the 1-of-n formula is valid (independent failures):

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: inventory-api
```

Without this, pods may co-locate in a single AZ, making the redundancy correlated (common-cause
failure on AZ fault) and the availability formula invalid.

---

### P7 — Golden-Signal Rollback as MTTR Lever

**Derives from Primitive 1: MTBF/MTTR**

**The problem.** MTTR is the single most actionable lever for services where failure rate (MTBF)
cannot be reduced further without structural rework. In a GitOps-managed system, most MTTR comes from
two sources: detection latency (time from deploy to golden-signal alert) and rollback latency
(time from alert to traffic restored from previous good version).

**Golden signal thresholds that trigger automated rollback.**

Define rollback thresholds per signal during SLO design, not during an incident:

```text
Success rate:   < SLO target for 5 consecutive minutes  → automated rollback
P99 latency:    > 2× baseline for 5 consecutive minutes → automated rollback
Error rate:     > 1% for 3 consecutive minutes          → automated rollback
Saturation:     CPU or memory > 90% for 5 minutes       → scale-up alert + manual review
```

**MTTR decomposition for a golden-signal rollback pipeline.**

```text
Total MTTR = T_detection + T_decision + T_rollback_execution + T_traffic_cutover

Typical unoptimized:    60 min total
  T_detection:          15 min  (alert fires 5 min after deploy; on-call paged at 15 min)
  T_decision:           10 min  (triage, confirm bad deploy vs external incident)
  T_rollback_execution: 5 min   (manual git revert, CI rebuild, ArgoCD sync)
  T_traffic_cutover:    30 min  (DNS TTL, cache warm)

Optimized with automation:
  T_detection:          2 min   (synthetic probe + deploy-annotated metric watch)
  T_decision:           0 min   (automated trigger on sustained threshold breach)
  T_rollback_execution: 1 min   (Argo Rollouts canary abort → previous ReplicaSet)
  T_traffic_cutover:    2 min   (in-cluster service mesh traffic split, no DNS change)
  Total MTTR:           ~5 min
```

The jump from 60-minute to 5-minute MTTR on the same MTBF improves monthly availability from 99.79%
to 99.997% — three nines gained without touching failure rate.

---

## Anti-Patterns

### A1 — SLO Set to Match Current Measured Availability

**Ignores Primitive 1: MTBF/MTTR and Primitive 8: Error Budgets**

Setting the SLO to whatever the system measured last quarter guarantees an always-full error budget
that never signals reliability investment need. The budget becomes decorative: it is never meaningfully
spent, never drives a deploy freeze, and never creates pressure for improvement. The team discovers
real reliability problems only from customer escalations, not from their own SLO machinery.

**Correct approach.** Set the SLO to the level customers actually require, compute the gap against
measured A_current, and derive the MTBF or MTTR improvement needed to close that gap. The budget
should be modestly tight: 20–40% should be spent in a typical month from normal changes and experiments.
If the budget is spent less than 10% per month, the SLO is too easy.

---

### A2 — Shared Error Budget Across Independent Services

**Misapplies Primitive 8: Error Budgets**

Pooling error budgets across multiple services means one team's reliability incident silences another
team's deploys. Service A causes a 3-hour outage, exhausts the shared budget, and Service B — which
has been perfectly healthy — cannot ship a critical security fix because the shared budget reads zero.

This breaks the budget's purpose as a reliability signal: teams lose the connection between their own
reliability choices and their own deploy velocity.

**Correct approach.** Maintain per-service error budgets. If a platform component (Kubernetes control
plane, secrets manager, Terraform state backend) affects multiple services, it receives its own budget
as a platform-layer SLO — separate from the product services that depend on it.

---

### A3 — Correlated Multi-AZ Replicas Treated as Independent

**Misapplies Primitive 7: Redundancy Math and Primitive 2: Availability Formulas**

The 1-of-n availability formula assumes independent failure. Two pods in the same AZ, or two replicas
sharing a single managed database primary, fail together on AZ fault or primary failure. The formula
`A = 1 - (1-A)^n` no longer applies; the effective redundancy collapses to n = 1 for correlated
failures.

This produces wildly optimistic availability predictions. A team that calculated five nines from a
two-replica deployment discovers during an AZ outage that they have zero replicas remaining.

**Correct approach.** Apply the imperfect-coverage formula from Primitive 7 when common-cause failures
are possible. Model the AZ failure probability as a common-cause factor. Use topology spread
constraints (Pattern P6) to make independence real, then re-verify with the composition formula from
Primitive 2.

---

### A4 — No FMEA Before Major Platform Changes

**Ignores Primitive 6: FMEA**

Rolling out a new secrets backend, upgrading the Kubernetes admission control stack, or migrating
Terraform state without a pre-change FMEA means the team discovers failure modes during the change
rather than before it. Platform changes have wide blast radius: a misconfigured admission webhook
that blocks pod creation or a Vault renewal misconfiguration that causes mass secret expiry can take
down dozens of services simultaneously.

The cost of a 2-hour FMEA sprint is trivial compared to a multi-team, multi-hour P0 caused by a
predictable failure mode that was not analyzed.

**Correct approach.** Run a scoped FMEA before every platform component change with S ≥ 7 failure
modes. Treat the FMEA worksheet as a go/no-go artifact in the change review process. Gate high-RPN
items on explicit mitigation before proceeding.

---

### A5 — Reliability Allocation Skipped for Third-Party Dependencies

**Ignores Primitive 11: Reliability Allocation**

When reliability targets are allocated only to internal services, third-party dependencies (managed
database providers, CDN vendors, payment processors, SaaS observability platforms) receive no explicit
reliability target. The product SLO is mathematically dependent on their availability, but no one
checks whether their published SLA matches the allocated target.

This creates invisible reliability debt: the system can never exceed the lowest-availability component
in its series chain, regardless of how reliable internal services are.

**Correct approach.** Include third-party dependencies as components in the reliability allocation.
Check each vendor's SLA against the allocated target. Where the vendor SLA falls short, add redundancy
(multi-vendor, fallback mode, or graceful degradation). Document the gap explicitly in the platform's
reliability model so it is reviewed at each architecture change.

---

## Recipes

### R1 — SLO + Error-Budget Bootstrap for a New Service

**Objective**: Derive a defensible SLO from measured data, compute the monthly error budget, configure
multi-window burn-rate alerts, and embed a deploy gate in CI/CD — all before the service accepts
production traffic.

**Primitive stack**: Primitive 1 (MTBF/MTTR) + Primitive 2 (Availability Formulas) + Primitive 8
(Error Budgets)

**Step 1: Extract MTBF and MTTR from staging or prior-generation data.**

```bash
# Pull incident timestamps from PagerDuty / Opsgenie
# If no incident history, use load-test failure events from staging.

python3 - <<'EOF'
import json, datetime

# incidents: list of {"start": ISO8601, "end": ISO8601}
incidents = json.load(open("incidents.json"))

total_downtime_h = sum(
    (datetime.datetime.fromisoformat(i["end"]) -
     datetime.datetime.fromisoformat(i["start"])).total_seconds() / 3600
    for i in incidents
)
observation_window_h = 2160  # 90 days
n = len(incidents)
uptime_h = observation_window_h - total_downtime_h

mtbf = uptime_h / n
mttr = total_downtime_h / n
a_current = mtbf / (mtbf + mttr)

print(f"MTBF:      {mtbf:.1f} h ({mtbf/24:.1f} days)")
print(f"MTTR:      {mttr*60:.1f} min")
print(f"A_current: {a_current:.5f}  ({a_current*100:.3f}%)")
print(f"Annual downtime: {(1-a_current)*8760*60:.0f} min")
EOF
```

**Step 2: Select SLO target and compute budget.**

```bash
# Choose SLO one step above A_current; verify required MTTR improvement.
SLO=0.999          # 99.9%
WINDOW_MIN=43800   # 30-day month in minutes

python3 -c "
slo = ${SLO}
budget = (1 - slo) * ${WINDOW_MIN}
print(f'Monthly error budget: {budget:.1f} min ({budget/60:.2f} h)')
print(f'Required MTTR to hit SLO with same MTBF:')
mtbf_h = 239  # from Step 1
mttr_required_h = mtbf_h * (1 - slo) / slo
print(f'  MTTR ≤ {mttr_required_h*60:.1f} min')
"
```

**Step 3: Create Prometheus burn-rate recording rules.**

```yaml
# prometheus/rules/slo_${SERVICE}.yaml
groups:
  - name: slo_burn_${SERVICE}
    interval: 1m
    rules:
      - record: slo:burn_rate_1h:ratio
        expr: |
          (1 - avg_over_time(up{job="${SERVICE}"}[1h]))
          /
          (1 - ${SLO})

      - record: slo:burn_rate_6h:ratio
        expr: |
          (1 - avg_over_time(up{job="${SERVICE}"}[6h]))
          /
          (1 - ${SLO})

      - alert: SloBudgetFastBurn_${SERVICE}
        expr: slo:burn_rate_1h:ratio > 14.4   # exhausts monthly budget in 72h at this rate
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "Fast error-budget burn on ${SERVICE}: {{ $value | humanize }}× normal rate"

      - alert: SloBudgetSlowBurn_${SERVICE}
        expr: slo:burn_rate_6h:ratio > 6      # exhausts monthly budget in 5 days
        for: 30m
        labels:
          severity: ticket
```

**Step 4: Add deploy gate to CI pipeline.**

```yaml
# .github/workflows/deploy.yml (partial)
jobs:
  budget-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check error budget before deploy
        run: |
          CONSUMED=$(curl -s "http://prometheus/api/v1/query?query=\
            sum_over_time(slo_bad_minutes_total{job='${SERVICE}'}[30d])" \
            | jq -r '.data.result[0].value[1]')
          BUDGET=$(python3 -c "print((1 - ${SLO}) * 43800)")
          REMAINING_PCT=$(python3 -c "print(100 * (${BUDGET} - ${CONSUMED}) / ${BUDGET})")
          echo "Budget remaining: ${REMAINING_PCT}%"
          if (( $(python3 -c "print(1 if ${REMAINING_PCT} < 10 else 0)") )); then
            echo "::error::Error budget < 10% — deploy frozen. Requires SRE approval."
            exit 1
          fi

  deploy:
    needs: budget-check
    # ... rest of deploy steps
```

**Step 5: Verify gate and alerts are wired before go-live.**

```bash
# Inject a synthetic failure to confirm burn-rate alert fires within 10 min.
kubectl exec -it deploy/${SERVICE} -- curl -X POST localhost:8080/debug/trigger-errors
# Confirm PagerDuty/Opsgenie receives the fast-burn alert within 10 min.
# Confirm deploy job is blocked when budget threshold is crossed.
# Reset and verify full recovery.
```

---

### R2 — Multi-Region Capacity Plan from Availability Targets

**Objective**: Given a system availability target, compute the minimum number of regions and replicas
required, verify the composition arithmetic, and produce a capacity plan with explicit failure-mode
assumptions.

**Primitive stack**: Primitive 2 (Availability Formulas) + Primitive 7 (Redundancy Math) + Primitive
11 (Reliability Allocation)

**Step 1: Define the system availability target and decompose into layers.**

```text
Target:  A_system = 0.9999  (four nines, ~52 min/year)
Layers (series):
  1. DNS / global load balancer
  2. Regional edge (CDN/WAF)
  3. Application tier (multi-replica per region)
  4. Data layer (primary + replica per region)

Equal allocation across 4 series layers:
  Rᵢ = 0.9999^(1/4) ≈ 0.999975  (each layer must achieve 99.9975%)
```

**Step 2: Compute per-layer replica count to hit allocated target.**

```bash
python3 - <<'EOF'
import math

allocated_R = 0.999975      # from equal allocation above
pod_availability = 0.9995   # typical well-run pod (from measured MTBF/MTTR)

# Minimum n such that 1 - (1 - pod_availability)^n >= allocated_R
for n in range(1, 10):
    r_n = 1 - (1 - pod_availability)**n
    sufficient = r_n >= allocated_R
    print(f"n={n}: A={r_n:.8f}  {'[OK]' if sufficient else '[X]'}")
    if sufficient:
        print(f"Minimum replicas needed: {n}")
        break
EOF
# Output example:
# n=1: A=0.99950000  [X]
# n=2: A=0.99999975  [OK]
# Minimum replicas needed: 2
```

**Step 3: Verify region count meets single-region failure tolerance.**

```bash
python3 - <<'EOF'
# Single-region availability for the full stack (2 replicas per layer, 4 series layers)
A_region = 0.99999975 ** 4   # all layers meeting allocated target in one region

# With multi-region active-active (1-of-n regions must be healthy)
# Assume coverage c = 0.998 (global LB health-check reliability)
c = 0.998

for n_regions in range(1, 4):
    A_parallel = 1 - (1 - A_region)**n_regions
    A_covered  = c * A_parallel + (1 - c) * A_region
    annual_min = (1 - A_covered) * 8760 * 60
    print(f"n_regions={n_regions}: A={A_covered:.7f}  annual_downtime={annual_min:.1f}min")
EOF
# Evaluate: 2 regions + c=0.998 achieves target; 3 regions adds buffer for LB imperfect coverage.
```

**Step 4: Document capacity assumptions and failure modes explicitly.**

```markdown
## Multi-Region Capacity Plan — ${SERVICE}

### Assumption table (invalidates plan if wrong)

| Assumption | Value | Source | Review cadence |
|------------|-------|---------|----------------|
| Per-pod availability | 0.9995 | 90-day measured MTBF=200h, MTTR=0.1h | Quarterly |
| Global LB coverage c | 0.998 | Vendor SLA (Cloudflare/AWS Global Accelerator) | On SLA change |
| Pod independence | True if topology spread enforced | Verified via kubectl describe pod | Per deploy |
| Region failure independence | Approximate | Different cloud regions share no infra | Annual review |

### Minimum viable configuration

- 2 regions, active-active
- 2 replicas per service tier per region
- topologySpreadConstraints: zone spread enforced
- PodDisruptionBudget: minAvailable=2 per tier per region
- Global LB health-check interval: ≤ 10s, threshold: 2 consecutive failures
```

**Step 5: Run a quarterly availability budget review.**

```bash
# Recompute A_system from actual incident data each quarter.
# Compare against allocated targets per layer.
# Update capacity plan if any layer's measured availability drops > 0.0002 below its target.
# Trigger reliability allocation re-run if A_system gap > 0.0001.
```

---

### R3 — Chaos Game Day Designed Against FMEA RPN Ranking

**Objective**: Design a game day where failure injection scenarios are prioritized by FMEA RPN,
execute them in a controlled sequence, and validate that MTTR, golden-signal rollback, and
redundancy arrangements perform as the availability model predicts.

**Primitive stack**: Primitive 6 (FMEA) + Primitive 1 (MTBF/MTTR) + Primitive 7 (Redundancy Math) +
Primitive 8 (Error Budgets)

**Step 1: Build the RPN-ranked failure scenario backlog from the FMEA worksheet.**

```bash
# Export FMEA worksheet to CSV and sort by RPN descending.
# Select top 5 failure modes for the game day; exclude S < 5 as low-value.
# For each selected scenario, record:
#   - Hypothesis: "If [failure mode], then [system behavior] because [mechanism]"
#   - Success criterion: "Service recovers within MTTR_target with < X% error-budget consumed"
#   - Rollback plan: how to restore state if scenario causes unexpected impact

# Example ranked list:
# 1. CI runner pool exhaustion (RPN 180)
#    Hypothesis: runner queue saturates → deploys block; service itself unaffected
#    Success: no production SLO impact; deploy queue clears within 15 min when runners added
#
# 2. Container registry outage (RPN 128)
#    Hypothesis: new pod starts fail with ImagePullBackOff; existing pods unaffected
#    Success: in-flight pods continue serving traffic; alert fires within 5 min; on-call escalates
#
# 3. Vault unavailability (RPN 81)
#    Hypothesis: pods with cached secrets continue; new pod starts fail after cache TTL
#    Success: cached TTL > incident duration; no customer impact for <15-min outages
```

**Step 2: Inject failures in order and measure actual MTTR against model prediction.**

```bash
# Scenario 2: Container registry outage simulation
# 1. Block registry egress at the network policy level (safe, reversible)
kubectl apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: chaos-block-registry
  namespace: staging
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - ${REGISTRY_CIDR}/16  # block only registry traffic
EOF

# 2. Trigger a rolling restart to force image pulls (confirms existing pods unaffected).
kubectl rollout restart deployment/${SERVICE} -n staging

# 3. Measure:
#    - Time from NetworkPolicy apply to ImagePullBackOff alert: _____ min (target ≤ 5 min)
#    - Number of pods stuck in Pending/ImagePullBackOff: _____
#    - Any impact on error rate for already-running pods: _____
#    - Time to alert and acknowledged: _____

# 4. Restore:
kubectl delete networkpolicy chaos-block-registry -n staging
kubectl rollout restart deployment/${SERVICE} -n staging   # clear any stuck pods
```

**Step 3: Validate redundancy model predictions against observed behavior.**

```bash
# Scenario: single AZ pod eviction (validates P6 replica sizing)
# 1. Cordon and drain all nodes in one AZ.
ZONE="us-east-1a"
for node in $(kubectl get nodes -l topology.kubernetes.io/zone=${ZONE} -o name); do
  kubectl cordon $node
  kubectl drain $node --ignore-daemonsets --delete-emptydir-data --grace-period=30
done

# 2. Observe:
#    - Do pods reschedule to remaining AZs? (confirms topologySpreadConstraints working)
kubectl get pods -o wide -l app=${SERVICE} --watch

#    - Does service remain healthy during rescheduling? (validates redundancy math)
#      Expected: zero error-budget consumed (k-of-n model predicts no service interruption)
#      Actual: check Grafana SLO dashboard

# 3. Measure prediction accuracy:
#    - Model predicted A = 0.999999 during single-AZ drain
#    - Actual: compare observed error rate to model prediction
#    - If actual degradation > model prediction: record coverage gap; update FMEA

# 4. Restore:
for node in $(kubectl get nodes -l topology.kubernetes.io/zone=${ZONE} -o name); do
  kubectl uncordon $node
done
```

**Step 4: Update FMEA with observed Detection scores and revise RPNs.**

```bash
# For each game-day scenario:
# - Record actual detection latency (T_detection)
# - Update D score in FMEA: if alert fired within 5 min → D=2; 5-15 min → D=5; >15 min → D=8
# - Recompute RPN with observed D scores
# - Prioritize game-day follow-up items where observed D > assumed D (detection was slower than modeled)
# - Open infra tickets for scenarios where MTTR exceeded model prediction

echo "Game day complete. Update FMEA worksheet with observed D scores."
echo "Scenarios where T_detection exceeded model: open runbook improvement tickets."
echo "Scenarios where redundancy model matched: document as validated architecture decision."
```

---

## Cross-References

### Foundation primitives

| # | Primitive | Link |
|---|-----------|------|
| 1 | MTBF / MTTR | [01-mtbf-mttr.md](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) |
| 2 | Availability Formulas | [02-availability-formulas.md](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) |
| 6 | FMEA | [06-fmea.md](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) |
| 7 | Redundancy Math | [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) |
| 8 | Error Budgets | [08-error-budgets.md](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) |
| 11 | Reliability Allocation | [11-reliability-allocation.md](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) |

Full primitive index: [foundations-reliability-theory SKILL.md](../../foundations-reliability-theory/SKILL.md)

### Sibling applied recipes in this skill

- [control-theory-applied.md](control-theory-applied.md) — PID autoscaling, circuit breakers, recovery
  throttling for platform incident response
- [queueing-theory-applied.md](queueing-theory-applied.md) — CI/CD pipeline saturation, multi-stage
  bottleneck analysis, capacity planning from Little's Law
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — CI/CD throughput recovery,
  review-SLA constraint surfacing, platform spend reallocation
