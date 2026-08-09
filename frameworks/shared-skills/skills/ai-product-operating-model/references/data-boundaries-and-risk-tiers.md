# Data Boundaries And Risk Tiers

Use this reference when the user needs a durable company model for AI in product, not just one feature design.

## The Three Data Planes

| Plane | What belongs here | What does not |
| --- | --- | --- |
| Operational truth | User, org, billing, permissions, workflow state, system-of-record facts | Prompt history, loose embeddings treated as source of truth |
| AI context layer | Retrieved evidence, derived memory, reusable context bundles, grounding metadata | Raw mutable business truth copied without provenance |
| Analytics layer | Events, identities, semantic metrics, marts, BI/NLQ outputs | Runtime authorization decisions or model-facing context bundles |

Rule:

- fetch operational truth live
- assemble AI context intentionally
- govern analytics as a semantic layer

Do not collapse these into one database or one vendor product by default.

## Risk Tiers

| Tier | Typical data or action | Default posture |
| --- | --- | --- |
| `Tier 0` | Low-risk product data, no PI, non-destructive generation | External APIs allowed with standard logging, cost, and abuse controls |
| `Tier 1` | PI or moderate-risk business data, internal productivity, user-visible recommendations | External APIs allowed only with minimization, masking, tenant controls, and audit |
| `Tier 2` | Sensitive or high-impact flows: financial, legal, compliance, destructive actions, cross-tenant risk | Narrow provider allowlist, stronger isolation, explicit approval, stricter rollout gates |

## Minimum Controls By Tier

| Control | Tier 0 | Tier 1 | Tier 2 |
| --- | --- | --- | --- |
| Data minimization | Required | Required | Required |
| Field redaction or masking | Optional when no PI exists | Required for sensitive fields | Required and reviewed |
| Tenant isolation checks | Required for multi-tenant apps | Required | Required with explicit testing |
| Provider allowlist | Recommended | Required | Required and narrow |
| Mutating-tool approval | Case by case | Required for meaningful side effects | Required with human approval |
| Audit logging | Required | Required | Required with retention review |
| Offline evals | Required | Required | Required with adversarial pack |
| Canary rollout | Recommended | Required | Required with rollback thresholds |

## Default Provider Posture

- Start with external APIs first.
- Add managed private endpoints when isolation or network controls materially reduce risk.
- Treat self-hosting as an exception path that must beat managed options on a concrete mix of cost, latency, data posture, or regulatory constraints.

## Common Failure Modes

- Using the analytics warehouse as the runtime authorization source for AI features.
- Treating prompt logs as durable memory.
- Sending full user or org records to a model when a smaller projection would work.
- Choosing one provider posture for all workloads instead of tiering by risk.
- Letting product teams invent incompatible model wrappers, eval schemas, and audit events.

## Decision Rule

If the user cannot clearly answer:

- what is operational truth
- what is context
- what is analytics
- what is the risk tier
- who owns provider policy

then the operating model is not ready for scale.
