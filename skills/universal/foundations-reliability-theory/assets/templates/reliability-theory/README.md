# Reliability Theory Primitives — Composition Guide

11 domain-agnostic reliability theory primitives. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | What It Computes |
|---|------|-----------------|
| 1 | [01-mtbf-mttr.md](01-mtbf-mttr.md) | Mean time between failures and mean time to repair from observation data |
| 2 | [02-availability-formulas.md](02-availability-formulas.md) | Availability from MTBF/MTTR; series and parallel composition |
| 3 | [03-hazard-functions.md](03-hazard-functions.md) | Instantaneous failure rate; classifies CFR/IFR/DFR |
| 4 | [04-bathtub-curve.md](04-bathtub-curve.md) | Three lifecycle phases: infant mortality, useful life, wear-out |
| 5 | [05-fault-tree-analysis.md](05-fault-tree-analysis.md) | Top-down failure decomposition; minimal cut sets; SPOF identification |
| 6 | [06-fmea.md](06-fmea.md) | Bottom-up failure mode enumeration; RPN scoring; mitigation ranking |
| 7 | [07-redundancy-math.md](07-redundancy-math.md) | Active, standby, k-of-n, m-out-of-n; coverage adjustment |
| 8 | [08-error-budgets.md](08-error-budgets.md) | SRE error budget arithmetic; multi-window burn rate |
| 9 | [09-weibull-analysis.md](09-weibull-analysis.md) | Weibull distribution fitting; B10 life; shape classification |
| 10 | [10-system-reliability.md](10-system-reliability.md) | Series/parallel/mixed topology; common-cause failure adjustment |
| 11 | [11-reliability-allocation.md](11-reliability-allocation.md) | Apportioning a system target to subsystems (AGREE, ARINC, equal) |

---

## Composition Recipes

### Service Availability Target (Start Here)

**Goal**: establish an SLO and confirm the architecture can meet it.

1. **Measure MTBF and MTTR** per component (primitive 01).
2. **Compute component availability** A = MTBF/(MTBF+MTTR) (primitive 02).
3. **Compose through the topology** (series × parallel) to get A_system (primitive 10).
4. **Allocate the SLO target** to each subsystem that is below spec (primitive 11).
5. **Set error budget** from the SLO to govern deployment decisions (primitive 08).

**Use when**: sizing a new service, onboarding a dependency, or reviewing an existing SLO against architecture reality.

---

### FMEA Before Launch

**Goal**: find and rank failure risks before shipping to production.

1. **Run FMEA** across all components and interfaces — output severity/obligations-first action table with secondary RPN screening (primitive 06).
2. **Build fault tree** for the top 2–3 highest-severity failure modes — find minimal cut sets and SPOFs (primitive 05).
3. **Apply redundancy math** to the identified SPOFs and high-probability paths — size the redundancy needed (primitive 07).
4. **Re-score FMEA** after mitigations are designed — validate the evidence for each changed S/O/D factor before accepting residual RPN.

**Use when**: pre-launch reliability review, design review gate, regulatory certification prep.

---

### Post-Incident Reliability Update

**Goal**: after an incident, update reliability models and improve the system.

1. **Update MTBF and MTTR** from the incident data (primitive 01).
2. **Reassess the hazard model** from age/exposure-adjusted failure history and uncertainty; one incident cannot establish a decreasing, constant or increasing hazard ([NIST](https://www.itl.nist.gov/div898/handbook/apr/section1/apr124.htm); primitives 03 and 04).
3. **Re-fit Weibull** when the additional data can change parameter uncertainty or the maintenance decision; retain censoring and exposure information (primitive 09).
4. **Add the failure mode to the FMEA** worksheet; re-score RPN (primitive 06).
5. **Re-allocate reliability targets** to subsystems that fell below spec (primitive 11).

**Use when**: post-incident review or when new failure/exposure data could change a reliability decision; no universal event count establishes a trustworthy fit.

---

### Sizing Redundancy for an SLO

**Goal**: choose the minimum redundancy architecture that achieves a reliability target.

1. **Choose the target**: mission reliability needs survival probability at the mission time; repairable-service availability needs mean up/down times. MTBF alone does not establish a survival curve (primitives 01, 02 and 09).
2. **Try active redundancy options**: use the parallel formula for 1-of-2 and the binomial k-of-n sum for 2-of-3 under independent, identical-component assumptions ([NIST](https://www.itl.nist.gov/div898/handbook/apr/section1/apr184.htm); primitive 07).
3. **Apply coverage adjustment** — model switchover/detection reliability; check if redundancy helps or hurts at current coverage c (primitive 07).
4. **Account for common-cause failures** using the beta-factor model (primitive 10).
5. **Verify the system meets the SLO** using full topology composition (primitive 10).

**Use when**: infrastructure sizing, deciding between active/standby architectures, evaluating quorum configurations.

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — full anti-patterns catalogue, decision checklist, and source notes
