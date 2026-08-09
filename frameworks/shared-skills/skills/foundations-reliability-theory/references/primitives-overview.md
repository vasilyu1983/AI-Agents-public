---
description: Domain-agnostic overview of 11 reliability theory primitives. Consumer skills get applied recipe layers in their own reference files.
last_verified: 2026-07-11
status: stable
---

# Reliability Theory Primitives Overview

## Table of Contents

- [Why Reliability Theory Matters](#why-reliability-theory-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Reliability Theory Matters

Reliability failures are not random bad luck — they are the outcome of system properties that can be measured, modelled, and managed. Without a reliability framework:

| Failure Mode | Engineering Diagnosis | What Goes Wrong |
|-------------|----------------------|-----------------|
| MTBF computed as arithmetic average of subsystem MTBFs | Series availability is multiplicative, not additive | System availability appears higher than it is; SLO breaches are surprises |
| MTTR estimated from median-case recovery | Tail incidents skew observed MTTR above the median; budget understated | Error budgets exhausted faster than predicted |
| Error budget burn measured only weekly | Multi-hour exhaustion events hidden in weekly aggregation | Pages arrive after the SLO is already breached |
| Redundancy added without modelling the switchover | Low-coverage failover reduces, not increases, availability | High-availability architecture performs worse than single-instance |
| Weibull fit on 3 failures | Confidence intervals span orders of magnitude; shape classification is noise | Maintenance schedule set on unreliable data; wrong phase assumed |

Each primitive below addresses one or more of these failure modes.

---

## Primitive Index

11 primitives, each with a full playbook under [`../assets/templates/reliability-theory/`](../assets/templates/reliability-theory/).

| # | Primitive | What It Computes | Primary Domains |
|---|-----------|-----------------|-----------------|
| 1 | [MTBF/MTTR](../assets/templates/reliability-theory/01-mtbf-mttr.md) | Mean failure interval and repair time from observation data | Operations, SRE, hardware, platform |
| 2 | [Availability Formulas](../assets/templates/reliability-theory/02-availability-formulas.md) | Steady-state availability; series and parallel composition | SLO design, architecture review |
| 3 | [Hazard Functions](../assets/templates/reliability-theory/03-hazard-functions.md) | Instantaneous failure rate; CFR / IFR / DFR classification | Lifetime analysis, distribution selection |
| 4 | [Bathtub Curve](../assets/templates/reliability-theory/04-bathtub-curve.md) | Lifecycle phase identification: infant mortality, useful life, wear-out | Burn-in planning, maintenance scheduling |
| 5 | [Fault Tree Analysis](../assets/templates/reliability-theory/05-fault-tree-analysis.md) | Top-down causal decomposition; minimal cut sets; SPOF identification | Safety analysis, incident root-cause, design review |
| 6 | [FMEA](../assets/templates/reliability-theory/06-fmea.md) | Bottom-up failure mode enumeration; RPN scoring | Pre-launch review, process audit, certification |
| 7 | [Redundancy Math](../assets/templates/reliability-theory/07-redundancy-math.md) | Active, standby, k-of-n, m-out-of-n; coverage adjustment | Infrastructure sizing, HA architecture |
| 8 | [Error Budgets](../assets/templates/reliability-theory/08-error-budgets.md) | SLO-derived allowable unreliability; multi-window burn rate | SRE, deployment governance, SLO management |
| 9 | [Weibull Analysis](../assets/templates/reliability-theory/09-weibull-analysis.md) | Lifetime distribution fitting; Bx life; shape parameter β | Maintenance planning, accelerated-life testing |
| 10 | [System Reliability](../assets/templates/reliability-theory/10-system-reliability.md) | Series/parallel/mixed topology; common-cause failure | Architecture design, supplier qualification |
| 11 | [Reliability Allocation](../assets/templates/reliability-theory/11-reliability-allocation.md) | Subsystem target apportionment from system goal | Requirements, contracts, improvement prioritisation |

---

## Anti-Patterns by Domain

### SLO Design and Operations

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Arithmetic average of subsystem MTBFs used for system MTBF | Series availability is multiplicative | Compute A_system = ∏ Aᵢ using primitive 02 |
| MTTR estimated from happy-path drills only | Tail incidents never practiced; actual MTTR is higher under stress | Sample actual incident MTTR from incident records; use 90th percentile, not mean |
| Error budget burn measured weekly when traffic is bursty | Burst failures exhaust hourly budget; weekly window masks it | Implement multi-window burn rate: 1-hour and 6-hour windows alongside monthly (primitive 08) |
| SLO set to match current reliability | Budget is always full; reliability signal is absent | Set SLO to the level customers need, not the level currently achieved |

### Architecture and Redundancy

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Parallel redundancy assumed to be independent | Common-cause failures (shared power, shared codebase, same AZ) violate independence | Apply beta-factor common-cause model in primitive 10 |
| Switchover reliability ignored in standby architecture | Failover fails; standby provides false confidence | Model coverage c; use imperfect-coverage formula in primitive 07 |
| Adding more replicas without improving coverage | Low-coverage redundancy scheme reduces reliability | Measure c first; fix switchover before adding units |
| Treating a microservices mesh as a simple series chain | Parallel paths and retries are ignored; availability is understated | Draw a reliability block diagram; model actual topology |

### Failure Analysis

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| RPN used as an objective ranking in FMEA | High-RPN items with low severity crowd out catastrophic low-RPN items | Always review S=9/10 items regardless of RPN |
| Fault tree top event defined vaguely | Tree is ambiguous; minimal cut sets are not actionable | Write the top event as a specific, measurable system state with a threshold |
| FMEA or FTA done once, never revisited | Architecture changes invalidate the analysis | Gate analysis reviews to each major architecture change and each significant incident |

### Lifetime and Distribution Fitting

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Weibull fit on fewer than 6 complete failures | β and η confidence intervals are too wide to be useful | Report confidence intervals; collect more data or use Bayesian priors before acting |
| Assuming constant hazard rate (CFR) without testing | Wrong maintenance schedule if system is in DFR or IFR phase | Plot empirical hazard function (primitive 03) before selecting exponential model |
| Ignoring right-censored data in distribution fitting | Survivorship bias; hazard underestimated | Use MLE with censoring; never drop unfailed units |

---

## Decision Checklist

- [ ] **Measured failure data available**: compute MTBF and MTTR → primitive 01.
- [ ] **Need availability percentage**: translate MTBF/MTTR to A → primitive 02.
- [ ] **Topology is series + parallel**: compose A_system from component availabilities → primitive 10.
- [ ] **SLO exists or needed**: derive error budget and burn-rate thresholds → primitive 08.
- [ ] **System target must be distributed to teams/suppliers**: allocate per-subsystem targets → primitive 11.
- [ ] **Pre-launch reliability review required**: run FMEA to enumerate and rank failure modes → primitive 06.
- [ ] **High-severity failure modes identified**: build fault tree for those top events → primitive 05.
- [ ] **Adding redundancy**: compute system reliability gain and verify coverage is sufficient → primitive 07.
- [ ] **Multiple failure time observations available**: fit Weibull for B10 life and phase classification → primitive 09.
- [ ] **Unclear which lifecycle phase the system is in**: plot empirical hazard function → primitive 03.
- [ ] **New deployment or hardware received**: check for infant-mortality phase; plan burn-in → primitive 04.

---

## Sources

Use primary engineering texts and standards as the strongest evidence tier. Practitioner blog posts and vendor SRE guides are useful for operational heuristics but should not be used to claim numeric thresholds transfer across domains.

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly.
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly.
- Weibull, W. (1951). A statistical distribution function of wide applicability. *Journal of Applied Mechanics*, 18(3), 293–297.
- IEEE Std 1413 (2010). *Reliability Prediction and Assessment for Electronic Systems and Equipment*.
- IEC 60812 (2018). *Failure modes and effects analysis (FMEA and FMECA)*.
- IEC 61025 (2006). *Fault tree analysis (FTA)*.
- MIL-HDBK-217F (1991). *Reliability Prediction of Electronic Equipment*. US DoD. (Field data should be validated against observed rates; known to overstate failure rates in modern components.)
