---
name: foundations-reliability-theory
description: Reliability-theory primitives for MTBF/MTTR, availability, hazards, FMEA, redundancy, error budgets, Weibull analysis, and SLOs. Use when modeling failure.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Reliability Theory Foundations


11 reliability theory primitives covering the mathematics of failure, availability, and repair. Each primitive is domain-agnostic: the same MTBF/MTTR arithmetic that governs hardware maintenance governs SLO budget calculation; the same fault tree that maps a safety system maps a payment pipeline's SPOF paths.

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Anti-Patterns](#anti-patterns)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Expert Judgment: When the Math Lies](#expert-judgment-when-the-math-lies)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Navigation](#navigation)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | When to Reach for It |
|---|-----------|---------------------|
| 1 | [MTBF / MTTR](assets/templates/reliability-theory/01-mtbf-mttr.md) | Measuring how often a system fails and how long it takes to recover |
| 2 | [Availability Formulas](assets/templates/reliability-theory/02-availability-formulas.md) | Converting MTBF/MTTR into a percentage; composing series and parallel components |
| 3 | [Hazard Functions](assets/templates/reliability-theory/03-hazard-functions.md) | Classifying current failure rate shape (constant / increasing / decreasing) |
| 4 | [Bathtub Curve](assets/templates/reliability-theory/04-bathtub-curve.md) | Identifying the lifecycle phase (infant mortality / useful life / wear-out) |
| 5 | [Fault Tree Analysis](assets/templates/reliability-theory/05-fault-tree-analysis.md) | Tracing a top event backwards to root causes; finding single points of failure |
| 6 | [FMEA](assets/templates/reliability-theory/06-fmea.md) | Enumerating failure modes bottom-up and ranking by RPN before launch |
| 7 | [Redundancy Math](assets/templates/reliability-theory/07-redundancy-math.md) | Sizing active/standby/k-of-n redundancy; checking coverage sensitivity |
| 8 | [Error Budgets](assets/templates/reliability-theory/08-error-budgets.md) | Deriving SRE error budget from SLO; computing multi-window burn rate |
| 9 | [Weibull Analysis](assets/templates/reliability-theory/09-weibull-analysis.md) | Fitting lifetime data to a distribution; estimating B10 life and phase |
| 10 | [System Reliability](assets/templates/reliability-theory/10-system-reliability.md) | Combining component reliabilities through series/parallel/mixed topologies |
| 11 | [Reliability Allocation](assets/templates/reliability-theory/11-reliability-allocation.md) | Apportioning a system reliability target to subsystems |

---

## When to Apply

**Apply reliability-theory when:**
- SLO design or error-budget math (availability targets, allowed downtime, burn rates)
- Redundancy decisions — single instance vs active-active vs N+1 vs geographic
- FMEA / fault-tree analysis on a system before launch or post-incident
- Hazard-rate questions — "is this an infant-mortality bug, random failure, or wear-out?"
- Composition math — when independent components form a chain or parallel system

**Skip and use simpler alternatives when:**
- Question is about latency/throughput, not availability — use foundations-queueing-theory
- Question is about consistency under partition — use foundations-distributed-systems
- Question is about feedback/anti-windup tuning — use foundations-control-theory
- System has no SLO and no business impact from downtime — over-engineering risk
- One-shot script, dev tooling, or non-production code — reliability math is overhead
- Failure modes are correlated (shared DB, single AZ) — independence assumption breaks composition math; flag the correlation first
- Software-control-loop or autonomous system where unsafe interactions (not just component failures) dominate — augment FTA with STPA (Leveson 2011) rather than extending the fault tree
- Stochastic-per-run AI agent where run-to-run variance is the primary concern — adapt primitives as described in [Domain Applicability Notes](#domain-applicability-notes) rather than using raw MTBF

---

## Primitive Index

Each primitive has a full playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources).

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [MTBF / MTTR](assets/templates/reliability-theory/01-mtbf-mttr.md) | No quantified failure rate or repair time; availability is guesswork |
| 2 | [Availability Formulas](assets/templates/reliability-theory/02-availability-formulas.md) | Availability computed incorrectly (additive instead of multiplicative in series) |
| 3 | [Hazard Functions](assets/templates/reliability-theory/03-hazard-functions.md) | Wrong distribution assumed (CFR when system is IFR or DFR) |
| 4 | [Bathtub Curve](assets/templates/reliability-theory/04-bathtub-curve.md) | Lifecycle phase invisible; burn-in skipped; wear-out surprises operations |
| 5 | [Fault Tree Analysis](assets/templates/reliability-theory/05-fault-tree-analysis.md) | Single points of failure and correlated causes not identified before launch |
| 6 | [FMEA](assets/templates/reliability-theory/06-fmea.md) | Failure modes not enumerated; highest-risk paths not mitigated before launch |
| 7 | [Redundancy Math](assets/templates/reliability-theory/07-redundancy-math.md) | Redundancy added without verifying it actually improves reliability |
| 8 | [Error Budgets](assets/templates/reliability-theory/08-error-budgets.md) | No principled mechanism to balance deployment velocity against stability |
| 9 | [Weibull Analysis](assets/templates/reliability-theory/09-weibull-analysis.md) | MTBF computed without fitting the actual distribution; maintenance timed wrong |
| 10 | [System Reliability](assets/templates/reliability-theory/10-system-reliability.md) | System availability computed from topology without common-cause correction |
| 11 | [Reliability Allocation](assets/templates/reliability-theory/11-reliability-allocation.md) | System target not distributed; teams build to arbitrary individual specs |

---

## Formal Supporting Theory

Load [`references/formal-theory-map.md`](references/formal-theory-map.md) when the work depends on reliability mathematics: survival and hazard functions, repairable vs. non-repairable systems, series/parallel composition, common-cause failure, FTA Boolean gates, FMEA scoring limits, Weibull shape interpretation, availability/SLO arithmetic, or allocation constraints.

### Key Identities Across Primitives

| Identity | Formula | Pitfall |
|----------|---------|---------|
| Availability from MTBF/MTTR | A = MTBF / (MTBF + MTTR) | Use 90th-percentile MTTR from incident records, not runbook estimate |
| Series availability | A_s = ∏ Aᵢ | Never average or sum; must multiply |
| Active-active (2 identical, independent) | A = 1 − (1−A₁)² | Fails when components share a dependency (common-cause) |
| k-of-n reliability | R = Σ C(n,j) Rʲ (1−R)ⁿ⁻ʲ, j=k..n | Assumes independence; check coverage factor c |
| Error budget (monthly) | budget_minutes = (1 − SLO) × 43,800 min | SLO definition drift invalidates budget comparisons |
| Weibull MTTF | MTTF = η · Γ(1 + 1/β) | Requires ≥10 complete failures for defensible β |
| AI agent chain reliability | R = ∏ rᵢ (per-step) | Per-step rᵢ must be measured across ≥10 runs per step |

These identities are expanded with derivations in [`references/formal-theory-map.md`](references/formal-theory-map.md).

## Misuse Boundaries

Load [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before claiming availability, using MTBF as a promise, adding redundancy, accepting an FMEA RPN ranking, fitting Weibull with sparse data, or converting SLOs into release policy. It contains scenarios, anti-patterns, and calculation traps.

---

## Anti-Patterns

| Anti-Pattern | Reliability Diagnosis | Fix |
|-------------|----------------------|-----|
| Arithmetic average of subsystem MTBFs used as system MTBF | Series availability is multiplicative; averaging overstates reliability | Compute A_system = ∏ Aᵢ using primitive 02; never sum or average MTBFs across parallel systems |
| MTTR estimated from happy-path runbook execution time | Tail incidents run longer than rehearsed recovery; actual MTTR is higher | Sample MTTR from real incident records; use 90th percentile not mean; include detection-to-restore, not just restore duration |
| Error budget burn measured weekly when traffic is bursty | A 4-hour burst failure exhausts the hourly budget invisibly inside a weekly window | Implement multi-window burn rate (1-hour and 6-hour) alongside the 30-day window (primitive 08) |
| Weibull fit applied to fewer than 6 complete failure observations | β and η confidence intervals span orders of magnitude; shape classification is noise | Report confidence intervals explicitly; do not act on β classification until ≥10 failures are observed |
| RPN score used as the sole prioritisation signal in FMEA | A Severity=10, Occurrence=1, Detection=10 item scores RPN=100 — low — but is catastrophic if it occurs | Always review all S≥9 items independently of RPN; never allow a low RPN to deprioritise a catastrophic failure mode |
| Redundancy added without modelling switchover reliability | Active/standby failover mechanism fails; redundancy provides no benefit or reduces reliability | Model coverage probability c in the imperfect-coverage formula; measure switchover reliability before sizing more units (primitive 07) |
| Correlated failures in parallel components treated as independent | Common power rail, same AZ, or shared codebase invalidates the independence assumption; parallel formula drastically overstates reliability | Apply beta-factor common-cause correction in primitive 10; audit shared dependencies before claiming availability improvement |
| Phase II (CFR) assumed without testing | Early or late phases have non-constant hazard rates; exponential MTBF formula produces wrong predictions | Plot empirical h(t) from observation data (primitive 03) before choosing a distribution |
| pass@1 used as the sole agent reliability metric | Single-run success conceals consistency variance: perturbations reduced success from 96.9% to 88.1% in one benchmark; capability and reliability rankings diverge at long horizons | Use pass^k across ≥10 runs as the consistency floor; pair with Markov chain step-reliability for sequential tool chains (primitive 10 extension). See [references/ai-agent-reliability.md](references/ai-agent-reliability.md) |
| MTBF applied directly to stochastic-per-run AI agents | Classic MTBF assumes a stationary failure rate; LLM agents degrade non-linearly with task duration (Reliability Decay Curve); single-run availability is not meaningful | Adapt primitive 01 by measuring pass^k and RDC across task-duration buckets; flag duration-dependent degradation explicitly |
| Multi-agent topology treated as a plain series chain | Series math (R = ∏ rᵢ) assumes a step's failure is contained. In uncoordinated multi-agent systems errors propagate *and amplify* across handoffs; MAST attributes ~41.8% of failures to specification/system-design and ~36.9% to inter-agent misalignment — neither is a per-step reliability drop | Use ∏ rᵢ as a best case, not an estimate. Enumerate handoff failure modes (context loss, format mismatch, missing termination) in agent FMEA (primitive 06); a centralised validation bottleneck contains amplification far better than peer-to-peer topology. See [references/ai-agent-reliability.md](references/ai-agent-reliability.md) |
| Agent monitoring assumed to detect agent failure | LLM systems fail "plausible": the model narrates a failed step into fluent prose, so the error never surfaces as an error. ~70% of silent failures in one production runtime were found by human observation despite 4,286 unit tests and 827 governance checks | Detection scores (the D in RPN) must be measured against *silent* failure, not crash failure. Add per-step output validation gates and end-to-end assertions on ground truth, not on the agent's own report of success |
| Safety-I only: treating reliability as absence of failures | FMEA/FTA enumerate deviations from a nominal; they cannot surface emergent failures that arise from normal work coupling in sociotechnical systems | Complement FTA/FMEA with Safety-II perspective (Hollnagel 2014): understand adaptive capacity, not only failure modes. See Conceptual Complements below |

---

## Decision Checklist

- [ ] **No failure rate data yet**: start by computing MTBF and MTTR from incident records → primitive 01.
- [ ] **Need an availability percentage**: translate MTBF/MTTR → primitive 02.
- [ ] **System has multiple components in series or parallel**: compose availability through topology → primitive 10.
- [ ] **SLO exists or is being set**: derive error budget and burn-rate alert thresholds → primitive 08.
- [ ] **System target must be distributed to teams or suppliers**: allocate per-subsystem reliability targets → primitive 11.
- [ ] **Pre-launch reliability review required**: enumerate failure modes with RPN ranking → primitive 06.
- [ ] **High-severity failure modes identified in FMEA**: build fault tree for those top events → primitive 05.
- [ ] **Adding redundancy**: verify coverage is sufficient; check whether redundancy helps or hurts → primitive 07. Then **validate coverage probability with fault injection experiments** before treating the redundancy as live (see primitive 07 Validation section).
- [ ] **Failure time data available**: fit Weibull for B10 life and maintenance scheduling → primitive 09.
- [ ] **Unclear which lifecycle phase the system is in**: classify hazard rate shape → primitive 03.
- [ ] **New deployment or hardware received**: plan burn-in; watch for infant-mortality phase → primitive 04.
- [ ] **AI/LLM agent system**: do not use MTBF directly — measure pass^k (k ≥ 10) for consistency; use Markov chain step-reliability for sequential tool chains (primitive 10 extension); measure RDC across task-duration buckets. See [`references/ai-agent-reliability.md`](references/ai-agent-reliability.md).

---

## Composition Recipes

Full composition guide and domain-scenario stacks live in [`assets/templates/reliability-theory/README.md`](assets/templates/reliability-theory/README.md).

Quick stacks:

**Service availability target** — establish and validate an SLO against real architecture:
Primitive 01 (measure MTBF/MTTR) → Primitive 02 (compute A per component) → Primitive 10 (compose through topology) → Primitive 11 (allocate target to lagging subsystems) → Primitive 08 (set error budget and burn-rate alerts).

**Worked example:** SLO 99.9% monthly = 43.8 min downtime budget. Single instance: MTBF=720 h, MTTR=2 h → A = 720/(720+2) = 99.72% → 121 min/month, blows budget. Add active-active pair (independent failures): A_pair ≈ 1 − (1−0.9972)² = 99.9992% → 0.35 min/month. But shared DB caps at A_DB = 99.95% → real A = min(99.9992%, 99.95%) = 99.95% (common-cause correction, primitive 10). Bathtub note: failure spike in first 30 days post-deploy is infant mortality (DFR phase), not random CFR — use canary or burn-in, not autoscale.

**FMEA before launch** — find and rank failure risks before shipping:
Primitive 06 (FMEA worksheet, RPN ranking) → Primitive 05 (fault tree for top S≥9 items, find SPOFs) → Primitive 07 (redundancy math for identified SPOFs) → Primitive 06 again (re-score residual RPN after mitigations).

**Post-incident reliability update** — update models and improve after an incident:
Primitive 01 (update MTBF/MTTR from incident) → Primitive 03 (re-classify hazard phase) → Primitive 09 (re-fit Weibull if ≥10 failures available) → Primitive 06 (add failure mode to FMEA) → Primitive 11 (re-allocate targets to subsystems that fell below spec).

**AI agent system reliability baseline** — establish a defensible reliability figure for an LLM agent pipeline:
Step 1: Run ≥10 independent episodes per task bucket (short / medium / long) — compute pass^k per bucket; do not use pass@1 alone.
Step 2: Map the agent's tool calls to a series chain → apply Markov step-reliability (primitive 10 extension): R_system = ∏ rᵢ.
Step 3: Run FMEA (primitive 06) with agent-specific failure modes (context overflow, tool hallucination, schema drift, rate-limit cascade) — score all S≥9 items independently of RPN.
Step 4: For highest-severity items (S≥9), build fault trees (primitive 05) and augment with STPA where control-loop hazards are present.
Step 5: Set error budget (primitive 08) extending to a correctness budget — fraction of responses meeting a quality bar — alongside availability.

**Worked example (agent pipeline):** A 5-step research agent with per-step reliabilities [0.98, 0.95, 0.97, 0.92, 0.99] → R_system = 0.98 × 0.95 × 0.97 × 0.92 × 0.99 ≈ 0.823. Single-run pass@1 on a short task was 0.94 — the chain composition reveals a ≈17.7% expected failure rate on full-length runs, far worse than the short-task figure suggests. Bottleneck is step 4 (r=0.92); improving it to 0.97 raises R_system to ≈0.867. (Corrected 2026-07-11: prior figures of 0.824/0.862 were rounding errors; exact products are 0.8225 and 0.8672.)

---

## Domain Applicability Notes

Different system types call for different subsets of the 11 primitives. The core arithmetic is domain-agnostic; the calibration data and vocabulary shift.

**Hardware / IEC context** (electronic equipment, safety instrumented systems, aerospace): All 11 primitives apply directly. MIL-HDBK-217, IEC 61508, ISO 26262, and DO-178C provide failure-rate data. Bathtub curve and Weibull analysis (primitives 04, 09) are first-class tools. FMEA governed by IEC 60812. FTA by IEC 61025.

**Software / SRE context** (cloud services, microservices, distributed systems): Primitives 01, 02, 08, 10 are the workhorses. The bathtub curve maps to the deploy lifecycle: infant-mortality phase corresponds to the first 24–72 hours post-deploy; random-failure phase is steady-state operation; wear-out corresponds to technical debt accumulation and dependency rot. SRGM critique applies (Xie 1991 assumes monotone DFR; breaks when code changes during the observation window).

**AI / LLM agent systems**: Classic MTBF is not directly applicable to stochastic-per-run agents. Three adaptations are required:
- Replace single-run availability with **pass^k** (all k runs succeed; k ≥ 10 minimum) as the consistency baseline.
- Use **Reliability Decay Curve (RDC)** and **Variance Amplification Factor (VAF)** to measure duration-dependent degradation rather than a time-stationary failure rate.
- Model sequential tool-call chains with **Markov chain step-reliability** (primitive 10 extension): R_system = ∏ rᵢ where rᵢ is the step-level reliability of each tool call.
- Treat R = ∏ rᵢ as an **upper bound** for multi-agent topologies, not an estimate — inter-agent handoffs add failure modes that no per-step reliability captures (see Anti-Patterns).
Full vocabulary and worked examples: [`references/ai-agent-reliability.md`](references/ai-agent-reliability.md).

**Where the reliability actually comes from.** A 2026 cross-benchmark decomposition of a production enterprise agent (Dastidar 2026, arXiv:2607.17044) found the uplift over the frontier base model came mostly from scaffolding, routing, and specialist-model selection — the verification loop contributed only ≈+1.5 points in isolation, with an instrumented catch rate of ≈0.20 and fix rate of 0.75. Two consequences for reliability allocation (primitive 11) on agent systems: a verifier is a low-coverage detection element, so scoring it as high Detection in an agent FMEA overstates protection; and reliability budget is better spent on the scaffold that prevents the failure than on the checker that might catch it. Independently, Rabanser et al. (ICML 2026) report that recent capability gains produced only small reliability improvements across 15 agents — capability and reliability must be budgeted separately.

**Sociotechnical systems** (human-automation coupling, autonomous vehicles, healthcare): Augment FTA/FMEA with STAMP/STPA (see Conceptual Complements below) for control-loop hazards invisible to Boolean gate analysis.

---

## Conceptual Complements

### Safety-II / Resilience Engineering (Hollnagel 2014)

Traditional FMEA and FTA are **Safety-I methods**: they enumerate deviations from a nominal design. Safety-II (Hollnagel, *Safety-I and Safety-II*, Ashgate/CRC, 2014) proposes that reliability emerges from **adaptive capacity** — understanding *what normally goes right*, not only cataloguing failures. The FRAM (Functional Resonance Analysis Method) models how system functions couple and resonate to create both safe and unsafe outcomes.

**When to add Safety-II framing:** any sociotechnical system where human-automation interaction, high variability of normal work, or emergent (non-deviation) failures are the dominant risk mode. FTA/FMEA remain valid; Safety-II is a complement, not a replacement.

**Signal to load this complement:** if post-incident reviews consistently find "everything worked as designed — but the combination produced the failure."

Source: Hollnagel, E. (2014). *Safety-I and Safety-II: The Past and Future of Safety Management*. Ashgate. See also Ham (2020), "Safety-II and Resilience Engineering in a Nutshell," *Safety and Health at Work* 12(1), PMC7940128.

### STAMP / STPA (Leveson 2011)

**STAMP** (System-Theoretic Accident Model and Processes) models accidents as control-loop failures, not component failures. **STPA** (System-Theoretic Process Analysis) derives hazardous control actions from STAMP structure — finding software errors, design errors, unsafe interactions, and human-automation coupling failures that FTA Boolean gates cannot reach.

**When to use STPA instead of (or alongside) FTA:** software-intensive systems, autonomous systems, or any system where unsafe interactions between correctly functioning components are the primary hazard. See the STAMP/STPA callout added to primitive 05.

Source: Leveson, N. G. (2011). *Engineering a Safer World*. MIT Press. Free PDF historically available via MIT (STAMP/STPA Handbook, 2018, also freely available).

---

## Expert Judgment: When the Math Lies

The formulas in this skill are exact. The systems they describe rarely satisfy the formulas' assumptions. A non-expert applies the formula; an expert asks which assumption is about to break.

**Redundancy math routinely overstates delivered reliability — for two structural reasons, not one.**
1. *Correlated failures.* The parallel formula `1-(1-R)^n` requires independence. Shared power, shared AZ, shared base image, shared on-call engineer running the same runbook on both nodes — any of these correlate failures, and the beta-factor correction (primitive 10) is itself a rough patch, not a measurement. Treat any claimed β < 0.02 as unverified until a joint-failure history exists to support it.
2. *The failover mechanism is a new, unmeasured single point of failure.* Standby and active-active architectures both introduce a switchover/detection path — health checks, DNS, consensus, a human paging decision — that has never failed because it has never been exercised under real load. Its coverage probability `c` (primitive 07) is asserted, not measured, until it has been fired in anger. The expert move: assume `c` is materially worse than the vendor spec or the tabletop estimate, size redundancy for the *measured* c from chaos/game-day results, and treat "we added a second region" as a *hypothesis* about reliability, not a delivered improvement, until failover has actually been triggered under production-like conditions.

**The 2025 outages are the correlated-failure argument in field data.** Three published vendor postmortems from late 2025 each defeated redundancy without any component becoming unreliable. AWS us-east-1 (19–20 Oct 2025): a race between two DNS Enactors left an empty DNS record for the DynamoDB regional endpoint — the automation that should have repaired it was the thing that broke it; DynamoDB itself recovered in ~2h52m but dependent services (EC2, Lambda, ECS/EKS) took most of the following day to drain backlogs. Cloudflare (18 Nov 2025): a database permissions change surfaced duplicate rows in a Bot Management feature file, doubling it past a 200-feature preallocation limit and panicking the Rust proxy — 3h38m of major impact, and because ClickHouse nodes picked up the change gradually, the file alternated good/bad every five minutes and initially read as a DDoS. Azure (Oct 2025): an Azure Front Door misconfiguration in the global routing layer.

Three reliability lessons the arithmetic will not give you. (1) **Config and control-plane propagation is a series element with fan-out N** — it sits upstream of every replica, so replication multiplies the blast radius rather than dividing it, and no parallel-path formula in primitive 07 or 10 models it. Enumerate it as a basic event in the fault tree. (2) **A bad signal that propagates fast is worse than a component that dies slowly**; the recovery time was dominated by backlog drain and by diagnosis being actively misled, not by restoring the failed part. Budget MTTR for a dependent-service backlog tail, not for the root fix. (3) **Redundancy is built against a remembered failure mode.** us-east-1 has now failed in three structurally different ways since 2021; teams that engineered around the previous one were still taken out. Ask which failure mode your redundancy encodes, and what a different one would do to it.

**MTBF-vs-percentile thinking.** MTBF is a mean; means are dominated by the bulk of a distribution and blind to the tail. Two systems with identical MTBF can have wildly different p99 MTTR — one recovers in minutes every time, the other recovers in minutes 95% of the time and takes six hours the other 5%. The mean tells you nothing about which one you're operating. Whenever a decision hinges on worst-case exposure (SLA penalties, safety margins, capacity planning for an incident), ask for the distribution or at least the p90/p99, not the mean. This is the same reasoning behind "use 90th-percentile MTTR, not the runbook estimate" (Anti-Patterns table) — generalize it to every reliability figure someone hands you as a single number.

**When reliability modeling is worth it vs. when chaos testing beats analysis.** Modeling (FTA, FMEA, Weibull, allocation) is worth the effort *before* the system exists or before a redundancy investment is committed — it is cheap, it forces explicit assumptions onto paper, and it catches SPOFs that no one would think to fault-inject. Once the system exists, model output is a hypothesis and controlled fault injection (chaos engineering, game days) is the only way to find out whether the assumptions — independence, coverage, MTTR — actually hold in production. Neither replaces the other: modeling without empirical validation produces confident wrong numbers (see the coverage-probability point above); chaos testing without a model wastes effort probing paths a five-minute fault tree would have flagged as low-priority. Sequence: model to decide where to invest, inject faults to confirm the investment worked, and feed the measured results back into the model's next iteration.

**Safety-margin reasoning.** A point-estimate reliability figure (R = 0.999) invites building to exactly that number. Real component reliabilities carry estimation uncertainty — small failure samples, unvalidated coverage factors, unmeasured common-cause correlation — and that uncertainty should widen the target, not narrow it. The size of the safety margin should scale with the *confidence interval* on the inputs, not with the point estimate: a Weibull fit from 6 failures needs a much larger margin than one from 200, even if both report the same β. When someone presents a reliability number without an uncertainty bound, the correct expert response is to ask what data would move that number, not to accept it as precise.

**The bathtub curve's contested applicability to software.** The classic bathtub curve was derived for physical hardware wear mechanisms (fatigue, corrosion, dielectric breakdown) that have no direct software analogue. The "software bathtub" mapping used in primitive 04 (deploy-time infant mortality, steady-state operation, tech-debt wear-out) is a useful metaphor for operational intuition, not a validated physical model — software failure rates are driven by code change velocity and dependency drift, not by elapsed wall-clock time, so the same service can re-enter "Phase I" behavior on every deploy regardless of how long it has run. Treat the software-bathtub framing as a communication device for stakeholders, and treat SRGM outputs (Xie 1991) as directional, per the Fact-Checking note below — not as a hazard-rate model with the same evidentiary weight as the hardware original.

---

## Workflow

1. Identify the reliability problem type: measurement, availability calculation, lifecycle classification, pre-launch analysis, or redundancy sizing.
2. Use the [Decision Checklist](#decision-checklist) to select the right primitive(s).
3. Open the per-primitive playbook in [`assets/templates/reliability-theory/`](assets/templates/reliability-theory/) for the full definition, formula, failure modes, and worked example.
4. For multi-primitive problems, use the [Composition Recipes](#composition-recipes) or the full [`assets/templates/reliability-theory/README.md`](assets/templates/reliability-theory/README.md).
5. Check [Anti-Patterns](#anti-patterns) before finalising calculations — most reliability mistakes are arithmetic errors (averaging instead of multiplying) or wrong distribution assumptions.

---

## ASCII Flow

```text
Failure, repair, or availability problem
  -> Define system boundary, top event, components, and SLO
  -> Classify system type:
     +-- Hardware/IEC    -> all 11 primitives available; use MIL-HDBK-217 / IEC data
     +-- Software/SRE   -> focus on 01, 02, 08, 10; SRGM caveat applies
     +-- AI/LLM agent   -> adapt 01→pass^k; use Markov step-reliability for chains;
                           measure RDC per task-duration bucket; agent FMEA (06)
     +-- Sociotechnical -> augment FTA (05) with STPA; add Safety-II framing
  -> Classify task: measure, calculate availability, analyze failure, size redundancy, allocate target
  -> Select primitive and gather failure/repair data
  -> Check independence, common-cause, and distribution assumptions
     +-- assumptions invalid -> model correlation or report uncertainty
     +-- assumptions valid -> compute reliability result
  -> Return risk, mitigation, SLO impact, and monitoring evidence
```

---

## Navigation

- Per-primitive playbooks: [`assets/templates/reliability-theory/`](assets/templates/reliability-theory/) (one file per primitive)
- Composition guide and domain-scenario stacks: [`assets/templates/reliability-theory/README.md`](assets/templates/reliability-theory/README.md)
- Domain-agnostic primitives overview with full anti-patterns and decision checklist: [`references/primitives-overview.md`](references/primitives-overview.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- AI/agent reliability extension (pass^k, RDC, Markov step-reliability, agent FMEA): [`references/ai-agent-reliability.md`](references/ai-agent-reliability.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

_Consumer skills will add applied recipe files (`references/reliability-theory-applied.md`) to their own directories. No cross-links are maintained in this file._

---

## Fact-Checking

- Numeric thresholds (beta-factor values, typical β ranges, MIL-HDBK-217 failure rates) are domain- and component-specific. Validate against your own failure history before using published tables.
- MIL-HDBK-217 is known to overstate failure rates for modern COTS and semiconductor components. Treat it as a conservative upper bound, not a field prediction.
- Weibull shape parameters from small samples (< 10 failures) have wide confidence intervals. Report uncertainty bounds; do not classify DFR/CFR/IFR from three data points.
- SLO arithmetic (error budgets, burn rates) assumes the good/bad event definition is stable. Changes to how you measure errors invalidate historical burn-rate comparisons.
- SRGMs (Jelinski-Moranda, Goel-Okumoto, Musa-Okumoto) assume the software failure rate monotonically decreases as bugs are fixed — a DFR analogue for software (Xie 1991). This assumption breaks when code is modified during the observation window (non-homogeneous process) or when AI-generated code introduces correlated fault clusters. ML-augmented SRGMs improve fit on complex datasets but introduce long-term prediction instability. Treat SRGM outputs as directional, not precise, unless field-calibrated.
- For AI agent systems: pass@1 from a small sample (< 20 runs) has wide confidence intervals. Wu et al. (2026) FAQ framework (arXiv:2601.20251, already in sources.json) delivers up to 5× effective sample size gains for LLM evaluation using adaptive sampling — use it to reduce required episode counts before quoting a reliability figure.
- Vendor postmortems (AWS 19–20 Oct 2025, Cloudflare 18 Nov 2025) are self-published by the party at fault and are scoped to a mechanism, not to a full sociotechnical account. The technical timelines are reliable and are what this skill cites; downstream damage estimates circulating in trade press are not from the vendors and should not be quoted as vendor figures.
- No standardised quantitative metric set for chaos engineering exists — Owotogbe et al. (2025, ACM CSUR) identify the absence of agreed MTTR/MTTD measurement as an open research gap. Chaos results validate assumptions (coverage, independence, MTTR); they do not yield a comparable reliability score across systems. SLO/error-budget gating of experiments (do not inject while the budget is already burning) is established practice; SLOs for agent autonomy and error budgets for agent behaviour are not yet settled practice as of August 2026.
- Multi-agent error-amplification figures (e.g. claims that uncoordinated topologies amplify errors an order of magnitude more than centralised ones) circulate widely but trace to secondary write-ups, not to MAST itself. MAST's own defensible numbers are the 14 failure modes, 3 categories, category shares (~41.8% / ~36.9%), 1,600+ traces, and κ = 0.88. Cite those; treat amplification multipliers as unverified.
- Sources: Lewis (1995) *Introduction to Reliability Engineering*; O'Connor & Kleyner (2012) *Practical Reliability Engineering*; Birolini (2017) *Reliability Engineering: Theory and Practice*; Beyer et al. (2016) *Site Reliability Engineering*; Beyer et al. (2018) *The Site Reliability Workbook*; Weibull (1951); IEEE Std 1413 (2010); IEC 60812 (2018); IEC 61025 (2006); NIST reliability handbook; NRC Fault Tree Handbook; Leveson (2011) *Engineering a Safer World*; Hollnagel (2014) *Safety-I and Safety-II*.
- **2026-07-11 audit corrections** (see `data/sources.json` for full detail): (1) per-primitive book-chapter citations for Lewis (1995), O'Connor & Kleyner (2012), and Birolini (2017) were removed from every primitive file — they could not be verified against the books' actual tables of contents, and Birolini's repeated "Chapter 2" across seven unrelated primitives was an outright fabrication signal; cite these three books at the title level, not the chapter level, until someone verifies chapter numbers against a physical copy. (2) The Site Reliability Workbook's multi-window-burn-rate citation was corrected from Chapter 2 to Chapter 5 ("Alerting on SLOs") after verification against the published table of contents. (3) The source previously filed as "Bourne2021" (id renamed `Modarres2017`) claimed a nonexistent "4th edition, 2021" — its ISBN resolves to the 3rd edition (2017); no 4th edition of this Modarres/Kaminskiy/Krivtsov title was found to exist. (4) The FMEA primitive's DOI for El Hassani et al. (2025) was corrected from `10.1017/dsj.2025.007` to the real DOI `10.1017/dsj.2025.7`. (5) Worked-example arithmetic errors were corrected in primitive 07 (imperfect-coverage redundancy example understated the result by ~2 orders of magnitude), primitive 09 (Weibull B10-life example mis-derived the shape-parameter term, understating B10 life by ~25%), primitive 05 (FTA example mislabeled a 200× risk ratio as "100×"), and the SKILL.md agent-pipeline composition example (rounding errors in the product of five terms). Re-derive any worked example before citing its numbers in a downstream document.
- **2026-08-14 review**: no prior claim was found to be wrong. Added, all verified against primary sources: the AWS and Cloudflare official postmortems (both fetched from vendor domains); MAST (arXiv:2503.13657, Cemri et al.) for multi-agent failure structure; arXiv:2606.14589 (Wu) for silent/"fail-plausible" failure in a production agent runtime; arXiv:2604.11978 (Wang et al., HORIZON) for long-horizon breakdown; arXiv:2607.17044 (Dastidar) for the verifier catch/fix decomposition. The Rabanser et al. HAL dashboard was re-fetched and is live (15 agents, 2 benchmarks, 12 metrics), now reporting frontier-model coverage and a corrected outcome-consistency formula — the paper's headline finding is unchanged and strengthened: capability gains have produced only small reliability gains.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
