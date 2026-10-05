---
description: Reliability-theory patterns for QA strategy — FMEA-driven risk-based test selection and error-budget-aware test gating, plus corrected layered-detection and minimal-cut-set formulas.
status: stable
primitives:
  - foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md
  - foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md
  - foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md
  - foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md
  - foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md
  - foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md
---

# Reliability Theory Applied — QA Testing Strategy

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. Definitions and derivations live there; this file keeps only the QA decisions they drive.

Scope: P1 (FMEA-driven test selection) and P6/R3 (error-budget-aware gating). Hazard, allocation and Weibull theory: [`foundations-reliability-theory`](../../foundations-reliability-theory/SKILL.md); chaos execution: [`qa-resilience`](../../qa-resilience/SKILL.md). Burn-rate alerting is owned by [qa-observability slo-design-guide](../../qa-observability/references/slo-design-guide.md#canonical-multi-window-burn-rate-table) — SRE Workbook ch. 5, Table 5-8 (99.9% SLO, 30 days): page at 14.4× over 1 h AND 5 min, page at 6× over 6 h AND 30 min, ticket at 1× over 3 d AND 6 h. Do not copy or extend it here.

## Contents

- [P1 — FMEA-Driven Risk-Based Test Selection](#p1--fmea-driven-risk-based-test-selection)
- [P6 — Error-Budget-Aware Test Gating](#p6--error-budget-aware-test-gating)
- [R3 — Error-Budget Gate with Post-Deploy Regression Cadence](#r3--error-budget-gate-with-post-deploy-regression-cadence)
- [Corrected formulas: layered detection and minimal cut sets](#corrected-formulas-layered-detection-and-minimal-cut-sets)
- [Cross-References](#cross-references)

---

### P1 — FMEA-Driven Risk-Based Test Selection

**Problem.** More candidate scenarios than CI budget; selection is informal (the PR author nominates tests) or coverage-weighted with no weighting by impact.

**Primitive.** FMEA scoring and its pitfalls: [`06-fmea.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md). Never rank by RPN alone — every S ≥ 9 row is reviewed and covered independently of RPN.

**Operationalization.** Before the release sprint, run a scoped FMEA over the components the release touches (component, failure mode, effect on the SLO, S/O/D, RPN). Tier the rows (thresholds are a local choice; recalibrate to your scoring scale):

- **Tier 1** (S ≥ 9, or RPN ≥ 150): mandatory, gate-blocking coverage.
- **Tier 2** (RPN 60–149 and S ≤ 8): targeted batch suite before the deploy gate.
- **Tier 3** (RPN < 60 and S ≤ 8): tracked, not tested this cycle; revisit if the component's failure rate changes.

For each Tier-1 row, write a test title and place it at the smallest effective layer (unit → component → integration → E2E).

**Output.** A test-selection manifest linking each gate-blocking scenario to its FMEA row, layer, and the S or RPN that justified it — kept as release evidence.

---

### P6 — Error-Budget-Aware Test Gating

**Problem.** A binary "tests pass → deploy" gate ignores how much error budget remains, so a passing release can still spend the headroom needed for the next incident.

**Primitive.** Budget = (1 − SLO) × window; consumed budget = bad events (or bad minutes) accumulated over the window. See [`08-error-budgets.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md). Keep the window a parameter; 30 days = 720 h = 43,200 min.

**Worked example** (99.9% SLO, 30-day window, 38 min downtime consumed):

```text
total budget     = 0.001 × 720 h × 60 = 43.2 min
remaining        = 43.2 − 38 = 5.2 min  (12.0% of budget)  → RESTRICTED tier
```

**Tiered gate** (fractions are a local policy choice, not from the SRE Workbook — tune per service):

- **> 50% remaining — standard:** required tests passing is sufficient.
- **20–50% — elevated:** all P1 Tier-1 scenarios, plus fault injection for the top-ranked minimal cut sets ([below](#corrected-formulas-layered-detection-and-minimal-cut-sets)); re-score FMEA for changed components if the last one is > 14 days old.
- **10–20% — restricted** (exactly 20% is elevated; exactly 10% is restricted): on-call sign-off, full E2E deploy-gate suite, and a risk statement citing current budget and projected release consumption.
- **< 10% — freeze:** reliability patches only, each with a written justification, rollback plan and post-deploy MTTR target ([`01-mtbf-mttr.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md)).

Publish the state as a named CI check, e.g. "Error Budget Gate: 8.7 min / 43.2 min remaining (20.1%). Elevated gate active." Units pitfall: 720 h is the *window*, not the budget; a 432-min budget would belong to a 99% SLO.

---

### R3 — Error-Budget Gate with Post-Deploy Regression Cadence

**When to use.** At every release decision point; implements P6 and adds a post-deploy cadence.

**Step 1 — compute budget state and gate tier.**

```bash
SLO_TARGET=0.999
WINDOW_HOURS=720          # 30-day rolling window; keep as a parameter
DOWNTIME_MINUTES=$(curl -s "$PROMETHEUS_URL/api/v1/query" \
  --data-urlencode 'query=sum_over_time(slo_downtime_minutes[30d])' \
  | jq -r '.data.result[0].value[1]')

TOTAL_BUDGET_MIN=$(echo "scale=6; (1 - $SLO_TARGET) * $WINDOW_HOURS * 60" | bc)
REMAINING_FRACTION=$(echo "scale=6; ($TOTAL_BUDGET_MIN - $DOWNTIME_MINUTES) / $TOTAL_BUDGET_MIN" | bc)

if   (( $(echo "$REMAINING_FRACTION > 0.5"  | bc -l) )); then echo "Gate: STANDARD"
elif (( $(echo "$REMAINING_FRACTION >= 0.2" | bc -l) )); then echo "Gate: ELEVATED — Tier-1 FMEA + top cut-set fault injection"
elif (( $(echo "$REMAINING_FRACTION >= 0.1" | bc -l) )); then echo "Gate: RESTRICTED — on-call sign-off + full E2E"
else echo "Gate: FREEZE — reliability patches only"; exit 1
fi
```

**Step 2 — run the tier's suites and emit a summary artifact.**

```text
Error Budget Gate Summary
  SLO / window:      99.9% / 30 days (720 h)
  Total budget:      43.2 min
  Consumed:          38 min   (88.0%)
  Remaining:         5.2 min  (12.0%)
  Gate tier:         RESTRICTED (10–20% band)
  Required suites:   smoke, tier1-fmea, contract, full E2E deploy-gate
  Sign-off:          on-call engineer, risk statement attached
  Deploy:            APPROVED WITH RESTRICTED GATE (all suites PASS)
```

**Step 3 — post-deploy watch (72 h).** Record the deploy timestamp and collect failure times for the changed components from production telemetry and post-deploy CI runs.

**Step 4 — choose cadence from the evidence you actually have.** Most fixes produce few post-deploy failures. Compare failure counts against the pre-fix baseline by default. Fit Weibull β only when the confidence interval on β is narrow enough to separate the regimes you would act on (β < 1 → full regression at 24 h; β ≈ 1 → return to weekly cadence; β > 1 → add drift tests to nightly). No fixed failure count guarantees that; decide from the CI width — see [`09-weibull-analysis.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md). Never branch on a point estimate whose interval spans more than one regime.

**Step 5 — append to the deploy record:** pre-deploy budget and tier, suite results, the count-vs-baseline comparison (and β with its interval if fitted), budget consumed in the window, cadence decision, and fix status.

**Verify.** Budget remaining is computed from the SLO gap, not the window length; the correct tier is applied; cadence changes cite either the baseline comparison or a β interval that excludes the other regimes.

---

## Corrected formulas: layered detection and minimal cut sets

Earlier versions of this file got both wrong; keep these forms when reasoning about test layers or fault-injection priority.

**Layered detection is a parallel (redundant) system.** A defect escapes only if every layer misses it:

```text
P(escape) = ∏ (1 − dᵢ)        dᵢ = detection probability of layer i
```

Example: unit 0.6, integration 0.5, E2E 0.3 → P(escape) = 0.4 × 0.5 × 0.7 = 0.14. Assumes independent layers; shared fixtures or oracles correlate blind spots and raise the real escape rate. Parallel-system math: [`10-system-reliability.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md).

**Rank minimal cut sets by rate, not λ₁ × λ₂** (units of 1/time², not a rate). Rare-event approximation for repairable components:

```text
qᵢ ≈ λᵢ × MTTRᵢ                       (steady-state unavailability)
size-1 cut set {A}:     rate ≈ λ_A
size-2 cut set {A, B}:  rate ≈ λ_A·q_B + λ_B·q_A
```

Rank fault-injection scenarios by these rates; a single point of failure usually dominates unless its λ is tiny, but compute it. Model common-cause failures (shared power, shared deploy) as their own size-1 cut set. Derivation: [`05-fault-tree-analysis.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md).

---

## Cross-References

- [`foundations-reliability-theory/SKILL.md`](../../foundations-reliability-theory/SKILL.md) and [`decision-and-validation.md`](../../foundations-reliability-theory/references/decision-and-validation.md) — canonical primitives and validation rules.
- [`qa-resilience`](../../qa-resilience/SKILL.md) — chaos and fault-injection execution for the cut sets ranked above.
- [`slo-design-guide.md`](../../qa-observability/references/slo-design-guide.md) — SLO design and burn-rate alert implementation.
- [`causal-inference-applied.md`](../../qa-debugging/references/causal-inference-applied.md) — attribute what failed after production; this file prioritises what to test before it.
- [`production-testing-and-shift-right.md`](production-testing-and-shift-right.md) — the P6/R3 budget state feeds these release-gate patterns.
- [`quality-metrics-dashboard.md`](quality-metrics-dashboard.md) — FMEA RPN trends from P1 are dashboard candidates.
