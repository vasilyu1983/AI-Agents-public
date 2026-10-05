---
name: foundations-reliability-theory
description: Computes availability for redundant and series designs, failover, SPOFs, fault trees, FMEA, Weibull, and error budgets. Use when asking what uptime a design gives.
compatibility: Portable core only.
version: "1.3"
last_validated: 2026-08-14
---

# Reliability Theory Foundations


11 reliability theory primitives covering the mathematics of failure, availability, and repair.

## Contents

- [Quick Reference](#quick-reference)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Anti-Patterns](#anti-patterns)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Expert Judgment: When the Math Lies](#expert-judgment-when-the-math-lies)
- [Workflow](#workflow)
- [Navigation](#navigation)
- [Related Skills](#related-skills)
- [Domain Verification Notes](#domain-verification-notes)

---

## Quick Reference

| # | Primitive | When to Reach for It | Failure Mode It Prevents |
|---|-----------|---------------------|--------------------------|
| 1 | [MTBF / MTTR](assets/templates/reliability-theory/01-mtbf-mttr.md) | Measuring how often a system fails and how long recovery takes | Availability is guesswork |
| 2 | [Availability Formulas](assets/templates/reliability-theory/02-availability-formulas.md) | Converting MTBF/MTTR to a percentage; series and parallel composition | Adding instead of multiplying in series |
| 3 | [Hazard Functions](assets/templates/reliability-theory/03-hazard-functions.md) | Classifying the failure-rate shape (constant / increasing / decreasing) | CFR assumed when the system is IFR or DFR |
| 4 | [Bathtub Curve](assets/templates/reliability-theory/04-bathtub-curve.md) | Identifying lifecycle phase (infant mortality / useful life / wear-out) | Burn-in skipped; wear-out surprises operations |
| 5 | [Fault Tree Analysis](assets/templates/reliability-theory/05-fault-tree-analysis.md) | Tracing a top event back to root causes; finding single points of failure | SPOFs and correlated causes found after launch |
| 6 | [FMEA](assets/templates/reliability-theory/06-fmea.md) | Bottom-up failure-mode enumeration; severity/obligations-first triage | Highest-risk paths unmitigated at launch |
| 7 | [Redundancy Math](assets/templates/reliability-theory/07-redundancy-math.md) | Sizing active/standby/k-of-n redundancy; coverage sensitivity | Redundancy that does not improve reliability |
| 8 | [Error Budgets](assets/templates/reliability-theory/08-error-budgets.md) | Error budget from SLO; Workbook burn-rate table; request- vs time-based SLIs, low-traffic bounds, latency non-composability | No principled velocity vs stability trade |
| 9 | [Weibull Analysis](assets/templates/reliability-theory/09-weibull-analysis.md) | Fitting lifetime data; B10 life and phase | Maintenance timed from an unfitted MTBF |
| 10 | [System Reliability](assets/templates/reliability-theory/10-system-reliability.md) | Combining reliabilities through series/parallel/mixed topologies | No common-cause correction |
| 11 | [Reliability Allocation](assets/templates/reliability-theory/11-reliability-allocation.md) | Apportioning a system target to subsystems | Teams build to arbitrary individual specs |

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

## Formal Supporting Theory

Load [references/formal-theory-map.md](references/formal-theory-map.md) when the work depends on reliability mathematics: survival and hazard functions, repairable vs. non-repairable systems, series/parallel composition, common-cause failure, FTA Boolean gates, FMEA scoring limits, Weibull shape interpretation, availability/SLO arithmetic, or allocation constraints.

### Key Identities Across Primitives

| Identity | Formula | Pitfall |
|----------|---------|---------|
| Availability from MTBF/MTTR | A = MTBF / (MTBF + MTTR) | Use mean observed downtime, including detection and recovery; report p90/p99 separately |
| Series availability | A_s = ∏ Aᵢ | Never average or sum; must multiply |
| Active-active (2 identical, independent) | A = 1 − (1−A₁)² | Fails when components share a dependency (common-cause) |
| k-of-n reliability | R = Σ C(n,j) Rʲ (1−R)ⁿ⁻ʲ, j=k..n | Assumes independence; check coverage factor c |
| Error budget | budget_minutes = (1 − SLO) × window_minutes (28 d = 40,320; 30 d = 43,200; average month = 43,800) | State the window; SLO definition drift invalidates budget comparisons |
| Weibull MTTF | MTTF = η · Γ(1 + 1/β) | Report censoring and uncertainty; no universal sample count guarantees defensible shape |
| AI agent chain reliability | R = ∏ P(success_i | prior successes) | Use conditional step-success probabilities, or justify independence of marginal estimates; choose sample size by precision |

These identities are expanded with derivations in [references/formal-theory-map.md](references/formal-theory-map.md).

## Misuse Boundaries

Load [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) before claiming availability, using MTBF as a promise, adding redundancy, accepting an FMEA RPN ranking, fitting Weibull with sparse data, or converting SLOs into release policy. It contains scenarios, anti-patterns, and calculation traps.

---

## Anti-Patterns

| Anti-Pattern | Reliability Diagnosis | Fix |
|-------------|----------------------|-----|
| Arithmetic average of subsystem MTBFs used as system MTBF | Series availability is multiplicative; averaging overstates reliability | Compute A_system = ∏ Aᵢ using primitive 02; never sum or average MTBFs across parallel systems |
| MTTR estimated from happy-path runbook execution time | Tail incidents run longer than rehearsed recovery; actual MTTR is higher | Sample MTTR from real incident records; use the arithmetic mean for availability and report tail percentiles separately; include detection-to-restore, not just restore duration |
| Error budget burn measured weekly when traffic is bursty | A 4-hour burst failure exhausts the hourly budget invisibly inside a weekly window | Use SRE Workbook Table 5-8: page at 14.4× over 1 h and 5 min, page at 6× over 6 h and 30 min, ticket at 1× over 3 d and 6 h (primitive 08) |
| Weibull shape acted on from a handful of failures | β and η confidence intervals span orders of magnitude; shape classification is noise | No universal failure count suffices: decide from the CI width on β and on the Bx quantile you will act on |
| RPN score used as the sole prioritisation signal in FMEA | A Severity=10, Occurrence=1, Detection=10 item scores RPN=100 — low — but is catastrophic if it occurs | Always review all S≥9 items independently of RPN; never allow a low RPN to deprioritise a catastrophic failure mode |
| Redundancy added without modelling switchover reliability | Active/standby failover mechanism fails; redundancy provides no benefit or reduces reliability | Model coverage probability c in the imperfect-coverage formula; measure switchover reliability before sizing more units (primitive 07) |
| Correlated failures in parallel components treated as independent | Common power rail, same AZ, or shared codebase invalidates the independence assumption; parallel formula drastically overstates reliability | Apply beta-factor common-cause correction in primitive 10; audit shared dependencies before claiming availability improvement |
| Phase II (CFR) assumed without testing | Early or late phases have non-constant hazard rates; exponential MTBF formula produces wrong predictions | Plot empirical h(t) from observation data (primitive 03) before choosing a distribution |
| pass@1 used as the sole agent reliability metric | Single-run success conceals consistency variance: perturbations reduced success from 96.9% to 88.1% in one benchmark (Gupta 2026, ReliabilityBench; see [references/ai-agent-reliability.md](references/ai-agent-reliability.md)); capability and reliability rankings diverge at long horizons | Use all-k consistency at a declared k alongside per-run estimates with confidence intervals as the consistency floor; pair with Markov chain step-reliability for sequential tool chains (primitive 10 extension). See [references/ai-agent-reliability.md](references/ai-agent-reliability.md) |
| MTBF applied directly to stochastic-per-run AI agents | Pooled mean uptime can hide differences between task populations; task success and service availability measure different events. Measure task-duration effects rather than assuming a constant per-step success rate | Adapt primitive 01 by measuring pass^k and RDC across task-duration buckets; flag duration-dependent degradation explicitly |
| Multi-agent topology treated as a plain series chain | Marginal series products require independence; conditional chain products explicitly model prior successful context. In uncoordinated multi-agent systems errors propagate *and amplify* across handoffs; as reported in [Cemri et al., MAST v3 Figure 4, p.8](https://arxiv.org/pdf/2503.13657v3), system-design and inter-agent labels account for 41.8% and 36.9% of illustrated failures in 210 traces; these are subset-specific failure-count shares — neither is a per-step reliability drop | Marginal ∏ rᵢ has no universal best-case interpretation under dependence. Use conditional chain probabilities or measured end-to-end outcomes. Enumerate handoff failure modes (context loss, format mismatch, missing termination) in agent FMEA (primitive 06); validate handoff controls and topology on matched tasks instead of inferring a universal coordinator advantage from failure-category shares. See [references/ai-agent-reliability.md](references/ai-agent-reliability.md) |
| Agent monitoring assumed to detect agent failure | LLM systems fail "plausible": the model narrates a failed step into fluent prose, so the error never surfaces as an error. ~70% of silent failures in one production runtime were found by human observation despite 4,286 unit tests and 827 governance checks (Wu 2026, arXiv:2606.14589; see [references/ai-agent-reliability.md](references/ai-agent-reliability.md)) | Detection scores (the D in RPN) must be measured against *silent* failure, not crash failure. Add per-step output validation gates and end-to-end assertions on ground truth, not on the agent's own report of success |
| Safety-I only: treating reliability as absence of failures | FMEA/FTA enumerate deviations from a nominal; they cannot surface emergent failures that arise from normal work coupling in sociotechnical systems | Hand off to [foundations-safety-engineering](../foundations-safety-engineering/SKILL.md) (Safety-II, STPA) |

---

## Decision Checklist

- [ ] **No failure rate data yet**: start by computing MTBF and MTTR from incident records → primitive 01.
- [ ] **Need an availability percentage**: translate MTBF/MTTR → primitive 02.
- [ ] **System has multiple components in series or parallel**: compose availability through topology → primitive 10.
- [ ] **SLO exists or is being set**: derive error budget and burn-rate alert thresholds → primitive 08.
- [ ] **System target must be distributed to teams or suppliers**: allocate per-subsystem reliability targets → primitive 11.
- [ ] **Pre-launch reliability review required**: enumerate failure modes with severity/obligations-first triage and secondary RPN screening → primitive 06.
- [ ] **High-severity failure modes identified in FMEA**: build fault tree for those top events → primitive 05.
- [ ] **Adding redundancy**: verify coverage is sufficient; check whether redundancy helps or hurts → primitive 07. Then **validate coverage probability with fault injection experiments** before treating the redundancy as live (see primitive 07 Validation section).
- [ ] **Failure time data available**: fit Weibull for B10 life and maintenance scheduling → primitive 09.
- [ ] **Unclear which lifecycle phase the system is in**: classify hazard rate shape → primitive 03.
- [ ] **New deployment or hardware received**: plan burn-in; watch for infant-mortality phase → primitive 04.
- [ ] **AI/LLM agent system**: do not use MTBF directly — measure per-run success with uncertainty and all-k consistency at a chosen k for consistency; use Markov chain step-reliability for sequential tool chains (primitive 10 extension); measure RDC across task-duration buckets. See [references/ai-agent-reliability.md](references/ai-agent-reliability.md).

---

## Composition Recipes

Full composition guide and domain-scenario stacks live in [assets/templates/reliability-theory/README.md](assets/templates/reliability-theory/README.md).

Quick stacks:

**Service availability target** — establish and validate an SLO against real architecture:
Primitive 01 (measure MTBF/MTTR) → Primitive 02 (compute A per component) → Primitive 10 (compose through topology) → Primitive 11 (allocate target to lagging subsystems) → Primitive 08 (set error budget and burn-rate alerts).

**Worked example:** SLO 99.9% monthly = 43.8 min downtime budget. Single instance: MTBF=720 h, MTTR=2 h → A = 720/(720+2) = 99.72% → about 121 min/month. An independent active-active pair gives A_pair ≈ 99.9992%. If every request also depends on a DB with A_DB = 99.95%, and pair and DB failures are independent, series availability is A_pair × A_DB ≈ 99.9492%; `min(A_pair, A_DB)` is only an upper bound. If failures are correlated, neither product nor parallel formulas apply without a common-cause model. State the service event, observation window, and dependence assumptions before converting this estimate into an SLO claim.

**FMEA before launch** — find and rank failure risks before shipping:
Primitive 06 (FMEA worksheet, severity/obligations-first triage) → Primitive 05 (fault tree for top S≥9 items, find SPOFs) → Primitive 07 (redundancy math for identified SPOFs) → Primitive 06 again (validate each changed S/O/D factor before accepting residual scores).

**Post-incident reliability update** — update models and improve after an incident:
Primitive 01 (update MTBF/MTTR from incident) → Primitive 03 (re-classify hazard phase) → Primitive 09 (re-fit Weibull when the new failures narrow the β CI enough to change a decision) → Primitive 06 (add failure mode to FMEA) → Primitive 11 (re-allocate targets to subsystems that fell below spec).

**AI agent system reliability baseline** — establish a defensible reliability figure for an LLM agent pipeline:
Step 1: Choose independent episodes per task bucket (short/medium/long) from desired confidence and precision; estimate per-run success and repeated-group all-k consistency at a chosen k.
Step 2: Map the agent's tool calls to a series chain → apply Markov step-reliability (primitive 10 extension): R_system = ∏ P(step i succeeds | previous steps succeed); marginal products require independence.
Step 3: Run FMEA (primitive 06) with agent-specific failure modes (context overflow, tool hallucination, schema drift, rate-limit cascade) — score all S≥9 items independently of RPN.
Step 4: For highest-severity items (S≥9), build fault trees (primitive 05) and augment with STPA where control-loop hazards are present.
Step 5: Set error budget (primitive 08) extending to a correctness budget — fraction of responses meeting a quality bar — alongside availability.

**Worked example (agent pipeline):** A 5-step research agent with per-step reliabilities [0.98, 0.95, 0.97, 0.92, 0.99] → R_system = 0.98 × 0.95 × 0.97 × 0.92 × 0.99 ≈ 0.823. Single-run pass@1 on a short task was 0.94 — the chain composition reveals a ≈17.7% expected failure rate on full-length runs, far worse than the short-task figure suggests. Bottleneck is step 4 (r=0.92); improving it to 0.97 raises R_system to ≈0.867.

---

## Domain Applicability Notes

Different system types call for different subsets of the 11 primitives. The core arithmetic is domain-agnostic; the calibration data and vocabulary shift.

**Hardware / IEC context** (electronic equipment, safety instrumented systems, aerospace): All 11 primitives apply directly. Use component field data or a calibrated prediction model such as MIL-HDBK-217 for failure rates. IEC 61508 and ISO 26262 frame functional-safety requirements; DO-178C addresses software assurance objectives, not a table of component failure rates ([FAA AC 20-115D, §6](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-115D.pdf)). Bathtub curve and Weibull analysis (primitives 04, 09) are first-class tools. FMEA governed by IEC 60812. FTA by IEC 61025.

**Software / SRE context** (cloud services, microservices, distributed systems): Primitives 01, 02, 08, 10 are the workhorses. The bathtub curve maps to the deploy lifecycle: infant-mortality phase corresponds to the first hours to days after a deploy (measure the window locally; no general figure is sourced here); random-failure phase is steady-state operation; wear-out corresponds to technical debt accumulation and dependency rot. SRGM critique applies (Xie 1991 assumes monotone DFR; breaks when code changes during the observation window).

**AI / LLM agent systems**: Task-level correctness needs per-run success and consistency measures alongside service-level MTBF and availability. Use these adaptations:
- Measure per-run success and **pass^k** (all k runs succeed; choose k from the operational consistency requirement and sample enough independent groups for uncertainty) as the consistency baseline.
- Use **Reliability Decay Curve (RDC)** and **Variance Amplification Factor (VAF)** to measure duration-dependent degradation rather than a time-stationary failure rate.
- Use the exact conditional chain rule: R_system = ∏ P(success_i | all prior steps successful), with each success including semantic and handoff correctness. A fitted Markov state model is optional and needs validation.
- Marginal step-success products require justified independence and are neither universal upper nor lower bounds. If two success indicators are identical with marginal .9, joint success is .9, not .81; enumerate handoff failure modes explicitly.
Full vocabulary and worked examples: [references/ai-agent-reliability.md](references/ai-agent-reliability.md).

**Where the reliability actually comes from.** A 2026 cross-benchmark decomposition of a production enterprise agent (Dastidar 2026, arXiv:2607.17044) found the uplift over the frontier base model came mostly from scaffolding, routing, and specialist-model selection — the isolated SpreadsheetBench loop contributed +1.5 percentage points; its Table 4 measured catch rate 8/40 = 0.20 and fix rate 6/8 = 0.75 ([§6.2 and Table 5](https://arxiv.org/html/2607.17044v1)). For reliability allocation (primitive 11), compare prevention and verification on matched tasks; these measurements do not establish another verifier’s coverage. In the primitive 06 scale, a low Detection score means easy detection, so awarding low D without measured coverage overstates protection. The GAIA decomposition uses estimated structure tiers and does not isolate the loop causally. Independently, Rabanser et al. (ICML 2026) report that recent capability gains produced only small reliability improvements across 15 agents — capability and reliability must be budgeted separately.

**Sociotechnical systems** (human-automation coupling, autonomous vehicles, healthcare): Augment FTA/FMEA with STAMP/STPA for control-loop hazards invisible to Boolean gate analysis; see [foundations-safety-engineering](../foundations-safety-engineering/SKILL.md).

## Conceptual Complements

Safety-II/FRAM (Hollnagel 2014) and STAMP/STPA (Leveson 2011), for emergent failures where every component "worked as designed", live in [foundations-safety-engineering](../foundations-safety-engineering/SKILL.md).

---

## Expert Judgment: When the Math Lies

**Redundancy math routinely overstates delivered reliability — for two structural reasons, not one.**
1. *Correlated failures.* The parallel formula `1-(1-R)^n` requires independence. Shared power, shared AZ, shared base image, shared on-call engineer running the same runbook on both nodes — any of these correlate failures, and the beta-factor correction (primitive 10) is itself a rough patch, not a measurement. Treat any claimed small β as unverified until a joint-failure history exists to support it.
2. *The failover mechanism is a new, unmeasured single point of failure.* Standby and active-active architectures both introduce a switchover/detection path — health checks, DNS, consensus, a human paging decision — that has never failed because it has never been exercised under real load. Its coverage probability `c` (primitive 07) is asserted, not measured, until it has been fired in anger. The expert move: assume `c` is materially worse than the vendor spec or the tabletop estimate, size redundancy for the *measured* c from chaos/game-day results, and treat "we added a second region" as a *hypothesis* about reliability, not a delivered improvement, until failover has actually been triggered under production-like conditions.

**Gray and fail-slow failures make drill-measured coverage optimistic.** Gray failure is defined by *differential observability*: "the system's failure detectors may not notice problems even when applications are afflicted by them" (Huang et al., HotOS 2017). Fail-slow hardware (degraded, not dead) appeared across disk, SSD, CPU, memory and network in 101 incident reports from 12 institutions (Gunawi et al., FAST 2018). A coverage `c` measured on clean-kill drills does not cover these classes: add drills that inject latency, partial errors and health-check-passing faults, and detect from the client's view of the SLI, not only from health checks.

**The 2025 outages are the correlated-failure argument in field data.** Three published vendor postmortems from late 2025 each defeated redundancy without any component becoming unreliable. AWS us-east-1 (19–20 Oct 2025): a race between two DNS Enactors left an empty DNS record for the DynamoDB regional endpoint — the automation that should have repaired it was the thing that broke it; DynamoDB itself recovered in ~2h52m but dependent services (EC2, Lambda, ECS/EKS) took most of the following day to drain backlogs. Cloudflare (18 Nov 2025): a database permissions change surfaced duplicate rows in a Bot Management feature file, doubling it past a 200-feature preallocation limit and panicking the Rust proxy — 3h38m of major impact, and because ClickHouse nodes picked up the change gradually, the file alternated good/bad every five minutes and initially read as a DDoS. Azure (Oct 2025): an Azure Front Door misconfiguration in the global routing layer.

Three reliability lessons the arithmetic will not give you. (1) **Config and control-plane propagation is a series element with fan-out N** — it sits upstream of every replica, so replication multiplies the blast radius rather than dividing it, and no parallel-path formula in primitive 07 or 10 models it. Enumerate it as a basic event in the fault tree. (2) **A bad signal that propagates fast is worse than a component that dies slowly**; the recovery time was dominated by backlog drain and by diagnosis being actively misled, not by restoring the failed part. Budget MTTR for a dependent-service backlog tail, not for the root fix. (3) **Redundancy is built against a remembered failure mode.** us-east-1's published postmortems show structurally different failure modes; teams that engineered around the previous one were still taken out. Ask which failure mode your redundancy encodes, and what a different one would do to it.

**Mean vs tail repair time.** Mean observed downtime belongs in mean availability arithmetic; report p90/p99 separately for recovery-risk decisions. Equal means can hide different tail exposure, and a percentile must not be substituted into the mean identity. Include occurrence-to-restoration boundaries and disclose detection delays. Sparse observations require uncertainty rather than a universal episode count.

**When reliability modeling is worth it vs. when chaos testing beats analysis.** Modeling (FTA, FMEA, Weibull, allocation) is worth the effort *before* the system exists or before a redundancy investment is committed — it is cheap, it forces explicit assumptions onto paper, and it catches SPOFs that no one would think to fault-inject. Once the system exists, model output is a hypothesis and controlled fault injection (chaos engineering, game days) is the only way to find out whether the assumptions — independence, coverage, MTTR — actually hold in production. Neither replaces the other: modeling without empirical validation produces confident wrong numbers (see the coverage-probability point above); chaos testing without a model wastes effort probing paths a five-minute fault tree would have flagged as low-priority. Sequence: model to decide where to invest, inject faults to confirm the investment worked, and feed the measured results back into the model's next iteration.

**Safety-margin reasoning.** A point-estimate reliability figure (R = 0.999) invites building to exactly that number. Real component reliabilities carry estimation uncertainty — small failure samples, unvalidated coverage factors, unmeasured common-cause correlation — and that uncertainty should widen the target, not narrow it. The size of the safety margin should scale with the *confidence interval* on the inputs, not with the point estimate: a Weibull fit from 6 failures needs a much larger margin than one from 200, even if both report the same β. When someone presents a reliability number without an uncertainty bound, the correct expert response is to ask what data would move that number, not to accept it as precise.

**The bathtub curve's contested applicability to software.** The classic bathtub curve was derived for physical hardware wear mechanisms (fatigue, corrosion, dielectric breakdown) that have no direct software analogue. The "software bathtub" mapping used in primitive 04 (deploy-time infant mortality, steady-state operation, tech-debt wear-out) is a useful metaphor for operational intuition, not a validated physical model — software failure rates are driven by code change velocity and dependency drift, not by elapsed wall-clock time, so the same service can re-enter "Phase I" behavior on every deploy regardless of how long it has run. Treat the software-bathtub framing as a communication device for stakeholders, and treat SRGM outputs (Xie 1991) as directional, per the Domain Verification Notes below — not as a hazard-rate model with the same evidentiary weight as the hardware original.

## Workflow

Classify the problem (measurement, availability, lifecycle, pre-launch analysis, redundancy sizing) → pick primitives from the [Decision Checklist](#decision-checklist) → open the playbook in [assets/templates/reliability-theory/](assets/templates/reliability-theory/) → state independence and window assumptions → check [Anti-Patterns](#anti-patterns) before reporting a number.

## Navigation

- Decision and validation worksheet (intake, model boundaries, uncertainty, acceptance examples): [references/decision-and-validation.md](references/decision-and-validation.md). [Regression cases](data/regression-cases.json) are independent expected answers, not executed agent results.
- Per-primitive playbooks: [assets/templates/reliability-theory/](assets/templates/reliability-theory/) (one file per primitive)
- Composition guide and domain-scenario stacks: [assets/templates/reliability-theory/README.md](assets/templates/reliability-theory/README.md)
- Domain-agnostic primitives overview with full anti-patterns and decision checklist: [references/primitives-overview.md](references/primitives-overview.md)
- Formal theory map: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- AI/agent reliability extension (pass^k, RDC, Markov step-reliability, agent FMEA): [references/ai-agent-reliability.md](references/ai-agent-reliability.md)
- Sources: [`data/sources.json`](data/sources.json)

## Related Skills

- [qa-observability](../qa-observability/SKILL.md): SLI/SLO design and burn-rate alert implementation ([slo-design-guide.md](../qa-observability/references/slo-design-guide.md)). This skill owns only the arithmetic.
- [qa-resilience](../qa-resilience/SKILL.md): chaos experiments that measure coverage, retries, cascading and metastable failure.
- [foundations-safety-engineering](../foundations-safety-engineering/SKILL.md): unsafe interactions, STPA, Safety-II, safety cases.
- [foundations-statistical-inference](../foundations-statistical-inference/SKILL.md): confidence intervals and sample sizes behind reliability claims.
- [foundations-queueing-theory](../foundations-queueing-theory/SKILL.md) and [foundations-distributed-systems](../foundations-distributed-systems/SKILL.md): latency and consistency questions this skill does not answer.

---

## Domain Verification Notes

- Numeric thresholds (beta-factor values, typical β ranges, MIL-HDBK-217 failure rates) are domain- and component-specific. Validate against your own failure history before using published tables.
- MIL-HDBK-217 is known to overstate failure rates for modern COTS and semiconductor components. Treat it as a conservative upper bound, not a field prediction.
- Weibull shape parameters from small samples have wide confidence intervals. Report uncertainty bounds; do not classify DFR/CFR/IFR from three data points.
- SLO arithmetic (error budgets, burn rates) assumes the good/bad event definition is stable. Changes to how you measure errors invalidate historical burn-rate comparisons.
- SRGMs (Jelinski-Moranda, Goel-Okumoto, Musa-Okumoto) assume the software failure rate monotonically decreases as bugs are fixed — a DFR analogue for software (Xie 1991). This assumption breaks when code is modified during the observation window (non-homogeneous process) or when AI-generated code introduces correlated fault clusters. ML-augmented SRGMs improve fit on complex datasets but introduce long-term prediction instability. Treat SRGM outputs as directional, not precise, unless field-calibrated.
- For finite benchmark evaluation, [Wu et al. (2026), abstract and §4](https://arxiv.org/html/2601.20251v1) report up to 5× effective sample size: matching uniform-sampling interval width with fewer queries. Use FAQ only when its historical-outcome and finite-population design fits the evaluation; that result is not a 5× interval-width reduction or evidence that sparse operational failure observations need fewer episodes.
- Vendor postmortems (AWS 19–20 Oct 2025, Cloudflare 18 Nov 2025) are self-published by the party at fault and are scoped to a mechanism, not to a full sociotechnical account. The technical timelines are reliable and are what this skill cites; downstream damage estimates circulating in trade press are not from the vendors and should not be quoted as vendor figures.
- No standardised quantitative metric set for chaos engineering exists — Owotogbe et al. (2025, ACM CSUR) identify the absence of agreed MTTR/MTTD measurement as an open research gap. Chaos results validate assumptions (coverage, independence, MTTR); they do not yield a comparable reliability score across systems. SLO/error-budget gating of experiments (do not inject while the budget is already burning) is established practice. Before using a correctness budget for agent autonomy, define the task population, quality threshold, evaluation window, and escalation policy; calibrate its release consequences locally.
- Multi-agent error-amplification figures (e.g. claims that uncoordinated topologies amplify errors an order of magnitude more than centralised ones) circulate widely but trace to secondary write-ups, not to MAST itself. MAST's own defensible numbers are the 14 failure modes, 3 categories, Figure 4 category shares (41.8%/36.9% on 210 illustrated traces, not all 1,642), 1,600+ traces, and κ = 0.88. Cite those; treat amplification multipliers as unverified.
- Sources: Lewis (1995) *Introduction to Reliability Engineering*; O'Connor & Kleyner (2012) *Practical Reliability Engineering*; Birolini (2017) *Reliability Engineering: Theory and Practice*; Beyer et al. (2016) *Site Reliability Engineering*; Beyer et al. (2018) *The Site Reliability Workbook*; Weibull (1951); IEEE Std 1413 (2010); IEC 60812 (2018); IEC 61025 (2006); NIST reliability handbook; NRC Fault Tree Handbook; Leveson (2011) *Engineering a Safer World*; Hollnagel (2014) *Safety-I and Safety-II*.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
