# Data Mesh Patterns

Decide whether to adopt mesh, where domain boundaries go, what makes a data product, and how governance is split. Mesh is an ownership model; it runs on the same lakehouse, catalog, and medallion layers as a central platform.

## Ready for Data Mesh?

Adopt only if every answer is yes, in this order; the first "no" is the next thing to fix:

1. More than a few distinct business domains produce analytical data? (No -> a central team is cheaper.)
2. The central data team is the bottleneck? (No -> optimize the current model; do not restructure.)
3. Domain teams have, or can hire, data engineers? (No -> "ownership" means nobody owns it.)
4. Executive sponsorship across domains? (No -> domains resist the change.)
5. A self-serve platform exists? (No -> build it first, then migrate domains incrementally.)

Then start with 2-3 pilot domains that are willing and capable.

## Principles — and What They Do Not Mean

| Principle | Means | Does NOT mean |
|-----------|-------|---------------|
| Domain ownership | Domain teams own their analytical data | Every team builds infrastructure from scratch |
| Data as a product | SLOs, docs, schema contract, discoverability | Every dataset is a product (tier by criticality) |
| Self-serve platform | Shared infrastructure lowers per-domain effort | No central team |
| Federated governance | Global standards enforced by automation, local execution | No governance |

## Domain Boundaries

Boundary signals: different business capability, different source-of-truth systems, different stakeholders, different change cadence, different compliance class (PII-heavy vs public).

- [ ] Each domain maps to a business capability, not an org-chart team.
- [ ] Each domain owns its source-of-truth systems.
- [ ] Each domain can build and deploy its products independently.
- [ ] Cross-domain dependencies are explicit contracts; no cycles.

## Data Product — Required Components

A dataset is a product only when all of these exist: versioned schema contract; SLOs (freshness, completeness, and how accuracy is reconciled); documentation (business context, grain, column meaning); catalog registration; lineage (upstream and downstream consumers); automated quality tests; access policy with a request path; named owner and escalation path. Mark PII columns and their masking rule in the contract.

## Federated Governance

| Global (platform-enforced, automated) | Local (domain-owned) |
|---------------------------------------|----------------------|
| Naming conventions (CI lint) | Transformation logic |
| Schema contract registration (deploy gate) | Refresh frequency above the SLO minimum |
| Minimum test coverage (CI check) | Additional quality tests |
| PII classification (scanner + review) | Internal model structure |
| SLO declared in the product spec | Extra tools, from the platform catalog |
| Cost guardrails (limits, alerts) | Team process |

Enforce global standards as CI/deploy gates, not review comments; standards that are not automated drift per domain.

## Cross-Domain Contracts

Each contract names provider, consumer, table, required columns with nullability, freshness bound, provider-side tests (schema match, freshness, volume anomaly), consumer-side tests (referential integrity), and a **breaking-change policy**: advance notice period, notification channel, and consumer approval. Contract testing and metric governance: `data-analytics-engineering` skill.

## Migration: Centralized to Mesh

1. **Foundation** — readiness check, domain boundaries, platform MVP (templates, CI/CD, catalog, IAM roles per domain), global standards.
2. **Pilot** — 2-3 domains ship first products with hands-on platform support; first cross-domain contracts; measure time-to-production for a new data product.
3. **Scale** — onboard remaining domains incrementally; migrate central models to domain ownership; SLO monitoring and a product review process.
4. **Optimize** — governance retrospective, per-domain cost, maturity assessment.

Never big-bang: each phase gates the next on its measured result.

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| Mesh without a platform | Build self-serve first |
| Mesh in a small org | Stay central until the bottleneck is real |
| Central team renamed "platform" but still gatekeeps | Platform must enable self-serve, not approve every change |
| Every dataset is a "product" | Tier products by criticality |
| Implicit cross-domain dependencies | Explicit contracts with breaking-change policy |
| No executive mandate | Secure sponsorship before starting |

Related: [security-access-patterns.md](security-access-patterns.md) for cross-domain access; `data-analytics-engineering` (lake-data-quality-patterns, semantic-layer-patterns, metric-governance).
