# Cloud Commitment Purchasing and Kubernetes Cost Allocation

Operational reference for the two areas most indie/scale-up cost guides skip: deciding whether and how much to commit to AWS/GCP/Azure discount programs, and allocating shared Kubernetes cluster cost back to teams and features. Written for teams that have grown past pure serverless/SaaS spend into owned cloud compute, and for teams running GPU capacity for AI workloads.

## Table of Contents

- [When This Guide Applies](#when-this-guide-applies)
- [Commitment Purchase Decision Math](#commitment-purchase-decision-math)
  - [The Core Trade-off](#the-core-trade-off)
  - [Sizing Rule: Commit To The d-Quantile](#sizing-rule-commit-to-the-d-quantile)
  - [Instrument Shapes](#instrument-shapes)
  - [When NOT to Buy a Commitment](#when-not-to-buy-a-commitment)
  - [Exit Rules: What Happens When You Are Wrong](#exit-rules-what-happens-when-you-are-wrong)
  - [Layered Commitment Strategy](#layered-commitment-strategy)
- [Egress and Storage-Class Traps](#egress-and-storage-class-traps)
- [Kubernetes Cost Allocation](#kubernetes-cost-allocation)
  - [Why K8s Cost Is Hard to Attribute](#why-k8s-cost-is-hard-to-attribute)
  - [Allocation Approach](#allocation-approach)
  - [Tooling](#tooling)
  - [Showback Before Chargeback](#showback-before-chargeback)
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

### Sizing Rule: Commit To The d-Quantile

Let d be the instrument's discount versus on-demand for the chosen term and payment option. Look it up at decision time on the provider's pricing page or in its commitment-recommendation tool, and record the date; do not carry a remembered percentage.

1. Pull 60–90 days of hourly on-demand-equivalent usage (or spend, for a $/hour instrument) for exactly the scope the instrument covers. Commitments are consumed per hour; an unused committed hour is lost.
2. A committed unit costs (1 − d) every hour and saves 1 only in the hours usage reaches it. Another unit pays while P(usage ≥ L) > 1 − d, so set the commitment level L at the **d-quantile of hourly usage expected over the term**. At d = 0.4, that is the level usage exceeds in 60% of hours.
3. Lower L only for a named risk over the term (forecast decline, a planned migration or architecture change, a shape change the instrument cannot follow) and write down the risk and the haircut.
4. Re-run when d or the usage shape changes: a deeper discount justifies committing higher up the distribution.

Sizing against the observed minimum, or a fraction of it, under-commits whenever usage sits above the minimum in more than a (1 − d) share of hours.

**Illustrative worked example (made-up profile, not measured data).** Hourly usage is 100, 120, 140, 160 or 200 units, each in 20% of hours, so mean on-demand cost is 144 units/hour. Saving per hour at level L is E[min(usage, L)] − (1 − d)·L; percentages are of the 144 on-demand baseline.

| Commit level L | Saving at d = 0.3 | Saving at d = 0.5 |
|---|---|---|
| 75 (75% of minimum) | 75 − 52.5 = 22.5 (15.6%) | 75 − 37.5 = 37.5 (26.0%) |
| 100 (minimum) | 100 − 70 = 30.0 (20.8%) | 100 − 50 = 50.0 (34.7%) |
| 120 (d-quantile at d = 0.3: exceeded in 80% ≥ 70% of hours) | 116 − 84 = **32.0 (22.2%)** | 116 − 60 = 56.0 (38.9%) |
| 140 (d-quantile at d = 0.5: exceeded in 60% ≥ 50% of hours) | 128 − 98 = 30.0 (20.8%) | 128 − 70 = **58.0 (40.3%)** |

A brute-force search over every integer L from 0 to 200 returns the same optimum (120 at d = 0.3, 140 at d = 0.5), and the deeper discount moves the optimum up the distribution, as step 4 says.

### Instrument Shapes

The three large clouds offer the same three shapes; names, discounts, terms and payment options differ and change, so read them from the provider at decision time.

| Shape | Examples | Waste profile | Use for |
|---|---|---|---|
| Flexible spend commitment ($/hour across families, sizes, regions, some serverless) | AWS Compute Savings Plans, GCP flexible CUDs, Azure Savings Plans | Survives instance-family and region changes; lost only if total eligible spend drops below L | The default baseline layer |
| Resource commitment (specific family, size or region) | AWS Standard/Convertible RIs, GCP resource-based CUDs, Azure Reservations | Stranded if that exact shape shrinks or moves | Long-lived resources whose shape is fixed for the term (a production database instance class unchanged for a year) |
| Interruptible capacity (no commitment, reclaimable at short notice) | AWS Spot, GCP Spot VMs, Azure Spot | Interruption, not stranded spend | Batch, CI runners, checkpointed training, non-critical workers; never a synchronous path that cannot retry |

Checks before buying:

- **Application order.** When a resource commitment and a spend commitment could both cover the same usage, providers apply them in a fixed order, resource commitment first. AWS documents it explicitly: Reserved Instances apply before Savings Plans, EC2 Instance Savings Plans before Compute Savings Plans, and within a plan the usage with the highest savings percentage is covered first, with each hour's unused commitment forfeited (https://docs.aws.amazon.com/savingsplans/latest/userguide/sp-applying.html, read 2026-09-27). Azure applies savings-plan benefit the same way, highest-discount usage first, unused hourly commitment expiring (https://learn.microsoft.com/en-us/azure/cost-management-billing/savings-plan/savings-plan-overview). A spend commitment sized to include already-reserved capacity over-commits. Read the provider's application-order page at decision time and size each layer on the usage left after the layer applied before it.
- **Scope of the spend instrument.** Spend commitments cover a named list of services and usually only the infrastructure component: Azure's compute savings plan excludes software, networking and storage charges; AWS Compute Savings Plans cover EC2, Fargate and Lambda, while RDS and other database engines sit under a separate Database Savings Plan (https://aws.amazon.com/savingsplans/faq/). Pull the eligible-usage list from the provider before treating "compute spend" as the commitment base.
- **Sharing scope.** Check whether the billing account shares commitment discounts across projects or accounts, and whether that was left on or turned off for chargeback reasons. Shared discounts change both the usage series you size against and who sees the saving (see [Showback Before Chargeback](#showback-before-chargeback)).
- **Payment option.** Upfront payment trades cash for a deeper d; compare at your cost of capital, not by the discount alone.

### When NOT to Buy a Commitment

This is the judgment a checklist misses — the highest-value thing a FinOps lead does is talk a team out of a commitment, not into one.

- **Workload is under ~4-6 weeks old.** There is no usage floor to commit against yet. Run on-demand until a stable baseline exists.
- **An active migration, re-platform, or major refactor is in flight.** Committing mid-migration is the single most common source of stranded commitment spend — the cost of waiting a quarter is always smaller than the cost of a 1-3 year commitment against an architecture that is about to change.
- **The team is actively evaluating a move to serverless, spot, ARM-based instances, or a different cloud.** A commitment locks in the old shape and creates an internal disincentive to make the efficiency improvement, because the unused commitment becomes a sunk cost someone has to explain.
- **Usage is genuinely volatile (seasonal, promotional, or highly elastic product).** Commitments are a bet on a stable floor; volatile workloads should lean toward Spot/on-demand plus autoscaling instead.
- **The organization cannot forecast growth with reasonable confidence 6-12 months out.** A 3-year RI on a team that doesn't know its own trajectory is a bet the finance team is making on the engineering team's roadmap stability — make sure finance knows that's the bet.

### Exit Rules: What Happens When You Are Wrong

Terms are one or three years on all three clouds, and the exit rules differ enough to change which instrument to buy. Verified against the provider pages on 2026-09-27; re-read them at decision time because the Azure rules in particular carry announced changes.

| Provider and instrument | Exit path | Source |
|---|---|---|
| AWS Reserved Instances | Purchase cannot be cancelled; only Standard RIs can be resold on the RI Marketplace, Convertible RIs can be exchanged but not resold | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ri-market-concepts-buying.html |
| AWS Savings Plans | No cancellation or resale; the FAQ allows a return only for a plan at or under a small hourly commitment, within seven days of purchase and inside the same calendar month, so treat the purchase as final once that window closes. Committed rates are fixed for the term | https://aws.amazon.com/savingsplans/faq/ and https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html |
| GCP committed use discounts (resource-based and spend-based) | "You can't cancel a commitment after its purchase" | https://docs.cloud.google.com/compute/docs/instances/committed-use-discounts-overview |
| Azure savings plans | "Savings plan purchases can't be canceled or refunded" | https://learn.microsoft.com/en-us/azure/cost-management-billing/savings-plan/savings-plan-overview |
| Azure reservations | Refundable up to a rolling 12-month cap per billing scope (50,000 USD at time of reading, no early-termination fee currently charged but one is announced as possible); exchangeable within a product family, but reservations bought on or after 1 February 2027 for services a savings plan covers lose exchange rights, and earlier ones keep one final exchange; trade-in to a savings plan stays open | https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/exchange-and-refund-azure-reservations |

Consequences for the sizing decision:

- Where no exit exists (AWS Savings Plans, GCP CUDs, Azure savings plans), the d-quantile haircut for named risks is the only protection; do not size to the optimum and plan to "fix it later".
- Where a resale or refund path exists, it is capped or discounted; model the exit as a partial loss, not a free option.
- Azure's own recommended order is right-size, exchange under-utilised reservations, trade rigid reservations in for savings plans, then buy new reservations, then new savings plans (https://learn.microsoft.com/en-us/azure/cost-management-billing/savings-plan/decide-between-savings-plan-reservation). The same sequence transfers to the other clouds: fix existing commitments before adding any.
- Price changes: Azure states that savings-plan prices can change monthly and the current price applies to an active plan; AWS states the rate stays fixed through the term. Confirm which rule applies before comparing an upfront-paid instrument against a monthly one.

### Layered Commitment Strategy

The pattern that works in practice, across all three clouds: **baseline with the flexible spend-commitment instrument, pin down genuinely static long-lived resources with the resource-commitment instrument for its deeper discount, and route everything interruption-tolerant to interruptible capacity.** Size each layer with the d-quantile rule on the usage left after the layers applied before it. The total saving depends on how much of the workload is stable; do not quote a saving before establishing the stable-versus-volatile split.

---

## Egress and Storage-Class Traps

Two line items that grow silently after a "cost-saving" change. Rates are not carried here; the shapes are, with the lookup that feeds the decision.

### Egress and data transfer

- Inbound from the internet is free on the large clouds; outbound to the internet, between regions, and between availability zones inside a region is metered. Within one availability zone, transfer is free (AWS: https://aws.amazon.com/blogs/architecture/overview-of-data-transfer-costs-for-common-architectures/, read 2026-09-27). The trap: a multi-AZ deployment of a chatty service (database replicas, message brokers, service mesh sidecars) pays cross-AZ transfer in both directions for every hop.
- NAT gateways charge a per-GB processing fee on top of transfer; AWS traffic to S3 and DynamoDB through a NAT gateway pays that fee, while a gateway VPC endpoint in the same region removes it. Interface endpoints carry an hourly plus per-GB charge instead. Check the current fee table before choosing.
- Lookup step before any migration or "move to cheaper storage" recommendation: pull one month of transfer by direction (internet out, inter-region, inter-AZ, NAT processed) from the billing export, multiply by the current per-GB rates from the provider's data-transfer pricing page, and record the date. A host that is cheaper per GB stored can cost more once egress at forecast volume is added; the [R2 egress crossover](vendor-billing-guide.md#r2-egress-crossover) is the same arithmetic for object storage.
- Architecture levers, in order of effect: keep chatty pairs in one AZ where the availability budget allows and document the trade; put a CDN or cache in front of internet-facing reads; use gateway endpoints for S3/DynamoDB-class services; compress before transfer; move egress-heavy objects to a store with no egress charge.

### Storage classes

Every cooler storage class trades a lower per-GB-month rate for three penalties that a lifecycle policy can turn into a bill increase:

| Penalty | Shape | Provider examples (read 2026-09-27; confirm the table before acting) |
|---|---|---|
| Minimum storage duration | An object deleted, overwritten or transitioned before the minimum is billed for the full minimum, prorated on Azure | AWS S3: 30 days IA, 90 days Glacier Instant and Flexible, 180 days Deep Archive (https://aws.amazon.com/s3/storage-classes/). GCP: 30 Nearline, 90 Coldline, 365 Archive (https://docs.cloud.google.com/storage/docs/storage-classes). Azure Blob: 30 cool, 90 cold, 180 archive on general-purpose v2 accounts (https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview) |
| Retrieval charge | Per-GB fee on every read from a cool or archive class, plus higher per-operation prices | All three clouds charge retrieval on their infrequent-access and archive classes; archive classes on AWS and Azure also need a rehydration or restore step measured in hours (AWS Deep Archive quotes 12 to 48 hours; Azure archive up to 15 hours) |
| Minimum billable object size and per-object overhead | Small objects are billed as if larger, and archived objects carry metadata overhead | AWS bills a 128 KB minimum on Glacier Instant Retrieval and adds metadata per archived object; Intelligent-Tiering charges a per-object monitoring fee and does not auto-tier objects under 128 KB |

Decision rule: compute the break-even for a class change from the object age distribution and the read rate, not from the per-GB rate alone. A bucket of small, short-lived or regularly read objects loses money in a cooler class. Before enabling a transition rule, pull object count, size distribution, age distribution and monthly GET volume from the storage inventory or access logs; transition only prefixes whose objects live past the minimum duration and are read less often than the retrieval charge pays for. Never archive anything a restore drill will need inside the rehydration window, and treat "move everything older than 30 days to archive" as a proposal to test on one prefix for a billing cycle.

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

- **Open-source allocation engine** (OpenCost is the common one) — reads cluster requests and usage plus cloud billing data and allocates cost per namespace, label and workload.
- **Commercial allocation products** built on such engines add UI, alerting, multi-cluster rollups and governance. Before a multi-year contract, check the vendor's ownership, roadmap and the open-source project's governance status; acquisitions in this space have changed priorities before.
- **Automated rightsizing tools** — commercial tools that go beyond allocation into automated rightsizing and bin-packing (evicting/rescheduling workloads onto fewer, better-utilized nodes). Consider when allocation alone has revealed waste but the team lacks bandwidth to act on it manually.
- **Cloud-native cost tools** (AWS Cost and Usage Report + Kubernetes cost allocation tags, GCP Cost Table export, Azure Cost Management) can approximate allocation without a dedicated K8s tool, but require more manual mapping and lack the request-vs-usage view.

### Showback Before Chargeback

- **Showback** reports each team's allocated cost without moving money. Run it until the allocation is trusted: tag coverage is high, the unallocated share is small and owned, and teams have agreed the keys for shared cost.
- **Chargeback** moves the cost into team budgets. Switch only for teams that control their cost drivers; charging a team for cost it cannot change produces disputes, not savings.
- **Shared cost** (control plane, platform services, a shared GPU pool) is allocated by a documented key: request share, usage share or an even split. Publish the key and keep it stable within a budget period.
- **Commitment discounts** are passed to the consuming teams at the effective rate. If the buying team keeps the discount, other teams see on-demand rates and avoid covered resources, which strands the commitment.
- **Unallocated and untagged cost** is its own line with an owner and a target. It is the first sign that allocation has drifted.
- ML and LLM workloads also carry `model` and `model_version` tags so cost can be tied to a release; the ML-specific levers are in [ai-mlops ML Cost Levers](../../ai-mlops/references/cost-management-finops.md).

---

## GPU Capacity for AI Workloads

GPU capacity for self-hosted model training and inference follows the same commitment logic as general compute, with a shorter stable-usage bar because the GPU market and model landscape both move faster than general compute:

- **On-demand** for exploratory work, fine-tuning experiments, and any workload whose shape is not yet settled.
- **Reserved GPU capacity** suits production inference serving that runs around the clock against a model not expected to change within the term. Size it with the [d-quantile rule](#sizing-rule-commit-to-the-d-quantile), using the discount the provider quotes for that term.
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

The largest hidden cost in most cost-optimization exercises is not on the cloud bill — it's the engineering time spent implementing the optimization. A migration that saves $2,000/month but consumes six weeks of a senior engineer's time (loaded cost of, say, $15,000-25,000) takes roughly 7.5-12.5 months to pay back, and that estimate assumes the migration goes smoothly and doesn't introduce new operational burden (a new system to monitor, patch, and staff on-call for).

Before recommending an architecture change or platform migration for cost reasons, estimate:

1. **Implementation cost**: engineer-weeks × loaded cost per week.
2. **Ongoing operational cost**: does the new approach need monitoring, on-call, or specialized expertise the team doesn't currently have? Self-hosting anything (a database, a GPU inference stack, a Kubernetes cluster) converts a subscription line item into a permanent operational responsibility — that responsibility has a cost even when nothing goes wrong, and a much larger one when something does.
3. **Payback period**: implementation cost ÷ monthly savings. A payback period beyond 12 months for anything except foundational infrastructure is usually not worth the distraction from product work, unless the savings compound with growth (i.e., the saving scales with traffic, not just with today's traffic).
4. **Reversibility**: can this be undone cheaply if the assumption behind it turns out wrong? Prefer reversible optimizations (config changes, plan downgrades) over irreversible ones (a from-scratch platform migration) when the expected savings are similar.

This is the judgment that separates "found a way to save money" from "found a way to save money that was actually worth doing."

---

## AI Spend Governance for Platform/Infra Leads

AI/LLM spend is the fastest-growing and least-governed line item on many infrastructure bills, because it is easy for any engineer to add an API call to a paid model without going through the same review a new cloud resource would get. This is a governance gap, not a pricing problem, and pricing optimization (covered in [ai-api-cost-guide.md](ai-api-cost-guide.md)) does not fix it on its own.

- **Require a cost estimate before a new AI feature ships**, the same way a new database or a new cloud resource would get one. Model choice, expected volume, and prompt-caching design should be reviewed at design time, not discovered on the bill a month later.
- **Set per-feature and per-environment spending limits**, not just an org-wide cap — an org-wide cap gets hit by whichever team happened to ship last, and by the time it's hit, attribution to the responsible feature is much harder.
- **Track cost per unit of product value** (cost per resolved support ticket, cost per generated document, cost per completed agent task), not just cost per token — token efficiency can improve while unit economics get worse if quality drops and the feature needs more retries or human fallback.
- **Treat agentic/multi-step AI workloads as a distinct governance category.** A single user action that triggers a multi-agent loop, tool calls, and sub-agent delegation can consume an order of magnitude more tokens than a single request-response call, and the per-request cost is much less predictable. Log per-session and per-task cost, not just per-call cost, for anything agentic — see [ai-api-cost-guide.md — Per-Trace and Per-User Cost Attribution](ai-api-cost-guide.md#per-trace-and-per-user-cost-attribution).
- **Review model and pricing changes quarterly, not annually.** The AI API market re-prices and re-tiers models far more often than traditional cloud infrastructure — a cost review cadence built for annual cloud contract renewals will miss several pricing changes per year in this category.

---

## FinOps Framework Alignment

Use the Framework's own vocabulary when a stakeholder audience knows it (terms read from https://www.finops.org/framework/ and https://www.finops.org/framework/scopes/ on 2026-09-27; the Framework is revised, so confirm names before quoting them in a deliverable):

- **Phases**: Inform, Optimize, Operate. This skill's workflow maps inventory and audit to Inform, diagnose and optimize to Optimize, and verify and monitor to Operate.
- **Domains**: Understand Usage & Cost, Quantify Business Value, Optimize Usage & Cost, Manage the FinOps Practice. Unit economics sits under Quantify Business Value ([unit-economics-guide.md](unit-economics-guide.md)); commitment sizing and rightsizing sit under Optimize Usage & Cost.
- **Capabilities** are the activities inside a domain (allocation, forecasting, unit economics, rate optimization, and so on) and are applied across scopes rather than owned by one.
- **Scopes** are segments of technology spend aligned to a business construct (product, cost center, environment, an AI initiative); public cloud is the default first scope, and SaaS, data center, licensing and AI are named further scopes. Describe the SaaS-heavy stack this skill audits as its own scope rather than forcing it into a cloud-infrastructure framing, and set scope-specific maturity targets: a fast-moving AI feature scope can reasonably tolerate more waste than a stable production cloud scope.
- **Personas**: core personas are FinOps Practitioner, Engineering, Finance, Leadership, Procurement and Product; allied personas include ITAM, ITFM, ITSM, Security and Sustainability. Name the persona a recommendation is addressed to; a rightsizing action for Engineering and a commitment purchase for Finance and Procurement are different deliverables.
- **Maturity**: Crawl, Walk, Run. State which level a capability is at before proposing a Run-level control (automated rightsizing, chargeback) on a Crawl-level allocation.

---

## What a Top FinOps Lead Catches That a Checklist Misses

A checklist finds the same waste every quarter. A senior practitioner also catches:

- **The commitment that made sense a year ago and doesn't anymore** — a 3-year RI bought against an architecture the team has since replaced. Nobody proactively surfaces this; it just sits as sunk cost until someone specifically goes looking for utilization below 100% on existing commitments.
- **The team that optimized the wrong layer.** Engineering spent two sprints reducing Lambda invocation count by 40% when Lambda was 5% of the bill and the database was 60% — a checklist would have marked the Lambda work "done" without checking whether it moved the total.
- **The metric that looks efficient but is hiding a quality regression.** Cost-per-request dropped because a model-cascading change silently downgraded quality and users started retrying failed responses more often — total user-facing cost (including support and churn) went up while the infra line item went down.
- **The commitment or architecture decision nobody owns.** When a cost-saving migration breaks something six months later, "why did we do this" needs a documented owner and rationale — not a git blame exercise. Insist that cost-driven architecture decisions get the same lightweight design-doc treatment as feature work.
- **Growth that looks like waste and waste that looks like growth.** Distinguishing "this cost line grew because we got more customers" from "this cost line grew because something is misconfigured" is the single highest-leverage question in any review — see [unit-economics-guide.md — Profitable Growth vs Destructive Growth](unit-economics-guide.md#profitable-growth-vs-destructive-growth) for the diagnostic questions.
