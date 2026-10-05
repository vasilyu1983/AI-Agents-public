---
name: ops-cost-optimization
description: "Audits SaaS, cloud, payment, and AI spend. Use when analyzing bills, right-sizing plans, sizing Savings Plans or CUDs, cutting payment-processing fees, or LLM self-host breakeven."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-27
---

# SaaS/PaaS Cost Optimization

Use this skill to audit, reduce, and monitor infrastructure and SaaS spending. Keep the output operational: cost breakdown, waste identification, optimization actions, and monitoring setup.

## Quick Reference

| Need | Starting Reference | Notes |
|------|--------------------|-------|
| audit a SaaS or infrastructure vendor bill (Vercel, Supabase, Cloudflare, Stripe, GitHub/CI, monitoring, email, domains) | [references/vendor-billing-guide.md](references/vendor-billing-guide.md) | vendor lookup step, plan-tier crossover, per-vendor billing dimensions and ranked levers |
| audit payment processing | [references/vendor-billing-guide.md#stripe](references/vendor-billing-guide.md#stripe) | stacked-fee arithmetic, IC+ rule, payment mix, Radar break-even, volume negotiation |
| audit AI API spend or self-host vs API breakeven | [references/ai-api-cost-guide.md](references/ai-api-cost-guide.md) | cost-per-success model, prompt caching, batch API, model routing, breakeven formula |
| quantify uncertain cost or budget risk | [references/cost-uncertainty-method.md](references/cost-uncertainty-method.md) | reproducible Monte Carlo, joint empirical dependence, Morris screening |
| decide on AWS/GCP/Azure commitments or K8s cost allocation | [references/cloud-commitment-and-k8s-cost-guide.md](references/cloud-commitment-and-k8s-cost-guide.md) | d-quantile commitment sizing, instrument shapes (Savings Plans, RIs, CUDs, Spot), application order, exit rules per provider, when NOT to commit, showback before chargeback, GPU capacity, FinOps Framework vocabulary |
| cut egress or storage-class cost | [references/cloud-commitment-and-k8s-cost-guide.md#egress-and-storage-class-traps](references/cloud-commitment-and-k8s-cost-guide.md#egress-and-storage-class-traps) | cross-AZ and NAT charges, minimum storage duration, retrieval and rehydration, small-object minimums, break-even before a lifecycle rule |
| set up cost monitoring | [references/cost-monitoring-setup.md](references/cost-monitoring-setup.md) | budget alerts, review cadence, FOCUS normalization |
| track unit economics | [references/unit-economics-guide.md](references/unit-economics-guide.md) | cost per customer/feature/request, ARPC tracking, FOCUS standard |
| IaC cost guardrails in CI | [references/vendor-billing-guide.md#iac-cost-guardrails](references/vendor-billing-guide.md#iac-cost-guardrails) | Infracost PR diffs, budget-threshold merge gates |
| monthly cost review | [assets/monthly-cost-review-checklist.md](assets/monthly-cost-review-checklist.md) | reusable review template |
| automated cost audit from billing data | [agents/cost-auditor.md](agents/cost-auditor.md) | parses screenshots/API data, ranks top 5 cost drivers, outputs prioritized actions |

## Workflow

1. **inventory** — list all paid services, current plans, billing cycles, and monthly spend
2. **audit** — for each service: pull usage data, compare to plan limits, identify top cost drivers by dollar amount
3. **diagnose** — classify each cost line:
   - **necessary**: directly supports revenue or product function
   - **reducible**: supports function but can be lowered via architecture or configuration
   - **wasteful**: unused, over-provisioned, or cheaper alternative exists
4. **optimize** — load the platform-specific reference file and apply the highest-impact tactics first
5. **verify** — keep the estimate as a forecast until a comparable usage export or closed bill shows the change; normalize for traffic, seats, storage, and billing-period length
6. **monitor** — set up budget alerts, usage dashboards, and a monthly review cadence using [references/cost-monitoring-setup.md](references/cost-monitoring-setup.md)

### Uncertain cost decisions

Trigger this only when ranges or dependence can change the decision. Supply bounded distributions with units, dated provenance, distribution rationale, an auditable component formula, budget, draws, and seed; use [the example](assets/cost-uncertainty-example.json) as the input contract. Run `python3 scripts/cost_uncertainty.py --input assets/cost-uncertainty-example.json --sensitivity`. Read cost quantiles and modeled budget-exceedance probability separately from `simulation_error`; more draws reduce numerical error, not model uncertainty. Use deterministic arithmetic for fixed inputs, and fall back to low/base/high scenarios when probability weights or dependence cannot be defended.

## Decision Rules

- start with the highest-cost service and work down
- distinguish usage-based charges (optimizable) from flat subscriptions (right-size or cancel)
- check if the free tier covers actual usage before paying for a plan
- look up current prices with the [vendor price lookup](references/vendor-billing-guide.md#vendor-lookup-step) and record the date; the references carry no prices
- between two plan tiers, switch when forecast usage exceeds the [crossover](references/vendor-billing-guide.md#plan-tier-crossover) u* = q_A + (f_B − f_A) / r_A
- prefer architecture changes (caching, CDN, SSG, on-demand ISR) over plan upgrades
- compare annual vs monthly pricing — annual is usually cheaper; compute the difference from the vendor's price page, and take annual only for services you expect to keep for the whole term
- consolidate services when one platform covers several needs at a lower total cost; confirm on each candidate's plan page which needs its existing plan already bundles
- never optimize a $2/month line before a $20/month line
- when in doubt, measure for one billing cycle before cutting
- never buy a commitment (Savings Plan, RI, CUD, Reservation) against usage that hasn't been stable for 4-6+ weeks, or during an active migration/re-platform — see [references/cloud-commitment-and-k8s-cost-guide.md](references/cloud-commitment-and-k8s-cost-guide.md#when-not-to-buy-a-commitment)
- size a commitment at the d-quantile of hourly usage over the term (d = the quoted discount), not at a fixed fraction of the minimum; lower it only for a named decline, migration, or architecture risk. See [the sizing rule](references/cloud-commitment-and-k8s-cost-guide.md#sizing-rule-commit-to-the-d-quantile)
- treat every commitment as final: GCP CUDs and Azure savings plans cannot be cancelled, AWS Savings Plans only inside a short small-plan return window, and RI resale or Azure reservation refunds are capped; size with the haircut for named risks instead of planning to unwind later — see [exit rules](references/cloud-commitment-and-k8s-cost-guide.md#exit-rules-what-happens-when-you-are-wrong)
- before a storage lifecycle rule or a "cheaper storage" move, compute the break-even from object age distribution, read rate and transfer direction, not the per-GB rate; cooler classes bill a minimum duration, per-GB retrieval and small-object minimums, and egress is charged per direction — see [egress and storage-class traps](references/cloud-commitment-and-k8s-cost-guide.md#egress-and-storage-class-traps)
- separate zero-risk waste elimination from margin/durability trade-offs before cutting — a cut that reduces headroom or DR posture needs an explicit risk owner, not just a plan-tier downgrade
- weigh implementation and ongoing operational cost (engineer-time, new on-call burden) against savings before recommending a migration — a cheaper service that costs six weeks to adopt often doesn't pay back for a year
- mark each result `forecast`, `observed`, or `realized`; only `realized` means the saving appeared on a closed bill without an unacceptable SLO, support, security, or recovery regression

## Cost Categories

| Category | Examples | Optimization Lever |
|----------|----------|--------------------|
| compute | Vercel Functions, Supabase database, edge workers | reduce invocations, optimize cold starts, right-size memory |
| bandwidth | Fast Origin Transfer, database egress, CDN transfer | caching, compression, image optimization, SSG |
| storage | Supabase storage, R2, S3, blob stores | lifecycle policies only past the class minimum duration and read-rate break-even, compression, deduplication |
| per-request | ISR writes/reads, API calls, email sends | batching, caching, debouncing, on-demand invalidation |
| subscriptions | Pro plans, seats, add-ons | right-size plan tier, remove unused seats/add-ons |
| transaction fees | Stripe processing, dispute fees | volume negotiation, reduce disputes, batch payouts |
| AI tokens | LLM APIs, fine-tuning, self-hosted GPU inference | prompt caching, model routing, batch API, shorter prompts, spot/reserved GPU capacity |
| cloud commitments | AWS Savings Plans/RIs, GCP CUDs, Azure Reservations | size at the d-quantile of stable usage, layer flexible + rigid instruments, never commit mid-migration |
| K8s cluster cost | shared node pools, control plane, storage, load balancers | namespace/label cost allocation (OpenCost or a similar allocation tool), showback before chargeback, request-vs-usage rightsizing |

## When to Use This Skill

- monthly bill is higher than expected and you want to find what's driving it
- launching new projects and want to forecast infrastructure costs
- comparing free tier vs paid tier for a service
- setting up cost alerts and budget monitoring
- annual cost review and plan right-sizing
- evaluating whether to switch or consolidate services
- deciding whether to buy a Savings Plan, Reserved Instance, or Committed Use Discount, and how much
- allocating shared Kubernetes cluster cost back to teams or features
- governing AI/LLM spend before a new model-backed feature ships

## Route Elsewhere

- company-level burn rate, runway, and financial operations -> `startup-operating-system`
- infrastructure architecture and platform design -> [ops-devops-platform](../ops-devops-platform/SKILL.md)
- choosing between managed backend platforms -> [software-baas-platforms](../software-baas-platforms/SKILL.md)
- AI API integration patterns (not cost) -> [software-ai-integration](../software-ai-integration/SKILL.md)
- payment system design (not cost) -> [software-payments](../software-payments/SKILL.md)
- ML training and inference infrastructure levers (GPU scheduling, serving autoscaling, retraining cadence) -> [ai-mlops](../ai-mlops/SKILL.md)
- LLM serving efficiency (batching, quantization, KV cache, engine choice) -> [ai-llm-inference](../ai-llm-inference/SKILL.md)

---

## Optimization Playbook

### Quick wins (do first)

- remove unused projects, environments, and preview deployments
- switch time-based ISR revalidation to on-demand revalidation
- enable image optimization and compression
- check for services still on paid plans but no longer used
- stop paying separately for DNS when a provider you already use bundles it in your plan (check its plan page)

### Architecture changes (do next)

- move static content to CDN or SSG to reduce function invocations
- add response caching at edge to reduce origin transfer
- batch API calls and email sends instead of per-request
- use prompt caching for repeated AI API calls
- implement connection pooling to reduce database compute

### Plan optimization (do quarterly)

- compare current usage against plan tier limits
- evaluate annual vs monthly billing
- check if usage has dropped below the free tier threshold
- negotiate volume pricing when crossing tier boundaries
- remove unused seats and add-ons

## Anti-Patterns

- switching to a cheaper service without accounting for migration effort
- cutting costs that directly support revenue-generating features
- skipping monitoring setup — costs drift back up within months
- over-provisioning "just in case" without measuring actual usage

---

## Navigation

### Platform references

- [references/vendor-billing-guide.md](references/vendor-billing-guide.md)
- [references/ai-api-cost-guide.md](references/ai-api-cost-guide.md)
- [references/cloud-commitment-and-k8s-cost-guide.md](references/cloud-commitment-and-k8s-cost-guide.md)
- [references/cost-uncertainty-method.md](references/cost-uncertainty-method.md)

### Cross-platform

- [references/cost-monitoring-setup.md](references/cost-monitoring-setup.md)
- [references/unit-economics-guide.md](references/unit-economics-guide.md)
- [assets/monthly-cost-review-checklist.md](assets/monthly-cost-review-checklist.md)
- [assets/cost-uncertainty-example.json](assets/cost-uncertainty-example.json)
- [assets/cost-uncertainty-joint-example.json](assets/cost-uncertainty-joint-example.json)
- [scripts/cost_uncertainty.py](scripts/cost_uncertainty.py)
- [scripts/cost_estimator.py](scripts/cost_estimator.py) - Per-call LLM API cost from token counts and a dated `--pricing` file (alias `--prices`) you copy from the provider pricing pages on the day you estimate: `{"checked": "YYYY-MM-DD", "models": {"<id>": {"input_per_1m": ..., "output_per_1m": ...}}}`. It carries no prices, prices standard input/output only (cache, batch and long-context tiers are not modelled), and exits 2 on a missing or unreadable price file, a model listed twice, non-positive tokens, a future `checked` date, or prices older than `--max-age-days N`. The age limit has no default; set it whenever the estimate feeds a decision. [ai-bot-builder](../ai-bot-builder/SKILL.md)'s per-conversation estimator reads the same file.
- [data/sources.json](data/sources.json)

### Agents

- [agents/cost-auditor.md](agents/cost-auditor.md)

## Related Skills

- `startup-operating-system`
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)
- [../software-baas-platforms/SKILL.md](../software-baas-platforms/SKILL.md)
- [../software-payments/SKILL.md](../software-payments/SKILL.md)
- [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md)
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md)
- [../ai-llm-inference/SKILL.md](../ai-llm-inference/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
