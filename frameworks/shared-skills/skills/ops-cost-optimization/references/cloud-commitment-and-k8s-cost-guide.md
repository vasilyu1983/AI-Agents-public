# Cloud Commitment Purchasing and Kubernetes Cost Allocation

Operational reference for the two areas most indie/scale-up cost guides skip: deciding whether and how much to commit to AWS/GCP/Azure discount programs, and allocating shared Kubernetes cluster cost back to teams and features. Written for teams that have grown past pure serverless/SaaS spend into owned cloud compute, and for teams running GPU capacity for AI workloads.

## Table of Contents

- [When This Guide Applies](#when-this-guide-applies)
- [Commitment Purchase Decision Math](#commitment-purchase-decision-math)
  - [The Core Trade-off](#the-core-trade-off)
  - [AWS: Savings Plans vs Reserved Instances vs Spot](#aws-savings-plans-vs-reserved-instances-vs-spot)
  - [GCP: Committed Use Discounts](#gcp-committed-use-discounts)
  - [Azure: Reservations vs Savings Plans](#azure-reservations-vs-savings-plans)
  - [When NOT to Buy a Commitment](#when-not-to-buy-a-commitment)
  - [Layered Commitment Strategy](#layered-commitment-strategy)
- [Kubernetes Cost Allocation](#kubernetes-cost-allocation)
  - [Why K8s Cost Is Hard to Attribute](#why-k8s-cost-is-hard-to-attribute)
  - [Allocation Approach](#allocation-approach)
  - [Tooling](#tooling)
- [GPU Capacity for AI Workloads](#gpu-capacity-for-ai-workloads)
- [Cost-Cut vs Reliability Trade-off Framework](#cost-cut-vs-reliability-trade-off-framework)
- [The Cheap-but-Slow Engineering-Time Trap](#the-cheap-but-slow-engineering-time-trap)
- [AI Spend Governance for Platform/Infra Leads](#ai-spend-governance-for-platforminfra-leads)
- [FinOps Framework Alignment](#finops-framework-alignment)
- [What a Top FinOps Lead Catches That a Checklist Misses](#what-a-top-finops-lead-catches-that-a-checklist-misses)

---

## When This Guide Applies

This skill's other reference files (Vercel, Supabase, Cloudflare, GitHub, AI APIs) cover metered PaaS/SaaS spend, where the optimization lever is usage and plan tier. This guide covers a different mechanic: **committing money up front in exchange for a lower rate**, and **attributing shared infrastructure cost to the teams and features that actually consume it**. Use it when:

- The organization runs owned compute on AWS, GCP, or Azure (EC2/GCE/Azure VMs, RDS, GPU instances) rather than only PaaS.
- A cloud bill is dominated by on-demand compute that has been running unchanged for months (a commitment candidate).
- The team runs Kubernetes and cannot answer "which product feature or team is responsible for this cluster's cost."
- The organization is scaling GPU spend for self-hosted LLM inference or training and treating it like a SaaS bill instead of a capacity-planning problem.

---

## Commitment Purchase Decision Math

### The Core Trade-off

Every commitment program trades **discount depth** for **flexibility**. The deeper the discount, the more precisely you must have predicted your future usage — and the more you pay for the difference between committed and actual usage when the prediction is wrong. The FinOps discipline is not "buy commitments," it is "buy the right amount of the right commitment type against a verified usage floor."

**The baseline rule:** commit only against the portion of usage that has been stable for long enough to trust, and buy the most flexible instrument that covers it. Never commit against usage you have not observed being stable, and never commit against 100% of current usage — leave headroom for architecture changes, migrations, and normal variance.

### AWS: Savings Plans vs Reserved Instances vs Spot

| Instrument | Commitment shape | Typical discount vs on-demand | Flexibility |
|---|---|---|---|
| Compute Savings Plans | $/hour spend commitment, 1 or 3 year | ~40-66% (deeper at 3yr, all-upfront) | Applies across EC2 instance family, size, OS, region, and to Fargate/Lambda |
| Reserved Instances (Standard) | Specific instance family + size + region, 1 or 3 year | Deepest discount of the three (can exceed Savings Plans for a stable, unchanging footprint) | Locked to the reserved configuration; convertible RIs trade some discount for the ability to change instance family |
| Spot Instances | No commitment, bid for spare capacity | Up to ~90% off on-demand | AWS can reclaim with a ~2-minute warning; unsuitable for anything that cannot tolerate interruption |

**Decision math:** pull 60-90 days of hourly on-demand cost, find the minimum (floor) across that window, and commit a Compute Savings Plan to ~70-80% of that floor — never to the peak, and never to 100% of the floor, since architecture changes will erode it. Cover long-lived, unchanging resources (a production RDS instance that has run the same instance class for a year) with Reserved Instances for the deeper discount. Route anything interruption-tolerant (batch jobs, CI runners, non-critical background workers, checkpointed training) to Spot.

### GCP: Committed Use Discounts

GCP CUDs come in two shapes, and the choice matters more than the commitment size:

- **Resource-based CUDs**: commit to a specific vCPU/memory quantity in a specific region and machine family. ~37% off at 1 year, ~55% off at 3 years. No upfront payment option — GCP does not offer AWS/Azure-style upfront discount tiers. Waste profile resembles AWS Standard RIs: if actual usage drops below the commitment, you still pay for the full commitment.
- **Flexible CUDs**: commit to a minimum hourly spend across eligible Compute Engine usage, region- and machine-family-agnostic within the billing account. Lower discount than resource-based, but far more forgiving of architecture change — prefer this by default unless a specific workload's shape (region, machine family) is genuinely fixed for the term.

As of mid-2026, new GCP billing accounts have CUD sharing enabled by default, meaning resource-based CUD discounts propagate automatically across all projects under the same billing account — verify this is enabled (or intentionally disabled for chargeback reasons) before assuming siloed CUD purchasing per project.

### Azure: Reservations vs Savings Plans

- **Azure Reservations**: commit to a specific VM family and region, 1 or 3 year. Deepest discount (reported up to ~72% at 3-year for stable Linux VM footprints).
- **Azure Savings Plans**: commit to a $/hour spend level, applies across VM family, region, and additionally across App Service, Container Instances, and Azure Functions. More flexible, slightly shallower discount (~65% ceiling).
- When both a Reservation and a Savings Plan could apply to the same VM, Azure applies the Reservation first (it carries the deeper discount) — a Savings Plan sized to include already-reserved capacity is over-committing and won't be corrected automatically in your favor.

### When NOT to Buy a Commitment

This is the judgment a checklist misses — the highest-value thing a FinOps lead does is talk a team out of a commitment, not into one.

- **Workload is under ~4-6 weeks old.** There is no usage floor to commit against yet. Run on-demand until a stable baseline exists.
- **An active migration, re-platform, or major refactor is in flight.** Committing mid-migration is the single most common source of stranded commitment spend — the cost of waiting a quarter is always smaller than the cost of a 1-3 year commitment against an architecture that is about to change.
- **The team is actively evaluating a move to serverless, spot, ARM-based instances, or a different cloud.** A commitment locks in the old shape and creates an internal disincentive to make the efficiency improvement, because the unused commitment becomes a sunk cost someone has to explain.
- **Usage is genuinely volatile (seasonal, promotional, or highly elastic product).** Commitments are a bet on a stable floor; volatile workloads should lean toward Spot/on-demand plus autoscaling instead.
- **The organization cannot forecast growth with reasonable confidence 6-12 months out.** A 3-year RI on a team that doesn't know its own trajectory is a bet the finance team is making on the engineering team's roadmap stability — make sure finance knows that's the bet.

### Layered Commitment Strategy

The pattern that works in practice, across all three clouds: **baseline with the flexible spend-commitment instrument (Savings Plan / flexible CUD), pin down genuinely static long-lived resources with the rigid resource-commitment instrument (RI / resource-based CUD / Azure Reservation) for the deeper discount, and route everything interruption-tolerant to Spot.** Reported outcomes for this layered approach are in the 50-65% savings range versus a pure on-demand footprint — but that figure depends entirely on how much of the workload is genuinely stable; do not quote it to a customer without first establishing their stable-vs-volatile split.

---

## Kubernetes Cost Allocation

### Why K8s Cost Is Hard to Attribute

A Kubernetes cluster bills as a small number of large line items (node-hours, attached storage, load balancers) shared across many namespaces, teams, and workloads. Without allocation tooling, the cloud bill shows "EKS cluster: $40,000/month" with no way to tell which of 30 microservices, which team, or which customer tier is responsible for it. This is the same unit-economics problem covered in [unit-economics-guide.md](unit-economics-guide.md), applied at the cluster level.

### Allocation Approach

1. **Tag at the namespace and label level first.** Require every workload to carry `team`, `feature`, and `environment` labels before it can be scheduled (enforce via admission policy, not convention — conventions decay).
2. **Allocate shared cluster overhead (control plane, DaemonSets, cluster-critical add-ons) proportionally** by CPU/memory request share, not by pod count — a namespace with few large pods can dominate resource consumption while looking small in a pod-count view.
3. **Distinguish requests from actual usage.** Cost allocation tools typically show both "cost if billed by request" and "cost if billed by actual usage" — the gap between them is the over-provisioning number, and it is usually the single largest optimization opportunity in a K8s cost review.
4. **Reconcile to the cloud bill monthly**, not just to the Kubernetes-reported numbers — node autoscaler behavior, spot node churn, and unschedulable pending pods can create discrepancies between "what Kubernetes thinks it's using" and "what the cloud provider is billing."

### Tooling

- **OpenCost** — CNCF project (donated by the Kubecost team, since graduated from Sandbox to Incubating status), open-source, the de facto standard cost-allocation engine for Kubernetes. Provides per-namespace, per-label, per-workload cost allocation using cluster metrics plus cloud billing data.
- **Kubecost** — commercial product built on the same allocation engine as OpenCost, adding a UI, alerting, multi-cluster rollups, and governance features. Kubecost was acquired by IBM in 2024 and is now positioned as part of IBM's broader FinOps suite (alongside Cloudability and Turbonomic) — evaluate current roadmap and independence before a multi-year commercial commitment, as the acquisition has raised community questions about long-term OSS prioritization (unverified how this resolves past 2026 — check current OpenCost governance status at decision time).
- **CAST AI, ScaleOps, and similar** — commercial tools that go beyond allocation into automated rightsizing and bin-packing (evicting/rescheduling workloads onto fewer, better-utilized nodes). Consider when allocation alone has revealed waste but the team lacks bandwidth to act on it manually.
- **Cloud-native cost tools** (AWS Cost and Usage Report + Kubernetes cost allocation tags, GCP Cost Table export, Azure Cost Management) can approximate allocation without a dedicated K8s tool, but require more manual mapping and lack the request-vs-usage view.

---

## GPU Capacity for AI Workloads

GPU capacity for self-hosted model training and inference follows the same commitment logic as general compute, with a shorter stable-usage bar because the GPU market and model landscape both move faster than general compute:

- **On-demand** for exploratory work, fine-tuning experiments, and any workload whose shape is not yet settled.
- **Reserved 1-3 year GPU capacity** cuts a reported 30-50% off on-demand and is appropriate for production inference serving that runs 24/7 against a model that is not expected to change within the term.
- **Spot/interruptible GPU capacity** for batch training with checkpoint/resume, offline batch inference, and evaluation runs — never for a synchronous production inference path.
- Reported on-demand GPU-hour pricing varies enormously by provider and changes weekly (specialized AI-cloud providers vs. hyperscalers vs. neoclouds) — do not carry a specific $/hour figure in this guide as authoritative; re-quote from the provider's current pricing page at decision time.
- See [ai-api-cost-guide.md — Self-Hosted / Open-Weight Inference](ai-api-cost-guide.md#self-hosted--open-weight-inference) for the build-vs-buy comparison against managed model APIs.

---

## Cost-Cut vs Reliability Trade-off Framework

Every cost-cutting action either has zero reliability impact (pure waste elimination) or trades some reliability/performance margin for savings. Treat these as two different approval paths:

| Category | Example | Approval bar |
|---|---|---|
| **Zero-risk waste elimination** | Unused reserved capacity, orphaned volumes, zombie load balancers, dev/staging left running 24/7 | Execute immediately, no sign-off needed beyond notifying the owning team |
| **Margin reduction (capacity headroom)** | Reducing autoscaling max replicas, shrinking a database instance class, lowering multi-AZ redundancy | Requires the service owner to confirm current headroom against known peak load, not just average load — cutting to "current usage plus 10%" without checking peak-to-average ratio is how outages happen during the next traffic spike |
| **Durability/DR reduction** | Reducing backup retention, dropping a standby replica, reducing replication factor | Requires an explicit, documented decision from whoever owns the recovery-time and recovery-point objectives — this is a risk-acceptance decision, not a cost optimization, and should be logged as one |
| **Commitment lock-in** | Buying a 3-year Reserved Instance or CUD | Requires confirming the usage floor is real (see commitment section above) — the "reliability" being traded is organizational flexibility, not runtime reliability, but it is still a real trade-off |

The single most common FinOps failure mode is treating category 2-4 actions as if they were category 1 — cutting a cost line with a plausible-looking 20% headroom margin, then hitting an incident three weeks later during a traffic spike that the removed headroom would have absorbed. A senior FinOps practitioner asks "what is this margin actually protecting against, and has that risk changed?" before recommending a cut — a checklist just says "right-size the instance."

---

## The Cheap-but-Slow Engineering-Time Trap

The largest hidden cost in most cost-optimization exercises is not on the cloud bill — it's the engineering time spent implementing the optimization. A migration that saves $2,000/month but consumes six weeks of a senior engineer's time (loaded cost easily $15,000-25,000) does not pay back for 8-12 months, and that estimate assumes the migration goes smoothly and doesn't introduce new operational burden (a new system to monitor, patch, and staff on-call for).

Before recommending an architecture change or platform migration for cost reasons, estimate:

1. **Implementation cost**: engineer-weeks × loaded cost per week.
2. **Ongoing operational cost**: does the new approach need monitoring, on-call, or specialized expertise the team doesn't currently have? Self-hosting anything (a database, a GPU inference stack, a Kubernetes cluster) converts a subscription line item into a permanent operational responsibility — that responsibility has a cost even when nothing goes wrong, and a much larger one when something does.
3. **Payback period**: implementation cost ÷ monthly savings. A payback period beyond 12 months for anything except foundational infrastructure is usually not worth the distraction from product work, unless the savings compound with growth (i.e., the saving scales with traffic, not just with today's traffic).
4. **Reversibility**: can this be undone cheaply if the assumption behind it turns out wrong? Prefer reversible optimizations (config changes, plan downgrades) over irreversible ones (a from-scratch platform migration) when the expected savings are similar.

This is the judgment that separates "found a way to save money" from "found a way to save money that was actually worth doing."

---

## AI Spend Governance for Platform/Infra Leads

AI/LLM spend is the fastest-growing and least-governed line item on most 2026 infrastructure bills, because it is easy for any engineer to add an API call to a paid model without going through the same review a new cloud resource would get. This is a governance gap, not a pricing problem, and pricing optimization (covered in [ai-api-cost-guide.md](ai-api-cost-guide.md)) does not fix it on its own.

- **Require a cost estimate before a new AI feature ships**, the same way a new database or a new cloud resource would get one. Model choice, expected volume, and prompt-caching design should be reviewed at design time, not discovered on the bill a month later.
- **Set per-feature and per-environment spending limits**, not just an org-wide cap — an org-wide cap gets hit by whichever team happened to ship last, and by the time it's hit, attribution to the responsible feature is much harder.
- **Track cost per unit of product value** (cost per resolved support ticket, cost per generated document, cost per completed agent task), not just cost per token — token efficiency can improve while unit economics get worse if quality drops and the feature needs more retries or human fallback.
- **Treat agentic/multi-step AI workloads as a distinct governance category.** A single user action that triggers a multi-agent loop, tool calls, and sub-agent delegation can consume an order of magnitude more tokens than a single request-response call, and the per-request cost is much less predictable. Log per-session and per-task cost, not just per-call cost, for anything agentic — see [ai-api-cost-guide.md — Per-Trace and Per-User Cost Attribution](ai-api-cost-guide.md#per-trace-and-per-user-cost-attribution).
- **Review model and pricing changes quarterly, not annually.** The AI API market re-prices and re-tiers models far more often than traditional cloud infrastructure — a cost review cadence built for annual cloud contract renewals will miss several pricing changes per year in this category.

---

## FinOps Framework Alignment

The FinOps Foundation's Framework was substantially expanded for 2026: the Foundation's stated mission moved from "Advancing the People who manage the Value of Cloud" to "Advancing the People who manage the Value of Technology," and the Framework introduced **FinOps Scopes** — the "Cloud+" expansion — covering Public Cloud, SaaS, Data Center, Data Cloud Platforms, and a newly dedicated **AI Technology Category** with its own capabilities, personas, KPIs, and FOCUS alignment guidance. This directly validates the scope this skill already covers (SaaS/PaaS spend alongside cloud and AI) as a legitimate FinOps Scope in its own right, not an afterthought to "real" cloud FinOps.

Practical implication: when framing a cost review for a stakeholder audience that knows the FinOps Framework, describe the SaaS-heavy stack this skill audits as its own FinOps Scope (e.g., "Product Engineering SaaS Scope") rather than trying to force it into a legacy "cloud infrastructure" framing — the 2026 Framework explicitly supports scope-specific maturity expectations, meaning a fast-moving AI feature scope can reasonably tolerate more waste than a stable production cloud scope, and that's a defensible position under the current Framework rather than a compromise.

Source: FinOps Foundation Framework — https://www.finops.org/framework/ (verify current page structure; the Framework is now issued as an annual revision, e.g. "Framework 2026," rather than a single version number).

---

## What a Top FinOps Lead Catches That a Checklist Misses

A checklist finds the same waste every quarter. A senior practitioner also catches:

- **The commitment that made sense a year ago and doesn't anymore** — a 3-year RI bought against an architecture the team has since replaced. Nobody proactively surfaces this; it just sits as sunk cost until someone specifically goes looking for utilization below 100% on existing commitments.
- **The team that optimized the wrong layer.** Engineering spent two sprints reducing Lambda invocation count by 40% when Lambda was 5% of the bill and the database was 60% — a checklist would have marked the Lambda work "done" without checking whether it moved the total.
- **The metric that looks efficient but is hiding a quality regression.** Cost-per-request dropped because a model-cascading change silently downgraded quality and users started retrying failed responses more often — total user-facing cost (including support and churn) went up while the infra line item went down.
- **The commitment or architecture decision nobody owns.** When a cost-saving migration breaks something six months later, "why did we do this" needs a documented owner and rationale — not a git blame exercise. Insist that cost-driven architecture decisions get the same lightweight design-doc treatment as feature work.
- **Growth that looks like waste and waste that looks like growth.** Distinguishing "this cost line grew because we got more customers" from "this cost line grew because something is misconfigured" is the single highest-leverage question in any review — see [unit-economics-guide.md — Profitable Growth vs Destructive Growth](unit-economics-guide.md#profitable-growth-vs-destructive-growth) for the diagnostic questions.
