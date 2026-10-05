# Reliability Theory Applied — Ops & DevOps Platform

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

Link adapter: which platform decisions each reliability primitive drives (SLO targets, deploy gates,
multi-AZ/multi-region topology, pipeline FMEA, replica sizing, rollback MTTR). Formulas and their
derivations live in the foundation; this file keeps only platform-specific thresholds, pitfalls, and
re-derived worked examples. SLO design and alert implementation are owned by
[`qa-observability/references/slo-design-guide.md`](../../qa-observability/references/slo-design-guide.md).

---

## Table of Contents

- [Why Reliability Theory Matters for Platform Engineering](#why-reliability-theory-matters-for-platform-engineering)
- [Patterns](#patterns)
  - [P1 — SLO Derivation from MTBF/MTTR Baselines](#p1--slo-derivation-from-mtbfmttr-baselines)
  - [P2 — Multi-AZ Active-Active Availability Composition](#p2--multi-az-active-active-availability-composition)
  - [P3 — Error-Budget Policy as a Deploy Gate](#p3--error-budget-policy-as-a-deploy-gate)
  - [P4 — Pre-Launch FMEA for CI/CD Pipelines](#p4--pre-launch-fmea-for-cicd-pipelines-and-platform-changes)
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
  - [R3 — Chaos Game Day Designed Against FMEA](#r3--chaos-game-day-designed-against-fmea)
- [Cross-References](#cross-references)

---

## Why Reliability Theory Matters for Platform Engineering

Platform teams own the availability of what they build and of everything running on it. Without the
arithmetic, SLOs are set by intuition, budgets are silently exhausted, and replica counts either
over-provision or fail on the first AZ fault. Each pattern below names the decision, the primitive
that answers it, and the platform-specific trap. Time windows are parameters: 30 days = 43,200 min;
28 days = 40,320 min; an average calendar month = 43,800 min. Use the window your SLO is defined on.

---

## Patterns

### P1 — SLO Derivation from MTBF/MTTR Baselines

**Decision:** which SLO to commit to and which lever (MTBF or MTTR) closes the gap.
**Theory:** [01-mtbf-mttr.md](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [02-availability-formulas.md](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md).

Worked example (payment API, 90 days, re-derived):

```text
uptime 2,154 h, 9 incidents, downtime 4.5 h
MTBF = 239 h (~10 days)   MTTR = 0.5 h (30 min)
A_current = 239 / 239.5 ≈ 0.99791 (99.79%)

99.9% target at constant MTBF:  MTTR = 239 × 0.001 / 0.999 ≈ 0.239 h ≈ 14 min
```

- Set the SLO from customer need, above A_current, and no more than one step beyond what 2 quarters
  of runbook/automation work can reach (99.79% → 99.9% is an MTTR cut from 30 to ~14 min; 99.99%
  needs structural change).
- Hand teams the MTTR or MTBF sub-target, not only the percentage.
- Track MTTR per team over rolling windows; it is the more actionable signal than the SLO percentage.

---

### P2 — Multi-AZ Active-Active Availability Composition

**Decision:** does multi-AZ actually buy the availability being claimed, and where to invest next.
**Theory:** parallel/series composition and imperfect coverage in [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) and [10-system-reliability.md](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md).

Worked example (re-derived; assumes independent AZ failures):

```text
A_single_az = 0.9995
2 AZs, perfect failover:          1 − 0.0005²            = 0.99999975
2 AZs, LB/DNS coverage c = 0.995: 0.995 × 0.99999975 + 0.005 × 0.9995 ≈ 0.9999973

Three-tier stack across 2 AZs:
  LB (single, managed)            0.9999
  App (2 AZs active-active)       0.99999975
  DB (2 replicas, c = 0.99, 0.9997 each)  0.99 × (1 − 0.0003²) + 0.01 × 0.9997 ≈ 0.999997
  System ≈ 0.99990  → ≈ 0.91 h/yr downtime
```

Platform takeaways:

- The failover coverage mechanism (ALB/NLB health checks, DNS failover, Service routing) is usually the
  binding constraint; improving detection depth and interval beats adding a third AZ while c < 0.999.
- In a series stack the weakest single component (here the LB at 0.9999) dominates; redundancy in the
  app tier buys almost nothing until that is addressed.
- Independence is an assumption to verify, not a given (see [A3](#a3--correlated-multi-az-replicas-treated-as-independent)).

---

### P3 — Error-Budget Policy as a Deploy Gate

**Decision:** whether the next production deploy should proceed, need approval, or be frozen.
**Theory:** [08-error-budgets.md](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md). Alert design: [slo-design-guide.md](../../qa-observability/references/slo-design-guide.md).

Burn rate = error rate / (1 − SLO). Use the multi-window thresholds from the SRE Workbook, Chapter 5
"Alerting on SLOs", **Table 5-8** ([sre.google/workbook/alerting-on-slos](https://sre.google/workbook/alerting-on-slos/)),
for a 99.9% SLO over 30 days. Fire only when **both** the long and the short window exceed the rate:

| Severity | Long window | Short window | Burn rate | Budget consumed | Budget exhausted in |
|----------|-------------|--------------|-----------|-----------------|---------------------|
| Page | 1 h | 5 min | 14.4 | 2% | 720 / 14.4 = 50 h |
| Page | 6 h | 30 min | 6 | 5% | 720 / 6 = 120 h (5 days) |
| Ticket | 3 d | 6 h | 1 | 10% | 30 days |

Budget consumed = burn rate × long window / period (e.g. 14.4 × 1 h / 720 h = 2%).

**Deploy tiers by budget remaining** (local policy choice, not from the Workbook; tune per service):

| Budget remaining | Allowed deploys |
|-----------------|----------------|
| > 50% | All, including risky migrations |
| 25%–50% | Features; no schema migrations or config overhauls |
| 10%–25% | Bugfixes and rollbacks; others need SRE sign-off |
| < 10% | Freeze; emergency rollbacks with dual approval |

```python
PERIOD_MIN = 30 * 24 * 60   # 43,200 — must match the SLO window

def burn(err_rate: float, slo: float) -> float:
    return err_rate / (1 - slo)

def deploy_gate_check(service: str, slo: float) -> str:
    b = lambda window: burn(get_error_rate(service, window), slo)
    if b("1h") > 14.4 and b("5m") > 14.4:
        return "BLOCK"               # Table 5-8 page tier: budget gone in ~50 h at this pace
    if b("6h") > 6 and b("30m") > 6:
        return "BLOCK"               # Table 5-8 page tier: budget gone in ~5 days
    if b("3d") > 1 and b("6h") > 1:
        return "REQUIRE_APPROVAL"    # Table 5-8 ticket tier
    remaining = 1 - get_budget_consumed_fraction(service, slo, PERIOD_MIN)
    if remaining < 0.10:
        return "FREEZE"
    if remaining < 0.25:
        return "BUGFIX_ONLY"
    return "ALLOW"
```

Embed as a pre-deploy CI step or Argo CD pre-sync hook, and print budget, consumed, remaining, and each
burn rate beside the verdict so the gate is auditable.

---

### P4 — Pre-Launch FMEA for CI/CD Pipelines and Platform Changes

**Decision:** which pipeline/platform failure modes to mitigate before a change ships.
**Theory:** [06-fmea.md](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md).

Platform components (secrets backends, registries, state backends, admission webhooks, runner pools)
fail with platform-wide blast radius. Run a 2-hour FMEA before major pipeline or platform changes:

| Component | Failure Mode | Effect on Deploys | S | O | D | RPN | Action |
|-----------|-------------|-------------------|---|---|---|-----|--------|
| Secrets manager (Vault) | Unavailable / sealed | New pods fail to start | 9 | 3 | 3 | 81 | Cache secrets in init-container with 15-min TTL |
| Container registry | Rate-limit or outage | ImagePullBackOff; pods Pending | 8 | 4 | 4 | 128 | Mirror critical images to a regional registry |
| Terraform state backend | Lock contention / storage outage | Plan/apply blocked | 7 | 3 | 5 | 105 | Per-environment state; state backup |
| Admission webhook (OPA/Kyverno) | Timeout under `failurePolicy: Fail` | Pod creation blocked cluster-wide | 10 | 2 | 3 | 60 | `failurePolicy: Ignore` for non-critical webhooks; timeouts |
| CI runner pool | All runners exhausted | Deploys and PRs queue | 6 | 5 | 6 | 180 | Autoscale runners; queue-depth alert |

**Never rank by RPN alone.** Review every S ≥ 9 item independently of RPN first: here the admission
webhook (S = 10, RPN 60) and Vault (S = 9, RPN 81) are mandatory mitigations despite ranking below the
runner pool (RPN 180) and registry (RPN 128). Then work the remaining items by RPN.

Close the loop: after each production incident, add the observed failure mode with its S, O, D so the
worksheet becomes a catalog anchored to real events.

---

### P5 — Reliability Allocation Across Microservices

**Decision:** what per-service target each team on a critical path owns.
**Theory:** equal, ARINC, and AGREE allocation in [11-reliability-allocation.md](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md).

Worked example (checkout path, 5 series services, target 0.9995; re-derived):

```text
Equal allocation: Rᵢ = 0.9995^(1/5) ≈ 0.9999 each

Measured (monthly):
  API gateway 0.99995 · Auth 0.99992 · Inventory 0.99980 · Payment 0.99988 · Order DB 0.99985
  System = product ≈ 0.99940  → misses 0.9995

Inventory has the largest failure share. Raise it to 0.99992:
  System ≈ 0.99952  → meets 0.9995
```

Translate the allocation into levers (average month, 43,800 min):

```text
Inventory now:    0.00020 × 43,800 ≈ 8.8 min/month  (≈1 incident/month at ~8.8 min MTTR)
Inventory target: 0.00008 × 43,800 ≈ 3.5 min/month
  Option A: MTTR ≤ 3.5 min at the same incident rate (a 60% cut)
  Option B: halve MTTR to ~4.4 min AND stretch MTBF by 1.25× (~30 → ~38 days)
```

---

### P6 — Kubernetes Replica Redundancy Sizing

**Decision:** replica count, PodDisruptionBudget, rollout surge, and topology spread.
**Theory:** 1-of-n and k-of-n in [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md).

With A_pod = 0.999 and genuinely independent pods: n=2 → 0.999999; n=3 → 0.999999999. Those numbers
are only valid under the Kubernetes conditions below.

- **Rollouts reduce n.** With 2 replicas and `maxUnavailable: 1`, each pod replacement runs on one pod —
  availability collapses to A_pod for that interval. Use `maxUnavailable: 0` with `maxSurge: 1`, or a
  PodDisruptionBudget `minAvailable: 2`. With 3 replicas and `maxUnavailable: 1`, the rollout keeps
  2-of-3 (≈ 0.999999 at A_pod = 0.999).
- **Independence must be enforced.** Without zone spread, pods co-locate and fail together on an AZ fault:

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: inventory-api
```

---

### P7 — Golden-Signal Rollback as MTTR Lever

**Decision:** which rollback automation to fund when MTBF cannot be improved cheaply.
**Theory:** [01-mtbf-mttr.md](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md).

Define rollback triggers during SLO design, not during an incident (thresholds are local defaults to tune):

```text
Success rate  < SLO target for 5 consecutive min   → automated rollback
P99 latency   > 2× baseline for 5 consecutive min  → automated rollback
Error rate    > 1% for 3 consecutive min           → automated rollback
Saturation    CPU/memory > 90% for 5 min           → scale-up alert + manual review
```

MTTR decomposition = detection + decision + rollback execution + traffic cutover:

| Phase | Unoptimized | Automated |
|-------|-------------|-----------|
| Detection | 15 min (paged late) | 2 min (synthetic probe + deploy-annotated metrics) |
| Decision | 10 min (triage) | 0 min (sustained-threshold trigger) |
| Rollback | 5 min (revert, rebuild, sync) | 1 min (Argo Rollouts abort → previous ReplicaSet) |
| Cutover | 30 min (DNS TTL, cache warm) | 2 min (mesh traffic split, no DNS change) |
| **Total** | **60 min** | **5 min** |

At the P1 MTBF of 239 h (re-derived): 60-min MTTR → 239 / 240 ≈ 99.58%; 5-min MTTR → ≈ 99.965%.
The whole gain comes from MTTR with failure rate unchanged.

---

## Anti-Patterns

### A1 — SLO Set to Match Current Measured Availability

An SLO copied from last quarter's measurement leaves the budget permanently full: it never drives a
freeze or investment, and problems surface through customer escalations instead. Set the SLO from
customer need, compute the gap to A_current, and derive the MTBF/MTTR lever (P1). A local heuristic
(not a published standard): if normal change consistently spends under ~10% of the budget, the SLO is
probably too loose. Theory: [08-error-budgets.md](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).

---

### A2 — Shared Error Budget Across Independent Services

Pooling budgets lets one team's outage freeze another team's healthy service (including its security
fixes) and severs the link between a team's reliability choices and its own velocity. Keep per-service
budgets; give shared platform components (control plane, secrets manager, state backend) their own
platform-layer SLO and budget.

---

### A3 — Correlated Multi-AZ Replicas Treated as Independent

Two pods in one AZ, or two replicas behind a single managed database primary, fail together; the 1-of-n
formula then overstates availability by orders of magnitude and effective n collapses to 1 for that
cause. Model common-cause and imperfect coverage ([07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md)),
enforce independence with topology spread (P6), and verify with a drain test (R3).

---

### A4 — No FMEA Before Major Platform Changes

New secrets backends, admission-control upgrades, and Terraform state migrations have wide blast radius;
without a pre-change FMEA the failure modes are discovered during the change. Run a scoped FMEA for any
platform change with S ≥ 7 modes, treat the worksheet as a go/no-go artifact, and require explicit
mitigation for every S ≥ 9 item regardless of RPN (P4).

---

### A5 — Reliability Allocation Skipped for Third-Party Dependencies

Managed databases, CDNs, payment processors, and SaaS observability sit in the series chain, so the
product SLO cannot exceed what they deliver. Include each vendor as a component in allocation (P5),
compare its published SLA to the allocated target, and where it falls short add redundancy
(multi-vendor, fallback, graceful degradation) and record the gap in the reliability model.

---

## Recipes

### R1 — SLO + Error-Budget Bootstrap for a New Service

**Objective:** measured SLO, budget, Table 5-8 alerts, and a CI deploy gate before production traffic.
**Primitives:** 01 MTBF/MTTR, 02 availability, 08 error budgets.

**Step 1 — MTBF/MTTR from incident history** (PagerDuty/Opsgenie export, or staging load-test failures):

```bash
python3 - <<'EOF'
import json, datetime
incidents = json.load(open("incidents.json"))   # [{"start": ISO8601, "end": ISO8601}]
dt = lambda i: (datetime.datetime.fromisoformat(i["end"]) -
                datetime.datetime.fromisoformat(i["start"])).total_seconds() / 3600
down_h = sum(dt(i) for i in incidents)
window_h = 90 * 24
n = len(incidents)
mtbf, mttr = (window_h - down_h) / n, down_h / n
print(f"MTBF {mtbf:.1f} h  MTTR {mttr*60:.1f} min  A {mtbf/(mtbf+mttr):.5f}")
EOF
```

**Step 2 — SLO and budget** (window is a parameter; 30 days = 43,200 min):

```bash
SLO=0.999
WINDOW_MIN=43200   # 30-day window; use 40320 for 28 days
python3 -c "
slo, w, mtbf_h = ${SLO}, ${WINDOW_MIN}, 239
print(f'Budget: {(1-slo)*w:.1f} min')                       # 43.2 min for 99.9% / 30 d
print(f'MTTR needed at same MTBF: {mtbf_h*(1-slo)/slo*60:.1f} min')   # ~14.4 min
"
```

**Step 3 — Prometheus rules (Table 5-8, long AND short window).** Replace `up` with your real SLI ratio.

```yaml
groups:
  - name: slo_burn_${SERVICE}
    rules:
      - record: slo:error_ratio:rate5m
        expr: 1 - avg_over_time(up{job="${SERVICE}"}[5m])
      - record: slo:error_ratio:rate30m
        expr: 1 - avg_over_time(up{job="${SERVICE}"}[30m])
      - record: slo:error_ratio:rate1h
        expr: 1 - avg_over_time(up{job="${SERVICE}"}[1h])
      - record: slo:error_ratio:rate6h
        expr: 1 - avg_over_time(up{job="${SERVICE}"}[6h])
      - record: slo:error_ratio:rate3d
        expr: 1 - avg_over_time(up{job="${SERVICE}"}[3d])

      - alert: SloBurnPageFast_${SERVICE}      # 14.4×: 2% of budget in 1 h; exhausts in ~50 h
        expr: |
          slo:error_ratio:rate1h > 14.4 * (1 - ${SLO})
          and slo:error_ratio:rate5m > 14.4 * (1 - ${SLO})
        labels: {severity: page}
      - alert: SloBurnPageSlow_${SERVICE}      # 6×: 5% of budget in 6 h; exhausts in ~5 days
        expr: |
          slo:error_ratio:rate6h > 6 * (1 - ${SLO})
          and slo:error_ratio:rate30m > 6 * (1 - ${SLO})
        labels: {severity: page}
      - alert: SloBurnTicket_${SERVICE}        # 1×: 10% of budget in 3 d
        expr: |
          slo:error_ratio:rate3d > 1 * (1 - ${SLO})
          and slo:error_ratio:rate6h > 1 * (1 - ${SLO})
        labels: {severity: ticket}
```

**Step 4 — CI deploy gate** (window in the query must match the budget window):

```yaml
jobs:
  budget-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check error budget before deploy
        run: |
          CONSUMED=$(curl -s "http://prometheus/api/v1/query?query=\
            sum_over_time(slo_bad_minutes_total{job='${SERVICE}'}[30d])" \
            | jq -r '.data.result[0].value[1]')
          BUDGET=$(python3 -c "print((1 - ${SLO}) * 43200)")   # 30 days
          REMAINING_PCT=$(python3 -c "print(100 * (${BUDGET} - ${CONSUMED}) / ${BUDGET})")
          echo "Budget remaining: ${REMAINING_PCT}%"
          if (( $(python3 -c "print(1 if ${REMAINING_PCT} < 10 else 0)") )); then
            echo "::error::Error budget < 10% — deploy frozen. Requires SRE approval."
            exit 1
          fi
  deploy:
    needs: budget-check
```

**Step 5 — Verify before go-live:** inject synthetic errors in staging, confirm the 1 h/5 min page fires,
confirm the deploy job blocks at the threshold, then reset and confirm recovery.

---

### R2 — Multi-Region Capacity Plan from Availability Targets

**Objective:** minimum replicas and regions for a system target, with explicit assumptions.
**Primitives:** 02 availability, 07 redundancy, 11 allocation.

**Step 1 — Allocate.** Target 0.9999 (~52 min/yr) across 4 series layers (global LB/DNS, edge, app,
data): equal allocation 0.9999^(1/4) ≈ 0.999975 per layer.

**Step 2 — Replicas per layer.**

```bash
python3 - <<'EOF'
target, a_pod = 0.999975, 0.9995
n = next(n for n in range(1, 10) if 1 - (1 - a_pod)**n >= target)
print(n, 1 - (1 - a_pod)**n)   # 2  0.99999975
EOF
```

**Step 3 — Regions.** On paper one region already meets the target (0.99999975⁴ ≈ 0.999999, ~0.5 min/yr),
because the per-layer model assumes independent pods and ignores region-wide common-cause failure. The
region count is therefore decided by an explicit region-outage term (cloud-region incident history,
control-plane and dependency outages) plus the global-LB coverage c, not by pod math. Model that term,
then compute `c × (1 − (1 − A_region)^n) + (1 − c) × A_region` for n = 1..3.

**Step 4 — Record the assumptions that invalidate the plan.**

| Assumption | Value | Source | Review cadence |
|------------|-------|--------|----------------|
| Per-pod availability | 0.9995 | 90-day MTBF 200 h, MTTR 0.1 h (200/200.1 ≈ 0.9995) | Quarterly |
| Global LB coverage c | e.g. 0.998 | Vendor SLA plus failover drill results | On SLA change |
| Pod independence | True only with zone spread | `kubectl get pods -o wide` | Per deploy |
| Region-outage rate | Measured / vendor history | Provider status history | Annual |

**Step 5 — Quarterly review:** recompute layer availability from incidents; re-run allocation if any
layer drifts below its target or the system gap reopens.

---

### R3 — Chaos Game Day Designed Against FMEA

**Objective:** inject failures chosen from the FMEA, measure actual MTTR and detection against the
model, and feed observed scores back.
**Primitives:** 06 FMEA, 01 MTBF/MTTR, 07 redundancy, 08 error budgets. Safety-II / STPA framing:
[foundations-safety-engineering](../../foundations-safety-engineering/SKILL.md).

**Step 1 — Select scenarios.** Take every S ≥ 9 mode first (from P4: admission webhook, Vault), then the
top remaining modes by RPN (runner pool 180, registry 128). For each record a hypothesis ("if X, then Y
because Z"), a success criterion (recovery within MTTR target, budget consumed < X%), and an abort plan.

**Step 2 — Inject in staging and measure** (registry outage example):

```bash
kubectl apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: chaos-block-registry, namespace: staging}
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - ipBlock: {cidr: 0.0.0.0/0, except: ["${REGISTRY_CIDR}"]}
EOF
kubectl rollout restart deployment/${SERVICE} -n staging
# Measure: time to ImagePullBackOff alert (target ≤ 5 min), stuck pods, error rate on running pods.
kubectl delete networkpolicy chaos-block-registry -n staging
kubectl rollout restart deployment/${SERVICE} -n staging
```

**Step 3 — Validate the redundancy model** by cordoning and draining one zone
(`kubectl drain <node> --ignore-daemonsets --delete-emptydir-data`), watching rescheduling, and
comparing observed error-budget burn with the P6 prediction (≈ zero with zone spread). Any excess is a
coverage gap: record it in the FMEA. Uncordon afterwards.

**Step 4 — Update the FMEA** with observed detection latency (local scale: ≤ 5 min → D = 2; 5–15 min →
D = 5; > 15 min → D = 8), recompute RPN, re-check the S ≥ 9 list, and open tickets where MTTR or
detection exceeded the model.

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
| 10 | System Reliability | [10-system-reliability.md](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) |
| 11 | Reliability Allocation | [11-reliability-allocation.md](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) |

Full index: [foundations-reliability-theory SKILL.md](../../foundations-reliability-theory/SKILL.md) ·
validation: [decision-and-validation.md](../../foundations-reliability-theory/references/decision-and-validation.md) ·
SLO/alert ownership: [slo-design-guide.md](../../qa-observability/references/slo-design-guide.md)

### Sibling applied recipes in this skill

- [control-theory-applied.md](control-theory-applied.md) — autoscaling, circuit breakers, recovery throttling
- [queueing-theory-applied.md](queueing-theory-applied.md) — CI/CD saturation and capacity from Little's Law
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — CI/CD throughput and review-SLA constraints
