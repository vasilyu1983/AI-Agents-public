# ML Technical Debt Taxonomy

The debt classes that are specific to ML systems, each paired with a detection signal you can instrument and a mitigation you can ship.

Use this when a system "works" but every change is expensive: fixes ripple, nobody knows who consumes a prediction, configuration is folklore, or a model's own output has quietly become its training data. This is the diagnostic layer that sits upstream of the operational references — once you have named the debt class, the mitigation usually lives in one of the linked patterns files.

**Source framing:** the taxonomy below is as presented in Vijay Janapa Reddi, *Machine Learning Systems* (Harvard / MLSysBook, open textbook, Oct 2025), Chapter 13 "ML Operations", §13.3 "Technical Debt and System Complexity" (book pp. 1108–1115). The textbook builds on and cites Sculley et al., "Hidden Technical Debt in Machine Learning Systems" (NeurIPS 2015). Claims here are attributed to the textbook's presentation, not to independent reading of the underlying paper.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [1. Why ML Debt Is Its Own Category](#1-why-ml-debt-is-its-own-category)
- [2. The Debt Map](#2-the-debt-map)
- [3. Boundary Erosion and CACHE](#3-boundary-erosion-and-cache)
- [4. Correction Cascades](#4-correction-cascades)
- [5. Interface and Dependency Debt](#5-interface-and-dependency-debt)
- [6. System Evolution Debt](#6-system-evolution-debt)
- [7. Detection and Mitigation Table](#7-detection-and-mitigation-table)
- [8. Debt Triage Workflow](#8-debt-triage-workflow)
- [9. Worked Failures the Textbook Cites](#9-worked-failures-the-textbook-cites)
- [10. Judgment: Which Debt to Pay Down First](#10-judgment-which-debt-to-pay-down-first)

## Quick Navigation

- [The Debt Map](#2-the-debt-map)
- [Boundary Erosion and CACHE](#3-boundary-erosion-and-cache)
- [Correction Cascades](#4-correction-cascades)
- [Interface and Dependency Debt](#5-interface-and-dependency-debt)
- [System Evolution Debt](#6-system-evolution-debt)
- [Detection and Mitigation Table](#7-detection-and-mitigation-table)
- [Debt Triage Workflow](#8-debt-triage-workflow)

---

## 1. Why ML Debt Is Its Own Category

The textbook's framing: in traditional software, broken code fails immediately. ML systems degrade **silently** through data changes, model interactions, and evolving requirements. The debt metaphor itself predates ML — the textbook attributes it to Ward Cunningham in 1992, comparing rushed coding decisions to financial debt that must be paid back with a rewrite.

Three properties of ML workflows generate debt classes that ordinary DevOps practice does not cover:

- **Reliance on data rather than deterministic logic** — behavior is a function of a distribution, not of a branch you can read.
- **Statistical rather than exact behavior** — there is no compile-time contract to violate loudly.
- **Implicit dependencies through data flows rather than explicit interfaces** — couplings bypass every dependency-analysis tool your language ecosystem provides.

The textbook's Figure 13.2 (attributed to Sculley et al.) makes the structural point: most engineering effort in a typical ML system concentrates on the components *surrounding* the model — data collection, data verification, feature extraction, configuration, serving infrastructure, monitoring, process management, analysis tools, machine resource management — rather than on the ML code itself. The debt accumulates in exactly those under-attended surfaces.

**Operational consequence:** a debt audit that only reads model code will find nothing. Audit the data path, the config path, and the consumer list.

---

## 2. The Debt Map

The textbook's Figure 13.3 is a hub-and-spoke diagram with **Hidden Technical Debt** at the hub and six spokes. Reproduced structurally:

```text
                Undeclared              Feedback         Configuration
                Consumers                 Loops              Debt
             (hidden model             (self-reinforcing  (parameter sprawl:
              dependencies)             coupling)         ad hoc settings,
                    \                       |             hard-coded values)
                     \                      |                    /
                      \                     |                   /
    Data Debt ------------  HIDDEN TECHNICAL DEBT  ------------ Boundary Erosion
 (quality issues:                    |         \                 (CACHE principle:
  inconsistent formats               |          \                 Change Anything
  and distributions)                 |           \                Changes Everything)
                                     |            \
                              Pipeline Debt     Correction Cascades
                            (fragile workflows: (sequential dependencies:
                             tightly coupled)    upstream fixes break
                                                 downstream systems)
```

Read the spokes as the textbook groups them: **boundary erosion** undermines modularity; **correction cascades** propagate fixes through dependencies; **feedback loops** create hidden coupling; **data, configuration, and pipeline debt** reflect poorly managed artifacts and workflows.

---

## 3. Boundary Erosion and CACHE

**What it is.** Traditional systems use modularity and abstraction to isolate change. ML systems blur those boundaries: data pipelines, feature engineering, model training, and downstream consumption become tightly coupled with poorly defined interfaces. The result is **entanglement** — dependencies so intertwined that local modifications require global understanding and coordination.

**CACHE — Change Anything Changes Everything.** The textbook's name for the manifestation: without strong boundaries, adjusting a feature encoding, a model hyperparameter, or a data-selection criterion changes downstream behavior unpredictably. Its worked example: changing the binning strategy of a numerical feature may cause a previously tuned model to underperform, triggering retraining and downstream evaluation changes.

**Framing against classical software principles.** The textbook makes the violation explicit:

- Boundary erosion violates the **Law of Demeter** and the **principle of least knowledge**. Traditional software achieves modularity through explicit interfaces and information hiding; ML systems create implicit couplings through data flows that bypass those boundaries entirely.
- CACHE represents a breakdown of the **Liskov Substitution Principle** — component modifications violate behavioral contracts that dependent components expected. Unlike traditional software with compile-time guarantees, ML systems operate with statistical behavior, producing inherently different coupling patterns.

The textbook's own caution: the challenge is reconciling traditional modularity with the interconnected nature of ML workflows, where statistical dependencies create coupling patterns that classical SE frameworks were not designed to handle. Treat Demeter and LSP as diagnostic lenses, not as fixes you can simply apply.

**Detection signals**

- A one-line feature-transform change requires re-running full downstream evaluation before anyone will merge it.
- No stage in the pipeline can be validated in isolation; there is no test that exercises feature engineering without invoking modelling.
- Changelogs show hyperparameter or encoding changes paired with unrelated downstream fixes in the same commit.
- Reviewers routinely ask "what else does this touch?" and nobody can answer from the code.

**Mitigations**

- Separate ingestion from feature engineering, and feature engineering from modelling, into layers that can be independently validated, monitored, and maintained — the textbook's stated remedy.
- Give each layer a documented interface (schema in, schema out) and test it at that boundary.
- Treat boundary erosion as an early-development invisible cost: it is cheapest to prevent before scale, most expensive to unwind after.
- See [feature-store-patterns.md](feature-store-patterns.md) for the batch/online parity boundary and [data-ingestion-patterns.md](data-ingestion-patterns.md) for contracts and schema evolution.

---

## 4. Correction Cascades

**What it is.** A sequence of dependent fixes that propagates **backward and forward** through the workflow after a small adjustment. The textbook's Figure 13.4 lays the ML lifecycle out as a spine — problem statement, data collection, data analysis, model training, model evaluation, model deployment — with arcs for corrective actions, red arrows for cascading revisions, and a dotted arc at the bottom for the drastic outcome: abandoning and restarting the process.

**Sources of instability the textbook color-codes in that figure:**

- Interacting with physical-world brittleness
- Inadequate application-domain expertise
- Conflicting reward systems (misaligned incentives)
- Poor cross-organizational documentation

**The common trigger: sequential model development.** Reusing or fine-tuning an existing model to accelerate a new task introduces hidden dependencies that are difficult to unwind. Assumptions baked into earlier models become implicit constraints on later ones. The textbook's example: a team fine-tunes a churn model for a new product; the original embeds product-specific behaviors and feature encodings that are invalid in the new setting; the team patches the model, then discovers the real problem sits several layers upstream in the original feature selection or labeling criteria.

**Why it persists.** The textbook's mechanism: cascades emerge from hidden feedback loops that violate modularity. When model A's outputs influence model B's training data, the dependency operates through data flows rather than code interfaces — invisible to conventional dependency-analysis tooling. From a systems-theory view, cascades are tight coupling between supposedly independent components; the textbook describes cascade propagation as following power-law distributions, where small initial changes trigger disproportionately large system-wide modifications, and draws the parallel to the butterfly effect.

**The reuse-vs-redesign tradeoff, as the textbook states it**

| Situation | Textbook's lean |
|---|---|
| Small, static dataset | Fine-tuning may be appropriate |
| Large or rapidly evolving dataset | Retraining from scratch gives greater control and adaptability |
| Compute-constrained setting | Fine-tuning is attractive (fewer resources) |
| Foundational component likely to change later | Fresh architecture, even if resource-intensive — modifying foundations later is extremely costly |

The textbook does not present this as a rule: it explicitly says scenarios remain where sequential model building makes sense, and calls for a balance between efficiency, flexibility, and long-term maintainability.

**Detection signals**

- A single incident fix generates follow-up tickets in stages both upstream and downstream of the change.
- Root-cause analyses repeatedly terminate in labeling criteria or feature selection decisions made in an earlier project.
- Model lineage shows a chain of fine-tunes with no run where the base was retrained from data.
- Retros mention "we patched it at the model layer" for a problem that was a data-definition problem.

**Mitigations**

- Record lineage depth as a first-class registry field: which base, which dataset revision, which labeling convention. See [model-registry-patterns.md](model-registry-patterns.md).
- Set an explicit reuse budget — after N sequential fine-tunes on drifting data, the default flips to retrain-from-scratch and the exception needs an owner.
- Make cascade-prone changes go through a staged rollout with a rollback target rather than a hot patch. See [deployment-lifecycle.md](deployment-lifecycle.md).
- Fix causes at the layer that owns them: a labeling-criteria defect gets fixed in labeling, not compensated for in the model.

---

## 5. Interface and Dependency Debt

The textbook groups two patterns here, both arising because ML components interact through data flows and shared outputs rather than explicit APIs.

### Undeclared Consumers

Model outputs serve downstream components without formal tracking or interface contracts. When models evolve, these hidden dependencies break silently. The textbook's example: a credit-scoring model's outputs feed an eligibility engine, which influences future applicant pools and therefore future training data — an untracked feedback loop that biases model behavior over time.

**Detection signals**

- No inventory exists mapping prediction endpoints or output tables to named consuming systems and owners.
- Prediction outputs are readable by any service with warehouse access.
- A model version bump ships with no consumer notification list because none exists.
- Query logs show read traffic on a prediction table from services nobody on the ML team can name.

**Mitigations**

- Strict access controls on model outputs — the textbook's first stated solution. Reads are granted, not defaulted.
- Formal interface contracts with documented schemas for every published output.
- Comprehensive monitoring of prediction *usage* patterns, not just prediction quality — you cannot govern consumers you cannot see.
- Register each consumer against the model version it depends on so a deprecation has a blast radius. See [model-registry-patterns.md](model-registry-patterns.md) and [api-design-patterns.md](api-design-patterns.md).

### Data Dependency Debt

Pipelines accumulate **unstable** data dependencies (sources whose structure or distribution changes underneath you) and **underutilized** ones (dependencies carried at maintenance cost for little benefit). The textbook's point of leverage: feature-engineering scripts, data joins, and labeling conventions lack the dependency-analysis tooling that traditional software development takes for granted. When a data source changes structure or distribution, downstream models fail unexpectedly.

**Detection signals**

- Features exist in the serving path that no live model version reads (underutilized).
- Upstream schema or distribution changes reach production without a pipeline alert (unstable).
- No lineage answers "which models would break if this table changed?"
- Feature ablation has never been run, so nobody knows which dependencies earn their keep.

**Mitigations**

- Data versioning and lineage tracking systems — the textbook's stated remedy for exactly this class.
- Periodic ablation to retire underutilized dependencies; each retained dependency should have a named consumer and a measured contribution.
- Contract tests on upstream sources so a distribution or schema change fails loudly at ingest rather than quietly at inference. See [data-ingestion-patterns.md](data-ingestion-patterns.md) and [drift-detection-guide.md](drift-detection-guide.md).

---

## 6. System Evolution Debt

The textbook's third grouping: challenges that appear as ML systems mature.

### Feedback Loops

Models influence their own future behavior through the data they generate. The textbook's canonical case is recommendation: suggested items shape user clicks, clicks become training data, and self-reinforcing biases follow. Two consequences it names — these loops **undermine data independence assumptions**, and they **can mask performance degradation for months**.

The textbook distinguishes the loop that runs through your own system from the one that runs through another team's: undeclared consumers (§5) are how a *hidden* feedback loop gets built without anyone deciding to build one.

**Detection signals**

- Training data cannot be partitioned into cohorts that were and were not exposed to the model's own output.
- Online metrics improve steadily while held-out or exposure-free evaluation is flat or falling.
- Engagement metrics and ranking logic share inputs with no documented separation.

**Mitigations**

- **Cohort-based monitoring for loop detection** — the textbook's named engineering solution.
- Delayed labeling and explicit disentanglement between engagement metrics and ranking logic (the mitigations it credits to YouTube's overhaul, §9).
- Hold out an unexposed slice where ethically and commercially possible, so a degradation signal survives the loop. See [online-evaluation-patterns.md](online-evaluation-patterns.md) and [monitoring-best-practices.md](monitoring-best-practices.md).

### Pipeline Debt

ML workflows evolve into **"pipeline jungles"** of ad hoc scripts and fragmented configurations. The textbook names the failure mode precisely: without modular interfaces, teams build **duplicate pipelines rather than refactor brittle ones**, producing inconsistent processing and a compounding maintenance burden.

**Detection signals**

- Two or more pipelines compute the same feature with different code paths.
- Preprocessing is duplicated between training and serving rather than shared.
- Adding a step means copying a script rather than registering a node in an orchestrated graph.

**Mitigations**

- Modular pipeline design with workflow orchestration tools — the textbook's stated solution.
- Deduplicate to a single computation per feature and treat the second implementation as a defect, not a variant. See [feature-store-patterns.md](feature-store-patterns.md).
- Refactor the brittle pipeline before the deadline that will otherwise produce the duplicate.

### Configuration Debt

The textbook's spoke label is **parameter sprawl: ad hoc settings and hard-coded values**. Its stated remedy is to treat configuration as a **first-class system component with versioning and validation**.

**Early-stage shortcuts** are the named upstream cause: rapid prototyping encourages embedding business logic in training code and making undocumented configuration changes. The textbook is even-handed here — these shortcuts are necessary for innovation, and become liabilities as systems scale across teams. Debt taken deliberately with a repayment date is not the failure mode; debt taken silently is.

**Detection signals**

- Behavior differs between environments and no config diff explains it.
- Business thresholds live inside training code rather than in reviewed configuration.
- Config changes ship without review, version, or validation.
- Nobody can reconstruct the exact configuration of a release that is currently serving.

**Mitigations**

- Version and validate configuration in the same pipeline as code; a config change is a release.
- Extract business logic out of training code into declared, reviewable settings.
- Bind the config version to the model version in the registry so a rollback restores both. See [model-registry-patterns.md](model-registry-patterns.md) and [deployment-lifecycle.md](deployment-lifecycle.md).

---

## 7. Detection and Mitigation Table

One row per debt class. Use it as an audit checklist.

| Debt class | Detection signal (cheapest first) | Primary mitigation | Where the pattern lives |
|---|---|---|---|
| Boundary erosion / entanglement (CACHE) | No stage validates in isolation; small transform changes force full downstream re-evaluation | Layer ingestion / feature engineering / modelling behind documented interfaces, independently validated | [data-ingestion-patterns.md](data-ingestion-patterns.md), [feature-store-patterns.md](feature-store-patterns.md) |
| Correction cascades | One fix generates upstream *and* downstream tickets; root causes land in old labeling or feature-selection decisions | Track lineage depth; set a reuse budget; fix causes at the owning layer; staged rollout with rollback target | [model-registry-patterns.md](model-registry-patterns.md), [deployment-lifecycle.md](deployment-lifecycle.md) |
| Undeclared consumers | No consumer inventory; prediction outputs world-readable; version bump has no notification list | Access control on outputs, documented schema contracts, monitoring of prediction *usage* | [api-design-patterns.md](api-design-patterns.md), [model-registry-patterns.md](model-registry-patterns.md) |
| Data dependency debt (unstable) | Upstream schema/distribution change reaches production without alerting | Lineage tracking plus contract tests that fail at ingest | [data-ingestion-patterns.md](data-ingestion-patterns.md), [drift-detection-guide.md](drift-detection-guide.md) |
| Data dependency debt (underutilized) | Served features no live model version reads; ablation never run | Periodic ablation and retirement; every dependency needs a named consumer | [feature-store-patterns.md](feature-store-patterns.md) |
| Feedback loops (direct and hidden) | Cannot partition training data by model exposure; online metrics rise while exposure-free eval is flat | Randomized no-action holdout or logged action propensities, cohort-based monitoring, delayed labeling, separate engagement metrics from ranking logic | [ai-evals online-production-eval](../../ai-evals/references/online-production-eval.md), [monitoring-best-practices.md](monitoring-best-practices.md) |
| Pipeline debt / pipeline jungles | Same feature computed by two code paths; duplication chosen over refactor | Modular pipelines under orchestration; one computation per feature | [feature-store-patterns.md](feature-store-patterns.md) |
| Configuration debt / parameter sprawl | Env behavior differs with no config diff; thresholds hard-coded in training code | Configuration as a first-class component: versioned, validated, bound to model version | [model-registry-patterns.md](model-registry-patterns.md), [deployment-lifecycle.md](deployment-lifecycle.md) |

---

## 8. Debt Triage Workflow

```text
symptom: changes are expensive / failures are silent
  |
  v
1. Can any single stage be validated in isolation?
     no  -> boundary erosion. Layer the system first; other fixes will not hold.
     yes -> continue
  |
  v
2. Do fixes generate follow-up work in other stages?
     yes -> correction cascade. Trace to the owning layer before patching.
  |
  v
3. Is there a written inventory of who consumes each model output?
     no  -> undeclared consumers. Build the inventory; gate reads.
  |
  v
4. Does every served data dependency have a named consumer and a measured contribution?
     no  -> data dependency debt. Ablate and retire, or contract-test and keep.
  |
  v
5. Can training data be partitioned by whether it was exposed to the model's own output?
     no  -> feedback loop. Add cohort-based monitoring before trusting any online metric.
  |
  v
6. Is any feature computed by more than one code path?
     yes -> pipeline debt. Deduplicate before adding the next pipeline.
  |
  v
7. Can you reconstruct the exact configuration of the release now serving?
     no  -> configuration debt. Version and validate config; bind it to the model version.
  |
  v
record which debts you are accepting, with an owner and a repayment trigger
```

The last step is the one teams skip. The textbook's own framing is that some debt is unavoidable during early development; understanding causes and impact is what lets engineers design maintainable systems. Accepted debt with an owner is a decision. Unnamed debt is the failure mode.

---

## 9. Worked Failures the Textbook Cites

The textbook presents four industry cases, one per debt class. Figures below are quoted as the textbook states them; it does not source each number to a primary filing, so treat them as the textbook's account rather than as independently verified magnitudes.

| Case | Debt class | Textbook's account |
|---|---|---|
| YouTube recommendations | Feedback loop debt | Recommendations influence user behavior, which becomes training data, leading to unintended content amplification. The textbook states the recommendation system drives 70% of watch time (1+ billion hours daily), that 2016 algorithmic changes increased average session time by 50% while inadvertently promoting conspiracy content, and that fixing the loops required 2+ years of engineering work and new evaluation frameworks — via cohort-based evaluation, delayed labeling, and explicit disentanglement of engagement metrics from ranking logic. |
| Zillow (Zestimate / iBuying) | Correction cascade failure | Initial valuation errors propagated into purchasing decisions; retroactive corrections triggered systemic instability requiring data revalidation, model redesign, and eventually a full system rollback. The textbook states Zillow lost $881 million in Q3 2021 across multiple factors including ML model failures, reports the Zestimate algorithm overvaluing homes by an average of 5–7%, and notes 2,000+ layoffs and a $569 million inventory write-down on shutting down Zillow Offers in 2021. |
| Tesla Autopilot (early deployments) | Undeclared consumer debt | Model outputs were repurposed across subsystems without clear boundaries; over-the-air updates occasionally introduced silent behavior changes affecting multiple subsystems (e.g. lane centering and braking) unpredictably. The textbook presents this as the risk of skipping strict interface governance in safety-critical ML systems. |
| Facebook News Feed | Configuration debt | Rapid experimentation without consistent configuration management produced opaque settings influencing content ranking with no clear documentation; behavior changes became difficult to trace and unintended consequences emerged from misaligned configurations. |

**How to use these:** as pattern recognizers, not as benchmarks. Each maps a debt class to a visible organizational symptom — content amplification, valuation instability, cross-subsystem surprise, untraceable ranking behavior. If your incident narrative rhymes with one of these, start the triage in §8 at that class.

---

## 10. Judgment: Which Debt to Pay Down First

- **Boundary erosion first, when present.** The other mitigations assume you can change one stage without changing all of them. If you cannot validate a stage in isolation, lineage tracking and consumer inventories will document a mess rather than reduce it.
- **Undeclared consumers before any deprecation.** The cheapest catastrophic failure in this taxonomy is shipping a model change that silently breaks a consumer you did not know existed. The inventory is a days-scale task; the outage is not.
- **Feedback loops before trusting online metrics.** The textbook's warning that loops can mask degradation for months means an unexamined online dashboard is not evidence of health. Build the cohort split before you build the promotion gate on top of it.
- **When predictions trigger actions, keep a counterfactual.** If the model's output decides an offer, a block, a review or a price, the labels you collect are shaped by those actions: a blocked transaction never shows whether it was fraud. Keep a small randomized no-action (or random-action) holdout, or log the probability with which each action was chosen, and compute drift, label metrics and champion/challenger comparisons on that slice or with propensity weights. Without one, retraining learns the old model's policy and every comparison favours the incumbent. Size the holdout from the cost of the withheld action, and decide it before launch; it cannot be added retroactively.
- **Configuration debt is the cheapest to fix and the most commonly deferred.** Versioning and validating config is largely mechanical and pays back on the first rollback.
- **Pipeline debt compounds on a schedule you control.** Every deadline that produces a duplicate pipeline rather than a refactor is a decision. Name it as one.
- **Do not treat "avoid all debt" as the goal.** The textbook is explicit that some debt is unavoidable during early development and that early-stage shortcuts are necessary for innovation. The engineering discipline is recording what you took, who owns it, and what triggers repayment — not refusing to take any.
- **The debt audit is a data-path audit.** Given the textbook's Figure 13.2 point that most system effort sits outside the model code, an audit that reads only model code will report a clean bill of health on a system that is deeply in debt.

---

## Sources

- Vijay Janapa Reddi, *Machine Learning Systems* (Harvard / MLSysBook, open textbook, October 2025), Chapter 13 "ML Operations", §13.3 "Technical Debt and System Complexity", book pp. 1108–1115, including Figure 13.2 (ML System Complexity), Figure 13.3 (ML Technical Debt Taxonomy), and Figure 13.4 (Correction Cascades).
- The textbook attributes the underlying taxonomy and Figure 13.2 to Sculley et al., "Hidden Technical Debt in Machine Learning Systems" (NeurIPS 2015), and the debt metaphor itself to Ward Cunningham (1992). Those works are cited here as the textbook cites them.
